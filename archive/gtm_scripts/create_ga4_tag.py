#!/usr/bin/env python
"""
GA4 Configuration Tag Creator

This script creates a basic GA4 configuration tag in an existing GTM workspace.
It's designed to be more focused and simpler than the full configurator.
"""

import logging
import time

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ga4-tag-creator')

# GTM and GA4 configuration
GTM_CONTAINER_ID = 'GTM-PC9Q9VC3'
GA4_MEASUREMENT_ID = 'G-3P8MK7MHQF'
SERVICE_ACCOUNT_FILE = '../GoogleAnalytics/gair-com-au-153c7f6062f4.json'
API_SCOPES = [
    'https://www.googleapis.com/auth/tagmanager.edit.containers',
    'https://www.googleapis.com/auth/tagmanager.publish',
    'https://www.googleapis.com/auth/tagmanager.readonly',
    'https://www.googleapis.com/auth/tagmanager.delete.containers',
    'https://www.googleapis.com/auth/tagmanager.manage.users',
    'https://www.googleapis.com/auth/tagmanager.manage.accounts'
]

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

def get_or_create_workspace(service, container_path):
    """Get an existing workspace or create a new one."""
    try:
        # Try to list existing workspaces
        workspaces = service.accounts().containers().workspaces().list(
            parent=container_path
        ).execute()
        
        if workspaces.get('workspace'):
            # Use the first available workspace
            workspace = workspaces.get('workspace')[0]
            workspace_path = f"{container_path}/workspaces/{workspace.get('workspaceId')}"
            logger.info(f"Using existing workspace: {workspace.get('name')} (ID: {workspace.get('workspaceId')})")
            return workspace_path
        
        # If no workspace exists, create one
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        workspace_name = f"GA4 Setup {timestamp}"
        
        workspace = service.accounts().containers().workspaces().create(
            parent=container_path,
            body={"name": workspace_name, "description": "Created for GA4 configuration"}
        ).execute()
        
        workspace_path = f"{container_path}/workspaces/{workspace['workspaceId']}"
        logger.info(f"Created new workspace: {workspace_path}")
        return workspace_path
    except Exception as e:
        logger.error(f"Error getting/creating workspace: {e}")
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            logger.warning("Rate limit hit. Waiting 60 seconds before retry...")
            time.sleep(60)
            try:
                workspaces = service.accounts().containers().workspaces().list(
                    parent=container_path
                ).execute()
                
                if workspaces.get('workspace'):
                    workspace = workspaces.get('workspace')[0]
                    workspace_path = f"{container_path}/workspaces/{workspace.get('workspaceId')}"
                    logger.info(f"Using existing workspace on retry: {workspace.get('name')} (ID: {workspace.get('workspaceId')})")
                    return workspace_path
            except Exception as retry_error:
                logger.error(f"Error on retry: {retry_error}")
        return None

def get_or_create_page_view_trigger(service, workspace_path):
    """Get an existing All Pages trigger or create a new one."""
    try:
        # Try to list existing triggers
        triggers = service.accounts().containers().workspaces().triggers().list(
            parent=workspace_path
        ).execute()
        
        # Look for an existing pageview trigger
        if triggers.get('trigger'):
            for trigger in triggers.get('trigger'):
                if trigger.get('type') == 'pageview':
                    logger.info(f"Using existing pageview trigger: {trigger.get('name')} (ID: {trigger.get('triggerId')})")
                    return trigger.get('triggerId')
        
        # If no pageview trigger exists, create one
        trigger = service.accounts().containers().workspaces().triggers().create(
            parent=workspace_path,
            body={
                "name": "All Pages",
                "type": "pageview"
            }
        ).execute()
        
        logger.info(f"Created new All Pages trigger with ID: {trigger.get('triggerId')}")
        return trigger.get('triggerId')
    except Exception as e:
        logger.error(f"Error getting/creating trigger: {e}")
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            logger.warning("Rate limit hit. Waiting 30 seconds before retry...")
            time.sleep(30)
            try:
                triggers = service.accounts().containers().workspaces().triggers().list(
                    parent=workspace_path
                ).execute()
                
                if triggers.get('trigger'):
                    for trigger in triggers.get('trigger'):
                        if trigger.get('type') == 'pageview':
                            logger.info(f"Using existing pageview trigger on retry: {trigger.get('name')} (ID: {trigger.get('triggerId')})")
                            return trigger.get('triggerId')
            except Exception as retry_error:
                logger.error(f"Error on retry: {retry_error}")
        return None

