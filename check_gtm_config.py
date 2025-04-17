#!/usr/bin/env python
"""
GTM Configuration Checker

This script checks the current state of the GTM container configuration
and reports what has been set up and what is still needed.
"""

import json
import logging
import time

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('gtm-config-checker')

# GTM and GA4 configuration
GTM_CONTAINER_ID = 'GTM-PC9Q9VC3'
GA4_MEASUREMENT_ID = 'G-3P8MK7MHQF'
SERVICE_ACCOUNT_FILE = 'GoogleAnalytics/gair-com-au-153c7f6062f4.json'
API_SCOPES = ['https://www.googleapis.com/auth/tagmanager.readonly']

# Hardcoded paths from previous runs
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

def check_container_info():
    """Check the container information."""
    service = build_service()
    
    # Use hardcoded paths
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    
    try:
        container = service.accounts().containers().get(
            path=container_path
        ).execute()
        
        print("\n=== GTM Container Information ===")
        print(f"Container Name: {container.get('name')}")
        print(f"Public ID: {container.get('publicId')}")
        print(f"Usage Context: {container.get('usageContext', [])}")
        print(f"Notes: {container.get('notes', 'None')}")
        
        return True
    except Exception as e:
        logger.error(f"Error checking container info: {e}")
        return False

def check_live_version():
    """Check if there's a published live version."""
    service = build_service()
    
    # Use hardcoded paths
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    
    try:
        # Get the container's latest published version
        container = service.accounts().containers().get(
            path=container_path
        ).execute()
        
        published_version_id = container.get('publicId')
        
        print("\n=== Published Versions ===")
        if published_version_id:
            print(f"Current published version: {published_version_id}")
        else:
            print("No published version found.")
        
        # List available versions
        try:
            versions = service.accounts().containers().version_headers().list(
                parent=container_path
            ).execute()
            
            if versions.get('containerVersionHeader'):
                print("\nAvailable versions:")
                for version in versions.get('containerVersionHeader', []):
                    print(f"  - Version: {version.get('name', 'Unnamed')} (ID: {version.get('containerId')})")
                    if version.get('deleted'):
                        print("    Status: Deleted")
                    elif version.get('numMacros', 0) > 0 or version.get('numRules', 0) > 0 or version.get('numTags', 0) > 0:
                        print(f"    Contains: {version.get('numTags', 0)} tags, {version.get('numTriggers', 0)} triggers, {version.get('numVariables', 0)} variables")
            else:
                print("No container versions found.")
        except Exception as list_error:
            logger.warning(f"Could not list version headers: {list_error}")
        
        return True
    except Exception as e:
        logger.error(f"Error checking live version: {e}")
        return False

def check_variables():
    """Check the configured variables."""
    service = build_service()
    
    # Use hardcoded paths
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    
    try:
        # First, get an available workspace
        workspaces = service.accounts().containers().workspaces().list(
            parent=container_path
        ).execute()
        
        if not workspaces.get('workspace'):
            print("\n=== Variables ===")
            print("No workspaces found to check variables.")
            return False
        
        # Use the first available workspace
        workspace = workspaces.get('workspace')[0]
        workspace_path = f"{container_path}/workspaces/{workspace.get('workspaceId')}"
        
        print(f"\n=== Variables (Workspace: {workspace.get('name')}) ===")
        
        # Get custom variables
        try:
            variables_response = service.accounts().containers().workspaces().variables().list(
                parent=workspace_path
            ).execute()
            
            variables = variables_response.get('variable', [])
            
            if variables:
                print(f"Custom Variables: {len(variables)}")
                for var in variables:
                    var_type = var.get('type', 'unknown')
                    var_name = var.get('name', 'Unnamed')
                    print(f"  - {var_name} (Type: {var_type})")
            else:
                print("No custom variables configured.")
        except Exception as var_error:
            logger.warning(f"Could not get custom variables: {var_error}")
            print("Could not retrieve custom variables.")
        
        # Get built-in variables
        try:
            built_in_vars_response = service.accounts().containers().workspaces().built_in_variables().list(
                parent=workspace_path
            ).execute()
            
            built_in_variables = built_in_vars_response.get('builtInVariable', [])
            
            if built_in_variables:
                print(f"Built-in Variables: {len(built_in_variables)}")
                for var in built_in_variables:
                    var_type = var.get('type', 'unknown')
                    print(f"  - {var_type}")
            else:
                print("No built-in variables enabled.")
        except Exception as built_in_error:
            logger.warning(f"Could not get built-in variables: {built_in_error}")
            print("Could not retrieve built-in variables.")
        
        return True
    except Exception as e:
        logger.error(f"Error checking variables: {e}")
        return False

def check_triggers():
    """Check the configured triggers."""
    service = build_service()
    
    # Use hardcoded paths
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    
    try:
        # First, get an available workspace
        workspaces = service.accounts().containers().workspaces().list(
            parent=container_path
        ).execute()
        
        if not workspaces.get('workspace'):
            print("\n=== Triggers ===")
            print("No workspaces found to check triggers.")
            return False
        
        # Use the first available workspace
        workspace = workspaces.get('workspace')[0]
        workspace_path = f"{container_path}/workspaces/{workspace.get('workspaceId')}"
        
        print(f"\n=== Triggers (Workspace: {workspace.get('name')}) ===")
        
        # Get triggers
        try:
            triggers_response = service.accounts().containers().workspaces().triggers().list(
                parent=workspace_path
            ).execute()
            
            triggers = triggers_response.get('trigger', [])
            
            if triggers:
                print(f"Triggers: {len(triggers)}")
                trigger_types = {}
                for trigger in triggers:
                    trigger_type = trigger.get('type', 'unknown')
                    trigger_name = trigger.get('name', 'Unnamed')
                    if trigger_type not in trigger_types:
                        trigger_types[trigger_type] = 0
                    trigger_types[trigger_type] += 1
                    print(f"  - {trigger_name} (Type: {trigger_type})")
                
                if trigger_types:
                    print("\nTrigger Types Summary:")
                    for t_type, count in trigger_types.items():
                        print(f"  - {t_type}: {count}")
            else:
                print("No triggers configured.")
        except Exception as trigger_error:
            logger.warning(f"Could not get triggers: {trigger_error}")
            print("Could not retrieve triggers.")
        
        return True
    except Exception as e:
        logger.error(f"Error checking triggers: {e}")
        return False

