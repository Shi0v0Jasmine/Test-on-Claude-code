# Where to DINE

**A GIS-Powered NYC Dining Hotspot Recommendation System**

Find popular dining areas in New York City based on real mobility data and multi-modal accessibility analysis.

---

## Overview

**Where to DINE** is an interactive WebGIS application that recommends dining hotspots by combining:

1. **Real mobility patterns** - NYC taxi drop-off data showing where people actually go
2. **Restaurant density** - Clustered dining zones from OpenStreetMap
3. **Multi-modal accessibility** - Walking, public transit, and driving service areas

Instead of relying solely on subjective reviews, our system uses "voting with feet" - analyzing millions of taxi trips to identify truly popular dining destinations.

---

## Features

### Interactive Map Interface
- Click anywhere in NYC to set your origin location
- Visualize reachable areas based on travel mode and time
- See ranked dining hotspots within your reach

### Multi-Modal Transportation
- **🚶 Walking** - 15-minute isochrones
- **🚇 Public Transit** - 30-minute service areas
- **🚗 Driving** - 20-minute coverage zones

### Smart Recommendations
- Ranked by popularity (taxi drop-off frequency)
- Weighted by dining hours (lunch/dinner, weekday/weekend)
- Scored based on accessibility and restaurant density

---

## Project Structure

```
where-to-dine/
├── frontend/                 # WebGIS Application
│   ├── index.html           # Main HTML page
│   ├── css/
│   │   └── style.css        # Styling
│   └── js/
│       ├── config.js        # Configuration
│       ├── map.js           # Map initialization
│       ├── serviceArea.js   # Service area calculations
│       ├── recommendations.js # Recommendation engine
│       └── app.js           # Main application logic
│
├── backend/                 # Data Processing
│   ├── data_processing/
│   │   ├── 01_cluster_restaurants.py      # Restaurant clustering
│   │   ├── 02_cluster_taxi_dropoffs.py    # Taxi hotspot analysis
│   │   ├── 03_combine_hotspots.py         # Spatial intersection
│   │   └── requirements.txt               # Python dependencies
│   └── api/                 # API endpoints (future)
│
├── data/                    # Data directory
│   ├── raw/                 # Raw input data
│   └── processed/           # Processed outputs
│
├── docs/                    # Documentation
│   ├── METHODOLOGY.md       # Detailed methodology
│   ├── DATA_SOURCES.md      # Data acquisition guide
│   └── GITHUB_GUIDE.md      # GitHub workflow tutorial
│
└── config/                  # Configuration files
```

---

## Quick Start

### 1. View the WebGIS Application

Simply open `frontend/index.html` in a web browser:

```bash
# From project root
cd frontend
open index.html  # Mac
start index.html # Windows
xdg-open index.html # Linux
```

Or use a local server:
```bash
# Python 3
python -m http.server 8000

# Then visit: http://localhost:8000/frontend/
```

### 2. Process Your Own Data

```bash
# Navigate to data processing
cd backend/data_processing

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run pipeline
python 01_cluster_restaurants.py
python 02_cluster_taxi_dropoffs.py
python 03_combine_hotspots.py
```

---

## Data Sources

### 1. NYC Taxi & Limousine Commission (TLC) Trip Records
- **Source:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Purpose:** Identify popular arrival destinations
- **Key Fields:** `dropoff_longitude`, `dropoff_latitude`, `dropoff_datetime`

### 2. OpenStreetMap (OSM) - Restaurant Locations
- **Source:** OpenStreetMap via Overpass API or OSMnx
- **Purpose:** Restaurant locations and density
- **Tag:** `amenity=restaurant`

### 3. MTA GTFS Data
- **Source:** http://web.mta.info/developers/
- **Purpose:** Public transit network (future implementation)

See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for detailed acquisition instructions.

---

## Methodology

### 1. Hotspot Identification

**Restaurant Clustering (HDBSCAN)**
- Clusters dense restaurant concentrations
- Creates "Dining Zone" polygons
- Parameters: `min_cluster_size=5`, `min_samples=3`

**Taxi Drop-off Clustering (HDBSCAN)**
- Analyzes millions of taxi drop-offs during dining hours
- Applies time-based weights (lunch/dinner, weekday/weekend)
- Creates "Hotspot Arrival Area" polygons

**Spatial Intersection**
- Combines dining zones with arrival areas
- Identifies areas that are both dense with restaurants AND popular destinations

