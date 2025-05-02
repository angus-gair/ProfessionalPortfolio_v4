"""
GA4 Setup Validation Script

This script checks if a GA4 Configuration tag exists in the GTM container and provides
confirmation that the basic tracking setup is in place.
"""

import logging
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ga4-setup-validator')

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

def validate_ga4_tag_exists():
    """Validate that a GA4 Configuration tag exists in the GTM container."""
    try:
        service = build_service()
        
        # Get a list of workspaces
        account_path = f"accounts/{GTM_ACCOUNT_ID}"
        container_path = f"{account_path}/containers/{GTM_CONTAINER_NUMERIC_ID}"
        
        # Get all workspaces
        print("\n--- Listing all workspaces ---")
        try:
            workspaces = service.accounts().containers().workspaces().list(
                parent=container_path
            ).execute()
            
            if not workspaces.get('workspace'):
                logger.error("No workspaces found in the container.")
                print("No workspaces found in the container.")
                return []
            
            for ws in workspaces.get('workspace', []):
                print(f"Workspace: {ws.get('name')} (ID: {ws.get('workspaceId')})")
        except Exception as e:
            logger.error(f"Error listing workspaces: {e}")
            print(f"Error listing workspaces: {e}")
            return []
        
        # Try looking at specific workspace 9 where we know we created tags
        print("\n--- Checking workspace ID 9 specifically ---")
        known_workspace_id = "9"
        workspace_path = f"{container_path}/workspaces/{known_workspace_id}"
        
        try:
            tags_in_workspace = service.accounts().containers().workspaces().tags().list(
                parent=workspace_path
            ).execute()
            
            print(f"Found {len(tags_in_workspace.get('tag', []))} tags in workspace ID 9")
            for tag in tags_in_workspace.get('tag', []):
                print(f"  - Tag: {tag.get('name')} (ID: {tag.get('tagId')}, Type: {tag.get('type')})")
                
                # Print parameters for GA4 tags
                if tag.get('type') == 'gaawc':
                    print(f"    Parameters:")
                    for param in tag.get('parameter', []):
                        print(f"      {param.get('key')}: {param.get('value')}")
        except Exception as e:
            logger.error(f"Error checking workspace ID 9: {e}")
            print(f"Error checking workspace ID 9: {e}")
        
        # Check each workspace for GA4 tags
        print("\n--- Checking all workspaces for GA4 tags ---")
        ga4_tags_found = []
        
        for workspace in workspaces.get('workspace', []):
            workspace_id = workspace.get('workspaceId')
            workspace_name = workspace.get('name')
            workspace_path = f"{container_path}/workspaces/{workspace_id}"
            
            print(f"Checking workspace: {workspace_name} (ID: {workspace_id})")
            
            try:
                tags = service.accounts().containers().workspaces().tags().list(
                    parent=workspace_path
                ).execute()
                
                ga4_count = 0
                if tags.get('tag'):
                    for tag in tags.get('tag'):
                        # Check for both gaawc (older format) and googtag (newer format) for GA4 tags
                        if tag.get('type') == 'gaawc' or (tag.get('type') == 'googtag' and 'GA4' in tag.get('name', '')):
                            ga4_count += 1
                            tag_info = {
                                'name': tag.get('name'),
                                'id': tag.get('tagId'),
                                'type': tag.get('type'),
                                'workspace': workspace_name,
                                'workspace_id': workspace_id
                            }
                            ga4_tags_found.append(tag_info)
                            
                            # Check if the tag has the correct measurement ID
                            if tag.get('parameter'):
                                measurement_id = None
                                for param in tag.get('parameter'):
                                    if param.get('key') == 'measurementId' or param.get('key') == 'tagId':
                                        measurement_id = param.get('value')
                                        if measurement_id == GA4_MEASUREMENT_ID:
                                            logger.info(f"Found GA4 tag with correct measurement ID: {tag.get('name')} (ID: {tag.get('tagId')})")
                                            tag_info['correct_measurement_id'] = True
                                        else:
                                            logger.warning(f"GA4 tag has incorrect measurement ID: {measurement_id} instead of {GA4_MEASUREMENT_ID}")
                                            tag_info['correct_measurement_id'] = False
                                        tag_info['measurement_id'] = measurement_id
                
                print(f"  Found {ga4_count} GA4 tag(s) in this workspace")
                
            except Exception as e:
                logger.error(f"Error checking workspace {workspace_name}: {e}")
                print(f"  Error checking workspace: {e}")
        
        if ga4_tags_found:
            logger.info(f"Found {len(ga4_tags_found)} GA4 Configuration tag(s) in GTM container.")
            for tag in ga4_tags_found:
                logger.info(f"  - Tag: {tag['name']} (ID: {tag['id']}) in workspace: {tag['workspace']}")
                if tag.get('correct_measurement_id') is True:
                    logger.info(f"    Measurement ID is correct: {GA4_MEASUREMENT_ID}")
                elif tag.get('correct_measurement_id') is False:
                    logger.warning(f"    Warning: Measurement ID is incorrect! ({tag.get('measurement_id')})")
            return ga4_tags_found
        else:
            logger.error("No GA4 Configuration tags found in any workspace.")
            return []
    except Exception as e:
        logger.error(f"Error validating GA4 tag: {e}")
        print(f"Error validating GA4 tag: {e}")
        return []

