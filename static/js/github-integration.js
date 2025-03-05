/**
 * GitHub API Integration
 * Fetches and displays repositories from GitHub
 */

document.addEventListener('DOMContentLoaded', function() {
    const repoContainer = document.getElementById('github-repos');
    
    if (!repoContainer) return;
    
    // Show loading indicator
    repoContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Loading GitHub repositories...</p>
        </div>
    `;
    
    // Fetch repositories from our API endpoint
    fetch('/api/github/repos')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(repos => {
            displayRepositories(repos, repoContainer);
        })
        .catch(error => {
            console.error('Error fetching GitHub repositories:', error);
            repoContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Failed to load repositories</h4>
                    <p>There was an error fetching GitHub repositories. Please try again later.</p>
                    <hr>
                    <p class="mb-0">Error details: ${error.message}</p>
                </div>
            `;
        });
});

/**
 * Displays GitHub repositories in the container
 * @param {Array} repos - Array of repository objects
 * @param {HTMLElement} container - Container element to display repositories
 */
function displayRepositories(repos, container) {
    if (!repos || repos.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading">No repositories found</h4>
                <p>No public repositories were found for this account.</p>
            </div>
        `;
        return;
    }
    
    // Sort repos by last updated date
    repos.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    
    // Create HTML for repos
    const reposHTML = repos.map(repo => {
        // Format the date
        const updatedDate = new Date(repo.updated_at);
        const formattedDate = updatedDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        // Determine the language badge color
        let languageClass = 'bg-secondary';
        if (repo.language) {
            switch(repo.language.toLowerCase()) {
                case 'python':
                    languageClass = 'bg-primary';
                    break;
                case 'javascript':
                    languageClass = 'bg-warning text-dark';
                    break;
                case 'html':
                    languageClass = 'bg-danger';
                    break;
                case 'css':
                    languageClass = 'bg-info text-dark';
                    break;
                case 'r':
                    languageClass = 'bg-success';
                    break;
                case 'sql':
                    languageClass = 'bg-info';
                    break;
            }
        }
        
        return `
            <div class="col-lg-6 mb-4">
                <div class="card repo-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="${repo.html_url}" target="_blank" class="text-decoration-none">
                                ${repo.name}
                            </a>
                        </h5>
                        <p class="card-text text-muted">
                            ${repo.description || 'No description provided'}
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                ${repo.language ? 
                                    `<span class="badge ${languageClass}">${repo.language}</span>` : 
                                    '<span class="badge bg-secondary">No language specified</span>'}
                            </div>
                            <div>
                                <small class="text-muted">
                                    <i class="bi bi-star me-1"></i>${repo.stargazers_count} 
                                    <i class="bi bi-diagram-2 ms-2 me-1"></i>${repo.forks_count}
                                </small>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer text-muted">
                        <small>Updated: ${formattedDate}</small>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <div class="row">
            ${reposHTML}
        </div>
    `;
}
