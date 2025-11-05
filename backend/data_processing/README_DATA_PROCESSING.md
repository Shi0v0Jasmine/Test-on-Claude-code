# Data Processing Pipeline

This directory contains Python scripts for processing NYC dining data and generating hotspot recommendations.

## Pipeline Overview

The data processing pipeline consists of three main steps:

```
1. Restaurant Clustering  → dining_zones.geojson
2. Taxi Drop-off Clustering → hotspot_arrival_areas.geojson
3. Spatial Combination → final_hotspot_dining_areas.geojson
```

## Scripts

### 1. `01_cluster_restaurants.py`
Identifies dense dining zones from restaurant location data using HDBSCAN clustering.

**Input:**
- `data/raw/restaurants_nyc.csv` - Restaurant locations from OpenStreetMap

**Output:**
- `data/processed/dining_zones.geojson` - Polygon features of restaurant clusters

**Key Parameters:**
- `MIN_CLUSTER_SIZE`: Minimum restaurants to form a cluster (default: 5)
- `MIN_SAMPLES`: Minimum core points (default: 3)

### 2. `02_cluster_taxi_dropoffs.py`
Identifies hotspot arrival areas from NYC TLC taxi trip records.

**Input:**
- `data/raw/taxi_trips_nyc.csv` - NYC TLC trip records

**Output:**
- `data/processed/hotspot_arrival_areas.geojson` - Polygon features of popular drop-off clusters

**Key Parameters:**
- `SAMPLE_FRACTION`: Fraction of data to process (default: 0.1 for 10%)
- `MIN_CLUSTER_SIZE`: Minimum trips to form a cluster (default: 10)
- `MIN_SAMPLES`: Minimum core points (default: 5)

**Time Weighting:**
- Weekday lunch (11:30-14:00): 0.8
- Weekday dinner (18:00-21:30): 1.0
- Weekend lunch (12:00-15:00): 0.9
- Weekend dinner (18:00-22:30): 1.0

### 3. `03_combine_hotspots.py`
Combines dining zones and arrival areas through spatial intersection.

**Inputs:**
- `data/processed/dining_zones.geojson`
- `data/processed/hotspot_arrival_areas.geojson`

**Outputs:**
- `data/processed/final_hotspot_dining_areas.geojson` - Final hotspot polygons
- `data/processed/hotspot_statistics.json` - Summary statistics

**Scoring Formula:**
```
combined_score = (normalized_restaurant_count * 50) + popularity_score
```

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## Usage

Run scripts in order:

```bash
# Step 1: Cluster restaurants
python 01_cluster_restaurants.py

# Step 2: Cluster taxi drop-offs
python 02_cluster_taxi_dropoffs.py

# Step 3: Combine results
python 03_combine_hotspots.py
```

Or run all at once:
```bash
python run_pipeline.py
```

## Data Sources

### Restaurant Data (OpenStreetMap)
Download using OSMnx or Overpass API:

```python
import osmnx as ox

# NYC bounding box
north, south, east, west = 40.9176, 40.4774, -73.7004, -74.2591

# Query restaurants
tags = {'amenity': 'restaurant'}
restaurants = ox.geometries_from_bbox(north, south, east, west, tags)
```

### NYC TLC Taxi Data
Download from: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Required columns:
- `dropoff_longitude`
- `dropoff_latitude`
- `dropoff_datetime`

### MTA GTFS Data
Download from: http://web.mta.info/developers/developer-data-terms.html

## Output Format

Final GeoJSON structure:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "rank": 1,
        "name": "Dining Hotspot #1",
        "restaurant_count": 45,
        "popularity_score": 87.5,
        "combined_score": 92.3
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      }
    }
  ]
}
```

## Troubleshooting

**Import errors:**
```bash
pip install --upgrade geopandas hdbscan
```

**Memory issues with taxi data:**
- Reduce `SAMPLE_FRACTION` in script
- Process data in chunks
- Use more powerful machine or cloud computing

**Clustering produces too few/many clusters:**
- Adjust `min_cluster_size` and `min_samples`
- Lower values = more clusters
- Higher values = fewer, denser clusters
