#!/usr/bin/env python3
"""
Google Tag Manager Configurator Script
This script uses the GTM API to set up variables, triggers, and tags for the portfolio website.

It configures:
1. Built-in variables needed for tracking
2. Custom data layer variables for event tracking
3. Triggers for page view and custom events
4. GA4 configuration tag
5. Event tags for all tracked events (scroll depth, time on page, etc.)
"""

import os
import json
import logging
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('gtm-configurator')

# GTM and GA4 configuration
GTM_CONTAINER_ID = 'GTM-PC9Q9VC3'
GA4_MEASUREMENT_ID = 'G-3P8MK7MHQF'
SERVICE_ACCOUNT_FILE = 'GoogleAnalytics/gair-com-au-153c7f6062f4.json'
API_SCOPES = ['https://www.googleapis.com/auth/tagmanager.edit.containers',
              'https://www.googleapis.com/auth/tagmanager.publish']

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

def get_account_and_container_paths(service):
    """Get account and container paths for the GTM container ID."""
    try:
        # List all accounts accessible to the authenticated user
        accounts = service.accounts().list().execute()
        
        # Search for the container in all accounts
        container_path = None
        account_path = None
        
        for account in accounts.get('account', []):
            account_id = account['accountId']
            account_path = f"accounts/{account_id}"
            
            try:
                # List containers in this account
                containers = service.accounts().containers().list(
                    parent=account_path).execute()
                
                # Find the container with our Container ID (public ID)
                for container in containers.get('container', []):
                    if container.get('publicId') == GTM_CONTAINER_ID:
                        container_id = container['containerId']
                        container_path = f"{account_path}/containers/{container_id}"
                        logger.info(f"Found container: {container_path}")
                        return account_path, container_path
            except Exception as container_error:
                logger.warning(f"Error listing containers for account {account_id}: {container_error}")
                
                # If we hit a rate limit, wait and retry
                if "rate" in str(container_error).lower() or "quota" in str(container_error).lower():
                    wait_time = 60
                    logger.warning(f"Rate limit hit, pausing for {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    
                    try:
                        # Retry listing containers
                        containers = service.accounts().containers().list(
                            parent=account_path).execute()
                        
                        # Find the container with our Container ID (public ID)
                        for container in containers.get('container', []):
                            if container.get('publicId') == GTM_CONTAINER_ID:
                                container_id = container['containerId']
                                container_path = f"{account_path}/containers/{container_id}"
                                logger.info(f"Found container: {container_path}")
                                return account_path, container_path
                    except Exception as retry_error:
                        logger.error(f"Error on retry: {retry_error}")
        
        if not container_path:
            logger.error(f"Container with ID {GTM_CONTAINER_ID} not found.")
            return None, None
            
    except Exception as e:
        logger.error(f"Error retrieving account and container paths: {e}")
        
        # If we hit a rate limit, wait and retry
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            wait_time = 60
            logger.warning(f"Rate limit hit, pausing for {wait_time} seconds before retry...")
            time.sleep(wait_time)
            
            try:
                # Retry listing accounts
                accounts = service.accounts().list().execute()
                
                for account in accounts.get('account', []):
                    account_id = account['accountId']
                    account_path = f"accounts/{account_id}"
                    
                    # List containers in this account
                    containers = service.accounts().containers().list(
                        parent=account_path).execute()
                    
                    # Find the container with our Container ID (public ID)
                    for container in containers.get('container', []):
                        if container.get('publicId') == GTM_CONTAINER_ID:
                            container_id = container['containerId']
                            container_path = f"{account_path}/containers/{container_id}"
                            logger.info(f"Found container on retry: {container_path}")
                            return account_path, container_path
            except Exception as retry_error:
                logger.error(f"Error on retry: {retry_error}")
        
        return None, None

def create_workspace(service, container_path):
    """Create a new workspace for the configuration."""
    # Add a timestamp to make the workspace name unique
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    workspace_name = f"API Created Configuration {timestamp}"
    
    try:
        logger.info(f"Creating workspace with name: {workspace_name}")
        workspace = service.accounts().containers().workspaces().create(
            parent=container_path,
            body={"name": workspace_name, "description": "Created via API"}
        ).execute()
        
        workspace_path = f"{container_path}/workspaces/{workspace['workspaceId']}"
        logger.info(f"Created workspace: {workspace_path}")
        return workspace_path
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        
        # If we hit a rate limit, wait and retry
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            wait_time = 120  # 2 minutes
            logger.warning(f"Rate limit hit, pausing for {wait_time} seconds before retry...")
            time.sleep(wait_time)
            
            try:
                logger.info(f"Retrying workspace creation after rate limit with name: {workspace_name}")
                workspace = service.accounts().containers().workspaces().create(
                    parent=container_path,
                    body={"name": workspace_name, "description": "Created via API (retry after rate limit)"}
                ).execute()
                
                workspace_path = f"{container_path}/workspaces/{workspace['workspaceId']}"
                logger.info(f"Created workspace: {workspace_path}")
                return workspace_path
            except Exception as retry_error:
                logger.error(f"Error on retry after rate limit: {retry_error}")
        
        # If the error is due to too many workspaces, let's try to list and delete an unused one
        if "RESOURCE_EXHAUSTED" in str(e):
            logger.warning("Too many workspaces. Attempting to list and delete an unused one...")
            try:
                # List all workspaces
                workspaces = service.accounts().containers().workspaces().list(
                    parent=container_path
                ).execute()
                
                if "workspace" in workspaces and workspaces["workspace"]:
                    # Try to delete the oldest workspace
                    oldest_workspace = workspaces["workspace"][0]
                    workspace_path_to_delete = f"{container_path}/workspaces/{oldest_workspace['workspaceId']}"
                    logger.info(f"Deleting workspace: {workspace_path_to_delete}")
                    
                    service.accounts().containers().workspaces().delete(
                        path=workspace_path_to_delete
                    ).execute()
                    
                    # Add delay to avoid rate limiting
                    time.sleep(5)
                    
                    # Try to create workspace again with the same name
                    logger.info("Retrying workspace creation after cleanup...")
                    retry_workspace = service.accounts().containers().workspaces().create(
                        parent=container_path,
                        body={"name": workspace_name, "description": "Created via API after cleanup"}
                    ).execute()
                    
                    retry_workspace_path = f"{container_path}/workspaces/{retry_workspace['workspaceId']}"
                    logger.info(f"Created workspace: {retry_workspace_path}")
                    return retry_workspace_path
            except Exception as cleanup_error:
                logger.error(f"Error during workspace cleanup: {cleanup_error}")
                # Check if this is a rate limit error too
                if "rate" in str(cleanup_error).lower() or "quota" in str(cleanup_error).lower():
                    wait_time = 120  # 2 minutes
                    logger.warning(f"Rate limit hit during cleanup, pausing for {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # We could also try to get an existing workspace as a fallback
        try:
            logger.info("Attempting to use an existing workspace as fallback...")
            workspaces = service.accounts().containers().workspaces().list(
                parent=container_path
            ).execute()
            
            if "workspace" in workspaces and workspaces["workspace"]:
                existing_workspace = workspaces["workspace"][0]
                existing_workspace_path = f"{container_path}/workspaces/{existing_workspace['workspaceId']}"
                logger.info(f"Using existing workspace: {existing_workspace_path}")
                return existing_workspace_path
        except Exception as fallback_error:
            logger.error(f"Error getting existing workspace: {fallback_error}")
        
        return None

def enable_built_in_variables(service, workspace_path):
    """Enable necessary built-in variables."""
    try:
        # Built-in variable types to enable
        variable_types = [
            # Page variables
            "pageUrl", "pageHostname", "pagePath", "referrer",
            # Utility variables
            "event", "containerId", "containerVersion", "environmentName", "debugMode",
            # Click variables
            "clickElement", "clickClasses", "clickId", "clickTarget", "clickUrl", "clickText",
            # Form variables
            "formElement", "formClasses", "formId", "formTarget", "formUrl", "formText",
        ]
        
        for i, var_type in enumerate(variable_types):
            try:
                logger.info(f"Enabling built-in variable {i+1}/{len(variable_types)}: {var_type}...")
                built_in_var = service.accounts().containers().workspaces().built_in_variables().create(
                    parent=workspace_path,
                    type=var_type
                ).execute()
                logger.info(f"Enabled built-in variable: {var_type}")
                
                # Add delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                # Variable might already be enabled
                logger.warning(f"Could not enable {var_type}: {e}")
                # If we hit a rate limit, wait longer and continue
                if "rate" in str(e).lower() or "quota" in str(e).lower():
                    logger.warning(f"Rate limit hit, pausing for 30 seconds...")
                    time.sleep(30)
        
        return True
    except Exception as e:
        logger.error(f"Error enabling built-in variables: {e}")
        return False

def create_data_layer_variables(service, workspace_path):
    """Create data layer variables for custom events."""
    variables = [
        {"name": "dlv_project_name", "dataLayerVariableName": "project_name"},
        {"name": "dlv_page_category", "dataLayerVariableName": "pageCategory"},
        {"name": "dlv_link_url", "dataLayerVariableName": "link_url"},
        {"name": "dlv_link_text", "dataLayerVariableName": "link_text"},
        {"name": "dlv_form_name", "dataLayerVariableName": "form_name"},
        {"name": "dlv_event_category", "dataLayerVariableName": "event_category"},
        {"name": "dlv_event_label", "dataLayerVariableName": "event_label"},
        {"name": "dlv_device_type", "dataLayerVariableName": "deviceType"},
        {"name": "dlv_browser", "dataLayerVariableName": "browser"},
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
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error creating variable {var['name']}: {e}")
            # If we hit a rate limit, wait longer and continue
            if "rate" in str(e).lower() or "quota" in str(e).lower():
                logger.warning(f"Rate limit hit, pausing for 30 seconds...")
                time.sleep(30)
    
    return created_vars

def create_custom_event_triggers(service, workspace_path):
    """Create custom event triggers."""
    triggers = [
        {"name": "CE - Page View", "event": "page_view"},
        {"name": "CE - Project Click", "event": "project_click"},
        {"name": "CE - External Link Click", "event": "external_link_click"},
        {"name": "CE - Form Submission", "event": "form_submission"},
        {"name": "CE - Tableau View Loaded", "event": "tableau_view_loaded"},
        {"name": "CE - GitHub Repo View", "event": "github_repo_view"},
        {"name": "CE - Tableau Interaction", "event": "tableau_interaction"},
        {"name": "CE - GitHub Repo Click", "event": "github_repo_click"},
        {"name": "CE - Skill Badge Click", "event": "skill_badge_click"},
        {"name": "CE - Resume Download", "event": "resume_download"},
        {"name": "CE - Scroll Depth", "event": "scroll_depth"},
        {"name": "CE - Time On Page", "event": "time_on_page"},
        {"name": "CE - Debug Event", "event": "debug_test_event"},
    ]
    
    created_triggers = {}
    
    # Create an "All Pages" trigger first
    try:
        logger.info("Creating All Pages trigger...")
        all_pages_trigger = service.accounts().containers().workspaces().triggers().create(
            parent=workspace_path,
            body={
                "name": "All Pages",
                "type": "pageview"
            }
        ).execute()
        
        created_triggers["All Pages"] = all_pages_trigger["triggerId"]
        logger.info(f"Created All Pages trigger with ID {all_pages_trigger['triggerId']}")
        # Add delay to avoid rate limiting
        time.sleep(2)
    except Exception as e:
        logger.error(f"Error creating All Pages trigger: {e}")
    
    # Then create custom event triggers with delays between calls
    for i, trig in enumerate(triggers):
        try:
            logger.info(f"Creating trigger {i+1}/{len(triggers)}: {trig['name']}...")
            trigger = service.accounts().containers().workspaces().triggers().create(
                parent=workspace_path,
                body={
                    "name": trig["name"],
                    "type": "customEvent",
                    "customEventFilter": [
                        {
                            "type": "equals",
                            "parameter": [
                                {"type": "template", "key": "arg0", "value": "{{_event}}"},
                                {"type": "template", "key": "arg1", "value": trig["event"]}
                            ]
                        }
                    ]
                }
            ).execute()
            
            trig_id = trigger["triggerId"]
            created_triggers[trig["name"]] = trig_id
            logger.info(f"Created trigger: {trig['name']} with ID {trig_id}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error creating trigger {trig['name']}: {e}")
            # If we hit a rate limit, wait longer and continue
            if "rate" in str(e).lower() or "quota" in str(e).lower():
                logger.warning(f"Rate limit hit, pausing for 60 seconds...")
                time.sleep(60)
    
    return created_triggers

def create_ga4_config_tag(service, workspace_path, all_pages_trigger_id):
    """Create the GA4 Configuration tag."""
    try:
        logger.info("Creating GA4 Configuration tag...")
        ga4_config_tag = service.accounts().containers().workspaces().tags().create(
            parent=workspace_path,
            body={
                "name": "GA4 Configuration",
                "type": "gaawc",  # GA4 Configuration tag
                "parameter": [
                    {"type": "template", "key": "measurementId", "value": GA4_MEASUREMENT_ID},
                    {"type": "boolean", "key": "sendPageView", "value": "false"},  # We'll handle page views separately
                    {"type": "boolean", "key": "useEcommerceDataLayer", "value": "false"},
                ]
            }
        ).execute()
        
        logger.info(f"Created GA4 Configuration tag - now adding trigger...")
        
        # Add delay to avoid rate limiting
        time.sleep(2)
        
        # Add firing trigger to tag
        tag_update = service.accounts().containers().workspaces().tags().update(
            path=f"{workspace_path}/tags/{ga4_config_tag['tagId']}",
            body={
                "name": "GA4 Configuration",
                "type": "gaawc",
                "parameter": [
                    {"type": "template", "key": "measurementId", "value": GA4_MEASUREMENT_ID},
                    {"type": "boolean", "key": "sendPageView", "value": "false"},
                    {"type": "boolean", "key": "useEcommerceDataLayer", "value": "false"},
                ],
                "firingTriggerId": [all_pages_trigger_id]
            }
        ).execute()
        
        logger.info(f"Created GA4 Configuration tag with ID {ga4_config_tag['tagId']}")
        return ga4_config_tag['tagId']
    except Exception as e:
        logger.error(f"Error creating GA4 Configuration tag: {e}")
        # If we hit a rate limit, wait and retry once
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            logger.warning(f"Rate limit hit, pausing for 60 seconds and retrying...")
            time.sleep(60)
            try:
                logger.info("Retrying GA4 Configuration tag creation...")
                ga4_config_tag = service.accounts().containers().workspaces().tags().create(
                    parent=workspace_path,
                    body={
                        "name": "GA4 Configuration",
                        "type": "gaawc",
                        "parameter": [
                            {"type": "template", "key": "measurementId", "value": GA4_MEASUREMENT_ID},
                            {"type": "boolean", "key": "sendPageView", "value": "false"},
                            {"type": "boolean", "key": "useEcommerceDataLayer", "value": "false"},
                        ],
                        "firingTriggerId": [all_pages_trigger_id]
                    }
                ).execute()
                
                logger.info(f"Successfully created GA4 Configuration tag with ID {ga4_config_tag['tagId']} on retry")
                return ga4_config_tag['tagId']
            except Exception as retry_error:
                logger.error(f"Error on retry: {retry_error}")
                return None
        return None

def create_ga4_event_tags(service, workspace_path, config_tag_id, triggers):
    """Create GA4 event tags for custom events."""
    event_tags = [
        {
            "name": "GA4 Event - Page View",
            "event_name": "page_view",
            "trigger_id": triggers.get("CE - Page View") or triggers.get("All Pages"),
            "parameters": [
                {"name": "page_title", "value": "{{Page Title}}"},
                {"name": "page_location", "value": "{{Page URL}}"},
                {"name": "page_path", "value": "{{Page Path}}"},
                {"name": "page_category", "value": "{{dlv_page_category}}"}
            ]
        },
        {
            "name": "GA4 Event - Project Click",
            "event_name": "project_click",
            "trigger_id": triggers.get("CE - Project Click"),
            "parameters": [
                {"name": "project_name", "value": "{{dlv_project_name}}"},
                {"name": "page_location", "value": "{{Page URL}}"}
            ]
        },
        {
            "name": "GA4 Event - External Link Click",
            "event_name": "outbound_click",
            "trigger_id": triggers.get("CE - External Link Click"),
            "parameters": [
                {"name": "link_url", "value": "{{dlv_link_url}}"},
                {"name": "link_text", "value": "{{dlv_link_text}}"}
            ]
        },
        {
            "name": "GA4 Event - Form Submission",
            "event_name": "form_submit",
            "trigger_id": triggers.get("CE - Form Submission"),
            "parameters": [
                {"name": "form_name", "value": "{{dlv_form_name}}"}
            ]
        },
        {
            "name": "GA4 Event - Tableau View Loaded",
            "event_name": "tableau_view",
            "trigger_id": triggers.get("CE - Tableau View Loaded"),
            "parameters": []
        },
        {
            "name": "GA4 Event - GitHub Repo View",
            "event_name": "github_repo_view",
            "trigger_id": triggers.get("CE - GitHub Repo View"),
            "parameters": []
        },
        {
            "name": "GA4 Event - Debug Test",
            "event_name": "debug_test",
            "trigger_id": triggers.get("CE - Debug Event"),
            "parameters": [
                {"name": "debug_source", "value": "GTM API"}
            ]
        }
    ]
    
    for i, tag_config in enumerate(event_tags):
        if not tag_config["trigger_id"]:
            logger.warning(f"Skipping {tag_config['name']} due to missing trigger")
            continue
            
        try:
            logger.info(f"Creating GA4 event tag {i+1}/{len(event_tags)}: {tag_config['name']}...")
            
            # Prepare parameters list for the event
            param_list = []
            for param in tag_config["parameters"]:
                param_list.append({
                    "type": "map",
                    "map": [
                        {"type": "template", "key": "name", "value": param["name"]},
                        {"type": "template", "key": "value", "value": param["value"]}
                    ]
                })
                
            # Create the GA4 event tag
            event_tag = service.accounts().containers().workspaces().tags().create(
                parent=workspace_path,
                body={
                    "name": tag_config["name"],
                    "type": "gaawe",  # GA4 Event tag
                    "parameter": [
                        {"type": "template", "key": "eventName", "value": tag_config["event_name"]},
                        {"type": "boolean", "key": "sendEcommerceData", "value": "false"},
                        {"type": "list", "key": "eventParameters", "list": param_list},
                        {"type": "tag_reference", "key": "measurementId", "value": config_tag_id}
                    ],
                    "firingTriggerId": [tag_config["trigger_id"]]
                }
            ).execute()
            
            logger.info(f"Created GA4 event tag: {tag_config['name']} with ID {event_tag['tagId']}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error creating tag {tag_config['name']}: {e}")
            # If we hit a rate limit, wait longer and continue
            if "rate" in str(e).lower() or "quota" in str(e).lower():
                logger.warning(f"Rate limit hit, pausing for 60 seconds...")
                time.sleep(60)
    
    return True

def create_version_and_publish(service, container_path, workspace_path):
    """Create a version from the workspace and publish it."""
    version_header = None  # Initialize to avoid "possibly unbound" error
    
    try:
        logger.info("Creating version from workspace...")
        # Create version
        version = service.accounts().containers().workspaces().create_version(
            path=workspace_path,
            body={
                "name": "GTM API Configuration",
                "notes": "Configured via Python API script"
            }
        ).execute()
        
        logger.info(f"Created version: {version.get('containerVersion', {}).get('name')}")
        
        # Get the version number
        version_header = version.get('containerVersion', {}).get('containerVersionId')
        
        if version_header:
            # Add delay to avoid rate limiting
            logger.info("Waiting before publishing...")
            time.sleep(5)
            
            # Publish the version
            logger.info(f"Publishing version {version_header}...")
            publish_result = service.accounts().containers().versions().publish(
                path=f"{container_path}/versions/{version_header}"
            ).execute()
            
            logger.info(f"Published version: {version_header}")
            return True
        else:
            logger.error("No version header found, cannot publish")
            return False
            
    except Exception as e:
        logger.error(f"Error publishing: {e}")
        # If we hit a rate limit, wait and retry once
        if ("rate" in str(e).lower() or "quota" in str(e).lower()) and version_header is not None:
            logger.warning(f"Rate limit hit, pausing for 60 seconds and retrying...")
            time.sleep(60)
            try:
                logger.info(f"Retrying publishing version {version_header}...")
                publish_result = service.accounts().containers().versions().publish(
                    path=f"{container_path}/versions/{version_header}"
                ).execute()
                
                logger.info(f"Successfully published version: {version_header} on retry")
                return True
            except Exception as retry_error:
                logger.error(f"Error on publishing retry: {retry_error}")
        return False

def main_step_1():
    """Step 1: Create workspace and enable built-in variables."""
    logger.info("Starting GTM configuration - Step 1")
    
    # Build the service
    service = build_service()
    
    # Use hardcoded paths to avoid API rate limits
    account_path = f"accounts/{GTM_ACCOUNT_ID}"
    container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
    logger.info(f"Using hardcoded container path: {container_path}")
    
    # Create a workspace
    workspace_path = create_workspace(service, container_path)
    if not workspace_path:
        logger.error("Failed to create workspace, exiting.")
        return False, None, None
    
    # Enable built-in variables
    if not enable_built_in_variables(service, workspace_path):
        logger.warning("Some issues with enabling built-in variables.")
    
    logger.info("Step 1 completed successfully!")
    logger.info(f"Container path: {container_path}")
    logger.info(f"Workspace path: {workspace_path}")
    return True, container_path, workspace_path

def main_step_2(container_path, workspace_path):
    """Step 2: Create data layer variables and triggers."""
    logger.info("Starting GTM configuration - Step 2")
    
    # Build the service
    service = build_service()
    
    # Create data layer variables
    variables = create_data_layer_variables(service, workspace_path)
    if not variables:
        logger.error("Failed to create variables, exiting.")
        return False, None
    
    # Create triggers
    triggers = create_custom_event_triggers(service, workspace_path)
    if not triggers:
        logger.error("Failed to create triggers, exiting.")
        return False, None
    
    logger.info("Step 2 completed successfully!")
    return True, triggers

def main_step_3(container_path, workspace_path, triggers):
    """Step 3: Create GA4 tags and publish."""
    logger.info("Starting GTM configuration - Step 3")
    
    # Build the service
    service = build_service()
    
    # Create GA4 Configuration tag
    config_tag_id = create_ga4_config_tag(service, workspace_path, triggers.get("All Pages"))
    if not config_tag_id:
        logger.error("Failed to create GA4 Configuration tag, exiting.")
        return False
    
    # Create GA4 event tags
    create_ga4_event_tags(service, workspace_path, config_tag_id, triggers)
    
    # Publish the configuration
    if create_version_and_publish(service, container_path, workspace_path):
        logger.info("GTM configuration completed and published successfully!")
        return True
    else:
        logger.error("Failed to publish configuration.")
        return False

def main():
    """Main function to execute all configuration steps."""
    # Step 1: Create workspace and enable built-in variables
    success, container_path, workspace_path = main_step_1()
    if not success:
        return False
    
    # Save paths to file for use in next steps
    with open("gtm_paths.txt", "w") as f:
        f.write(f"{container_path}\n{workspace_path}\n")
    
    logger.info("Step 1 completed. Run this script with --step=2 to continue...")
    return True

if __name__ == "__main__":
    import sys
    import pickle
    
    # Parse command line arguments
    step = 1
    for arg in sys.argv[1:]:
        if arg.startswith("--step="):
            try:
                step = int(arg.split("=")[1])
            except (ValueError, IndexError):
                print(f"Invalid step argument: {arg}")
                sys.exit(1)
    
    if step == 1:
        main()
    elif step == 2:
        # Load paths from file
        try:
            with open("gtm_paths.txt", "r") as f:
                lines = f.read().strip().split("\n")
                container_path = lines[0]
                workspace_path = lines[1]
                
            logger.info(f"Loaded container_path: {container_path}")
            logger.info(f"Loaded workspace_path: {workspace_path}")
            
            success, triggers = main_step_2(container_path, workspace_path)
            if success:
                # Save triggers to file
                with open("gtm_triggers.pickle", "wb") as f:
                    pickle.dump(triggers, f)
                logger.info("Step 2 completed. Run this script with --step=3 to continue...")
        except Exception as e:
            logger.error(f"Error in step 2: {e}")
            sys.exit(1)
    elif step == 3:
        # Load paths and triggers from files
        try:
            with open("gtm_paths.txt", "r") as f:
                lines = f.read().strip().split("\n")
                container_path = lines[0]
                workspace_path = lines[1]
            
            with open("gtm_triggers.pickle", "rb") as f:
                triggers = pickle.load(f)
                
            logger.info(f"Loaded container_path: {container_path}")
            logger.info(f"Loaded workspace_path: {workspace_path}")
            logger.info(f"Loaded {len(triggers)} triggers")
            
            success = main_step_3(container_path, workspace_path, triggers)
            if success:
                logger.info("Step 3 completed. GTM configuration is complete!")
        except Exception as e:
            logger.error(f"Error in step 3: {e}")
            sys.exit(1)
    else:
        logger.error(f"Invalid step: {step}. Valid steps are 1, 2, or 3.")
        sys.exit(1)