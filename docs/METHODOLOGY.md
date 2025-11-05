# Methodology

Detailed technical methodology for the Where to DINE recommendation system.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Collection](#data-collection)
3. [Hotspot Identification](#hotspot-identification)
4. [Accessibility Analysis](#accessibility-analysis)
5. [Recommendation Algorithm](#recommendation-algorithm)
6. [Validation](#validation)

---

## Overview

The Where to DINE system uses a three-stage pipeline:

```
Stage 1: Hotspot Identification
├── Restaurant Clustering (HDBSCAN)
├── Taxi Drop-off Clustering (HDBSCAN)
└── Spatial Intersection

Stage 2: Accessibility Analysis
├── Multi-modal Network Construction
├── Service Area Calculation
└── Isochrone Generation

Stage 3: Recommendation Engine
├── Spatial Query (Within Service Areas)
├── Scoring Algorithm
└── Ranking and Display
```

---

## Data Collection

### 1. Restaurant Data

**Source:** OpenStreetMap

**Extraction Method:**
```python
import osmnx as ox

# NYC bounding box
north, south, east, west = 40.9176, 40.4774, -73.7004, -74.2591

# Query
tags = {'amenity': 'restaurant'}
restaurants = ox.geometries_from_bbox(north, south, east, west, tags)
```

**Data Cleaning:**
- Remove duplicates (same name + location within 50m)
- Filter out closed restaurants
- Validate coordinates (within NYC bounds)
- Extract centroids from polygon geometries

**Expected Output:** ~20,000-30,000 restaurant points

### 2. Taxi Trip Data

**Source:** NYC TLC Trip Records

**Temporal Filtering:**

Dining hours are defined as:

| Period | Weekday | Weekend |
|--------|---------|---------|
| Lunch | 11:30 AM - 2:00 PM | 12:00 PM - 3:00 PM |
| Dinner | 6:00 PM - 9:30 PM | 6:00 PM - 10:30 PM |

**Weighting Scheme:**
```python
def calculate_weight(datetime, is_weekend):
    hour = datetime.hour
    time_decimal = hour + datetime.minute / 60.0

    if not is_weekend:
        if 11.5 <= time_decimal <= 14.0: return 0.8  # Weekday lunch
        if 18.0 <= time_decimal <= 21.5: return 1.0  # Weekday dinner
    else:
        if 12.0 <= time_decimal <= 15.0: return 0.9  # Weekend lunch
        if 18.0 <= time_decimal <= 22.5: return 1.0  # Weekend dinner

    return 0  # Outside dining hours
```

**Spatial Filtering:**
- NYC bounding box only
- Remove invalid coordinates (0,0) or outliers
- Remove trips to airports (JFK, LGA, EWR)

**Sampling:**
- Use 10-20% random sample for computational efficiency
- Stratified by day of week
- Maintain temporal distribution

---

## Hotspot Identification

### Stage 1: Restaurant Clustering

**Algorithm:** HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise)

**Why HDBSCAN?**
- Discovers clusters of varying densities
- No need to specify number of clusters
- Handles noise (isolated restaurants)
- Works well with geographic coordinates

**Parameters:**

```python
from sklearn.cluster import HDBSCAN

clusterer = HDBSCAN(
    min_cluster_size=5,        # Min restaurants to form a dining zone
    min_samples=3,             # Core point threshold
    metric='haversine',        # Great circle distance
    cluster_selection_epsilon=0.001,  # ~111 meters
    cluster_selection_method='eom'    # Excess of mass
)

# Convert to radians for haversine
coords_rad = np.radians(restaurant_coords)
labels = clusterer.fit_predict(coords_rad)
```

**Output:** Dining zone polygons (convex hulls of clusters)

**Polygon Creation:**
```python
from shapely.geometry import MultiPoint

# For each cluster
points = [Point(lon, lat) for lon, lat in cluster_coords]
multipoint = MultiPoint(points)
polygon = multipoint.convex_hull.buffer(0.001)  # ~111m buffer
```

**Statistics:**
- Expected clusters: 50-100 dining zones
- Avg cluster size: 10-50 restaurants
- Noise points: 20-30% (isolated restaurants)

### Stage 2: Taxi Drop-off Clustering

**Algorithm:** HDBSCAN with weighted points

**Weighting Method:**
Instead of using instance weights (not well-supported in HDBSCAN), we duplicate points based on their weight:

```python
def prepare_weighted_coords(df):
    coords_list = []
    for _, row in df.iterrows():
        lon, lat = row['dropoff_longitude'], row['dropoff_latitude']
        weight = int(row['weight'] * 10)  # Scale to integer

        # Add point multiple times
        for _ in range(weight):
            coords_list.append([lon, lat])

    return np.array(coords_list)
```

**Parameters:**

```python
clusterer = HDBSCAN(
    min_cluster_size=10,       # Min trips to form hotspot
    min_samples=5,
    metric='haversine',
    cluster_selection_epsilon=0.001,
    cluster_selection_method='eom'
)
```

**Output:** Hotspot arrival area polygons

**Popularity Score:**
```python
popularity_score = min(100, dropoff_count / 10)
```
Normalized to 0-100 scale.

### Stage 3: Spatial Intersection

**Goal:** Find areas that are BOTH restaurant-dense AND popular destinations

**Method:** Spatial overlay (intersection)

```python
import geopandas as gpd

hotspot_dining_areas = gpd.overlay(
    dining_zones,
    arrival_areas,
    how='intersection'
)
```

**Scoring:**
```python
combined_score = (
    (restaurant_count / max_restaurant_count) * 50 +
    popularity_score
)
```

**Output:** Final hotspot dining areas (ranked)

---

## Accessibility Analysis

### Network Construction

**Current Implementation:** Distance-based buffers

**Walking Speed:** 1.2 km per 15 minutes = 80 m/min
- **Buffer:** 1200 meters

**Public Transit Speed:** 5 km per 30 minutes = 166 m/min
- **Buffer:** 5000 meters

**Driving Speed:** 8 km per 20 minutes = 400 m/min
- **Buffer:** 8000 meters

### Future Implementation: Network-Based

**Road Network (OSM):**
```python
import osmnx as ox

# Get road network
G = ox.graph_from_bbox(north, south, east, west, network_type='drive')

# Calculate isochrones
center_node = ox.distance.nearest_nodes(G, origin_lon, origin_lat)
subgraph = nx.ego_graph(G, center_node, radius=1000, distance='length')
isochrone = ox.convex_hull(subgraph)
```

**Transit Network (GTFS):**
```python
import gtfs_kit as gk
import networkx as nx

# Load GTFS
feed = gk.read_feed('subway.zip')

# Build transit network
G_transit = nx.Graph()

# Add stops as nodes
for _, stop in feed.stops.iterrows():
    G_transit.add_node(stop.stop_id, pos=(stop.stop_lon, stop.stop_lat))

# Add trips as edges (with travel times)
for _, trip in feed.stop_times.iterrows():
    G_transit.add_edge(trip.from_stop, trip.to_stop, weight=trip.travel_time)
```

### Service Area Calculation

**Algorithm:** Network service area analysis

```python
from esri.geometry import geometryEngine

# Calculate service area polygon
service_area = geometryEngine.geodesicBuffer(
    origin_point,
    buffer_distance,
    'meters'
)
```

**Multi-modal Integration:**
```python
# Union of all service areas
total_accessible_area = unary_union([
    walking_service_area,
    transit_service_area,
    driving_service_area
])
```

---

## Recommendation Algorithm

### Step 1: Spatial Query

Find hotspots within service areas:

```python
import geopandas as gpd
from shapely.geometry import Point

# For each hotspot
accessible_hotspots = []

for hotspot in hotspots:
    centroid = hotspot.geometry.centroid

    # Check if within any service area
    for service_area in service_areas:
        if service_area.geometry.contains(centroid):
            accessible_hotspots.append({
                'hotspot': hotspot,
                'mode': service_area.mode,
                'time': service_area.time
            })
            break
```

### Step 2: Scoring Algorithm

**Base Score Components:**

1. **Popularity Score (0-100):**
   - From taxi drop-off frequency
   - Pre-calculated in clustering stage

2. **Restaurant Density (0-50):**
   ```python
   density_score = (restaurant_count / max_restaurant_count) * 50
   ```

3. **Distance Penalty:**
   ```python
   distance_km = geodesic_distance(origin, hotspot_centroid)
   distance_penalty = distance_km * 2  # 2 points per km
   ```

4. **Multi-modal Bonus:**
   ```python
   if len(accessible_by_modes) > 1:
       bonus += 10
   if len(accessible_by_modes) > 2:
       bonus += 10  # Total +20 for all three modes
   ```

5. **Mode Preference Bonus:**
   ```python
   for mode in accessible_modes:
       if mode == 'walking': bonus += 5  # Encourage walkability
       if mode == 'transit': bonus += 3  # Encourage sustainability
   ```

**Final Score Formula:**

```python
def calculate_score(hotspot, origin, accessible_modes):
    # Base score from popularity and density
    base_score = hotspot.popularity_score

    # Distance penalty
    distance = calculate_distance(origin, hotspot.centroid)
    base_score -= (distance * 2)

    # Multi-modal bonus
    if len(accessible_modes) > 1:
        base_score += 10
    if len(accessible_modes) > 2:
        base_score += 10

    # Mode preference
    for mode in accessible_modes:
        if mode.type == 'walking':
            base_score += 5
        elif mode.type == 'transit':
            base_score += 3

    return max(0, base_score)  # Non-negative
```

### Step 3: Ranking

```python
# Sort by score descending
recommendations = sorted(
    accessible_hotspots,
    key=lambda x: x['score'],
    reverse=True
)

# Take top N
top_recommendations = recommendations[:10]
```

---

## Validation

### 1. Ground Truth Validation

**Method:** Compare with known popular dining areas

**NYC Popular Dining Districts:**
- Greenwich Village / SoHo
- Williamsburg, Brooklyn
- Astoria, Queens
- Flushing, Queens
- East Village / Lower East Side
- Upper West Side
- Chelsea / Meatpacking District

**Expected:** Top-ranked hotspots should align with these areas

### 2. Cross-Validation with Yelp

**Method:** Compare hotspot locations with high-density Yelp review areas

```python
# Calculate correlation
from scipy.stats import spearmanr

yelp_density = get_yelp_review_density_by_area()
our_popularity = get_hotspot_popularity_scores()

correlation, p_value = spearmanr(yelp_density, our_popularity)
```

**Expected:** Correlation > 0.7

### 3. Temporal Validation

**Method:** Test clustering on different time periods

```python
# Cluster using September data
hotspots_sept = cluster_taxi_data('2023-09')

# Cluster using October data
hotspots_oct = cluster_taxi_data('2023-10')

# Calculate overlap
overlap_percentage = calculate_polygon_overlap(hotspots_sept, hotspots_oct)
```

**Expected:** Overlap > 80% (stable hotspots)

### 4. Sensitivity Analysis

**Test parameter variations:**

| Parameter | Baseline | Test Range | Expected Δ |
|-----------|----------|------------|------------|
| min_cluster_size | 5 | 3-10 | ±20 clusters |
| min_samples | 3 | 2-5 | ±15 clusters |
| time_weight | 0.8-1.0 | 0.5-1.0 | ±10% scores |
| distance_penalty | 2 | 1-5 | Ranking shifts |

### 5. User Testing

**Method:** Present recommendations to users, collect feedback

**Metrics:**
- Relevance rating (1-5 stars)
- Visit intention (Yes/No/Maybe)
- Surprise factor (Expected/Unexpected)

**Sample Size:** 20-30 test users

---

## Limitations & Future Work

### Current Limitations

1. **Simplified Service Areas**
   - Uses distance buffers instead of actual routing
   - Doesn't account for barriers (rivers, highways)
   - No real-time traffic

2. **Static Analysis**
   - Doesn't capture temporal dynamics
   - No seasonal variations
   - Fixed time thresholds

3. **Data Completeness**
   - OSM may have incomplete restaurant data
   - Taxi data doesn't include Uber/Lyft
   - No pedestrian activity data

### Future Enhancements

1. **Advanced Routing**
   - Integrate pgRouting or ArcGIS Network Analyst
   - Real-time traffic from Google Maps API
   - Actual GTFS transit routing

2. **Machine Learning**
   - Predict popularity trends
   - Personalized recommendations
   - Temporal demand forecasting

3. **Enhanced Data**
   - Social media check-ins (Foursquare, Instagram)
   - Credit card transaction data (aggregated)
   - Pedestrian foot traffic sensors

4. **Dynamic Weights**
   - Learn optimal weights from user feedback
   - Time-of-day adjustments
   - Weather-based recommendations

---

## References

### Clustering
- **HDBSCAN Paper:** McInnes, L., Healy, J., & Astels, S. (2017). "hdbscan: Hierarchical density based clustering." *Journal of Open Source Software*, 2(11), 205.
- **Scikit-learn Documentation:** https://scikit-learn.org/stable/modules/clustering.html

### Geospatial Analysis
- **GeoPandas:** https://geopandas.org/
- **Shapely:** https://shapely.readthedocs.io/
- **OSMnx:** Boeing, G. (2017). "OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks." *Computers, Environment and Urban Systems*, 65, 126-139.

### Transportation
- **GTFS Specification:** https://gtfs.org/
- **Network Analysis:** Páez, A., Scott, D. M., & Morency, C. (2012). "Measuring accessibility: positive and normative implementations of various accessibility indicators." *Journal of Transport Geography*, 25, 141-153.

---

## Reproducibility

All code and parameters are documented to ensure reproducibility:

- Python version: 3.8+
- Library versions: See `requirements.txt`
- Random seeds: Set to 42
- Data sources: Documented with download dates
- Parameters: Defined in config files

```python
# Set random seed for reproducibility
import random
import numpy as np

random.seed(42)
np.random.seed(42)
```

---

**Last Updated:** 2024
**Contact:** [Your Name/Email]
