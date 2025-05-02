#!/usr/bin/env python3
"""
DataLayer Variables Creator

This script sets up the necessary DataLayer variables in GTM for tracking:
1. Scroll depth variables (scroll_percent)
2. Time on page variables (time_seconds)
3. User engagement variables (page_title, page_path)

These variables will be used by the GA4 event tags to send data to Google Analytics.
"""

import os
import time
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('datalayer-variables-creator')

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
    workspace_name = f"DataLayer Variables {timestamp}"
    
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
            body={"name": workspace_name, "description": "Created for DataLayer variables"}
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

def create_datalayer_variables(service, workspace_path):
    """Create DataLayer variables for tracking metrics."""
    variables = [
        {"name": "dlv_scroll_percent", "dataLayerVariableName": "scroll_percent"},
        {"name": "dlv_time_seconds", "dataLayerVariableName": "time_seconds"},
        {"name": "dlv_page_title", "dataLayerVariableName": "page_title"},
        {"name": "dlv_page_path", "dataLayerVariableName": "page_path"},
        {"name": "dlv_page_category", "dataLayerVariableName": "page_category"},
        {"name": "dlv_client_id", "dataLayerVariableName": "client_id"},
        {"name": "dlv_session_id", "dataLayerVariableName": "session_id"},
        {"name": "dlv_user_engagement", "dataLayerVariableName": "user_engagement"}
    ]
    
    created_vars = {}
    
    for i, var in enumerate(variables):
        try:
            logger.info(f"Creating variable {i+1}/{len(variables)}: {var['name']}...")
            variable = service.accounts().containers().workspaces().variables().create(
                parent=workspace_path,
                body={
                    "name": var["name"],
                    "type": "v",  # Data Layer Variable
                    "parameter": [
                        {"type": "template", "key": "name", "value": var["dataLayerVariableName"]},
                        {"type": "integer", "key": "dataLayerVersion", "value": "2"}
                    ]
                }
            ).execute()
            
            var_id = variable["variableId"]
            created_vars[var["name"]] = var_id
            logger.info(f"Created variable: {var['name']} with ID {var_id}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error creating variable {var['name']}: {e}")
            # If we hit a rate limit, wait longer and continue
            if "rate" in str(e).lower() or "quota" in str(e).lower():
                logger.warning(f"Rate limit hit, pausing for 30 seconds...")
                time.sleep(30)
                # Try this variable again after waiting
                try:
                    logger.info(f"Retrying variable {var['name']} after rate limit wait...")
                    variable = service.accounts().containers().workspaces().variables().create(
                        parent=workspace_path,
                        body={
                            "name": var["name"],
                            "type": "v",
                            "parameter": [
                                {"type": "template", "key": "name", "value": var["dataLayerVariableName"]},
                                {"type": "integer", "key": "dataLayerVersion", "value": "2"}
                            ]
                        }
                    ).execute()
                    
                    var_id = variable["variableId"]
                    created_vars[var["name"]] = var_id
                    logger.info(f"Created variable on retry: {var['name']} with ID {var_id}")
                except Exception as retry_error:
                    logger.error(f"Failed on retry for {var['name']}: {retry_error}")
    
    return created_vars

def create_version_and_publish(service, container_path, workspace_path):
    """Create a version from the workspace and publish it."""
    try:
        # Create a version
        logger.info("Creating a version from the workspace...")
        version = service.accounts().containers().workspaces().create_version(
            path=workspace_path,
            body={
                "name": f"DataLayer Variables {time.strftime('%Y-%m-%d')}",
                "notes": "Added DataLayer variables for tracking metrics"
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
    """Main function to create DataLayer variables."""
    try:
        # Step 1: Set up service and get paths
        service = build_service()
        account_path, container_path = get_account_and_container_paths(service)
        
        # Step 2: Get or create a workspace
        workspace_path = get_or_create_workspace(service, container_path)
        if not workspace_path:
            logger.error("Failed to get or create a workspace.")
            return False
        
        # Step 3: Create DataLayer variables
        variables = create_datalayer_variables(service, workspace_path)
        if not variables:
            logger.error("Failed to create DataLayer variables.")
            return False
        
        # Step 4: Create a version and publish it
        success = create_version_and_publish(service, container_path, workspace_path)
        
        if success:
            logger.info("DataLayer variables have been created successfully!")
            return True
        else:
            logger.warning("DataLayer variables were created but couldn't be published.")
            logger.info("Please log in to GTM and publish the workspace manually.")
            return True
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    print("=" * 40)
    print("  DATALAYER VARIABLES CREATOR")
    print("=" * 40)
    
    if main():
        print("\nSuccess! DataLayer variables for tracking metrics")
        print("have been created in your GTM container.")
        print("\nThese variables will be used by GA4 event tags")
        print("to send data to Google Analytics.")
    else:
        print("\nThere was an issue creating the DataLayer variables.")
        print("Please check the log messages above for details.")