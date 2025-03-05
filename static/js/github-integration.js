/**
 * GitHub API Integration
 * Fetches and displays repositories from GitHub
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the GitHub repositories container
    const reposContainer = document.getElementById('github-repos');
    
    if (reposContainer) {
        fetchGitHubRepositories(reposContainer);
    }
});

/**
 * Fetch repositories from GitHub API via our backend endpoint
 * @param {HTMLElement} container - Container element to display repositories
 */
function fetchGitHubRepositories(container) {
    fetch('/api/github/repos')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(repos => {
            displayRepositories(repos, container);
        })
        .catch(error => {
            console.error('Error fetching GitHub repositories:', error);
            displayError(container, error.message);
        });
}

/**
 * Displays GitHub repositories in the container
 * @param {Array} repos - Array of repository objects
 * @param {HTMLElement} container - Container element to display repositories
 */
function displayRepositories(repos, container) {
    // Clear loading indicator
    container.innerHTML = '';
    
    if (!repos || repos.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <p>No public repositories found.</p>
            </div>
        `;
        return;
    }
    
    // Create repositories grid
    const reposGrid = document.createElement('div');
    reposGrid.className = 'row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4';
    
    // Sort repositories by most recently updated
    repos.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    
    // Create cards for each repository
    repos.forEach(repo => {
        const repoCard = createRepositoryCard(repo);
        reposGrid.appendChild(repoCard);
    });
    
    container.appendChild(reposGrid);
}

/**
 * Creates a card element for a repository
 * @param {Object} repo - Repository object
 * @returns {HTMLElement} - Card element
 */
function createRepositoryCard(repo) {
    // Create card column
    const col = document.createElement('div');
    col.className = 'col';
    
    // Get language badge
    const languageBadge = repo.language 
        ? `<span class="badge bg-primary">${repo.language}</span>` 
        : '';
    
    // Format the updated date
    const updatedDate = new Date(repo.updated_at).toLocaleDateString();
    
    // HTML for repository card
    col.innerHTML = `
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">${repo.name}</h5>
                <p class="card-text text-muted small mb-2">Last updated: ${updatedDate}</p>
                <p class="card-text">${repo.description || 'No description available.'}</p>
                <div class="mb-3">
                    ${languageBadge}
                    <span class="badge bg-secondary"><i class="bi bi-star-fill me-1"></i>${repo.stargazers_count}</span>
                    <span class="badge bg-secondary"><i class="bi bi-diagram-2-fill me-1"></i>${repo.forks_count}</span>
                </div>
            </div>
            <div class="card-footer bg-transparent border-top-0">
                <a href="${repo.html_url}" target="_blank" class="btn btn-sm btn-outline-primary">View on GitHub</a>
            </div>
        </div>
    `;
    
    return col;
}

/**
 * Displays an error message in the container
 * @param {HTMLElement} container - Container element
 * @param {string} message - Error message to display
 */
function displayError(container, message) {
    container.innerHTML = `
        <div class="alert alert-warning">
            <h4 class="alert-heading">Unable to load GitHub repositories</h4>
            <p>${message}</p>
            <hr>
            <p class="mb-0">Please check your internet connection or try again later.</p>
        </div>
    `;
}