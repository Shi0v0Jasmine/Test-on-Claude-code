/**
 * Service Area calculation and visualization
 */

/**
 * Calculate service areas for selected transport modes
 */
function calculateServiceAreas(originPoint) {
    // Get selected transport modes
    const walkingEnabled = document.getElementById('walking-mode').checked;
    const transitEnabled = document.getElementById('transit-mode').checked;
    const drivingEnabled = document.getElementById('driving-mode').checked;

    // Clear previous service areas
    serviceAreaLayer.removeAll();

    // Calculate for each enabled mode
    if (walkingEnabled) {
        calculateWalkingServiceArea(originPoint);
    }
    if (transitEnabled) {
        calculateTransitServiceArea(originPoint);
    }
    if (drivingEnabled) {
        calculateDrivingServiceArea(originPoint);
    }

    // After calculating service areas, find recommendations
    setTimeout(() => {
        findRecommendations(originPoint);
    }, 1000);
}

/**
 * Calculate walking service area (15 minutes)
 * For demo purposes, creates a circular buffer
 * In production, this should use actual network analysis
 */
function calculateWalkingServiceArea(point) {
    require([
        "esri/Graphic",
        "esri/geometry/geometryEngine"
    ], function(Graphic, geometryEngine) {

        // Walking speed: approximately 1.2 km in 15 minutes = 1200 meters
        const bufferDistance = 1200; // meters

        // Create buffer
        const buffer = geometryEngine.geodesicBuffer(point, bufferDistance, "meters");

        // Create graphic
        const serviceAreaGraphic = new Graphic({
            geometry: buffer,
            symbol: {
                type: "simple-fill",
                color: CONFIG.colors.walking,
                outline: {
                    color: [46, 204, 113, 0.8],
                    width: 2
                }
            },
            attributes: {
                type: "walking",
                time: CONFIG.serviceArea.walking
            }
        });

        serviceAreaLayer.add(serviceAreaGraphic);
        console.log("Walking service area calculated");
    });
}

/**
 * Calculate public transit service area (30 minutes)
 * For demo purposes, creates a larger circular buffer
 * In production, this should use actual transit network analysis
 */
function calculateTransitServiceArea(point) {
    require([
        "esri/Graphic",
        "esri/geometry/geometryEngine"
    ], function(Graphic, geometryEngine) {

        // Transit: approximately 5 km in 30 minutes = 5000 meters
        const bufferDistance = 5000; // meters

        // Create buffer
        const buffer = geometryEngine.geodesicBuffer(point, bufferDistance, "meters");

        // Create graphic
        const serviceAreaGraphic = new Graphic({
            geometry: buffer,
            symbol: {
                type: "simple-fill",
                color: CONFIG.colors.transit,
                outline: {
                    color: [52, 152, 219, 0.8],
                    width: 2
                }
            },
            attributes: {
                type: "transit",
                time: CONFIG.serviceArea.transit
            }
        });

        serviceAreaLayer.add(serviceAreaGraphic);
        console.log("Transit service area calculated");
    });
}

/**
 * Calculate driving service area (20 minutes)
 * For demo purposes, creates a larger circular buffer
 * In production, this should use actual road network analysis
 */
function calculateDrivingServiceArea(point) {
    require([
        "esri/Graphic",
        "esri/geometry/geometryEngine"
    ], function(Graphic, geometryEngine) {

        // Driving: approximately 8 km in 20 minutes = 8000 meters
        const bufferDistance = 8000; // meters

        // Create buffer
        const buffer = geometryEngine.geodesicBuffer(point, bufferDistance, "meters");

        // Create graphic
        const serviceAreaGraphic = new Graphic({
            geometry: buffer,
            symbol: {
                type: "simple-fill",
                color: CONFIG.colors.driving,
                outline: {
                    color: [231, 76, 60, 0.8],
                    width: 2
                }
            },
            attributes: {
                type: "driving",
                time: CONFIG.serviceArea.driving
            }
        });

        serviceAreaLayer.add(serviceAreaGraphic);
        console.log("Driving service area calculated");
    });
}

/**
 * Check if a point is within any service area
 */
function isWithinServiceArea(point) {
    require([
        "esri/geometry/geometryEngine"
    ], function(geometryEngine) {

        const serviceAreas = serviceAreaLayer.graphics.toArray();

        for (let i = 0; i < serviceAreas.length; i++) {
            if (geometryEngine.contains(serviceAreas[i].geometry, point)) {
                return {
                    within: true,
                    mode: serviceAreas[i].attributes.type,
                    time: serviceAreas[i].attributes.time
                };
            }
        }

        return { within: false };
    });
}

/**
 * Get all service area polygons
 */
function getServiceAreaPolygons() {
    return serviceAreaLayer.graphics.toArray().map(graphic => ({
        geometry: graphic.geometry,
        type: graphic.attributes.type,
        time: graphic.attributes.time
    }));
}

/**
 * Calculate actual travel time (placeholder for future implementation)
 * This would integrate with routing services
 */
async function calculateTravelTime(origin, destination, mode) {
    // TODO: Implement actual routing calculation
    // For now, return estimated time based on distance
    require([
        "esri/geometry/geometryEngine"
    ], function(geometryEngine) {

        const distance = geometryEngine.geodesicLength(
            geometryEngine.geodesicDensify(
                {
                    type: "polyline",
                    paths: [
                        [origin.longitude, origin.latitude],
                        [destination.longitude, destination.latitude]
                    ]
                },
                1000
            ),
            "meters"
        );

        // Rough estimates
        const speeds = {
            walking: 80,   // meters/minute
            transit: 166,  // meters/minute
            driving: 400   // meters/minute
        };

        const estimatedTime = Math.round(distance / speeds[mode]);
        return estimatedTime;
    });
}
