# Google Tag Manager Setup Guide

## Overview

This document provides detailed setup instructions for configuring Google Tag Manager (GTM) to properly track user interactions on your portfolio website. Since automatic configuration via the GTM API requires additional permissions, these instructions will walk through manual setup steps.

## Prerequisites

1. Access to Google Tag Manager account with container ID: **GTM-PC9Q9VC3**
2. Access to Google Analytics 4 property with Measurement ID: **G-3P8MK7MHQF**

## GTM Installation Status

The website already has GTM correctly installed with:

1. Container snippet in the `<head>` of the HTML
2. No-script fallback in the `<body>` of the HTML

## Setup Instructions

### 1. Verify GTM Installation

First, let's verify the current installation:

1. Visit the website and open your browser developer tools (F12)
2. Go to the Network tab and filter for "gtm"
3. Reload the page
4. You should see a request to `gtm.js` with your container ID

### 2. Configure Basic Settings

#### Create a GA4 Configuration Tag

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Select your container (GTM-PC9Q9VC3)
3. Click **Tags** in the left sidebar
4. Click **New** to create a new tag
5. Name it "**GA4 Configuration**"
6. Click the tag type and select **Google Analytics: GA4 Configuration**
7. Enter your Measurement ID: **G-3P8MK7MHQF**
8. Under **Advanced Settings** > **Tag Firing Options**, select **Once per page**
9. In the Triggering section, add the **All Pages** trigger
10. Save the tag

### 3. Enable Built-in Variables

1. Click **Variables** in the left sidebar
2. Under **Built-in Variables**, click **Configure**
3. Enable the following variable groups:
   - Page Variables
   - Clicks Variables
   - Form Variables
   - Utility Variables
4. Click **Save**

### 4. Create Custom Variables

Create the following DataLayer variables:

| Variable Name | Data Layer Variable Name | Description |
|---------------|--------------------------|-------------|
| dlv_project_name | project_name | Captures clicked project name |
| dlv_page_category | pageCategory | Captures page category from meta tag |
| dlv_link_url | link_url | Captures clicked external link URL |
| dlv_link_text | link_text | Captures clicked external link text |
| dlv_form_name | form_name | Captures form name on submission |
| dlv_device_type | deviceType | Captures user's device type |
| dlv_browser | browser | Captures user's browser |

For each variable:

1. Go to **Variables** > **User-Defined Variables**
2. Click **New**
3. Name the variable (e.g., "dlv_project_name")
4. Select **Data Layer Variable** as the type
5. Enter the Data Layer Variable Name (e.g., "project_name")
6. Set Version to "Version 2"
7. Click **Save**

### 5. Create Custom Triggers

Create the following triggers for each custom event:

| Trigger Name | Event Name | Description |
|--------------|------------|-------------|
| CE - Page View | page_view | Fires on page view events |
| CE - Project Click | project_click | Fires when a project is clicked |
| CE - External Link Click | external_link_click | Fires when an external link is clicked |
| CE - Form Submission | form_submission | Fires when a form is submitted |
| CE - Tableau View Loaded | tableau_view_loaded | Fires when a Tableau view loads |
| CE - GitHub Repo View | github_repo_view | Fires when GitHub repos are viewed |
| CE - Debug Event | debug_test_event | For testing event tracking |

For each trigger:

1. Go to **Triggers** in the left sidebar
2. Click **New**
3. Name the trigger (e.g., "CE - Page View")
4. Click to configure the trigger
5. Select **Custom Event**
6. Enter the corresponding event name (e.g., "page_view") 
7. Set "This trigger fires on" to "All Custom Events"
8. Click **Save**

### 6. Create GA4 Event Tags

For each event, create a corresponding GA4 event tag:

#### Page View Tag

1. Create a new tag
2. Name it "**GA4 Event - Page View**"
3. Select **Google Analytics: GA4 Event** as the tag type
4. Enter "page_view" as the Event Name
5. Add these parameters:
   - page_title: {{Page Title}}
   - page_location: {{Page URL}}
   - page_path: {{Page Path}}
   - page_category: {{dlv_page_category}}
6. Under Configuration Tag, select your GA4 Configuration tag
7. Add the "CE - Page View" trigger
8. Save the tag

#### Project Click Tag

1. Create a new tag
2. Name it "**GA4 Event - Project Click**"
3. Select **Google Analytics: GA4 Event** as the tag type
4. Enter "project_click" as the Event Name
5. Add these parameters:
   - project_name: {{dlv_project_name}}
   - page_location: {{Page URL}}
6. Under Configuration Tag, select your GA4 Configuration tag
7. Add the "CE - Project Click" trigger
8. Save the tag

#### External Link Click Tag

1. Create a new tag
2. Name it "**GA4 Event - External Link Click**"
3. Select **Google Analytics: GA4 Event** as the tag type
4. Enter "outbound_click" as the Event Name
5. Add these parameters:
   - link_url: {{dlv_link_url}}
   - link_text: {{dlv_link_text}}
6. Under Configuration Tag, select your GA4 Configuration tag
7. Add the "CE - External Link Click" trigger
8. Save the tag

#### Form Submission Tag

1. Create a new tag
2. Name it "**GA4 Event - Form Submission**"
3. Select **Google Analytics: GA4 Event** as the tag type
4. Enter "form_submit" as the Event Name 
5. Add these parameters:
   - form_name: {{dlv_form_name}}
6. Under Configuration Tag, select your GA4 Configuration tag
7. Add the "CE - Form Submission" trigger
8. Save the tag

Create similar tags for the other custom events.

### 7. Test Your Configuration

1. Click the **Preview** button in GTM
2. Enter your website URL
3. Test each interaction:
   - Load different pages
   - Click on projects
   - Click external links
   - Submit the contact form
   - View Tableau dashboards
   - View GitHub repositories
4. Check the GTM Preview panel to see if events are firing correctly

### 8. Use the Debug Panel

Visit the `/analytics-debug` page on your website, which provides a testing interface for:

- Viewing the current dataLayer state
- Sending test events
- Checking if GTM is loaded correctly
- Verifying cookie presence

### 9. Publish Your Container

When everything is working correctly:

1. Click **Submit** in the top right corner
2. Add a version name (e.g., "Initial GA4 Events Setup")
3. Add a description of the changes made
4. Click **Publish**

## Verification and Troubleshooting

### Verify in Google Analytics

After publishing, check if data is flowing into Google Analytics:

1. Log in to [Google Analytics](https://analytics.google.com/)
2. Navigate to your GA4 property
3. Go to **Reports** > **Realtime**
4. Visit your website and perform various interactions
5. Verify that events are appearing in the Realtime report

### Common Issues and Solutions

1. **No data in Google Analytics**
   - Data can take 24-48 hours to appear in standard reports
   - Try using DebugView for immediate validation
   - Ensure your IP address isn't excluded in GA

2. **Events not firing**
   - Check browser console for JavaScript errors
   - Verify triggers are set up correctly in GTM
   - Test with the `/analytics-debug` page

3. **GTM Preview not working**
   - Clear browser cache and cookies
   - Try a different browser
   - Disable any ad blockers or privacy extensions

4. **DataLayer not detecting events**
   - Verify the dataLayer initialization script is loading before GTM
   - Check for JavaScript errors that might prevent event pushes
   - Use console.log to debug dataLayer pushes

## Next Steps

Once your basic tracking is working, consider enhancing your implementation with:

1. Enhanced e-commerce tracking for download clicks
2. User engagement metrics (scroll depth, time on page)
3. Custom dimensions for user segmentation
4. Setting up goals and conversions in GA4