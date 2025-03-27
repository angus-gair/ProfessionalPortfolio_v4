#!/usr/bin/env python3
"""
Google Tag Manager Configurator Script
This script uses the GTM API to set up variables, triggers, and tags for the portfolio website.
"""

import os
import json
import logging
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
        
        if not container_path:
            logger.error(f"Container with ID {GTM_CONTAINER_ID} not found.")
            return None, None
            
    except Exception as e:
        logger.error(f"Error retrieving account and container paths: {e}")
        return None, None

def create_workspace(service, container_path):
    """Create a new workspace for the configuration."""
    try:
        workspace_name = "API Created Configuration"
        workspace = service.accounts().containers().workspaces().create(
            parent=container_path,
            body={"name": workspace_name, "description": "Created via API"}
        ).execute()
        
        workspace_path = f"{container_path}/workspaces/{workspace['workspaceId']}"
        logger.info(f"Created workspace: {workspace_path}")
        return workspace_path
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
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
        
        for var_type in variable_types:
            try:
                built_in_var = service.accounts().containers().workspaces().built_in_variables().create(
                    parent=workspace_path,
                    type=var_type
                ).execute()
                logger.info(f"Enabled built-in variable: {var_type}")
            except Exception as e:
                # Variable might already be enabled
                logger.warning(f"Could not enable {var_type}: {e}")
        
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
    
    for var in variables:
        try:
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
            
        except Exception as e:
            logger.error(f"Error creating variable {var['name']}: {e}")
    
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
    
    for trig in triggers:
        try:
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
            
        except Exception as e:
            logger.error(f"Error creating trigger {trig['name']}: {e}")
    
    # Create an "All Pages" trigger
    try:
        all_pages_trigger = service.accounts().containers().workspaces().triggers().create(
            parent=workspace_path,
            body={
                "name": "All Pages",
                "type": "pageview"
            }
        ).execute()
        
        created_triggers["All Pages"] = all_pages_trigger["triggerId"]
        logger.info(f"Created All Pages trigger with ID {all_pages_trigger['triggerId']}")
    except Exception as e:
        logger.error(f"Error creating All Pages trigger: {e}")
    
    return created_triggers

def create_ga4_config_tag(service, workspace_path, all_pages_trigger_id):
    """Create the GA4 Configuration tag."""
    try:
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
    
    for tag_config in event_tags:
        if not tag_config["trigger_id"]:
            logger.warning(f"Skipping {tag_config['name']} due to missing trigger")
            continue
            
        try:
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
            
        except Exception as e:
            logger.error(f"Error creating tag {tag_config['name']}: {e}")
    
    return True

def create_version_and_publish(service, container_path, workspace_path):
    """Create a version from the workspace and publish it."""
    try:
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
            # Publish the version
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
        return False

def main():
    """Main function to configure GTM."""
    logger.info("Starting GTM configuration")
    
    # Build the service
    service = build_service()
    
    # Get account and container paths
    account_path, container_path = get_account_and_container_paths(service)
    if not container_path:
        logger.error("Container not found, exiting.")
        return False
    
    # Create a workspace
    workspace_path = create_workspace(service, container_path)
    if not workspace_path:
        logger.error("Failed to create workspace, exiting.")
        return False
    
    # Enable built-in variables
    if not enable_built_in_variables(service, workspace_path):
        logger.warning("Some issues with enabling built-in variables.")
    
    # Create data layer variables
    variables = create_data_layer_variables(service, workspace_path)
    if not variables:
        logger.error("Failed to create variables, exiting.")
        return False
    
    # Create triggers
    triggers = create_custom_event_triggers(service, workspace_path)
    if not triggers:
        logger.error("Failed to create triggers, exiting.")
        return False
    
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

if __name__ == "__main__":
    main()