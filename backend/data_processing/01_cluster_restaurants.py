"""
Restaurant Clustering using HDBSCAN
Identifies dense dining zones from restaurant location data
"""

import pandas as pd
import numpy as np
from sklearn.cluster import HDBSCAN
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.ops import unary_union
import json


def load_restaurant_data(filepath):
    """
    Load restaurant location data from OSM or other sources
    Expected columns: name, longitude, latitude, category
    """
    print(f"Loading restaurant data from {filepath}...")

    # TODO: Replace with actual data loading
    # This is a placeholder structure
    df = pd.read_csv(filepath)

    print(f"Loaded {len(df)} restaurants")
    return df


def prepare_coordinates(df):
    """
    Prepare coordinate array for clustering
    """
    coords = df[['longitude', 'latitude']].values
    return coords


def cluster_restaurants(coords, min_cluster_size=5, min_samples=3):
    """
    Apply HDBSCAN clustering to restaurant locations

    Parameters:
    - coords: numpy array of (longitude, latitude) pairs
    - min_cluster_size: minimum number of points to form a cluster
    - min_samples: minimum number of points for core points

    Returns:
    - cluster labels for each point
    """
    print("Running HDBSCAN clustering...")

    # HDBSCAN works better with scaled coordinates
    # For geographic coordinates, we can use metric='haversine'
    # But first convert to radians
    coords_rad = np.radians(coords)

    clusterer = HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='haversine',
        cluster_selection_epsilon=0.001,  # ~111 meters in radians
        cluster_selection_method='eom'
    )

    labels = clusterer.fit_predict(coords_rad)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f"Found {n_clusters} restaurant clusters")
    print(f"Noise points: {n_noise}")

    return labels, clusterer


def create_dining_zone_polygons(df, labels):
    """
    Create polygon geometries for each dining zone cluster
    Uses convex hull around cluster points
    """
    print("Creating dining zone polygons...")

    df['cluster'] = labels

    # Filter out noise points (-1 label)
    clustered = df[df['cluster'] != -1].copy()

    zones = []

    for cluster_id in clustered['cluster'].unique():
        cluster_points = clustered[clustered['cluster'] == cluster_id]

        # Create points
        points = [Point(row['longitude'], row['latitude'])
                  for _, row in cluster_points.iterrows()]

        # Create convex hull
        if len(points) >= 3:
            multipoint = MultiPoint(points)
            polygon = multipoint.convex_hull

            # Buffer slightly to make zones more inclusive (0.001 degrees ~ 111m)
            polygon = polygon.buffer(0.001)

            zones.append({
                'cluster_id': int(cluster_id),
                'geometry': polygon,
                'restaurant_count': len(points),
                'restaurants': cluster_points['name'].tolist()[:10]  # Sample names
            })

    print(f"Created {len(zones)} dining zone polygons")

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(zones, crs='EPSG:4326')

    return gdf


def save_dining_zones(gdf, output_path):
    """
    Save dining zones to GeoJSON
    """
    print(f"Saving dining zones to {output_path}...")
    gdf.to_file(output_path, driver='GeoJSON')
    print("Saved successfully")


def main():
    """
    Main execution pipeline
    """
    print("=" * 50)
    print("RESTAURANT CLUSTERING PIPELINE")
    print("=" * 50)

    # Configuration
    INPUT_FILE = '../data/raw/restaurants_nyc.csv'
    OUTPUT_FILE = '../data/processed/dining_zones.geojson'

    # Parameters
    MIN_CLUSTER_SIZE = 5
    MIN_SAMPLES = 3

    try:
        # Load data
        df = load_restaurant_data(INPUT_FILE)

        # Prepare coordinates
        coords = prepare_coordinates(df)

        # Cluster
        labels, clusterer = cluster_restaurants(
            coords,
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=MIN_SAMPLES
        )

        # Create polygons
        gdf = create_dining_zone_polygons(df, labels)

        # Save results
        save_dining_zones(gdf, OUTPUT_FILE)

        print("\n" + "=" * 50)
        print("CLUSTERING COMPLETE")
        print("=" * 50)

    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
        print("Please ensure restaurant data is available in data/raw/")
    except Exception as e:
        print(f"Error during processing: {e}")
        raise


if __name__ == "__main__":
    main()
