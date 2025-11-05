# Data Sources Guide

Complete guide for acquiring and preparing data for the Where to DINE project.

---

## Overview

This project requires three main data sources:
1. NYC Taxi trip records (drop-off locations)
2. Restaurant locations from OpenStreetMap
3. MTA transit data (GTFS)

---

## 1. NYC Taxi & Limousine Commission (TLC) Data

### About
NYC TLC provides open data on all taxi and for-hire vehicle trips in New York City.

### Download Links
- **Main Portal:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **AWS Open Data:** https://registry.opendata.aws/nyc-tlc-trip-records-pds/

### Recommended Datasets

**Yellow Taxi Trip Records:**
- Most comprehensive dataset
- Monthly files in Parquet format
- Files: `yellow_tripdata_YYYY-MM.parquet`

**For this project, use:**
- 1-3 months of recent data
- Focus on peak dining months (avoid January/February)
- Example: September 2023 - November 2023

### Data Schema

**Required Columns:**
```
tpep_dropoff_datetime    : Timestamp of drop-off
dropoff_longitude        : Longitude coordinate (deprecated in newer files)
dropoff_latitude         : Latitude coordinate (deprecated in newer files)
DOLocationID             : Taxi zone ID (newer files)
```

**Note:** Post-2016 files use location IDs instead of coordinates. You'll need to join with taxi zone lookup:
- **Lookup File:** https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv
- **Zone Shapefile:** https://data.cityofnewyork.us/Transportation/NYC-Taxi-Zones/d3c5-ddgc

### Download Example

```bash
# Using wget
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-09.parquet

# Or using curl
curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-09.parquet
```

### Python Download Script

```python
import requests

def download_taxi_data(year, month):
    """Download NYC TLC data for specific month"""
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
    filename = f"data/raw/taxi_trips_{year}_{month:02d}.parquet"

    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)

    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Saved to {filename}")

# Download September-November 2023
for month in [9, 10, 11]:
    download_taxi_data(2023, month)
```

### Data Size Warning

**File Sizes:**
- Single month: ~100-200 MB (Parquet)
- Uncompressed: ~1-2 GB
- Total rows: 2-4 million per month

**Processing Tips:**
- Use sampling (10-20% of data is sufficient)
- Process one month at a time
- Filter early (only dining hours)
- Use Parquet format (faster than CSV)

---

## 2. OpenStreetMap (OSM) Restaurant Data

### About
OpenStreetMap is a collaborative mapping project with detailed POI data including restaurants.

### Method 1: Using OSMnx (Recommended)

```python
import osmnx as ox
import geopandas as gpd

# NYC bounding box coordinates
north, south = 40.9176, 40.4774
east, west = -73.7004, -74.2591

# Query restaurants
tags = {'amenity': 'restaurant'}
restaurants = ox.geometries_from_bbox(north, south, east, west, tags)

# Extract relevant columns
restaurants_clean = restaurants[['name', 'cuisine', 'geometry']].copy()

# Convert to centroids (lat/lon)
restaurants_clean['longitude'] = restaurants_clean.geometry.centroid.x
restaurants_clean['latitude'] = restaurants_clean.geometry.centroid.y

# Save
restaurants_clean.to_csv('data/raw/restaurants_nyc.csv', index=False)
```

### Method 2: Overpass API

**Overpass Turbo:** https://overpass-turbo.eu/

**Query:**
```
[out:json][timeout:90];
(
  node["amenity"="restaurant"](40.4774,-74.2591,40.9176,-73.7004);
  way["amenity"="restaurant"](40.4774,-74.2591,40.9176,-73.7004);
  relation["amenity"="restaurant"](40.4774,-74.2591,40.9176,-73.7004);
);
out center;
```

Click "Export" → "GeoJSON"

### Method 3: NYC Open Data

**Alternative:** NYC Department of Health Restaurant Inspections
- **Link:** https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j
- **Advantage:** Includes inspection grades
- **Format:** CSV, API available

```bash
# Download via Socrata API
curl "https://data.cityofnewyork.us/resource/43nn-pn8j.json?\$limit=50000" > data/raw/nyc_restaurants.json
```

### Expected Data Format

```csv
name,cuisine,latitude,longitude,category
Joe's Pizza,pizza,40.7308,-74.0020,restaurant
Katz's Delicatessen,deli,40.7223,-73.9875,restaurant
Le Bernardin,french,40.7624,-73.9820,restaurant
```

---

## 3. MTA GTFS Data

### About
General Transit Feed Specification (GTFS) provides NYC subway and bus schedules.

### Download

**MTA GTFS Feeds:**
- **Subway:** http://web.mta.info/developers/data/nyct/subway/google_transit.zip
- **Bus (Manhattan):** http://web.mta.info/developers/data/nyct/bus/google_transit_manhattan.zip
- **Bus (Bronx):** http://web.mta.info/developers/data/nyct/bus/google_transit_bronx.zip
- **Bus (Brooklyn):** http://web.mta.info/developers/data/nyct/bus/google_transit_brooklyn.zip
- **Bus (Queens):** http://web.mta.info/developers/data/nyct/bus/google_transit_queens.zip
- **Bus (Staten Island):** http://web.mta.info/developers/data/nyct/bus/google_transit_staten_island.zip

### Download Script

