# System Patterns - Professional Portfolio v4

## Architecture Overview
This application uses a Flask-based web architecture with a simple structure:
- Flask web server handling routes and API endpoints
- Jinja2 templating for HTML rendering
- Static assets for CSS, JavaScript, and images
- External API integrations (GitHub, Tableau)

## Key Technical Decisions
1. **Flask Framework**: Used for its simplicity, flexibility, and Python ecosystem compatibility
2. **API-driven Content**: Dynamic content from GitHub and Tableau APIs for up-to-date information
3. **Responsive Frontend**: HTML/CSS/JS for responsive layout and interactions
4. **No Database Required**: Static content with external API integrations eliminates need for local database
5. **Analytics Integration**: Google Analytics for tracking visitor interactions

## Component Relationships
```
┌──────────────┐      ┌──────────────┐
│ Flask Routes │─────▶│ Jinja2       │
│ & Controllers│      │ Templates    │
└──────┬───────┘      └──────────────┘
       │
       ▼
┌──────────────┐      ┌──────────────┐
│ API          │─────▶│ External     │
│ Integrations │      │ Services     │
└──────────────┘      │ (GitHub,     │
                      │  Tableau)    │
                      └──────────────┘
```

## Design Patterns
1. **MVC-like Structure**: 
   - Routes/Controllers (Flask routes)
   - Views (Jinja2 templates)
   - Models (API responses)

2. **API Proxy Pattern**:
   - Application acts as a proxy for external APIs
   - Simplifies client-side interactions with these services

3. **Template Inheritance**:
   - Base template defines common structure
   - Individual page templates extend the base 