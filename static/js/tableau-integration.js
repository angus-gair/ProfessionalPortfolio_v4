/**
 * Tableau Dashboard Integration
 * Handles embedding and interaction with Tableau dashboards
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeRemainingTableauDashboards();
});

/**
 * Initializes tableau dashboards that aren't directly embedded
 */
function initializeRemainingTableauDashboards() {
    // Find dashboard containers with data-tableau-url attribute (older method)
    const tableauContainers = document.querySelectorAll('.tableau-container[data-tableau-url]');
    
    if (tableauContainers.length === 0) {
        console.log('No legacy Tableau containers found on page');
        return;
    }
    
    // Load Tableau API if needed
    loadTableauAPI(function() {
        // Initialize each dashboard with the legacy approach
        tableauContainers.forEach(container => {
            const url = container.getAttribute('data-tableau-url');
            if (url) {
                const containerId = container.id;
                initializeTableauDashboard(containerId, url);
            }
        });
    });
}

/**
 * Loads the Tableau JavaScript API
 * @param {Function} callback - Function to call when API is loaded
 */
function loadTableauAPI(callback) {
    // Check if Tableau is already loaded
    if (window.tableau && window.tableau.Viz) {
        if (callback) callback();
        return;
    }

    // Create script element to load Tableau JavaScript API
    const script = document.createElement('script');
    script.src = 'https://public.tableau.com/javascripts/api/tableau-2.min.js';
    script.onload = function() {
        console.log('Tableau API loaded successfully');
        if (callback) callback();
    };
    script.onerror = function() {
        console.error('Error loading Tableau API');
        handleTableauError();
    };
    
    document.head.appendChild(script);
}

/**
 * Initializes a specific Tableau dashboard
 * @param {string} containerId - ID of the container element
 * @param {string} url - URL of the Tableau dashboard
 */
function initializeTableauDashboard(containerId, url) {
    const containerElement = document.getElementById(containerId);
    if (!containerElement) {
        console.error(`Container element with ID "${containerId}" not found`);
        return;
    }
    
    try {
        // Clear container
        containerElement.innerHTML = '';
        
        // Set container height
        containerElement.style.height = '500px';
        
        // Create viz options
        const options = {
            hideTabs: true,
            hideToolbar: true,
            width: '100%',
            height: '100%',
            onFirstInteractive: function() {
                console.log(`Tableau dashboard in container ${containerId} loaded successfully`);
            }
        };
        
        // Create the viz
        new tableau.Viz(containerElement, url, options);
        
    } catch (error) {
        console.error('Error creating Tableau visualisation:', error);
        displayTableauError(containerElement);
    }
}

/**
 * Displays an error message when Tableau fails to load
 */
function handleTableauError() {
    const tableauContainers = document.querySelectorAll('.tableau-container[data-tableau-url]');
    tableauContainers.forEach(container => {
        displayTableauError(container);
    });
}

/**
 * Displays an error message in the Tableau container
 * @param {HTMLElement} container - The Tableau container element
 * @param {string} message - Error message to display
 */
function displayTableauError(container, message = 'Unable to load Tableau visualisation. Please check your connection or try again later.') {
    container.innerHTML = `
        <div class="alert alert-warning" role="alert">
            <h4 class="alert-heading">Visualisation Unavailable</h4>
            <p>${message}</p>
            <hr>
            <p class="mb-0">
                <small>
                    Note: For this demo, Tableau visualisations are placeholders. 
                    In a production environment, these would connect to actual Tableau dashboards.
                </small>
            </p>
        </div>
    `;
}