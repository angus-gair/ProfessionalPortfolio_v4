#!/usr/bin/env python3
"""
Google Tag Manager DataLayer Tester

This script helps test if events are being properly pushed to the dataLayer
by simulating the behavior of the website. It outputs sample dataLayer pushes
that you can verify are correctly captured in GTM.
"""

import json
import time
from datetime import datetime

def simulate_datalayer_events():
    """Simulate various dataLayer events as they would be pushed on the website."""
    
    # Create dataLayer structure - this would be window.dataLayer in JavaScript
    dataLayer = []
    
    print("== Google Tag Manager DataLayer Tester ==")
    print("This script simulates dataLayer pushes that occur on your website.")
    print("Review the output to confirm your GTM triggers will capture these events.\n")
    
    # Initial page view (happens when page loads)
    pageview = {
        'event': 'page_view',
        'pageCategory': 'projects',
        'page_title': 'Projects - Angus Gair Portfolio',
        'page_location': 'https://example.com/projects',
        'page_path': '/projects',
        'timestamp': datetime.now().isoformat()
    }
    
    dataLayer.append(pageview)
    print("\033[1mPushing Page View Event:\033[0m")
    print(json.dumps(pageview, indent=2))
    print("\nThis should trigger: 'CE - Page View' and 'GA4 Event - Page View' tag.\n")
    time.sleep(1)
    
    # Project click
    project_click = {
        'event': 'project_click',
        'project_name': 'Budget Optimization Model',
        'page_location': 'https://example.com/projects',
        'timestamp': datetime.now().isoformat()
    }
    
    dataLayer.append(project_click)
    print("\033[1mPushing Project Click Event:\033[0m")
    print(json.dumps(project_click, indent=2))
    print("\nThis should trigger: 'CE - Project Click' and 'GA4 Event - Project Click' tag.\n")
    time.sleep(1)
    
    # External link click
    external_click = {
        'event': 'external_link_click',
        'link_url': 'https://github.com/angusgair',
        'link_text': 'GitHub Profile',
        'timestamp': datetime.now().isoformat()
    }
    
    dataLayer.append(external_click)
    print("\033[1mPushing External Link Click Event:\033[0m")
    print(json.dumps(external_click, indent=2))
    print("\nThis should trigger: 'CE - External Link Click' and 'GA4 Event - External Link Click' tag.\n")
    time.sleep(1)
    
    # Form submission
    form_submit = {
        'event': 'form_submission',
        'form_name': 'contact_form',
        'timestamp': datetime.now().isoformat()
    }
    
    dataLayer.append(form_submit)
    print("\033[1mPushing Form Submission Event:\033[0m")
    print(json.dumps(form_submit, indent=2))
    print("\nThis should trigger: 'CE - Form Submission' and 'GA4 Event - Form Submission' tag.\n")
    time.sleep(1)
    
    # Debug event
    debug_event = {
        'event': 'debug_test_event',
        'event_category': 'testing',
        'event_label': 'python_script_test',
        'test_value': 42,
        'timestamp': datetime.now().isoformat()
    }
    
    dataLayer.append(debug_event)
    print("\033[1mPushing Debug Test Event:\033[0m")
    print(json.dumps(debug_event, indent=2))
    print("\nThis should trigger: 'CE - Debug Event' and 'GA4 Event - Debug Test' tag.\n")
    
    # Summary
    print("\n== DataLayer Summary ==")
    print(f"Total events pushed: {len(dataLayer)}")
    
    # Output complete dataLayer as it would exist in the browser
    print("\n== Complete DataLayer State ==")
    print(json.dumps(dataLayer, indent=2))
    
    print("\n== Verification Steps ==")
    print("1. In GTM, enter Preview mode and go to your site")
    print("2. Perform the actions that would trigger these events")
    print("3. Check if the events appear in the GTM preview pane")
    print("4. Verify that the correct GA4 event tags fire")
    print("5. Check GA4 DebugView to confirm events are sent to Google Analytics")

if __name__ == "__main__":
    simulate_datalayer_events()