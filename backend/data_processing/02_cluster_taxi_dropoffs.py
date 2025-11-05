"""
Taxi Drop-off Clustering using HDBSCAN
Identifies hotspot arrival areas from NYC TLC trip records
"""

import pandas as pd
import numpy as np
from sklearn.cluster import HDBSCAN
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from datetime import datetime, time
import json


def load_taxi_data(filepath, sample_frac=0.1):
    """
    Load NYC TLC taxi trip records
    Expected columns: dropoff_longitude, dropoff_latitude, dropoff_datetime

    Parameters:
    - filepath: path to taxi data (CSV or parquet)
    - sample_frac: fraction of data to sample (for memory management)
    """
    print(f"Loading taxi data from {filepath}...")

    # TLC data is large, so we sample
    if filepath.endswith('.parquet'):
        df = pd.read_parquet(filepath)
    else:
        df = pd.read_csv(filepath)

    # Sample if dataset is too large
    if sample_frac < 1.0:
        df = df.sample(frac=sample_frac, random_state=42)

    print(f"Loaded {len(df)} trip records")
    return df


def filter_dining_hours(df, datetime_col='dropoff_datetime'):
    """
    Filter for dining hours and add time-based weights

    Dining hours:
    - Weekday lunch: 11:30 AM - 2:00 PM (weight: 0.8)
    - Weekday dinner: 6:00 PM - 9:30 PM (weight: 1.0)
    - Weekend lunch: 12:00 PM - 3:00 PM (weight: 0.9)
    - Weekend dinner: 6:00 PM - 10:30 PM (weight: 1.0)
    """
    print("Filtering for dining hours...")

    df[datetime_col] = pd.to_datetime(df[datetime_col])
    df['hour'] = df[datetime_col].dt.hour
    df['minute'] = df[datetime_col].dt.minute
    df['dayofweek'] = df[datetime_col].dt.dayofweek  # 0=Monday, 6=Sunday
    df['is_weekend'] = df['dayofweek'] >= 5

    def get_dining_weight(row):
        """Assign weight based on time and day"""
        hour = row['hour']
        minute = row['minute']
        is_weekend = row['is_weekend']

        time_decimal = hour + minute / 60.0

        # Weekday
        if not is_weekend:
            # Lunch: 11:30 - 14:00
            if 11.5 <= time_decimal <= 14.0:
                return 0.8
            # Dinner: 18:00 - 21:30
            elif 18.0 <= time_decimal <= 21.5:
                return 1.0
        # Weekend
        else:
            # Lunch: 12:00 - 15:00
            if 12.0 <= time_decimal <= 15.0:
                return 0.9
            # Dinner: 18:00 - 22:30
            elif 18.0 <= time_decimal <= 22.5:
                return 1.0

        return 0  # Outside dining hours

    df['weight'] = df.apply(get_dining_weight, axis=1)

    # Filter only dining hours
    df_dining = df[df['weight'] > 0].copy()

    print(f"Filtered to {len(df_dining)} trips during dining hours")
    print(f"Original: {len(df)} trips")

    return df_dining


def prepare_weighted_coordinates(df):
    """
    Prepare coordinates with weights for clustering
    Duplicate points based on weights to influence clustering
    """
    coords_list = []

    for _, row in df.iterrows():
        lon, lat = row['dropoff_longitude'], row['dropoff_latitude']
        weight = int(row['weight'] * 10)  # Convert to integer multiplier

        # Add point multiple times based on weight
        for _ in range(weight):
            coords_list.append([lon, lat])

    coords = np.array(coords_list)
    print(f"Prepared {len(coords)} weighted coordinate points")

    return coords


def cluster_taxi_dropoffs(coords, min_cluster_size=10, min_samples=5):
    """
    Apply HDBSCAN clustering to taxi drop-off locations
    """
    print("Running HDBSCAN clustering on taxi drop-offs...")

    # Convert to radians for haversine metric
    coords_rad = np.radians(coords)

    clusterer = HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='haversine',
        cluster_selection_epsilon=0.001,
        cluster_selection_method='eom'
    )

    labels = clusterer.fit_predict(coords_rad)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f"Found {n_clusters} hotspot arrival clusters")
    print(f"Noise points: {n_noise}")

    return labels, clusterer


def create_hotspot_polygons(coords, labels):
    """
    Create polygon geometries for hotspot arrival areas
    """
    print("Creating hotspot polygons...")

    df = pd.DataFrame(coords, columns=['longitude', 'latitude'])
    df['cluster'] = labels

    # Filter noise
    clustered = df[df['cluster'] != -1].copy()

    hotspots = []

    for cluster_id in clustered['cluster'].unique():
        cluster_points = clustered[clustered['cluster'] == cluster_id]

        points = [Point(row['longitude'], row['latitude'])
                  for _, row in cluster_points.iterrows()]

        if len(points) >= 3:
            multipoint = MultiPoint(points)
            polygon = multipoint.convex_hull
            polygon = polygon.buffer(0.0015)  # Slightly larger buffer

            hotspots.append({
                'cluster_id': int(cluster_id),
                'geometry': polygon,
                'dropoff_count': len(points),
                'popularity_score': min(100, len(points) / 10)  # Normalize to 0-100
            })

    print(f"Created {len(hotspots)} hotspot polygons")

    gdf = gpd.GeoDataFrame(hotspots, crs='EPSG:4326')

    return gdf


def save_hotspots(gdf, output_path):
    """
    Save hotspot areas to GeoJSON
    """
    print(f"Saving hotspots to {output_path}...")
    gdf.to_file(output_path, driver='GeoJSON')
    print("Saved successfully")


def main():
    """
    Main execution pipeline
    """
    print("=" * 50)
    print("TAXI DROP-OFF CLUSTERING PIPELINE")
    print("=" * 50)

    # Configuration
    INPUT_FILE = '../data/raw/taxi_trips_nyc.csv'
    OUTPUT_FILE = '../data/processed/hotspot_arrival_areas.geojson'

    # Parameters
    SAMPLE_FRACTION = 0.1  # Use 10% of data for faster processing
    MIN_CLUSTER_SIZE = 10
    MIN_SAMPLES = 5

    try:
        # Load data
        df = load_taxi_data(INPUT_FILE, sample_frac=SAMPLE_FRACTION)

        # Filter dining hours and add weights
        df_dining = filter_dining_hours(df)

        # Prepare weighted coordinates
        coords = prepare_weighted_coordinates(df_dining)

        # Cluster
        labels, clusterer = cluster_taxi_dropoffs(
            coords,
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=MIN_SAMPLES
        )

        # Create polygons
        gdf = create_hotspot_polygons(coords, labels)

        # Save results
        save_hotspots(gdf, OUTPUT_FILE)

        print("\n" + "=" * 50)
        print("CLUSTERING COMPLETE")
        print("=" * 50)

    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
        print("Please download NYC TLC data from: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page")
    except Exception as e:
        print(f"Error during processing: {e}")
        raise


if __name__ == "__main__":
    main()
