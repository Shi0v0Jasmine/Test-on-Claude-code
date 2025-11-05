/**
 * Main application initialization and event handlers
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Where to DINE - Application Starting...");

    // Initialize the map
    initializeMap();

    // Set up event listeners
    setupEventListeners();

    console.log("Application initialized successfully");
});

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // Clear button
    const clearBtn = document.getElementById('clear-btn');
    clearBtn.addEventListener('click', clearSelection);

    // Transport mode checkboxes
    const transportCheckboxes = document.querySelectorAll('.transport-option input[type="checkbox"]');
    transportCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleTransportModeChange);
    });

    console.log("Event listeners registered");
}

/**
 * Handle transport mode changes
 */
function handleTransportModeChange() {
    // If an origin is already set, recalculate service areas
    const graphics = graphicsLayer.graphics.toArray();
    const originGraphic = graphics.find(g => g.attributes && g.attributes.type === 'origin');

    if (originGraphic) {
        calculateServiceAreas(originGraphic.geometry);
    }
}

/**
 * Show loading indicator
 */
function showLoading(message = 'Loading...') {
    // TODO: Implement loading overlay
    console.log(message);
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    // TODO: Implement loading overlay removal
    console.log('Loading complete');
}

/**
 * Show error message
 */
function showError(message) {
    alert(`Error: ${message}`);
    console.error(message);
}

/**
 * Show success message
 */
function showSuccess(message) {
    console.log(`Success: ${message}`);
}

/**
 * Utility function to format numbers
 */
function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

/**
 * Utility function to format distance
 */
function formatDistance(meters) {
    if (meters < 1000) {
        return `${Math.round(meters)} m`;
    } else {
        return `${(meters / 1000).toFixed(2)} km`;
    }
}

/**
 * Utility function to format time
 */
function formatTime(minutes) {
    if (minutes < 60) {
        return `${Math.round(minutes)} min`;
    } else {
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        return `${hours}h ${mins}min`;
    }
}

// Make functions globally accessible
window.clearSelection = clearSelection;
window.highlightHotspot = highlightHotspot;
window.calculateServiceAreas = calculateServiceAreas;
window.findRecommendations = findRecommendations;
