import os
import logging
from flask import Flask, render_template, send_file, jsonify, request
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# GitHub API configuration
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "angusgair")
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN", "")

@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/projects')
def projects():
    return render_template('projects.html', active_page='projects')

@app.route('/skills')
def skills():
    return render_template('skills.html', active_page='skills')

@app.route('/experience')
def experience():
    return render_template('experience.html', active_page='experience')

@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')

@app.route('/resume')
def resume():
    # In a real implementation, this would return a PDF file
    # For now, we'll just redirect to the experience page
    return render_template('experience.html', active_page='experience')

@app.route('/api/github/repos')
def github_repos():
    """Fetch GitHub repositories using GitHub API."""
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    headers = {}
    
    if GITHUB_API_TOKEN:
        headers["Authorization"] = f"token {GITHUB_API_TOKEN}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        
        # Filter and process repos to return relevant information
        processed_repos = []
        for repo in repos:
            if not repo.get('fork') and not repo.get('private', False):
                processed_repos.append({
                    'name': repo.get('name'),
                    'description': repo.get('description'),
                    'html_url': repo.get('html_url'),
                    'language': repo.get('language'),
                    'stargazers_count': repo.get('stargazers_count'),
                    'forks_count': repo.get('forks_count'),
                    'updated_at': repo.get('updated_at')
                })
        
        return jsonify(processed_repos)
    except Exception as e:
        app.logger.error(f"Error fetching GitHub repos: {str(e)}")
        return jsonify({"error": "Failed to fetch repositories", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
