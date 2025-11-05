/**
 * Configuration file for Where to DINE application
 */

const CONFIG = {
    // Map Configuration
    map: {
        center: [-73.9712, 40.7831], // NYC coordinates [longitude, latitude]
        zoom: 12,
        basemap: 'streets-navigation-vector'
    },

    // Service Area Time Thresholds (in minutes)
    serviceArea: {
        walking: 15,
        transit: 30,
        driving: 20
    },

    // Service Area Colors
    colors: {
        walking: [46, 204, 113, 0.3],    // Green
        transit: [52, 152, 219, 0.3],    // Blue
        driving: [231, 76, 60, 0.3]      // Red
    },

    // API Endpoints (update these with your backend URLs)
    api: {
        // For now, using mock data. Replace with actual endpoints when backend is ready
        hotspots: './data/hotspots.json',
        serviceArea: './api/service-area',
        recommendations: './api/recommendations'
    },

    // Clustering Parameters
    clustering: {
        minClusterSize: 5,
        minSamples: 3
    },

    // Symbol Sizes
    symbols: {
        originSize: 12,
        hotspotSize: 8,
        restaurantSize: 4
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