def check_tags():
    """Check the configured tags."""
    service = build_service()
    
    # Use hardcoded paths
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    
    try:
        # First, get an available workspace
        workspaces = service.accounts().containers().workspaces().list(
            parent=container_path
        ).execute()
        
        if not workspaces.get('workspace'):
            print("\n=== Tags ===")
            print("No workspaces found to check tags.")
            return False
        
        # Use the first available workspace
        workspace = workspaces.get('workspace')[0]
        workspace_path = f"{container_path}/workspaces/{workspace.get('workspaceId')}"
        
        print(f"\n=== Tags (Workspace: {workspace.get('name')}) ===")
        
        # Get tags
        try:
            tags_response = service.accounts().containers().workspaces().tags().list(
                parent=workspace_path
            ).execute()
            
            tags = tags_response.get('tag', [])
            
            if tags:
                print(f"Tags: {len(tags)}")
                tag_types = {}
                for tag in tags:
                    tag_type = tag.get('type', 'unknown')
                    tag_name = tag.get('name', 'Unnamed')
                    if tag_type not in tag_types:
                        tag_types[tag_type] = 0
                    tag_types[tag_type] += 1
                    print(f"  - {tag_name} (Type: {tag_type})")
                
                if tag_types:
                    print("\nTag Types Summary:")
                    for t_type, count in tag_types.items():
                        print(f"  - {t_type}: {count}")
                
                # Check for GA4 configuration
                ga4_config_tags = [t for t in tags if t.get('type') == 'gaawc']
                if ga4_config_tags:
                    print("\nGA4 Configuration Found:")
                    for ga4_tag in ga4_config_tags:
                        measurement_id = None
                        send_page_view = None
                        for param in ga4_tag.get('parameter', []):
                            if param.get('key') == 'measurementId':
                                measurement_id = param.get('value')
                            elif param.get('key') == 'sendPageView':
                                send_page_view = param.get('value')
                        
                        print(f"  - {ga4_tag.get('name')}")
                        print(f"    Measurement ID: {measurement_id}")
                        print(f"    Send Page View: {send_page_view}")
                else:
                    print("\nNo GA4 Configuration Tags Found!")
            else:
                print("No tags configured.")
        except Exception as tag_error:
            logger.warning(f"Could not get tags: {tag_error}")
            print("Could not retrieve tags.")
        
        return True
    except Exception as e:
        logger.error(f"Error checking tags: {e}")
        return False

def analyze_configuration():
    """Analyze the configuration and provide recommendations."""
    print("\n=== Configuration Analysis ===")
    
    # Check if basic GTM snippet is properly installed
    print("1. GTM Installation:")
    print("   - The GTM container ID (GTM-PC9Q9VC3) should be properly installed in your website's HTML.")
    print("   - You should have both the <head> and <body> snippets installed.")
    
    # Check if dataLayer is properly initialized
    print("\n2. DataLayer Initialization:")
    print("   - The dataLayer should be initialized before the GTM snippet.")
    print("   - Basic user and page information should be included in the dataLayer.")
    
    # Recommendations for proper event tracking
    print("\n3. Event Tracking:")
    print("   - Key website interactions should be tracked with appropriate events.")
    print("   - Common events include page_view, click_event, form_submission, etc.")
    print("   - DataLayer pushes should include relevant contextual information.")
    
    # Recommendations for proper GA4 configuration
    print("\n4. GA4 Configuration:")
    print("   - A GA4 Configuration tag should be set up with measurement ID G-3P8MK7MHQF.")
    print("   - This tag should fire on all pages.")
    print("   - Event tags should reference this configuration tag.")
    
    print("\n5. Next Steps:")
    print("   - If GTM is not properly configured, run the gtm_configurator.py script.")
    print("   - Verify event tracking by checking the analytics_debug page.")
    print("   - Test events through the GTM preview mode.")

def main():
    """Main function to check GTM configuration."""
    print("\n========================================")
    print("         GTM CONFIGURATION CHECK        ")
    print("========================================")
    
    # Check if we can access the container
    if not check_container_info():
        print("\nError: Could not access GTM container information.")
        return
    
    # Check if there's a published version
    if not check_live_version():
        print("\nError: Could not check published versions.")
    
    # Check variables
    if not check_variables():
        print("\nError: Could not check variables.")
    
    # Check triggers
    if not check_triggers():
        print("\nError: Could not check triggers.")
    
    # Check tags
    if not check_tags():
        print("\nError: Could not check tags.")
    
    # Analyze configuration and provide recommendations
    analyze_configuration()
    
    print("\n========================================")
    print("         CHECK COMPLETE                 ")
    print("========================================")

if __name__ == "__main__":
    main()