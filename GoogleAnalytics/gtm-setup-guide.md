# Google Tag Manager Setup Guide

This document provides instructions for setting up Google Tag Manager (GTM) for tracking user behavior on your portfolio website.

## Container Details
- **GTM Container ID**: GTM-PC9Q9VC3
- **GA4 Measurement ID**: G-3P8MK7MHQF

## Implementation Overview

GTM has been implemented on the website with the following components:

1. **GTM Container Code**: Installed in the `<head>` section of the base template
2. **GTM No-Script Fallback**: Installed immediately after the opening `<body>` tag
3. **DataLayer Initialization**: Custom JavaScript that populates the dataLayer with user and page information
4. **Custom Event Tracking**: JavaScript that pushes events to the dataLayer when users interact with the site

## Required Tag Manager Configuration

Log in to [Google Tag Manager](https://tagmanager.google.com/) and complete the following configuration:

### 1. Variables Setup

#### Built-in Variables
Enable the following built-in variables:

- **Page Variables**:
  - Page URL
  - Page Hostname
  - Page Path
  - Referrer

- **Utility Variables**:
  - Event
  - Container ID
  - Container Version
  - Environment Name
  - Debug Mode

- **Click Variables**:
  - Click Element
  - Click Classes
  - Click ID
  - Click Target
  - Click URL
  - Click Text

- **Form Variables**:
  - Form Element
  - Form Classes
  - Form ID
  - Form Target
  - Form URL
  - Form Text

#### Custom Variables

Create the following **Data Layer Variables**:

| Name                  | Data Layer Variable Name | Description                       |
|-----------------------|--------------------------|-----------------------------------|
| dlv_project_name      | project_name             | Project being clicked/viewed      |
| dlv_page_category     | pageCategory             | Category of current page          |
| dlv_link_url          | link_url                 | URL of clicked external link      |
| dlv_link_text         | link_text                | Text of clicked link              |
| dlv_form_name         | form_name                | Name of submitted form            |
| dlv_event_category    | event_category           | Category for custom events        |
| dlv_event_label       | event_label              | Label for custom events           |
| dlv_device_type       | deviceType               | User's device type                |
| dlv_browser           | browser                  | User's browser                    |
| dlv_screen_resolution | screenWidth + "x" + screenHeight | Screen resolution        |

### 2. Triggers Setup

Create the following **custom event triggers**:

| Trigger Name                | Event Name          | Description                      |
|-----------------------------|---------------------|----------------------------------|
| CE - Page View              | page_view           | When a page view occurs          |
| CE - Project Click          | project_click       | When a project card is clicked   |
| CE - External Link Click    | external_link_click | When an external link is clicked |
| CE - Form Submission        | form_submission     | When a form is submitted         |
| CE - Tableau View Loaded    | tableau_view_loaded | When a Tableau view loads        |
| CE - GitHub Repo View       | github_repo_view    | When a GitHub repo card is viewed |
| CE - Tableau Interaction    | tableau_interaction | Interactions with Tableau views  |
| CE - GitHub Repo Click      | github_repo_click   | When a GitHub repo link is clicked |
| CE - Skill Badge Click      | skill_badge_click   | When a skill badge is clicked    |
| CE - Resume Download        | resume_download     | When the resume is downloaded    |
| CE - Scroll Depth           | scroll_depth        | When user scrolls to key depths  |
| CE - Time On Page           | time_on_page        | Time spent on page metrics       |
| CE - Debug Event            | debug_test_event    | For testing GTM configuration    |

### 3. Google Analytics Setup

First, create a **GA4 Configuration Tag**:

| Setting              | Value                 |
|----------------------|-----------------------|
| Tag Name             | GA4 Configuration     |
| Tag Type             | Google Analytics: GA4 Configuration |
| Measurement ID       | G-3P8MK7MHQF          |
| Send Page View       | No (handled separately) |
| Triggering           | All Pages             |

Then, create **GA4 Event Tags** for each event:

#### Page View Event Tag

| Setting              | Value                                  |
|----------------------|----------------------------------------|
| Tag Name             | GA4 Event - Page View                  |
| Tag Type             | Google Analytics: GA4 Event            |
| Event Name           | page_view                              |
| Event Parameters     | page_category: {{dlv_page_category}}   |
|                      | page_path: {{Page Path}}               |
|                      | page_title: {{Page Title}}             |
| Triggering           | CE - Page View or All Pages             |

#### Project Click Event Tag

| Setting              | Value                                  |
|----------------------|----------------------------------------|
| Tag Name             | GA4 Event - Project Click              |
| Tag Type             | Google Analytics: GA4 Event            |
| Event Name           | project_click                          |
| Event Parameters     | project_name: {{dlv_project_name}}     |
|                      | page_location: {{Page URL}}            |
| Triggering           | CE - Project Click                     |

#### External Link Event Tag

| Setting              | Value                                  |
|----------------------|----------------------------------------|
| Tag Name             | GA4 Event - External Link Click        |
| Tag Type             | Google Analytics: GA4 Event            |
| Event Name           | outbound_click                         |
| Event Parameters     | link_url: {{dlv_link_url}}             |
|                      | link_text: {{dlv_link_text}}           |
| Triggering           | CE - External Link Click               |

#### Form Submission Event Tag

| Setting              | Value                                  |
|----------------------|----------------------------------------|
| Tag Name             | GA4 Event - Form Submission            |
| Tag Type             | Google Analytics: GA4 Event            |
| Event Name           | form_submit                            |
| Event Parameters     | form_name: {{dlv_form_name}}           |
| Triggering           | CE - Form Submission                   |

#### Create similar tags for other events following the same pattern

### 4. Testing Your Configuration

1. Use the GTM Preview mode to test your setup
2. Visit the website's `/analytics-debug` page
3. Click the various test buttons to generate events
4. Verify in GTM Preview that the events are being received and tags are firing
5. Check the GA4 DebugView in your Google Analytics property to confirm events are being recorded

### 5. Publishing

After testing and confirming all tags, triggers, and variables are working:

1. Click "Submit" in the top right corner
2. Name your version (e.g., "Initial GTM Setup with GA4 Events")
3. Add a description of the changes
4. Click "Publish"

## Event References

The website tracks the following events via dataLayer pushes:

- **Basic Page Events**:
  - page_view - On page load
  - scroll_depth - When user scrolls to 25%, 50%, 75%, 90% of page
  - time_on_page - After 30s, 60s, 120s, 300s on page
  - page_exit - When user leaves page

- **Interaction Events**:
  - project_click - When a project card/link is clicked
  - external_link_click - When external link clicked
  - form_submission - When contact form submitted
  - tableau_view_loaded - When Tableau visualization loads
  - tableau_interaction - When user interacts with Tableau
  - github_repo_view - When GitHub repo card is viewed
  - github_repo_click - When GitHub repo link is clicked
  - skill_badge_click - When skill badge is clicked
  - resume_download - When resume is downloaded

## Debugging

If you encounter issues with tracking:

1. Visit the `/analytics-debug` page
2. Use the testing tools to check if events are properly pushed to dataLayer
3. Check for any JavaScript console errors
4. Verify GTM container code installation
5. Use GTM Preview mode for detailed debugging

## Important Notes

- Google Analytics data may take 24-48 hours to fully process
- Ad blockers and privacy extensions may block Google Tag Manager
- If using a VPN, your IP may be filtered in Google Analytics settings
- GTM preview mode requires you to be logged into your Google Tag Manager account