"""
Restaurant Clustering using HDBSCAN
Identifies dense dining zones from restaurant location data

Supports both Google Maps and OpenStreetMap data formats
"""

import pandas as pd
import numpy as np
from sklearn.cluster import HDBSCAN
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.ops import unary_union
import json
import os


def detect_data_source(df):
    """
    Detect whether data is from Google Maps or OpenStreetMap
    based on column names
    """
    if 'place_id' in df.columns and 'rating' in df.columns:
        return 'google_maps'
    elif 'amenity' in df.columns or 'cuisine' in df.columns:
        return 'openstreetmap'
    else:
        return 'unknown'


def load_restaurant_data(filepath):
    """
    Load restaurant location data from Google Maps or OpenStreetMap

    Supported formats:
    - Google Maps: place_id, name, address, latitude, longitude, rating, etc.
    - OpenStreetMap: name, latitude, longitude, cuisine, amenity, etc.
    """
    print(f"Loading restaurant data from {filepath}...")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Load CSV
    df = pd.read_csv(filepath)

    # Detect data source
    source = detect_data_source(df)
    print(f"Detected data source: {source.upper()}")

    # Ensure required columns exist
    required_cols = ['name', 'latitude', 'longitude']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Remove rows with invalid coordinates
    original_count = len(df)
    df = df.dropna(subset=['latitude', 'longitude'])

    # Filter to reasonable NYC bounds
    df = df[
        (df['latitude'] >= 40.4) &
        (df['latitude'] <= 41.0) &
        (df['longitude'] >= -74.3) &
        (df['longitude'] <= -73.7)
    ]

    filtered_count = original_count - len(df)
    if filtered_count > 0:
        print(f"Filtered out {filtered_count} restaurants with invalid/out-of-bounds coordinates")

    print(f"Loaded {len(df)} valid restaurants")

    return df, source


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
    - clusterer object
    """
    print(f"Running HDBSCAN clustering...")
    print(f"  Parameters: min_cluster_size={min_cluster_size}, min_samples={min_samples}")

    # Convert to radians for haversine metric
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

    print(f"✅ Found {n_clusters} restaurant clusters")
    print(f"   Noise points: {n_noise} ({n_noise/len(labels)*100:.1f}%)")

    return labels, clusterer


def create_dining_zone_polygons(df, labels, source='unknown'):
    """
    Create polygon geometries for each dining zone cluster
    Uses convex hull around cluster points

    Parameters:
    - df: DataFrame with restaurant data
    - labels: cluster labels from HDBSCAN
    - source: data source ('google_maps' or 'openstreetmap')
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

            # Extract additional info based on data source
            zone_info = {
                'cluster_id': int(cluster_id),
                'geometry': polygon,
                'restaurant_count': len(points),
                'restaurants': cluster_points['name'].dropna().tolist()[:10],  # Sample names
            }

            # Add source-specific attributes
            if source == 'google_maps':
                # Calculate average rating
                if 'rating' in cluster_points.columns:
                    avg_rating = cluster_points['rating'].mean()
                    zone_info['avg_rating'] = round(avg_rating, 2) if not pd.isna(avg_rating) else None

                # Calculate average price level
                if 'price_level' in cluster_points.columns:
                    avg_price = cluster_points['price_level'].mean()
                    zone_info['avg_price_level'] = round(avg_price, 1) if not pd.isna(avg_price) else None

                # Count total ratings
                if 'user_ratings_total' in cluster_points.columns:
                    total_ratings = cluster_points['user_ratings_total'].sum()
                    zone_info['total_user_ratings'] = int(total_ratings) if not pd.isna(total_ratings) else 0

            elif source == 'openstreetmap':
                # Most common cuisines
                if 'cuisine' in cluster_points.columns:
                    cuisines = cluster_points['cuisine'].dropna()
                    if len(cuisines) > 0:
                        # Split cuisines (might be semicolon-separated)
                        all_cuisines = []
                        for c in cuisines:
                            all_cuisines.extend([x.strip() for x in str(c).split(';')])

                        from collections import Counter
                        cuisine_counts = Counter(all_cuisines)
                        top_3_cuisines = [c for c, _ in cuisine_counts.most_common(3)]
                        zone_info['top_cuisines'] = top_3_cuisines

            zones.append(zone_info)

    print(f"✅ Created {len(zones)} dining zone polygons")

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(zones, crs='EPSG:4326')

    return gdf