def create_ga4_config_tag(service, workspace_path, trigger_id):
    """Create a GA4 Configuration tag."""
    try:
        # Check if a GA4 config tag already exists
        tags = service.accounts().containers().workspaces().tags().list(
            parent=workspace_path
        ).execute()
        
        # Check for existing GA4 tag
        existing_ga4_tag = None
        existing_tag_names = []
        if tags.get('tag'):
            for tag in tags.get('tag'):
                existing_tag_names.append(tag.get('name', ''))
                if tag.get('type') == 'gaawc':
                    existing_ga4_tag = tag
                    logger.info(f"Found existing GA4 tag: {tag.get('name')}")
                    return tag.get('tagId')
        
        # Generate a unique name
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        tag_name = f"GA4 Configuration {timestamp}"
        
        # If we have a name conflict, make it unique
        counter = 1
        while tag_name in existing_tag_names:
            tag_name = f"GA4 Configuration {timestamp} ({counter})"
            counter += 1
        
        logger.info(f"Using tag name: {tag_name}")
        
        # Create a new GA4 Configuration tag
        ga4_tag = service.accounts().containers().workspaces().tags().create(
            parent=workspace_path,
            body={
                "name": tag_name,
                "type": "gaawc",
                "parameter": [
                    {"type": "template", "key": "measurementId", "value": GA4_MEASUREMENT_ID},
                    {"type": "boolean", "key": "sendPageView", "value": "true"},
                    {"type": "boolean", "key": "useEcommerceDataLayer", "value": "false"}
                ],
                "firingTriggerId": [trigger_id]
            }
        ).execute()
        
        logger.info(f"Created GA4 Configuration tag with ID: {ga4_tag.get('tagId')}")
        return ga4_tag.get('tagId')
    except Exception as e:
        logger.error(f"Error creating GA4 tag: {e}")
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            logger.warning("Rate limit hit. Waiting 60 seconds before retry...")
            time.sleep(60)
            try:
                # Generate a unique retry name
                retry_timestamp = time.strftime("%Y%m%d-%H%M%S")
                ga4_tag = service.accounts().containers().workspaces().tags().create(
                    parent=workspace_path,
                    body={
                        "name": f"GA4 Configuration Retry {retry_timestamp}",
                        "type": "gaawc",
                        "parameter": [
                            {"type": "template", "key": "measurementId", "value": GA4_MEASUREMENT_ID},
                            {"type": "boolean", "key": "sendPageView", "value": "true"},
                            {"type": "boolean", "key": "useEcommerceDataLayer", "value": "false"}
                        ],
                        "firingTriggerId": [trigger_id]
                    }
                ).execute()
                
                logger.info(f"Created GA4 Configuration tag on retry with ID: {ga4_tag.get('tagId')}")
                return ga4_tag.get('tagId')
            except Exception as retry_error:
                logger.error(f"Error on retry: {retry_error}")
        return None

def submit_workspace(service, workspace_path):
    """Create a version from the workspace."""
    try:
        # Submit the workspace changes
        # The correct method is create_version, not submit
        version = service.accounts().containers().workspaces().create_version(
            path=workspace_path,
            body={
                "name": f"GA4 Setup Version {time.strftime('%Y%m%d-%H%M%S')}",
                "notes": "Added GA4 Configuration tag"
            }
        ).execute()
        
        logger.info(f"Created version from workspace. CompilerError: {version.get('compilerError', 'No errors')}")
        return True
    except Exception as e:
        logger.error(f"Error creating version from workspace: {e}")
        return False

def publish_container(service, container_path, workspace_path):
    """Publish the container version."""
    try:
        # Create a version first (same as submit_workspace but getting the version ID)
        version = service.accounts().containers().workspaces().create_version(
            path=workspace_path,
            body={
                "name": f"GA4 Setup Published {time.strftime('%Y%m%d-%H%M%S')}",
                "notes": "Added GA4 Configuration tag and published"
            }
        ).execute()
        
        # Get the version ID from the response
        version_id = version.get('containerVersion', {}).get('containerVersionId')
        if not version_id:
            logger.error(f"No version ID returned: {version}")
            return False
        
        logger.info(f"Created version with ID: {version_id}")
        
        # Then publish it
        try:
            publish_response = service.accounts().containers().versions().publish(
                path=f"{container_path}/versions/{version_id}"
            ).execute()
            
            logger.info(f"Published container version: {publish_response.get('containerVersion', {}).get('containerVersionId')}")
            return True
        except Exception as publish_error:
            logger.error(f"Error publishing version: {publish_error}")
            return False
    except Exception as e:
        logger.error(f"Error creating version for publishing: {e}")
        return False

def main():
    """Main function to set up GA4 in GTM."""
    logger.info("Starting GA4 setup in GTM")
    
    # Build the service
    service = build_service()
    
    # Use hardcoded paths
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    
    # Get or create a workspace
    workspace_path = get_or_create_workspace(service, container_path)
    if not workspace_path:
        logger.error("Failed to get a workspace. Exiting.")
        return False
    
    # Get or create a page view trigger
    trigger_id = get_or_create_page_view_trigger(service, workspace_path)
    if not trigger_id:
        logger.error("Failed to get a trigger. Exiting.")
        return False
    
    # Create GA4 Configuration tag
    tag_id = create_ga4_config_tag(service, workspace_path, trigger_id)
    if not tag_id:
        logger.error("Failed to create GA4 tag. Exiting.")
        return False
    
    # Submit the workspace
    if not submit_workspace(service, workspace_path):
        logger.error("Failed to submit workspace.")
        return False
    
    # Try to publish the container
    if publish_container(service, container_path, workspace_path):
        logger.info("GA4 setup completed and published successfully!")
    else:
        logger.warning("GA4 setup completed but failed to publish. Please publish the container manually.")
    
    return True

if __name__ == "__main__":
    main()