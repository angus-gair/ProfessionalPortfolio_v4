import os
import json
import requests
import time
from flask import Flask, render_template, redirect, url_for, request, jsonify, send_from_directory, abort
from pathlib import Path
import logging
import re

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

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

@app.route('/architecture')
def architecture():
    return render_template('architecture.html', active_page='projects')

@app.route('/optimisation')
def optimisation():
    """Serve the Christmas budget optimisation HTML file directly with collapsible sections."""
    try:
        # Check if file exists in the primary location
        optimization_path = os.path.join('static', 'historical_projects', 'WooliesX-ChristmasCampaign', 'budget_optimisation.html')
        if not os.path.exists(optimization_path):
            # Try the archived location
            optimization_path = os.path.join('archive', 'historical_projects', 'WooliesX-ChristmasCampaign', 'budget_optimisation.html')
            if not os.path.exists(optimization_path):
                app.logger.error("Optimization HTML file not found in any location")
                return "Optimization visualization not found", 404
        
        with open(optimization_path, 'r') as f:
            content = f.read()
        
        # Inject Bootstrap and jQuery for collapsible sections
        content = content.replace('</head>', 
                                '<link rel="stylesheet" href="/static/css/collapsible.css">\n</head>')
        content = content.replace('</body>', 
                                '<script src="/static/js/collapsible.js"></script>\n</body>')
        
        return content
    except Exception as e:
        app.logger.error(f"Error serving optimization page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/resume')
def resume():
    # Redirect to the downloadable resume file
    return redirect('/static/files/Angus_Gair_Resume.pdf')

@app.route('/api/github_repos')
def github_repos():
    """Fetch GitHub repositories using GitHub API."""
    try:
        github_username = 'analytics-designer'
        response = requests.get(f'https://api.github.com/users/{github_username}/repos')
        
        if response.status_code == 200:
            repos = response.json()
            # Extract only the needed information
            simplified_repos = []
            for repo in repos:
                simplified_repos.append({
                    'name': repo['name'],
                    'description': repo['description'] or 'No description provided',
                    'url': repo['html_url'],
                    'topics': repo.get('topics', []),
                    'language': repo['language'],
                    'fork': repo['fork']
                })
            return jsonify(simplified_repos)
        else:
            app.logger.warning(f"GitHub API returned status code {response.status_code}")
            return jsonify({'error': 'Could not fetch repositories', 'status': response.status_code}), 500
    except Exception as e:
        app.logger.error(f"Error fetching GitHub repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tableau_views')
def tableau_views():
    """Get available Tableau Public views for embedding."""
    try:
        return jsonify([
            {
                'name': 'BigW Rewards Monthly Dashboard',
                'viz_url': 'https://public.tableau.com/views/BigWRewardsMonthlyDashboard/BigWRewardsMonthlyDashboard',
                'thumbnail': '/static/images/bigw_rewards_thumbnail.png',
                'description': 'Interactive dashboard showing key metrics for BigW rewards program'
            },
            {
                'name': 'Woolworths Christmas Campaign Analysis',
                'viz_url': 'https://public.tableau.com/views/WoolworthsChristmasCampaignAnalysis/CampaignDashboard',
                'thumbnail': '/static/images/christmas_campaign_thumbnail.png',
                'description': 'Performance analysis of the Christmas marketing campaign'
            }
        ])
    except Exception as e:
        app.logger.error(f"Error fetching Tableau views: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/jupyter/<path:notebook_path>')
def serve_notebook(notebook_path):
    """Serve a Jupyter notebook file."""
    try:
        # Construct the full path to the notebook
        notebook_file = Path(f'static/historical_projects/{notebook_path}')
        
        # Check if the notebook exists
        if not notebook_file.exists():
            # Try the archived location
            archived_notebook_file = Path(f'archive/historical_projects/{notebook_path}')
            if archived_notebook_file.exists():
                notebook_file = archived_notebook_file
            else:
                app.logger.error(f"Notebook not found at either location: {notebook_path}")
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

@app.route('/api/notebooks/<path:notebook_path>')
def get_notebook_content(notebook_path):
    """Get the content of a Jupyter notebook file."""
    try:
        # Construct the full path to the notebook
        notebook_file = Path(f'static/historical_projects/{notebook_path}')
        
        # Check if the notebook exists
        if not notebook_file.exists():
            # Try the archived location
            archived_notebook_file = Path(f'archive/historical_projects/{notebook_path}')
            if archived_notebook_file.exists():
                notebook_file = archived_notebook_file
            else:
                app.logger.error(f"Notebook not found at either location: {notebook_path}")
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
        app.logger.error(f"Error fetching notebook content: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/mmm_viz')
def mmm_viz():
    """Serve the Marketing Mix Modeling visualization page."""
    try:
        # Check if file exists in the primary location
        viz_path = 'static/historical_projects/WooliesX-CampaignOptimisation/mmm-viz.html'
        
        # If not found in primary, check the archived location
        if not os.path.exists(viz_path):
            viz_path = 'archive/visualizations/mmm-viz.html'
            if not os.path.exists(viz_path):
                app.logger.error("MMM visualization file not found")
                return "MMM visualization not found", 404
                
        # Use render_template for the mmm_viz.html which will include the visualization
        return render_template('mmm_viz.html', active_page='projects')
    except Exception as e:
        app.logger.error(f"Error serving MMM visualization: {str(e)}")
        return str(e), 500

@app.route('/interactive_chart')
def interactive_chart():
    """Serve the Interactive Chart page for the XGBoost project."""
    try:
        # Check if file exists in the primary location
        viz_path = 'static/historical_projects/wooliesx_budget_optimization/interactive_chart.html'
        
        # If not found in primary, check the archived location
        if not os.path.exists(viz_path):
            viz_path = 'archive/visualizations/interactive_chart.html'
            if not os.path.exists(viz_path):
                app.logger.error("Interactive chart file not found")
                return "Interactive chart not found", 404
                
        # Use render_template for the interactive_chart.html which will include the visualization
        return render_template('interactive_chart.html', active_page='projects')
    except Exception as e:
        app.logger.error(f"Error serving interactive chart: {str(e)}")
        return str(e), 500

@app.route('/retail_loyalty_analytics')
def retail_loyalty_analytics():
    """Serve the Retail Loyalty Analytics visualization page."""
    try:
        # Check if file exists in the primary location
        viz_path = 'static/visualizations/Retail_Loyalty_Program_Analytics.html'
        
        # If not found in primary, check the archived location
        if not os.path.exists(viz_path):
            viz_path = 'archive/visualizations/Retail_Loyalty_Program_Analytics.html'
            # If still not found, check attached_assets
            if not os.path.exists(viz_path):
                viz_path = 'attached_assets/Retail_Loyalty_Program_Analytics.html'
                if not os.path.exists(viz_path):
                    app.logger.error("Retail loyalty analytics file not found in any location")
                    return "Retail loyalty analytics visualization not found", 404
        
        # Read the HTML content directly
        with open(viz_path, 'r') as f:
            html_content = f.read()
            
        # Return the HTML content directly
        return html_content
    except Exception as e:
        app.logger.error(f"Error serving retail loyalty analytics: {str(e)}")
        return str(e), 500

@app.route('/analytics-debug')
def analytics_debug():
    """
    Debug page for Google Analytics verification.
    This page helps test that the GA4 configuration is working correctly.
    """
    return render_template('analytics_debug.html', active_page='debug')

@app.route('/api/test-analytics-event', methods=['POST'])
def test_analytics_event():
    """
    Endpoint to verify analytics tracking by sending a test event directly to the 
    Google Analytics Measurement Protocol API.
    """
    try:
        # Get the measurement ID and API secret from the request
        data = request.json
        measurement_id = data.get('measurement_id')
        api_secret = data.get('api_secret')
        
        if not measurement_id or not api_secret:
            return jsonify({"error": "Missing measurement_id or api_secret"}), 400
        
        # Create a test event
        event_data = {
            "client_id": "test-client-id-123456789",
            "events": [{
                "name": "test_event",
                "params": {
                    "test_param": "test_value",
                    "timestamp_micros": int(time.time() * 1000000)
                }
            }]
        }
        
        # Send the event to GA4
        response = requests.post(
            f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={api_secret}",
            json=event_data
        )
        
        if response.status_code == 204:
            return jsonify({"success": True, "message": "Test event sent successfully"})
        else:
            return jsonify({"error": f"Failed to send test event: {response.text}"}), 500
            
    except Exception as e:
        app.logger.error(f"Error sending test analytics event: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ecosystem')
def ecosystem():
    """
    Serve the ecosystem diagram page.
    """
    return render_template('ecosystem.html', active_page='projects')

@app.route('/listing.html')
def job_listing():
    """
    Serve the Data Analyst job listing from Charterhouse.
    """
    try:
        job_listing_path = 'attached_assets/Data Analyst Job in Canberra at Charterhouse - SEEK.html'
        
        if not os.path.exists(job_listing_path):
            app.logger.error("Job listing HTML file not found")
            return "Job listing not found", 404
            
        # Extract relevant content from the job listing HTML
        with open(job_listing_path, 'r') as f:
            content = f.read()
        
        # Get the job title using regex
        title_match = re.search(r'<title>(.*?)</title>', content)
        job_title = title_match.group(1) if title_match else "Data Analyst Job Listing"
        
        # Get the job description by extracting from content
        # For simplicity, we'll render a structured version in a template
        
        return render_template('job_listing.html', 
                               active_page='resources',
                               job_title=job_title,
                               source="SEEK",
                               company="Charterhouse")
    except Exception as e:
        app.logger.error(f"Error serving job listing: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
