#!/usr/bin/env python3
"""
Google Tag Manager Setup Verification Script
This script tests if the GTM container is properly configured by checking container info
and validating if the required tags, triggers, and variables are set up.
"""

import os
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('gtm-verifier')

# GTM configuration
GTM_CONTAINER_ID = 'GTM-PC9Q9VC3'
SERVICE_ACCOUNT_FILE = '../GoogleAnalytics/gair-com-au-153c7f6062f4.json'
API_SCOPES = ['https://www.googleapis.com/auth/tagmanager.readonly']

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
        
        container_path = None
        account_path = None
        container_info = None
        
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
                    container_info = container
                    logger.info(f"Found container: {container_path}")
                    return account_path, container_path, container_info
        
        logger.error(f"Container with ID {GTM_CONTAINER_ID} not found.")
        return None, None, None
            
    except Exception as e:
        logger.error(f"Error retrieving account and container paths: {e}")
        return None, None, None

def check_published_version(service, container_path):
    """Check if there's a published version for the container."""
    try:
        # Get the published version
        published = service.accounts().containers().versions().published(
            parent=container_path).execute()
        
        if published:
            version = published.get('containerVersion', {})
            logger.info(f"Published version found: {version.get('name')} (Version {version.get('containerVersionId')})")
            logger.info(f"Published on: {version.get('fingerprint')}")
            
            # Count items in the container
            tag_count = len(version.get('tag', []))
            trigger_count = len(version.get('trigger', []))
            variable_count = len(version.get('variable', []))
            
            logger.info(f"Container contains {tag_count} tags, {trigger_count} triggers, and {variable_count} variables")
            return True
        else:
            logger.warning("No published version found for this container")
            return False
            
    except Exception as e:
        logger.error(f"Error checking published version: {e}")
        return False

def check_ga4_config(service, container_path):
    """Check if the GA4 configuration is set up."""
    try:
        # Get the published version
        published = service.accounts().containers().versions().published(
            parent=container_path).execute()
        
        if not published:
            logger.warning("No published version to check GA4 config")
            return False
            
        version = published.get('containerVersion', {})
        tags = version.get('tag', [])
        
        # Look for GA4 Configuration tag
        ga4_config = None
        for tag in tags:
            if tag.get('type') == 'gaawc':  # GA4 Configuration tag type
                ga4_config = tag
                break
        
        if ga4_config:
            # Get Measurement ID
            for param in ga4_config.get('parameter', []):
                if param.get('key') == 'measurementId':
                    logger.info(f"Found GA4 Configuration tag with Measurement ID: {param.get('value')}")
                    return True
            
            logger.warning("GA4 Configuration tag found but missing Measurement ID")
            return False
        else:
            logger.warning("No GA4 Configuration tag found")
            return False
            
    except Exception as e:
        logger.error(f"Error checking GA4 configuration: {e}")
        return False

def check_event_tags(service, container_path):
    """Check if the event tags are set up."""
    try:
        # Get the published version
        published = service.accounts().containers().versions().published(
            parent=container_path).execute()
        
        if not published:
            logger.warning("No published version to check event tags")
            return False
            
        version = published.get('containerVersion', {})
        tags = version.get('tag', [])
        
        # Expected event tags
        expected_tags = [
            "GA4 Event - Page View",
            "GA4 Event - Project Click",
            "GA4 Event - External Link Click",
            "GA4 Event - Form Submission"
        ]
        
        found_tags = []
        
        # Check for event tags
        for tag in tags:
            if tag.get('type') == 'gaawe':  # GA4 Event tag type
                tag_name = tag.get('name', '')
                found_tags.append(tag_name)
                logger.info(f"Found GA4 event tag: {tag_name}")
        
        # Check if all expected tags are found
        missing_tags = [tag for tag in expected_tags if tag not in found_tags]
        
        if missing_tags:
            logger.warning(f"Missing expected event tags: {', '.join(missing_tags)}")
            return False
        else:
            logger.info("All expected event tags are configured")
            return True
            
    except Exception as e:
        logger.error(f"Error checking event tags: {e}")
        return False

def main():
    """Main function to verify GTM setup."""
    logger.info("Starting GTM setup verification")
    
    # Build the service
    service = build_service()
    
    # Get account and container paths
    account_path, container_path, container_info = get_account_and_container_paths(service)
    if not container_path:
        logger.error("Container not found, verification failed.")
        return False
    
    logger.info(f"Container info: {json.dumps(container_info, indent=2)}")
    
    # Check published version
    version_ok = check_published_version(service, container_path)
    
    # Check GA4 configuration
    ga4_ok = check_ga4_config(service, container_path)
    
    # Check event tags
    events_ok = check_event_tags(service, container_path)
    
    # Overall status
    if version_ok and ga4_ok and events_ok:
        logger.info("✅ GTM setup verification PASSED")
        return True
    else:
        if not version_ok:
            logger.error("❌ No published version found")
        if not ga4_ok:
            logger.error("❌ GA4 configuration issue")
        if not events_ok:
            logger.error("❌ Event tags issue")
            
        logger.error("❌ GTM setup verification FAILED")
        return False

if __name__ == "__main__":
    main()