def validate_gtm_container_installed():
    """Check if the GTM container ID is installed in base.html."""
    try:
        with open("templates/base.html", "r") as file:
            content = file.read()
            
            # Check for GTM container snippet in the <head>
            head_gtm_script = f"https://www.googletagmanager.com/gtm.js?id={GTM_CONTAINER_ID}"
            
            # Check for GTM noscript snippet in the <body>
            body_gtm_script = f"https://www.googletagmanager.com/ns.html?id={GTM_CONTAINER_ID}"
            
            if head_gtm_script in content and body_gtm_script in content:
                logger.info(f"GTM container {GTM_CONTAINER_ID} is properly installed in base.html.")
                return True
            elif head_gtm_script in content:
                logger.warning(f"GTM container {GTM_CONTAINER_ID} is installed in <head> but missing <body> noscript tag.")
                return True
            elif body_gtm_script in content:
                logger.warning(f"GTM container {GTM_CONTAINER_ID} is installed in <body> noscript but missing <head> script.")
                return True
            else:
                logger.error(f"GTM container {GTM_CONTAINER_ID} is not installed in base.html.")
                return False
    except Exception as e:
        logger.error(f"Error checking GTM container installation: {e}")
        return False

def main():
    """Main function to validate the GA4 setup."""
    logger.info("Starting GA4 setup validation")
    
    # Check if GTM container is installed
    gtm_installed = validate_gtm_container_installed()
    
    # Check if GA4 Configuration tag exists
    ga4_tags = validate_ga4_tag_exists()
    
    # Output summary
    print("\n===== GA4 SETUP VALIDATION SUMMARY =====")
    print(f"GTM Container {GTM_CONTAINER_ID} installed: {'Yes' if gtm_installed else 'No'}")
    print(f"Number of GA4 Configuration tags found: {len(ga4_tags)}")
    
    if ga4_tags:
        print("\nGA4 Configuration Tags:")
        for i, tag in enumerate(ga4_tags, 1):
            measurement_id_status = "✓ Correct" if tag.get('correct_measurement_id') is True else "✗ Incorrect" if tag.get('correct_measurement_id') is False else "? Unknown"
            print(f"  {i}. {tag['name']} (ID: {tag['id']}) in workspace: {tag['workspace']}")
            print(f"     Measurement ID: {measurement_id_status}")
    
    print("\nSetup Status: " + ("✓ Complete" if gtm_installed and ga4_tags else "✗ Incomplete"))
    if not gtm_installed:
        print("  - GTM container is not properly installed in base.html")
    if not ga4_tags:
        print("  - No GA4 Configuration tag found in GTM container")
    
    if gtm_installed and ga4_tags:
        print("\nNext Steps:")
        print("  1. Verify that dataLayer events are being properly tracked")
        print("  2. Check Google Analytics 4 real-time reports to confirm data is flowing")
        print("  3. Consider creating additional event tags for custom events")
    else:
        print("\nRecommended Actions:")
        if not gtm_installed:
            print("  1. Install GTM container snippet in base.html")
        if not ga4_tags:
            print("  2. Create a GA4 Configuration tag in GTM with measurement ID: " + GA4_MEASUREMENT_ID)
    
    return gtm_installed and bool(ga4_tags)

if __name__ == "__main__":
    main()