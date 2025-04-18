# Technical Context - Professional Portfolio v4

## Technologies Used

### Backend
- **Python 3.11+**: Core programming language
- **Flask 2.x**: Web framework for routing and view handling
- **Jinja2**: Templating engine (included with Flask)
- **python-dotenv**: For environment variable management
- **Requests**: HTTP library for API integrations

### Frontend
- **HTML5**: Structure and content
- **CSS3**: Styling and animations
- **JavaScript**: Client-side interactivity
- **Bootstrap 5**: CSS framework for responsive design
- **Bootstrap Icons**: Icon library for visual elements

### APIs & Integrations
- **GitHub API**: For fetching repository information
- **Tableau Public API**: For embedding data visualizations

### Analytics & Tracking
- **Google Tag Manager**: Container for analytics scripts
- **Google Analytics 4**: Analytics tracking and reporting
- **Custom DataLayer**: Enhanced tracking implementation

### Deployment & Infrastructure
- **Ubuntu 24.04 WSL**: Development environment
- **Python virtual environment**: Dependency isolation
- **Replit**: Alternative development/deployment platform

## Development Setup
1. **Environment Setup**:
   - Python 3.11+ installed
   - Virtual environment created and activated
   - Dependencies installed via `pip install -r requirements.txt`

2. **Configuration**:
   - Environment variables set in `.env` file:
     - `SESSION_SECRET`: Secret key for Flask sessions
     - `GITHUB_USERNAME`: GitHub username for API calls
     - `GITHUB_API_TOKEN`: GitHub API token (optional)
     - `TABLEAU_PUBLIC_USERNAME`: Tableau Public username

3. **Running the Application**:
   - Execute `./run.sh` script or
   - Run `python app.py` directly

## Technical Constraints

1. **API Rate Limits**:
   - GitHub API has rate limitations, especially for unauthenticated requests
   - Tableau Public API access is limited to public visualizations

2. **Environment Dependencies**:
   - Flask requires proper WSGI setup for production deployment
   - Virtual environment must be activated before running the application

3. **Browser Compatibility**:
   - Modern browsers supported (Chrome, Firefox, Safari, Edge)
   - Bootstrap 5 does not support Internet Explorer

4. **Analytics Limitations**:
   - Google Analytics may be blocked by ad blockers
   - Cookie consent may be required in some jurisdictions

5. **Security Considerations**:
   - API tokens must be kept secure in environment variables
   - Contact form needs server-side validation

## Dependencies

### Python Packages
```
Flask==2.0.1
Jinja2==3.0.1
python-dotenv==0.19.0
requests==2.26.0
```

### Frontend Libraries
- Bootstrap 5.3.0
- Bootstrap Icons 1.11.1
- Google Fonts (Inter font family)

### Development Tools
- **WSL**: Windows Subsystem for Linux
- **Python venv**: Virtual environment management
- **Git**: Version control
- **Cursor**: AI-powered code editor with Memory Bank

## Technical Documentation Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Google Tag Manager Documentation](https://developers.google.com/tag-manager) 