# Google Tag Manager Implementation Guide

## Overview

This document outlines the Google Tag Manager (GTM) implementation for tracking visitor behavior on the portfolio website. The data collected is sent to Google Analytics 4 (GA4) for analysis.

## Configuration

### Container Information

- **GTM Container ID:** `GTM-PC9Q9VC3`
- **GA4 Measurement ID:** `G-3P8MK7MHQF`

### Installation

The GTM container is implemented in the website's templates/base.html file with:

1. **Head snippet:** Placed in the `<head>` section before any other scripts
2. **Body snippet:** Placed immediately after the opening `<body>` tag

### DataLayer Initialization

The dataLayer is initialized in the base template and enhanced with:

- **datalayer-init.js:** Sets up the initial dataLayer parameters
- **gtm-config.js:** Provides functions for pushing events to the dataLayer

## Events Being Tracked

The following events are being tracked through the DataLayer:

| Event Name | Description | Parameters |
|------------|-------------|------------|
| `page_view` | Triggered when a user loads any page | `page_title`, `page_location`, `page_path`, `page_category` |
| `scroll_depth` | Triggered when user scrolls to 25%, 50%, 75%, 90% of page | `scroll_percent`, `page_title`, `page_path` |
| `time_on_page` | Triggered at 30s, 60s, 120s, 300s intervals | `time_seconds`, `page_title`, `page_path` |
| `project_click` | Triggered when a user clicks on a project | `project_name`, `page_location` |
| `external_link_click` | Triggered when a user clicks an external link | `link_url`, `link_text` |
| `form_submission` | Triggered on contact form submission | `form_name`, `page_location` |
| `tableau_view_loaded` | Triggered when a Tableau visualization loads | `visualization_name` |
| `github_repo_view` | Triggered when GitHub repositories are viewed | `repo_count` |
| `github_repo_click` | Triggered when a GitHub repository is clicked | `repo_name`, `repo_url` |
| `resume_download` | Triggered when the resume is downloaded | `file_format` |

## GTM Container Structure

The GTM container includes:

### Variables

#### Built-in Variables
- Page variables (Page URL, Page Hostname, Page Path, etc.)
- Click variables (Click Element, Click Classes, Click ID, etc.)
- Form variables (Form Element, Form Classes, Form ID, etc.)
- Utility variables (Container ID, Environment, etc.)

#### Custom Variables
- `dlv_scroll_percent` - Captures scroll depth percentage
- `dlv_time_seconds` - Captures time spent on page
- `dlv_page_title` - Captures the page title
- `dlv_page_path` - Captures the page path
- `dlv_page_category` - Captures the page category
- `dlv_project_name` - Captures project names
- `dlv_link_url` - Captures external link URLs
- `dlv_link_text` - Captures external link text
- `dlv_form_name` - Captures form names
- `dlv_event_category` - Captures event categories
- `dlv_event_label` - Captures event labels

### Triggers

- **Page View:** Fires on all page views
- **Custom Event Triggers:**
  - `CE - Scroll Depth` - Fires on scroll_depth events
  - `CE - Time On Page` - Fires on time_on_page events
  - `CE - Project Click` - Fires on project_click events
  - `CE - External Link Click` - Fires on external_link_click events
  - `CE - Form Submission` - Fires on form_submission events
  - `CE - Tableau View Loaded` - Fires on tableau_view_loaded events
  - `CE - GitHub Repo View` - Fires on github_repo_view events
  - `CE - GitHub Repo Click` - Fires on github_repo_click events
  - `CE - Resume Download` - Fires on resume_download events

### Tags

- **GA4 Configuration:** Sets up the base GA4 configuration with Measurement ID
- **Event Tags:**
  - `GA4 Event - Page View` - Sends page view data to GA4
  - `GA4 Event - Scroll Depth` - Sends scroll depth data to GA4
  - `GA4 Event - Time On Page` - Sends time on page data to GA4
  - `GA4 Event - Project Click` - Sends project click data to GA4
  - `GA4 Event - External Link Click` - Sends external link click data to GA4
  - `GA4 Event - Form Submission` - Sends form submission data to GA4
  - `GA4 Event - Tableau Interaction` - Sends Tableau interaction data to GA4
  - `GA4 Event - GitHub Repo Click` - Sends GitHub repo click data to GA4

## Debugging

A debugging page is available at `/analytics-debug` or `/analytics-debug` that shows:

1. All events being pushed to the dataLayer
2. The current status of the GTM container
3. Test buttons to manually trigger events
4. Links to GTM Preview mode

To test that events are being captured properly:

1. Visit the analytics debug page
2. Check that events are appearing in the DataLayer Contents section
3. Click the "Test Page View Event" and "Send Test Event" buttons to verify event tracking
4. Use the "Open GTM Debug Mode" button to view events in GTM's Preview mode

## Configuration Scripts

Several Python scripts are available for configuring and validating the GTM setup:

- `check_gtm_config.py` - Checks the current GTM container configuration
- `gtm_configurator.py` - Sets up the GTM container with variables, triggers, and tags
- `create_ga4_tag.py` - Creates a GA4 configuration tag
- `create_datalayer_variables.py` - Creates DataLayer variables for tracking metrics
- `create_advanced_ga4_events.py` - Configures scroll depth and time on page tracking
- `verify_ga4_events.py` - Verifies that the GA4 events are properly configured
- `validate_ga4_setup.py` - Validates that the GA4 configuration tag exists
- `verify_gtm_setup.py` - Verifies that the GTM container is properly configured

## Next Steps

After setting up the GTM container, you should:

1. **Log into GTM** and publish the workspace with the new configuration
2. **Log into GA4** and check that data is flowing into your Analytics property
3. Set up **custom reports** in GA4 to analyze the collected data

The data should start appearing in GA4 reports within 24-48 hours after implementation.