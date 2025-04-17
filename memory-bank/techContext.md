# Technical Context - Professional Portfolio v4

## Technologies Used
1. **Backend**:
   - Python 3.11+
   - Flask 3.1.0 (Web framework)
   - Flask-SQLAlchemy 3.1.1 (ORM)
   - Gunicorn 23.0.0 (WSGI HTTP Server)

2. **Frontend**:
   - HTML5
   - CSS3
   - JavaScript
   - Bootstrap (for responsive design)

3. **External Services**:
   - GitHub API (Repository integration)
   - Tableau Public (Data visualization embedding)
   - Google Analytics (Web analytics)

4. **Development Tools**:
   - WSL (Windows Subsystem for Linux)
   - Ubuntu 24.04
   - Git

## Dependencies
```
flask>=3.1.0
flask-sqlalchemy>=3.1.1
google-api-python-client>=2.166.0
google-auth>=2.38.0
google-auth-httplib2>=0.2.0
gunicorn>=23.0.0
psycopg2-binary>=2.9.10
requests>=2.32.3
email-validator>=2.2.0
```

## Development Setup
The application requires:
1. Python 3.11 or newer
2. Environment variables:
   - SESSION_SECRET (secret key for Flask sessions)
   - GITHUB_USERNAME (for GitHub API integration)
   - GITHUB_API_TOKEN (optional, for higher rate limits)
   - TABLEAU_PUBLIC_USERNAME (for Tableau integration)

## Technical Constraints
1. Must run on Ubuntu 24.04 in WSL environment
2. Must be accessible via URL
3. GitHub API has rate limits (higher with authentication token)
4. Tableau Public integration relies on publicly available dashboards 