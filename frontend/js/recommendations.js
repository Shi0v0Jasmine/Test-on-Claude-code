/**
 * Recommendations engine - finds and ranks dining hotspots
 */

/**
 * Find recommendations based on service areas
 */
function findRecommendations(originPoint) {
    require([
        "esri/geometry/geometryEngine"
    ], function(geometryEngine) {

        const recommendations = [];

        // Get service area polygons
        const serviceAreas = serviceAreaLayer.graphics.toArray();
        const hotspots = hotspotsLayer.graphics.toArray();

        if (serviceAreas.length === 0 || hotspots.length === 0) {
            displayNoRecommendations();
            return;
        }

        // Check each hotspot against service areas
        hotspots.forEach(hotspot => {
            const hotspotGeometry = hotspot.geometry;
            const hotspotCentroid = hotspotGeometry.centroid || hotspotGeometry.extent.center;

            // Check which service areas contain this hotspot
            const accessibleBy = [];

            serviceAreas.forEach(serviceArea => {
                if (geometryEngine.intersects(hotspotGeometry, serviceArea.geometry) ||
                    geometryEngine.contains(serviceArea.geometry, hotspotCentroid)) {
                    accessibleBy.push({
                        mode: serviceArea.attributes.type,
                        time: serviceArea.attributes.time
                    });
                }
            });

            // If hotspot is accessible by at least one mode
            if (accessibleBy.length > 0) {
                // Calculate distance from origin
                const distance = geometryEngine.geodesicLength(
                    {
                        type: "polyline",
                        paths: [[
                            [originPoint.longitude, originPoint.latitude],
                            [hotspotCentroid.longitude, hotspotCentroid.latitude]
                        ]]
                    },
                    "kilometers"
                );

                // Calculate score (popularity weighted by distance)
                const popularity = hotspot.attributes.popularity || 50;
                const score = calculateScore(popularity, distance, accessibleBy);

                recommendations.push({
                    name: hotspot.attributes.name,
                    popularity: popularity,
                    distance: distance.toFixed(2),
                    accessibleBy: accessibleBy,
                    score: score,
                    geometry: hotspotCentroid
                });
            }
        });

        // Sort by score (descending)
        recommendations.sort((a, b) => b.score - a.score);

        // Display recommendations
        displayRecommendations(recommendations);
    });
}

/**
 * Calculate recommendation score
 * Higher score = better recommendation
 */
function calculateScore(popularity, distance, accessibleModes) {
    // Base score from popularity (0-100)
    let score = popularity;

    // Distance penalty (closer is better)
    // Reduce score by 2 points per km
    score -= (distance * 2);

    // Bonus for multiple transport options
    if (accessibleModes.length > 1) {
        score += 10;
    }
    if (accessibleModes.length > 2) {
        score += 10;
    }

    // Mode preference bonus (transit and walking are preferred)
    accessibleModes.forEach(mode => {
        if (mode.mode === 'walking') score += 5;
        if (mode.mode === 'transit') score += 3;
    });

    return Math.max(0, score); // Ensure non-negative
}

/**
 * Display recommendations in the UI
 */
function displayRecommendations(recommendations) {
    const listContainer = document.getElementById('recommendations-list');

    if (recommendations.length === 0) {
        displayNoRecommendations();
        return;
    }

    // Take top 10 recommendations
    const topRecommendations = recommendations.slice(0, 10);

    // Build HTML
    let html = '';
    topRecommendations.forEach((rec, index) => {
        const modesText = rec.accessibleBy.map(m => {
            const icons = {
                walking: '🚶',
                transit: '🚇',
                driving: '🚗'
            };
            return `${icons[m.mode]} ${m.time}min`;
        }).join(', ');

        html += `
            <div class="recommendation-item" onclick="highlightHotspot('${rec.name}')">
                <span class="rank">${index + 1}</span>
                <div style="display: inline-block; vertical-align: top; width: calc(100% - 45px);">
                    <div class="name">${rec.name}</div>
                    <div class="details">
                        📍 ${rec.distance} km away<br>
                        ${modesText}
                    </div>
                    <span class="popularity">⭐ Popularity: ${rec.popularity}/100</span>
                </div>
            </div>
        `;
    });

    listContainer.innerHTML = html;
    console.log(`Displayed ${topRecommendations.length} recommendations`);
}

/**
 * Display message when no recommendations found
 */
function displayNoRecommendations() {
    const listContainer = document.getElementById('recommendations-list');
    listContainer.innerHTML = `
        <p class="placeholder">
            No dining hotspots found within your selected travel range.
            Try selecting a different location or enabling more transport modes.
        </p>
    `;
}

/**
 * Clear recommendations display
 */
function clearRecommendations() {
    const listContainer = document.getElementById('recommendations-list');
    listContainer.innerHTML = '<p class="placeholder">Results will appear here after selecting an origin</p>';
}

/**
 * Highlight a hotspot on the map when clicked
 */
function highlightHotspot(hotspotName) {
    require([
        "esri/Graphic"
    ], function(Graphic) {

        // Find the hotspot
        const hotspots = hotspotsLayer.graphics.toArray();
        const hotspot = hotspots.find(h => h.attributes.name === hotspotName);

        if (hotspot) {
            // Zoom to hotspot
            view.goTo({
                target: hotspot.geometry,
                zoom: 15
            }).then(() => {
                // Show popup
                view.popup.open({
                    location: hotspot.geometry.centroid || hotspot.geometry.extent.center,
                    title: hotspot.attributes.name,
                    content: `
                        <b>Popularity Score:</b> ${hotspot.attributes.popularity}/100<br>
                        <p>This is a popular dining area based on real mobility data.</p>
                    `
                });
            });
        }
    });
}

/**
 * Export recommendations to CSV (future feature)
 */
function exportRecommendations(recommendations) {
    // TODO: Implement CSV export functionality
    console.log("Export feature coming soon");
}