def save_dining_zones(gdf, output_path):
    """
    Save dining zones to GeoJSON
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Saving dining zones to {output_path}...")
    gdf.to_file(output_path, driver='GeoJSON')

    # Get file size
    file_size = os.path.getsize(output_path) / 1024  # KB
    print(f"✅ Saved successfully ({file_size:.1f} KB)")


def print_statistics(gdf):
    """
    Print statistics about the dining zones
    """
    print("\n" + "=" * 60)
    print("📊 DINING ZONES STATISTICS")
    print("=" * 60)

    print(f"\nTotal dining zones: {len(gdf)}")
    print(f"Total restaurants in clusters: {gdf['restaurant_count'].sum()}")
    print(f"Average restaurants per zone: {gdf['restaurant_count'].mean():.1f}")
    print(f"Largest zone: {gdf['restaurant_count'].max()} restaurants")
    print(f"Smallest zone: {gdf['restaurant_count'].min()} restaurants")

    if 'avg_rating' in gdf.columns:
        avg_rating = gdf['avg_rating'].mean()
        print(f"\nAverage rating across zones: {avg_rating:.2f}/5.0")

    if 'top_cuisines' in gdf.columns:
        print(f"\nSample of popular cuisines:")
        for i, cuisines in enumerate(gdf['top_cuisines'].head(5), 1):
            if cuisines:
                print(f"  Zone {i}: {', '.join(cuisines)}")

    print("=" * 60)


def main():
    """
    Main execution pipeline
    """
    print("=" * 60)
    print("🍽️  RESTAURANT CLUSTERING PIPELINE")
    print("=" * 60)

    # Configuration - Try both Google Maps and OSM
    POSSIBLE_INPUT_FILES = [
        '../data/raw/restaurants_nyc_googlemaps.csv',
        '../data/raw/restaurants_nyc_osm.csv',
        '../data/raw/restaurants_nyc.csv'
    ]

    OUTPUT_FILE = '../data/processed/dining_zones.geojson'

    # Find available input file
    INPUT_FILE = None
    for file_path in POSSIBLE_INPUT_FILES:
        if os.path.exists(file_path):
            INPUT_FILE = file_path
            break

    if INPUT_FILE is None:
        print("\n❌ Error: No restaurant data file found!")
        print("\nPlease ensure one of these files exists:")
        for f in POSSIBLE_INPUT_FILES:
            print(f"  - {f}")
        print("\nRun the data collection notebooks first!")
        return

    print(f"\n📂 Using input file: {INPUT_FILE}")

    # Parameters
    MIN_CLUSTER_SIZE = 8  # Increased for better quality clusters
    MIN_SAMPLES = 4

    try:
        # Load data
        df, source = load_restaurant_data(INPUT_FILE)

        # Prepare coordinates
        coords = prepare_coordinates(df)

        # Cluster
        labels, clusterer = cluster_restaurants(
            coords,
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=MIN_SAMPLES
        )

        # Create polygons
        gdf = create_dining_zone_polygons(df, labels, source)

        # Save results
        save_dining_zones(gdf, OUTPUT_FILE)

        # Print statistics
        print_statistics(gdf)

        print("\n" + "=" * 60)
        print("✅ CLUSTERING COMPLETE")
        print("=" * 60)
        print(f"\n📄 Output saved to: {OUTPUT_FILE}")
        print(f"🎯 Next step: Run 02_cluster_taxi_dropoffs.py")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease run the data collection notebooks first!")
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