```bash
mkdir -p data/raw/gtfs

# Download subway
wget -O data/raw/gtfs/subway.zip http://web.mta.info/developers/data/nyct/subway/google_transit.zip

# Download Manhattan bus
wget -O data/raw/gtfs/bus_manhattan.zip http://web.mta.info/developers/data/nyct/bus/google_transit_manhattan.zip

# Unzip
unzip data/raw/gtfs/subway.zip -d data/raw/gtfs/subway/
unzip data/raw/gtfs/bus_manhattan.zip -d data/raw/gtfs/bus_manhattan/
```

### GTFS File Structure

```
gtfs/
├── agency.txt          # Transit agencies
├── stops.txt           # Stop locations
├── routes.txt          # Route information
├── trips.txt           # Individual trips
├── stop_times.txt      # Stop sequences and times
├── calendar.txt        # Service schedules
└── shapes.txt          # Route geometries
```

### Processing with Python

```python
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load stops
stops = pd.read_csv('data/raw/gtfs/subway/stops.txt')

# Create GeoDataFrame
geometry = [Point(xy) for xy in zip(stops.stop_lon, stops.stop_lat)]
stops_gdf = gpd.GeoDataFrame(stops, geometry=geometry, crs='EPSG:4326')

# Save as GeoJSON
stops_gdf.to_file('data/processed/subway_stops.geojson', driver='GeoJSON')
```

### Using gtfs-kit

```python
import gtfs_kit as gk

# Load GTFS feed
feed = gk.read_feed('data/raw/gtfs/subway.zip', dist_units='km')

# Get stops as GeoDataFrame
stops = feed.stops

# Get routes
routes = feed.routes

# Get shapes (route geometries)
shapes = feed.shapes
```

---

## Additional Optional Data Sources

### 4. NYC Neighborhood Boundaries

**Link:** https://data.cityofnewyork.us/City-Government/Neighborhood-Tabulation-Areas-NTA-/cpf4-rkhq

**Use:** Label hotspots with neighborhood names

### 5. Census Data (Demographics)

**Link:** https://data.census.gov/

**Use:** Analyze correlations between demographics and dining patterns

### 6. Yelp Dataset

**Link:** https://www.yelp.com/dataset

**Use:** Validate hotspots with review data (requires application)

---

## Data Directory Structure

After downloading, organize like this:

```
data/
├── raw/
│   ├── restaurants_nyc.csv
│   ├── taxi_trips_2023_09.parquet
│   ├── taxi_trips_2023_10.parquet
│   ├── taxi_trips_2023_11.parquet
│   └── gtfs/
│       ├── subway.zip
│       └── subway/
│           ├── stops.txt
│           ├── routes.txt
│           └── ...
└── processed/
    ├── dining_zones.geojson
    ├── hotspot_arrival_areas.geojson
    └── final_hotspot_dining_areas.geojson
```

---

## Data Preparation Checklist

- [ ] Download NYC taxi data (1-3 months)
- [ ] Extract restaurant locations from OSM
- [ ] Download MTA GTFS subway data
- [ ] Verify file formats and column names
- [ ] Check coordinate systems (should be WGS84/EPSG:4326)
- [ ] Inspect data for null values and outliers
- [ ] Create backup of raw data
- [ ] Document data versions and download dates

---

## Storage Recommendations

### Local Development
- Store raw data in `data/raw/` (add to `.gitignore`)
- Only commit processed outputs if small (<10 MB)
- Use external drive for full datasets

### Team Sharing
- **Option 1:** Google Drive / Dropbox (sync `data/` folder)
- **Option 2:** AWS S3 / Google Cloud Storage
- **Option 3:** Git LFS (Large File Storage)

### Git LFS Setup

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.parquet"
git lfs track "*.geojson"

# Commit .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS"
```

---

## Data Update Frequency

- **Taxi Data:** Monthly (update quarterly for this project)
- **OSM Restaurants:** Weekly (extract once per project)
- **GTFS Transit:** Weekly (MTA updates regularly)

---

## Legal & Ethical Considerations

### NYC TLC Data
- **License:** Public domain
- **Attribution:** NYC Taxi & Limousine Commission
- **Privacy:** Data is anonymized (no passenger info)

### OpenStreetMap
- **License:** Open Database License (ODbL)
- **Attribution Required:** © OpenStreetMap contributors
- **Usage:** https://www.openstreetmap.org/copyright

### MTA GTFS
- **License:** Public domain (government data)
- **Attribution:** Metropolitan Transportation Authority

### Your Usage
- Always provide attribution in your app and documentation
- Don't redistribute large raw datasets
- Include data licenses in your LICENSE file

---

## Troubleshooting

**Problem:** Large files won't download
- **Solution:** Use `wget` or `curl` instead of browser
- **Solution:** Download during off-peak hours

**Problem:** OSMnx times out
- **Solution:** Reduce bounding box size
- **Solution:** Add `timeout=300` parameter
- **Solution:** Split into smaller queries

**Problem:** Coordinates seem wrong
- **Solution:** Check coordinate order (lon, lat vs lat, lon)
- **Solution:** Verify CRS is EPSG:4326 (WGS84)
- **Solution:** Some files use northing/easting

---

## Questions?

If you encounter issues with data acquisition:
1. Check the data source documentation
2. Search Stack Overflow / GIS Stack Exchange
3. Contact the data provider
4. Ask your instructor or TA

Happy data collecting!
