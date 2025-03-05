/**
 * Tableau Dashboard Integration
 * Handles embedding and interaction with Tableau dashboards
 */

document.addEventListener('DOMContentLoaded', function() {
    // Look for tableau dashboard containers
    const tableauContainers = document.querySelectorAll('.tableau-container');
    
    if (tableauContainers.length === 0) return;
    
    // Check if the Tableau JavaScript API is loaded
    if (typeof tableau === 'undefined') {
        // Load the Tableau JavaScript API if not already loaded
        loadTableauAPI();
    } else {
        // Initialize dashboards if API is already loaded
        initializeTableauDashboards();
    }
});

/**
 * Loads the Tableau JavaScript API
 */
function loadTableauAPI() {
    const script = document.createElement('script');
    script.src = 'https://public.tableau.com/javascripts/api/tableau-2.min.js';
    script.onload = function() {
        initializeTableauDashboards();
    };
    script.onerror = function() {
        console.error('Failed to load Tableau JavaScript API');
        handleTableauError();
    };
    document.head.appendChild(script);
}

/**
 * Initializes all Tableau dashboards on the page
 */
function initializeTableauDashboards() {
    const tableauContainers = document.querySelectorAll('.tableau-container');
    
    tableauContainers.forEach(container => {
        const url = container.dataset.tableauUrl;
        const dashboardId = container.id;
        
        if (!url) {
            console.error('Tableau URL not provided for container:', dashboardId);
            return;
        }
        
        try {
            // Initialize the dashboard
            initializeTableauDashboard(dashboardId, url);
        } catch (error) {
            console.error('Error initializing Tableau dashboard:', error);
            displayTableauError(container, error.message);
        }
    });
}

/**
 * Initializes a specific Tableau dashboard
 * @param {string} containerId - ID of the container element
 * @param {string} url - URL of the Tableau dashboard
 */
function initializeTableauDashboard(containerId, url) {
    const containerDiv = document.getElementById(containerId);
    
    if (!containerDiv) {
        console.error('Container not found:', containerId);
        return;
    }
    
    // Clear the container
    containerDiv.innerHTML = '';
    
    // Define dashboard options
    const options = {
        hideTabs: true,
        hideToolbar: false,
        width: '100%',
        height: '100%',
        onFirstInteractive: function() {
            console.log('Dashboard loaded successfully:', containerId);
        }
    };
    
    try {
        // Create a new Tableau Viz object
        new tableau.Viz(containerDiv, url, options);
    } catch (error) {
        console.error('Error creating Tableau visualization:', error);
        displayTableauError(containerDiv, error.message);
    }
}

/**
 * Displays an error message when Tableau fails to load
 */
function handleTableauError() {
    const tableauContainers = document.querySelectorAll('.tableau-container');
    
    tableauContainers.forEach(container => {
        displayTableauError(container, 'Failed to load Tableau JavaScript API');
    });
}

/**
 * Displays an error message in the Tableau container
 * @param {HTMLElement} container - The Tableau container element
 * @param {string} message - Error message to display
 */
function displayTableauError(container, message) {
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <h4 class="alert-heading">Dashboard Error</h4>
            <p>There was an error loading the Tableau dashboard.</p>
            <hr>
            <p class="mb-0">Error details: ${message}</p>
        </div>
    `;
}
