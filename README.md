# Professional Portfolio v4

A professional portfolio website built with Flask that showcases skills, projects, experience, and contact information.

## Setup Instructions

1. **Clone the repository**

2. **Install Python 3.11 or newer**

3. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   ```

4. **Install dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   
   Create a `.env` file with the following variables:
   ```
   SESSION_SECRET=your-secure-session-key
   GITHUB_USERNAME=your-github-username
   GITHUB_API_TOKEN=your-github-token (optional)
   TABLEAU_PUBLIC_USERNAME=your-tableau-username
   ```

6. **Run the application**
   ```bash
   ./run.sh
   ```

## Features

- Home page with personal introduction
- Projects page with GitHub repository integration
- Skills page with visualization
- Experience page with career history
- Contact page
- Tableau Public visualization integration
- Analytics debugging features

## Documentation

Project documentation is available in the `memory-bank/` directory, following the Cursor Memory Bank system:

- `projectbrief.md` - Project overview and goals
- `productContext.md` - Project purpose and user experience goals
- `systemPatterns.md` - Architecture and design patterns
- `techContext.md` - Technologies and dependencies
- `activeContext.md` - Current work focus and next steps
- `progress.md` - Project status and known issues

## Making the Application Accessible via URL

### Local Network Access
By default, the application runs on http://localhost:5000. To make it accessible on your local network:

1. Edit `app.py` to change the host from "0.0.0.0" to your machine's IP address
2. Ensure your firewall allows connections on port 5000

### Public Access
For public access, consider deploying to a web hosting service or setting up a reverse proxy with Nginx or Apache. 