### 2. Multi-Modal Accessibility

**Service Area Calculation**
- Walking: 15-minute isochrones
- Public Transit: 30-minute service areas
- Driving: 20-minute travel zones

Currently uses simplified distance-based buffers. Future versions will integrate:
- Actual road network from OSM
- Real-time transit schedules (GTFS)
- ArcGIS Network Analyst or pgRouting

### 3. Recommendation Engine

**Scoring Algorithm:**
```
combined_score = (normalized_restaurant_count × 50) + popularity_score

Where:
- restaurant_count: Number of restaurants in hotspot
- popularity_score: Taxi drop-off frequency (0-100)
```

**Accessibility Bonus:**
- Multiple transport modes available: +10 points
- Walking accessible: +5 points
- Transit accessible: +3 points

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for detailed algorithms.

---

## Technology Stack

### Frontend
- **ArcGIS JavaScript API 4.28** - Interactive mapping
- **HTML5/CSS3** - User interface
- **Vanilla JavaScript** - Application logic

### Backend (Data Processing)
- **Python 3.8+** - Data processing pipeline
- **GeoPandas** - Geospatial data handling
- **HDBSCAN** - Density-based clustering
- **Shapely** - Geometric operations
- **Pandas/NumPy** - Data manipulation

### Potential Extensions
- **Node.js/Express** - API server
- **PostgreSQL + PostGIS** - Spatial database
- **Docker** - Containerization

---

## Using GitHub for This Project

This project provides an excellent opportunity to learn GitHub workflows. See [`docs/GITHUB_GUIDE.md`](docs/GITHUB_GUIDE.md) for a complete tutorial covering:

- Repository initialization and cloning
- Branching strategies for team collaboration
- Commit message best practices
- Pull requests and code review
- Issue tracking for tasks
- GitHub Pages for hosting the web app

---

## Future Enhancements

### Phase 1 (Current)
- ✅ Interactive map interface
- ✅ Basic service area visualization
- ✅ Hotspot clustering algorithms
- ✅ Recommendation system

### Phase 2 (Planned)
- [ ] Real network-based service areas (OSM + routing)
- [ ] Actual GTFS transit integration
- [ ] Backend API with PostgreSQL/PostGIS
- [ ] User authentication and saved locations
- [ ] Restaurant detail pages with reviews

### Phase 3 (Advanced)
- [ ] Real-time traffic integration
- [ ] Machine learning for demand prediction
- [ ] Mobile application (React Native)
- [ ] Social features (share recommendations)
- [ ] Business analytics dashboard

---

## Applications

### For Residents
- Discover dining hotspots near you
- Plan dining trips with optimal transport
- Explore neighborhoods by food popularity

### For Urban Planners
- Assess accessibility to dining amenities
- Identify "food deserts" or underserved areas
- Evaluate transportation infrastructure

### For Businesses
- Optimal restaurant location selection
- Competitive analysis of dining markets
- Understand customer mobility patterns

### For Researchers
- Study relationships between dining, mobility, and urban structure
- Analyze temporal patterns in dining behavior
- Evaluate transit equity and access

---

## Team & Credits

**Project Type:** Academic GIS Project
**Course:** Advanced GIS / Urban Informatics
**Institution:** [Your University]

### Contributors
- [Your Name] - Project Lead, Full Stack Development
- [Team Member 2] - Data Analysis, Clustering Algorithms
- [Team Member 3] - Frontend Development, UI/UX
- [Team Member 4] - Documentation, Testing

### Acknowledgments
- NYC Taxi & Limousine Commission for open data
- OpenStreetMap contributors
- HDBSCAN library developers

---

## License

This project is open-source and available under the MIT License.

```
MIT License

Copyright (c) 2024 [Your Name/Team]

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

## Contact & Support

- **Issues:** https://github.com/[your-username]/where-to-dine/issues
- **Email:** [your-email@university.edu]
- **Documentation:** [`docs/`](docs/)

---

## Citation

If you use this project in research, please cite:

```bibtex
@software{where_to_dine_2024,
  title = {Where to DINE: A GIS-Powered NYC Dining Hotspot Recommendation System},
  author = {[Your Name]},
  year = {2024},
  url = {https://github.com/[your-username]/where-to-dine}
}
```

---

**Built with ❤️ for better urban exploration through GIS**
