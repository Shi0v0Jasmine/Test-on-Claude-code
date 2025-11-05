/**
 * Map initialization and management
 */

let map, view;
let graphicsLayer, serviceAreaLayer, hotspotsLayer;

/**
 * Initialize the map and view
 */
function initializeMap() {
    require([
        "esri/Map",
        "esri/views/MapView",
        "esri/layers/GraphicsLayer",
        "esri/Graphic",
        "esri/geometry/Point"
    ], function(Map, MapView, GraphicsLayer, Graphic, Point) {

        // Create graphics layers
        graphicsLayer = new GraphicsLayer({ id: 'graphics-layer' });
        serviceAreaLayer = new GraphicsLayer({ id: 'service-area-layer' });
        hotspotsLayer = new GraphicsLayer({ id: 'hotspots-layer' });

        // Create map
        map = new Map({
            basemap: CONFIG.map.basemap,
            layers: [hotspotsLayer, serviceAreaLayer, graphicsLayer]
        });

        // Create view
        view = new MapView({
            container: "viewDiv",
            map: map,
            center: CONFIG.map.center,
            zoom: CONFIG.map.zoom,
            popup: {
                dockEnabled: true,
                dockOptions: {
                    position: "top-right",
                    breakpoint: false
                }
            }
        });

        // Add click event listener
        view.on("click", handleMapClick);

        // Load initial hotspots data (mock for now)
        loadHotspotsData();

        console.log("Map initialized successfully");
    });
}

/**
 * Handle map click events
 */
function handleMapClick(event) {
    require([
        "esri/Graphic",
        "esri/geometry/Point"
    ], function(Graphic, Point) {

        // Clear previous graphics
        graphicsLayer.removeAll();
        serviceAreaLayer.removeAll();

        // Get coordinates
        const point = event.mapPoint;
        const latitude = point.latitude.toFixed(4);
        const longitude = point.longitude.toFixed(4);

        // Add origin point graphic
        const originSymbol = {
            type: "simple-marker",
            color: [226, 119, 40],
            outline: {
                color: [255, 255, 255],
                width: 2
            },
            size: CONFIG.symbols.originSize
        };

        const pointGraphic = new Graphic({
            geometry: point,
            symbol: originSymbol,
            attributes: {
                type: "origin",
                latitude: latitude,
                longitude: longitude
            }
        });

        graphicsLayer.add(pointGraphic);

        // Update UI
        updateOriginInfo(latitude, longitude);

        // Calculate service areas based on selected transport modes
        calculateServiceAreas(point);

        // Enable clear button
        document.getElementById('clear-btn').disabled = false;
    });
}

/**
 * Update origin information in the UI
 */
function updateOriginInfo(lat, lon) {
    const originInfo = document.getElementById('origin-info');
    originInfo.innerHTML = `
        <p><strong>Selected Location</strong></p>
        <p class="coordinates">Lat: ${lat}, Lon: ${lon}</p>
    `;
}

/**
 * Clear all selections and graphics
 */
function clearSelection() {
    graphicsLayer.removeAll();
    serviceAreaLayer.removeAll();

    document.getElementById('origin-info').innerHTML =
        '<p>Click on the map to set your starting location</p>';
    document.getElementById('clear-btn').disabled = true;

    clearRecommendations();
}

/**
 * Load hotspots data (mock function - replace with actual data loading)
 */
function loadHotspotsData() {
    require([
        "esri/Graphic",
        "esri/geometry/Polygon"
    ], function(Graphic, Polygon) {

        // TODO: Replace with actual hotspot data from backend
        // This is mock data for demonstration
        const mockHotspots = [
            {
                name: "Times Square Area",
                geometry: {
                    type: "polygon",
                    rings: [[
                        [-73.9876, 40.7580],
                        [-73.9830, 40.7580],
                        [-73.9830, 40.7600],
                        [-73.9876, 40.7600],
                        [-73.9876, 40.7580]
                    ]]
                },
                popularity: 95
            },
            {
                name: "Chelsea Market Area",
                geometry: {
                    type: "polygon",
                    rings: [[
                        [-74.0070, 40.7420],
                        [-74.0040, 40.7420],
                        [-74.0040, 40.7445],
                        [-74.0070, 40.7445],
                        [-74.0070, 40.7420]
                    ]]
                },
                popularity: 88
            }
        ];

        // Add hotspots to layer
        mockHotspots.forEach(hotspot => {
            const polygon = new Polygon(hotspot.geometry);

            const graphic = new Graphic({
                geometry: polygon,
                symbol: {
                    type: "simple-fill",
                    color: [255, 193, 7, 0.2],
                    outline: {
                        color: [255, 152, 0],
                        width: 2
                    }
                },
                attributes: {
                    name: hotspot.name,
                    popularity: hotspot.popularity
                },
                popupTemplate: {
                    title: "{name}",
                    content: "Popularity Score: {popularity}/100"
                }
            });

            hotspotsLayer.add(graphic);
        });

        console.log("Hotspots loaded");
    });
}

/**
 * Zoom to a specific location
 */
function zoomToLocation(longitude, latitude, zoom = 15) {
    if (view) {
        view.goTo({
            center: [longitude, latitude],
            zoom: zoom
        });
    }
}
