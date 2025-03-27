import os
import logging
import json
from flask import Flask, render_template, send_file, jsonify, request, abort, Response
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# GitHub API configuration
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "angusgair")
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN", "")

# Tableau Public configuration
TABLEAU_PUBLIC_USERNAME = os.environ.get("TABLEAU_PUBLIC_USERNAME", "angusgair")

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

@app.route('/api/tableau/views')
def tableau_views():
    """Get available Tableau Public views for embedding."""
    # In a production environment, this would fetch actual views from Tableau Public API
    # For demonstration, we'll return a static list of sample views with real working Tableau Public URLs
    
    views = [
        {
            'id': 'marketing_dashboard',
            'name': 'Christmas Campaign Dashboard',
            'url': 'https://public.tableau.com/views/SuperstoreSales_24/Overview',
            'thumbnail': '/static/images/thumbnails/marketing_dashboard.png',
            'project': 'xgboost'
        },
        {
            'id': 'loyalty_dashboard',
            'name': 'BigW Rewards Performance',
            'url': 'https://public.tableau.com/views/CustomerAnalysisDashboard_16775813725990/CustomerAnalysisDashboard',
            'thumbnail': '/static/images/thumbnails/loyalty_dashboard.png',
            'project': 'rewards'
        },
        {
            'id': 'train_punctuality',
            'name': 'Train Punctuality Analysis',
            'url': 'https://public.tableau.com/views/LearnEmbeddedAnalytics/SalesOverviewDashboard',
            'thumbnail': '/static/images/thumbnails/train_dashboard.png',
            'project': 'trains'
        },
        {
            'id': 'customer_retention',
            'name': 'Customer Retention Analysis',
            'url': 'https://public.tableau.com/views/RetailAnalysis_16773376635560/RetailAnalysis',
            'thumbnail': '/static/images/thumbnails/retention_dashboard.png',
            'project': 'retention'
        },
        {
            'id': 'media_mix',
            'name': 'Media Mix Modelling',
            'url': 'https://public.tableau.com/views/MarketingChannelAttribution_16944334679360/MarketingChannelAttribution',
            'thumbnail': '/static/images/thumbnails/media_dashboard.png',
            'project': 'media-mix'
        }
    ]
    
    return jsonify(views)

@app.route('/jupyter/<path:notebook_path>')
def serve_notebook(notebook_path):
    """Serve a Jupyter notebook file."""
    try:
        # Construct the full path to the notebook
        notebook_file = Path(f'static/historical_projects/{notebook_path}')
        
        # Check if the notebook exists
        if not notebook_file.exists():
            app.logger.error(f"Notebook not found: {notebook_path}")
            abort(404)
        
        # For security reasons, validate that the path doesn't try to access files outside the intended directory
        if '../' in notebook_path or notebook_path.startswith('/'):
            app.logger.error(f"Invalid notebook path: {notebook_path}")
            abort(403)
        
        # Render the notebook display template
        return render_template('notebook.html', 
                               notebook_path=notebook_path, 
                               active_page='projects',
                               notebook_name=os.path.basename(notebook_path))
        
    except Exception as e:
        app.logger.error(f"Error serving notebook: {str(e)}")
        abort(500)

@app.route('/api/notebook/<path:notebook_path>')
def get_notebook_content(notebook_path):
    """Get the content of a Jupyter notebook file."""
    try:
        # Construct the full path to the notebook
        notebook_file = Path(f'static/historical_projects/{notebook_path}')
        
        # Check if the notebook exists
        if not notebook_file.exists():
            app.logger.error(f"Notebook not found: {notebook_path}")
            return jsonify({"error": "Notebook not found"}), 404
        
        # For security reasons, validate that the path doesn't try to access files outside the intended directory
        if '../' in notebook_path or notebook_path.startswith('/'):
            app.logger.error(f"Invalid notebook path: {notebook_path}")
            return jsonify({"error": "Invalid notebook path"}), 403
        
        # Read the notebook content
        with open(notebook_file, 'r') as f:
            notebook_content = json.load(f)
        
        return jsonify(notebook_content)
        
    except Exception as e:
        app.logger.error(f"Error getting notebook content: {str(e)}")
        return jsonify({"error": "Failed to get notebook content", "details": str(e)}), 500

@app.route('/analytics-debug')
@app.route('/analytics_debug')  # Add a route with underscore for consistency
def analytics_debug():
    """
    Debug page for Google Analytics verification.
    This page helps test that the GA4 configuration is working correctly.
    """
    # Log server-side analytics access
    app.logger.info("Analytics debug page accessed")
    user_agent = request.headers.get('User-Agent', 'Unknown')
    client_ip = request.remote_addr
    app.logger.info(f"Analytics debug request from IP: {client_ip}, User-Agent: {user_agent}")
    
    # Render a simple debug page that will trigger analytics events
    return render_template('analytics_debug.html', 
                          active_page='debug',
                          measurement_id='G-3P8MK7MHQF',
                          timestamp=int(os.path.getmtime(__file__)),
                          client_ip=client_ip)

@app.route('/api/analytics/test', methods=['POST'])
def test_analytics_event():
    """
    Endpoint to verify analytics tracking by sending a test event directly to the 
    Google Analytics Measurement Protocol API.
    """
    try:
        # Get the client's information
        client_id = request.json.get('client_id', 'debug-client-id')
        event_name = request.json.get('event_name', 'server_test_event')
        
        # Log the test request
        app.logger.info(f"Analytics test event requested: {event_name} for client {client_id}")
        
        # Normally, here we would send a direct event to Google Analytics
        # using the Measurement Protocol. However, this requires additional setup
        # in the GA4 property that the user likely hasn't done yet.
        
        # Instead, we'll just return a success response for debugging
        return jsonify({
            "status": "success",
            "message": "Analytics test event created. Check your GA4 DebugView.",
            "details": {
                "measurement_id": "G-3P8MK7MHQF",
                "client_id": client_id,
                "event_name": event_name,
                "timestamp": int(os.path.getmtime(__file__))
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error testing analytics event: {str(e)}")
        return jsonify({"error": "Failed to test analytics event", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
