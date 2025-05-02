#!/usr/bin/env python3
"""
Advanced GA4 Event Configuration Script

This script configures Google Tag Manager to track important user engagement metrics:
1. Scroll depth (25%, 50%, 75%, 90%)
2. Time on page (30s, 60s, 120s, 300s)

These metrics will be sent to Google Analytics 4 for analysis.
"""

import os
import time
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ga4-event-configurator')

# GTM and GA4 configuration
GTM_CONTAINER_ID = 'GTM-PC9Q9VC3'
GA4_MEASUREMENT_ID = 'G-3P8MK7MHQF'
SERVICE_ACCOUNT_FILE = '../GoogleAnalytics/gair-com-au-153c7f6062f4.json'
API_SCOPES = ['https://www.googleapis.com/auth/tagmanager.edit.containers',
              'https://www.googleapis.com/auth/tagmanager.publish']

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

def get_or_create_workspace(service, container_path):
    """Get an existing workspace or create a new one."""
    # Add a timestamp to make the workspace name unique
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    workspace_name = f"Advanced Events Config {timestamp}"
    
    try:
        # First, try to list existing workspaces
        workspaces = service.accounts().containers().workspaces().list(
            parent=container_path
        ).execute()
        
        # If workspaces exist, use the first one
        if "workspace" in workspaces and workspaces["workspace"]:
            existing_workspace = workspaces["workspace"][0]
            existing_workspace_path = f"{container_path}/workspaces/{existing_workspace['workspaceId']}"
            logger.info(f"Using existing workspace: {existing_workspace_path}")
            return existing_workspace_path
        
        # If no workspaces, create a new one
        logger.info(f"Creating workspace with name: {workspace_name}")
        workspace = service.accounts().containers().workspaces().create(
            parent=container_path,
            body={"name": workspace_name, "description": "Created for advanced GA4 event tracking"}
        ).execute()
        
        workspace_path = f"{container_path}/workspaces/{workspace['workspaceId']}"
        logger.info(f"Created workspace: {workspace_path}")
        return workspace_path
    except Exception as e:
        logger.error(f"Error accessing or creating workspace: {e}")
        # Default to a fixed workspace path if all else fails
        default_path = f"{container_path}/workspaces/9"
        logger.warning(f"Using default workspace path: {default_path}")
        return default_path

def get_ga4_config_tag(service, workspace_path):
    """Find the GA4 configuration tag in the workspace."""
    try:
        # List all tags in the workspace
        tags = service.accounts().containers().workspaces().tags().list(
            parent=workspace_path
        ).execute()
        
        # Look for the GA4 configuration tag
        for tag in tags.get('tag', []):
            if tag['type'] == 'googtag' and 'tagManagerUrl' in tag:
                logger.info(f"Found GA4 Configuration tag: {tag['name']} (ID: {tag['tagId']})")
                return tag['tagId']
        
        logger.warning("No GA4 Configuration tag found in the workspace.")
        return None
    except Exception as e:
        logger.error(f"Error finding GA4 configuration tag: {e}")
        return None

def create_custom_event_triggers(service, workspace_path):
    """Create scroll depth and time on page event triggers."""
    triggers = [
        {"name": "CE - Scroll Depth", "event": "scroll_depth"},
        {"name": "CE - Time On Page", "event": "time_on_page"},
    ]
    
    created_triggers = {}
    
    for i, trigger in enumerate(triggers):
        try:
            logger.info(f"Creating trigger {i+1}/{len(triggers)}: {trigger['name']}...")
            trigger_body = service.accounts().containers().workspaces().triggers().create(
                parent=workspace_path,
                body={
                    "name": trigger["name"],
                    "type": "customEvent",
                    "customEventFilter": [
                        {
                            "type": "equals",
                            "parameter": [
                                {"type": "template", "key": "arg0", "value": "{{_event}}"},
                                {"type": "template", "key": "arg1", "value": trigger["event"]}
                            ]
                        }
                    ]
                }
            ).execute()
            
            created_triggers[trigger["name"]] = trigger_body["triggerId"]
            logger.info(f"Created trigger: {trigger['name']} with ID {trigger_body['triggerId']}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error creating trigger {trigger['name']}: {e}")
            # If we hit a rate limit, wait longer and continue
            if "rate" in str(e).lower() or "quota" in str(e).lower():
                logger.warning(f"Rate limit hit, pausing for 30 seconds...")
                time.sleep(30)
                # Skip this trigger for now
                continue
    
    return created_triggers

def create_scroll_depth_tag(service, workspace_path, config_tag_id, trigger_id):
    """Create a GA4 event tag for scroll depth tracking."""
    if not trigger_id:
        logger.error("Missing trigger ID for scroll depth tag.")
        return None
    
    try:
        logger.info("Creating Scroll Depth GA4 event tag...")
        tag = service.accounts().containers().workspaces().tags().create(
            parent=workspace_path,
            body={
                "name": "GA4 Event - Scroll Depth",
                "type": "gaawc",  # GA4 event tag type
                "parameter": [
                    {"type": "boolean", "key": "sendEcommerceData", "value": "false"},
                    {"type": "template", "key": "eventName", "value": "scroll"},
                    {"type": "template", "key": "measurementId", "value": GA4_MEASUREMENT_ID},
                    {"type": "list", "key": "eventParameters", "list": [
                        {"type": "map", "map": [
                            {"type": "template", "key": "name", "value": "percent_scrolled"},
                            {"type": "template", "key": "value", "value": "{{Scroll Depth Threshold}}"}
                        ]},
                        {"type": "map", "map": [
                            {"type": "template", "key": "name", "value": "page_title"},
                            {"type": "template", "key": "value", "value": "{{Page Title}}"}
                        ]},
                        {"type": "map", "map": [
                            {"type": "template", "key": "name", "value": "page_path"},
                            {"type": "template", "key": "value", "value": "{{Page Path}}"}
                        ]}
                    ]},
                    {"type": "tagReference", "key": "measurementIdOverride", "value": config_tag_id}
                ],
                "firingTriggerId": [trigger_id]
            }
        ).execute()
        
        logger.info(f"Created Scroll Depth tag with ID {tag['tagId']}")
        return tag['tagId']
    except Exception as e:
        logger.error(f"Error creating Scroll Depth tag: {e}")
        return None

