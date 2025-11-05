"""
Combine Dining Zones and Hotspot Arrival Areas
Creates final hotspot dining areas through spatial intersection
"""

import geopandas as gpd
from shapely.ops import unary_union
import json


def load_geojson(filepath):
    """
    Load GeoJSON file as GeoDataFrame
    """
    print(f"Loading {filepath}...")
    gdf = gpd.read_file(filepath)
    print(f"Loaded {len(gdf)} features")
    return gdf


def combine_hotspots(dining_zones, arrival_areas):
    """
    Perform spatial intersection to find areas that are both:
    1. Dense with restaurants (dining zones)
    2. Popular destinations (arrival areas)

    Returns GeoDataFrame of final hotspot dining areas
    """
    print("Combining dining zones and arrival areas...")

    # Perform spatial intersection
    hotspot_dining_areas = gpd.overlay(
        dining_zones,
        arrival_areas,
        how='intersection'
    )

    # Calculate combined score
    hotspot_dining_areas['combined_score'] = (
        (hotspot_dining_areas['restaurant_count'] /
         hotspot_dining_areas['restaurant_count'].max() * 50) +
        (hotspot_dining_areas['popularity_score'])
    )

    # Sort by score
    hotspot_dining_areas = hotspot_dining_areas.sort_values(
        'combined_score',
        ascending=False
    ).reset_index(drop=True)

    # Add ranking
    hotspot_dining_areas['rank'] = range(1, len(hotspot_dining_areas) + 1)

    # Generate names
    hotspot_dining_areas['name'] = hotspot_dining_areas.apply(
        lambda row: f"Dining Hotspot #{row['rank']}", axis=1
    )

    print(f"Created {len(hotspot_dining_areas)} final hotspot dining areas")

    return hotspot_dining_areas


def calculate_statistics(gdf):
    """
    Calculate statistics for the hotspot areas
    """
    stats = {
        'total_hotspots': len(gdf),
        'avg_restaurant_count': gdf['restaurant_count'].mean(),
        'avg_popularity_score': gdf['popularity_score'].mean(),
        'avg_combined_score': gdf['combined_score'].mean(),
        'total_area_km2': gdf.geometry.area.sum() * 111 * 111  # Rough conversion
    }

    print("\nStatistics:")
    print(f"  Total Hotspots: {stats['total_hotspots']}")
    print(f"  Avg Restaurants per Hotspot: {stats['avg_restaurant_count']:.1f}")
    print(f"  Avg Popularity Score: {stats['avg_popularity_score']:.1f}")
    print(f"  Avg Combined Score: {stats['avg_combined_score']:.1f}")

    return stats


def save_hotspot_dining_areas(gdf, output_geojson, output_stats):
    """
    Save final hotspot dining areas
    """
    print(f"\nSaving hotspot dining areas to {output_geojson}...")

    # Select relevant columns
    output_gdf = gdf[[
        'rank',
        'name',
        'restaurant_count',
        'popularity_score',
        'combined_score',
        'geometry'
    ]].copy()

    # Save as GeoJSON
    output_gdf.to_file(output_geojson, driver='GeoJSON')

    # Calculate and save statistics
    stats = calculate_statistics(gdf)

    with open(output_stats, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"Saved statistics to {output_stats}")
    print("Save complete!")


def main():
    """
    Main execution pipeline
    """
    print("=" * 50)
    print("HOTSPOT COMBINATION PIPELINE")
    print("=" * 50)

    # Input files
    DINING_ZONES_FILE = '../data/processed/dining_zones.geojson'
    ARRIVAL_AREAS_FILE = '../data/processed/hotspot_arrival_areas.geojson'

    # Output files
    OUTPUT_GEOJSON = '../data/processed/final_hotspot_dining_areas.geojson'
    OUTPUT_STATS = '../data/processed/hotspot_statistics.json'

    try:
        # Load data
        dining_zones = load_geojson(DINING_ZONES_FILE)
        arrival_areas = load_geojson(ARRIVAL_AREAS_FILE)

        # Combine
        hotspot_dining_areas = combine_hotspots(dining_zones, arrival_areas)

        # Save results
        save_hotspot_dining_areas(
            hotspot_dining_areas,
            OUTPUT_GEOJSON,
            OUTPUT_STATS
        )

        print("\n" + "=" * 50)
        print("COMBINATION COMPLETE")
        print("=" * 50)

    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
        print("Please run clustering scripts first:")
        print("  1. python 01_cluster_restaurants.py")
        print("  2. python 02_cluster_taxi_dropoffs.py")
    except Exception as e:
        print(f"Error during processing: {e}")
        raise


if __name__ == "__main__":
    main()
