#!/usr/bin/env python3
"""
GA4 Events Verification Script

This script checks if the GA4 Configuration tag and event tags exist in the GTM container
and verifies that the necessary triggers and variables are set up for proper event tracking.
"""

import os
import json
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ga4-events-verifier')

# GTM and GA4 configuration
GTM_CONTAINER_ID = 'GTM-PC9Q9VC3'
GA4_MEASUREMENT_ID = 'G-3P8MK7MHQF'
SERVICE_ACCOUNT_FILE = 'GoogleAnalytics/gair-com-au-153c7f6062f4.json'
API_SCOPES = ['https://www.googleapis.com/auth/tagmanager.readonly']

# Hardcoded paths from previous configurations
GTM_ACCOUNT_ID = '6275069304'
GTM_CONTAINER_NUMERIC_ID = '209628263'

def get_credentials():
    """Get credentials for the Google Tag Manager API."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=API_SCOPES)
        return credentials
    except Exception as e:
        logger.error(f"Error getting credentials: {e}")
        raise

def build_service():
    """Build the Tag Manager service."""
    credentials = get_credentials()
    service = build('tagmanager', 'v2', credentials=credentials)
    return service

def get_account_and_container_paths(service):
    """Get account and container paths for the GTM container ID."""
    # Hardcoded paths to avoid API quota limits
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    return account_path, container_path

def get_live_workspace_path(service, container_path):
    """Get the live workspace path."""
    try:
        # Get published container version
        published = service.accounts().containers().versions().live(
            parent=container_path
        ).execute()
        
        if "containerVersion" in published:
            workspace_id = published["containerVersion"].get("workspaceId", "9")
            workspace_path = f"{container_path}/workspaces/{workspace_id}"
            return workspace_path
        else:
            # Fallback to the default workspace
            return f"{container_path}/workspaces/9"
    except Exception as e:
        logger.error(f"Error getting live workspace: {e}")
        # Fallback to the default workspace
        return f"{container_path}/workspaces/9"

def check_ga4_config_tag(service, workspace_path):
    """Check if the GA4 configuration tag exists and has the correct measurement ID."""
    try:
        # List all tags in the workspace
        tags = service.accounts().containers().workspaces().tags().list(
            parent=workspace_path
        ).execute()
        
        ga4_config_tags = []
        
        # Find GA4 configuration tags
        for tag in tags.get('tag', []):
            if tag['type'] == 'googtag':  # GA4 configuration tag type
                # Check if this is the main GA4 configuration tag
                is_config = False
                measurement_id = None
                
                for param in tag.get('parameter', []):
                    if param.get('key') == 'tagId' and 'value' in param:
                        measurement_id = param['value']
                    
                    if param.get('key') == 'configTag' and param.get('value') == 'true':
                        is_config = True
                
                if is_config and measurement_id == GA4_MEASUREMENT_ID:
                    ga4_config_tags.append({
                        'name': tag['name'],
                        'id': tag['tagId'],
                        'measurement_id': measurement_id
                    })
        
        if ga4_config_tags:
            print("\n=== GA4 Configuration Tags ===")
            for tag in ga4_config_tags:
                print(f"✓ Found GA4 configuration tag: {tag['name']} (ID: {tag['id']})")
                print(f"  - Measurement ID: {tag['measurement_id']}")
            return True
        else:
            print("\n=== GA4 Configuration Tags ===")
            print("✗ No GA4 configuration tags found with the correct measurement ID.")
            return False
    
    except Exception as e:
        logger.error(f"Error checking GA4 configuration tags: {e}")
        return False

def check_event_tags(service, workspace_path):
    """Check if the event tags exist and are properly configured."""
    try:
        # List all tags in the workspace
        tags = service.accounts().containers().workspaces().tags().list(
            parent=workspace_path
        ).execute()
        
        event_tags = []
        
        # Find GA4 event tags
        for tag in tags.get('tag', []):
            if tag['type'] == 'googtag' or tag['type'] == 'gaawc':  # GA4 event tag types
                # Check if this is an event tag (not a configuration tag)
                is_event = False
                event_name = None
                
                for param in tag.get('parameter', []):
                    if param.get('key') == 'eventName' and 'value' in param:
                        event_name = param['value']
                        is_event = True
                
                if is_event:
                    event_tags.append({
                        'name': tag['name'],
                        'id': tag['tagId'],
                        'event_name': event_name
                    })
        
        print("\n=== GA4 Event Tags ===")
        if event_tags:
            for tag in event_tags:
                print(f"✓ Found GA4 event tag: {tag['name']} (ID: {tag['id']})")
                print(f"  - Event Name: {tag['event_name']}")
            return True
        else:
            print("✗ No GA4 event tags found.")
            return False
    
    except Exception as e:
        logger.error(f"Error checking GA4 event tags: {e}")
        return False

def check_custom_event_triggers(service, workspace_path):
    """Check if the custom event triggers exist."""
    try:
        # List all triggers in the workspace
        triggers = service.accounts().containers().workspaces().triggers().list(
            parent=workspace_path
        ).execute()
        
        custom_triggers = []
        
        # Find custom event triggers
        for trigger in triggers.get('trigger', []):
            if trigger['type'] == 'customEvent':  # Custom event trigger type
                event_name = None
                
                # Extract the event name
                for filter_group in trigger.get('customEventFilter', []):
                    for param in filter_group.get('parameter', []):
                        if param.get('key') == 'arg1' and 'value' in param:
                            event_name = param['value']
                
                custom_triggers.append({
                    'name': trigger['name'],
                    'id': trigger['triggerId'],
                    'event_name': event_name
                })
        
        print("\n=== Custom Event Triggers ===")
        if custom_triggers:
            for trigger in custom_triggers:
                print(f"✓ Found custom event trigger: {trigger['name']} (ID: {trigger['id']})")
                if trigger['event_name']:
                    print(f"  - Event Name: {trigger['event_name']}")
            return True
        else:
            print("✗ No custom event triggers found.")
            return False
    
    except Exception as e:
        logger.error(f"Error checking custom event triggers: {e}")
        return False

def check_data_layer_variables(service, workspace_path):
    """Check if the data layer variables exist."""
    try:
        # List all variables in the workspace
        variables = service.accounts().containers().workspaces().variables().list(
            parent=workspace_path
        ).execute()
        
        data_layer_vars = []
        
        # Find data layer variables
        for var in variables.get('variable', []):
            if var['type'] == 'v':  # Data layer variable type
                var_name = None
                
                # Extract the variable name
                for param in var.get('parameter', []):
                    if param.get('key') == 'name' and 'value' in param:
                        var_name = param['value']
                
                data_layer_vars.append({
                    'name': var['name'],
                    'id': var['variableId'],
                    'data_layer_name': var_name
                })
        
        print("\n=== Data Layer Variables ===")
        if data_layer_vars:
            for var in data_layer_vars:
                print(f"✓ Found data layer variable: {var['name']} (ID: {var['id']})")
                if var['data_layer_name']:
                    print(f"  - Data Layer Name: {var['data_layer_name']}")
            return True
        else:
            print("✗ No data layer variables found.")
            return False
    
    except Exception as e:
        logger.error(f"Error checking data layer variables: {e}")
        return False

def check_dataLayer_implementation():
    """Check if the dataLayer is properly implemented on the website."""
    print("\n=== Website DataLayer Implementation ===")
    print("To verify the dataLayer implementation on your website:")
    print("1. Open your website in Chrome")
    print("2. Open Developer Tools (F12)")
    print("3. Go to the Console tab")
    print("4. Type 'window.dataLayer' and press Enter")
    print("5. You should see an array of dataLayer objects")
    print("\nAlternatively, visit the analytics debug page:")
    print("https://www.yourdomain.com/analytics-debug")
    print("This page will show you the dataLayer contents and events.")

def main():
    """Main function to verify GA4 events setup."""
    try:
        print("=" * 50)
        print("          GA4 EVENTS VERIFICATION")
        print("=" * 50)
        
        # Step 1: Set up service and get paths
        service = build_service()
        account_path, container_path = get_account_and_container_paths(service)
        
        # Step 2: Get the live workspace path
        workspace_path = get_live_workspace_path(service, container_path)
        if not workspace_path:
            print("Failed to get the live workspace path.")
            return False
        
        print(f"\nChecking GTM Container: {GTM_CONTAINER_ID}")
        print(f"GA4 Measurement ID: {GA4_MEASUREMENT_ID}")
        
        # Step 3: Check GA4 configuration tag
        has_config = check_ga4_config_tag(service, workspace_path)
        
        # Step 4: Check event tags
        has_events = check_event_tags(service, workspace_path)
        
        # Step 5: Check custom event triggers
        has_triggers = check_custom_event_triggers(service, workspace_path)
        
        # Step 6: Check data layer variables
        has_variables = check_data_layer_variables(service, workspace_path)
        
        # Step 7: Check dataLayer implementation
        check_dataLayer_implementation()
        
        # Provide summary
        print("\n=== Summary ===")
        print(f"GA4 Configuration Tag: {'✓' if has_config else '✗'}")
        print(f"GA4 Event Tags: {'✓' if has_events else '✗'}")
        print(f"Custom Event Triggers: {'✓' if has_triggers else '✗'}")
        print(f"Data Layer Variables: {'✓' if has_variables else '✗'}")
        
        # Overall status
        if has_config and has_events and has_triggers and has_variables:
            print("\n✅ GA4 events setup is complete!")
            print("Data should be flowing into your Google Analytics account.")
            print("Check your GA4 reports in 24-48 hours to see the data.")
            return True
        else:
            print("\n⚠️ GA4 events setup is incomplete.")
            print("Some components are missing. Please run the appropriate configuration scripts.")
            return False
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    main()