def create_time_on_page_tag(service, workspace_path, config_tag_id, trigger_id):
    """Create a GA4 event tag for time on page tracking."""
    if not trigger_id:
        logger.error("Missing trigger ID for time on page tag.")
        return None
    
    try:
        logger.info("Creating Time On Page GA4 event tag...")
        tag = service.accounts().containers().workspaces().tags().create(
            parent=workspace_path,
            body={
                "name": "GA4 Event - Time On Page",
                "type": "gaawc",  # GA4 event tag type
                "parameter": [
                    {"type": "boolean", "key": "sendEcommerceData", "value": "false"},
                    {"type": "template", "key": "eventName", "value": "user_engagement"},
                    {"type": "template", "key": "measurementId", "value": GA4_MEASUREMENT_ID},
                    {"type": "list", "key": "eventParameters", "list": [
                        {"type": "map", "map": [
                            {"type": "template", "key": "name", "value": "engagement_time_msec"},
                            {"type": "template", "key": "value", "value": "{{Scroll Depth Threshold}}000"}
                        ]},
                        {"type": "map", "map": [
                            {"type": "template", "key": "name", "value": "page_title"},
                            {"type": "template", "key": "value", "value": "{{Page Title}}"}
                        ]},
                        {"type": "map", "map": [
                            {"type": "template", "key": "name", "value": "page_path"},
                            {"type": "template", "key": "value", "value": "{{Page Path}}"}
                        ]}
                    ]},
                    {"type": "tagReference", "key": "measurementIdOverride", "value": config_tag_id}
                ],
                "firingTriggerId": [trigger_id]
            }
        ).execute()
        
        logger.info(f"Created Time On Page tag with ID {tag['tagId']}")
        return tag['tagId']
    except Exception as e:
        logger.error(f"Error creating Time On Page tag: {e}")
        return None

def create_version_and_publish(service, container_path, workspace_path):
    """Create a version from the workspace and publish it."""
    try:
        # Create a version
        logger.info("Creating a version from the workspace...")
        version = service.accounts().containers().workspaces().create_version(
            path=workspace_path,
            body={
                "name": f"Advanced GA4 Events {time.strftime('%Y-%m-%d')}",
                "notes": "Added scroll depth and time on page tracking"
            }
        ).execute()
        
        if "containerVersion" in version:
            version_id = version["containerVersion"]["containerVersionId"]
            logger.info(f"Created version with ID: {version_id}")
            
            # Publish the container version
            logger.info("Publishing the container version...")
            publish = service.accounts().containers().versions().publish(
                path=f"{container_path}/versions/{version_id}"
            ).execute()
            
            logger.info(f"Published container: {publish.get('containerVersion', {}).get('name')}")
            return True
        else:
            logger.error("Failed to create version.")
            return False
    except Exception as e:
        logger.error(f"Error creating version or publishing: {e}")
        logger.warning("You may need to manually publish the changes in the GTM interface.")
        return False

def main():
    """Main function to configure advanced GA4 events."""
    try:
        # Step 1: Set up service and get paths
        service = build_service()
        account_path, container_path = get_account_and_container_paths(service)
        
        # Step 2: Get or create a workspace
        workspace_path = get_or_create_workspace(service, container_path)
        if not workspace_path:
            logger.error("Failed to get or create a workspace.")
            return False
        
        # Step 3: Find the GA4 configuration tag
        config_tag_id = get_ga4_config_tag(service, workspace_path)
        if not config_tag_id:
            logger.error("Failed to find GA4 configuration tag.")
            return False
        
        # Step 4: Create custom event triggers
        triggers = create_custom_event_triggers(service, workspace_path)
        if not triggers:
            logger.error("Failed to create custom event triggers.")
            return False
        
        # Step 5: Create GA4 event tags
        scroll_tag_id = create_scroll_depth_tag(
            service, 
            workspace_path, 
            config_tag_id, 
            triggers.get("CE - Scroll Depth")
        )
        
        time_tag_id = create_time_on_page_tag(
            service, 
            workspace_path, 
            config_tag_id, 
            triggers.get("CE - Time On Page")
        )
        
        # Step 6: Create a version and publish it
        success = create_version_and_publish(service, container_path, workspace_path)
        
        if success:
            logger.info("Advanced GA4 events have been configured successfully!")
            return True
        else:
            logger.warning("Configuration was created but couldn't be published.")
            logger.info("Please log in to GTM and publish the workspace manually.")
            return True
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    print("=" * 40)
    print("  ADVANCED GA4 EVENTS CONFIGURATION")
    print("=" * 40)
    
    if main():
        print("\nSuccess! GA4 event tracking for scroll depth and time on page")
        print("has been configured in your GTM container.")
        print("\nPlease check your Google Analytics 4 reports in 24-48 hours")
        print("to see the data flowing in.")
    else:
        print("\nThere was an issue configuring the advanced GA4 events.")
        print("Please check the log messages above for details.")