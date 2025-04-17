This developer's guide walks you through the steps required to access, create, and manage entities within a Google Tag Manager account via the Tag Manager API v2.

Introduction
This guide walks you through various steps to access and configure a Google Tag Manager account. Upon completion, you will have a basic understanding of how to do the following tasks:

Create a Tag Manager service object.
Authenticate and authorize a user.
Work with the Tag Manager API to access and manage resources.
Before you begin
Before you begin the guide, we recommend that you become familiar with Google Tag Manager by visiting the Google Tag Manager help center.

Using a test account
If you intend to use the Tag Manager API to create, configure, or delete entities, we recommend that you implement and verify your code with a test account. Using a test account will help prevent you from making accidental changes to an active account. Once you've tested and confirmed that your code is working as expected using the test account, then you can start using the implementation with your real accounts.

Caution: When performing destructive operations using the API there will be no warnings, no confirmations, and no undo. Use a test account to test and verify your code before working with active accounts.
Select a language
Select the programming language you intend follow examples in:

Python
JavaScript

Python is selected for all code snippets in this guide.

Program overview
The example program included in this guide is a command-line app. Given an account ID, the app finds a container named Greetings and creates a Universal Analytics tag in that container. When a user visits hello-world.html, the tag sends a pageview hit.

To develop this application, you need to follow these steps:

Set up your development environment and project in the Google API Console.
Create a Tag Manager service object.
Authorize access to a Tag Manager account.
Create a Tag Manager service object.
Query the API, handle the response, and output the results.
Get an initialized Tag Manager service object.
Use the Tag Manager service object to query the Tag Manager API to do the following tasks:
Retrieve the Greetings container for the authenticated Google Tag Manager account.
Create a new workspace.
Create the Universal Analytics tag.
Create the trigger to fire the tag.
Update the tag to fire on the trigger.
Set up your development environment and project
Create the Greetings container
This guide assumes you have a Google Tag Manager account with a container named Greetings. Follow the instructions for Setup and Workflow (Web) to create an Account and a Container named Greetings.

Install a client library
Before you start, install and configure a Google APIs client library.

Create and configure a project in the Google API Console
To get started using Tag Manager API, you need to first use the setup tool, which guides you through creating a project in the Google API Console, enabling the API, and creating credentials.

This guide uses an Installed Application authentication flow. Follow the instructions below to create your project credentials. When prompted, select Installed Application for APPLICATION TYPE and Other for INSTALLED APPLICATION TYPE.

From the Credentials page, click Create credentials > OAuth client ID to create your OAuth 2.0 credentials or Create credentials > Service account key to create a service account.
If you created an OAuth client ID, then select your application type.
Fill in the form and click Create.
Your application's client IDs and service account keys are now listed on the Credentials page. For details, click a client ID; parameters vary depending on the ID type, but might include email address, client secret, JavaScript origins, or redirect URIs.

Download the client details by clicking the Download JSON button. Rename this file to client_secrets.json. This file will be used later on for authentication purposes.

Create a Tag Manager service object
The Tag Manager service object is what you'll use to make API requests.

The steps required to create a Tag Manager service object are as follows:

Authorize access to a Google Tag Manager account.
Instantiate the Tag Manager service object.
Authorize access to a Google Tag Manager account
When a user starts an application built with the Google Tag Manager API, they will have to grant the application access to their Google Tag Manager account. This process is called authorization. The recommended method for authorizing users is OAuth 2.0. If you'd like to learn more, read Tag Manager API Authorization.

The code below uses the project and client details created above to authenticate the user of the application and asks their permission to access Google Tag Manager on their behalf.

The application will attempt to open the default browser and navigate the user to a URL hosted on google.com. The user will be prompted to sign-in and grant the application access to their Tag Manager account. Once granted, the application will attempt to read a code from the browser window, then close the window.

Note: If an error occurs, the application will instead prompt the user to enter their authorization code on the command line.

Python
JavaScript

"""Access and manage a Google Tag Manager account."""

import argparse
import sys

import httplib2

from apiclient.discovery import build
from oauth2client import client
from oauth2client import file
from oauth2client import tools


def GetService(api_name, api_version, scope, client_secrets_path):
  """Get a service that communicates to a Google API.

  Args:
    api_name: string The name of the api to connect to.
    api_version: string The api version to connect to.
    scope: A list of strings representing the auth scopes to authorize for the
      connection.
    client_secrets_path: string A path to a valid client secrets file.

  Returns:
    A service that is connected to the specified API.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      client_secrets_path, scope=scope,
      message=tools.message_if_missing(client_secrets_path))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage(api_name + '.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service

def main(argv):
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/tagmanager.edit.containers']

  # Authenticate and construct service.
  service = GetService('tagmanager', 'v2', scope, 'client_secrets.json')


if __name__ == '__main__':
  main(sys.argv)

Query the Tag Manager API
The Tag Manager service object can be used to query the Tag Manager API. The following steps are required to implement the sample program:

Retrieve the Greetings container
Create the Universal Analytics tag
Create the trigger to fire the tag
Update the tag to fire on the trigger
1. Retrieve the Greetings container
The following function illustrates how a Tag Manager service object can be used to query the Tag Manager API to list all containers of an account and retrieve the container named Greetings.

You can find your Google Tag Manager account in the address bar of the Google Tag Manger web interface. For example, the account ID in the URL https://tagmanager.google.com/#/admin/accounts/112233/containers/2292948/users is 112233.
Python
JavaScript

def FindGreetingsContainer(service, account_path):
  """Find the greetings container.

  Args:
    service: the Tag Manager service object.
    account_path: the path of the Tag Manager account from which to retrieve the
      Greetings container.

  Returns:
    The greetings container if it exists, or None if it does not.
  """
  # Query the Tag Manager API to list all containers for the given account.
  container_wrapper = service.accounts().containers().list(
      parent=account_path).execute()

  # Find and return the Greetings container if it exists.
  for container in container_wrapper['container']:
    if container['name'] == 'Greetings':
      return container
  return None

Next update the main execution branch of the program to call the findGreetingsContainer function given a Tag Manager accountId. For example:

Python
JavaScript

def main(argv):
  # Get tag manager account ID from command line.
  assert len(argv) == 2 and 'usage: gtm-api-hello-world.py <account_id>'
  account_id = str(argv[1])
  account_path = 'accounts/%s' % account_id

  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/tagmanager.edit.containers']

  # Authenticate and construct service.
  service = GetService('tagmanager', 'v2', scope, 'client_secrets.json')

  # Find the greetings container.
  container = FindGreetingsContainer(service, account_path)

if __name__ == '__main__':
  main(sys.argv)

2. Create a New Workspace
The following code snippet uses the Tag Manager API to create a new workspace, which we use to manage our changes to triggers and tags. You can review the Workspace create method reference for the list of required and optional properties that can be set when creating a workspace.

Python
JavaScript

def CreateWorkspace(service, container):
    """Creates a workspace named 'my workspace'.

    Args:
      service: the Tag Manager service object.
      container: the container to insert the workspace within.

    Returns:
      The created workspace.
    """
    return service.accounts().containers().workspaces().create(
        parent=container['path'],
        body={
            'name': 'my workspace',
        }).execute()

3. Create the Universal Analytics tag
The following code snippet uses the Tag Manager API to create a Universal Analytics tag. You can review the Tag create method reference for the list of required and optional properties that can be set when creating a tag and the Tag Dictionary Reference for a list of properties for each tag type.

Python
JavaScript

def CreateHelloWorldTag(service, workspace, tracking_id):
  """Create the Universal Analytics Hello World Tag.

  Args:
    service: the Tag Manager service object.
    workspace: the workspace to create a tag within.
    tracking_id: the Universal Analytics tracking ID to use.

  Returns:
    The created tag.
  """

  hello_world_tag = {
      'name': 'Universal Analytics Hello World',
      'type': 'ua',
      'parameter': [{
          'key': 'trackingId',
          'type': 'template',
          'value': str(tracking_id),
      }],
  }

  return service.accounts().containers().workspaces().tags().create(
      parent=workspace['path'],
      body=hello_world_tag).execute()


4. Create the trigger to fire the tag
Now that a tag has been created, the next step is to create a Trigger that will fire on any page.

The trigger will be named Hello World Trigger and will fire for any page view. For example:

Python
JavaScript

def CreateHelloWorldTrigger(service, workspace):
  """Create the Hello World Trigger.

  Args:
    service: the Tag Manager service object.
    workspace: the workspace to create the trigger within.

  Returns:
    The created trigger.
  """

  hello_world_trigger = {
      'name': 'Hello World Rule',
      'type': 'PAGEVIEW'
  }

  return service.accounts().containers().workspaces().triggers().create(
      parent=workspace['path'],
      body=hello_world_trigger).execute()

5. Update the tag to fire on the trigger
Now that a tag and trigger have been created, they need to be associated with each other. To do this, add the triggerId to the list of firingTriggerIds associated with the tag. For example:

Note: To simplify the process, you could create the trigger first, then specify the triggerId when you create the tag instead of performing an additional update on the tag.
Python
JavaScript

def UpdateHelloWorldTagWithTrigger(service, tag, trigger):
  """Update a Tag with a Trigger.

  Args:
    service: the Tag Manager service object.
    tag: the tag to associate with the trigger.
    trigger: the trigger to associate with the tag.
  """
  # Get the tag to update.
  tag = service.accounts().containers().workspaces().tags().get(
      path=tag['path']).execute()

  # Update the Firing Trigger for the Tag.
  tag['firingTriggerId'] = [trigger['triggerId']]

  # Update the Tag.
  response = service.accounts().containers().workspaces().tags().update(
      path=tag['path'],
      body=tag).execute()

Next update the main execution branch of the program to call the create and update functions. For example:

Python
JavaScript

def main(argv):
  # Get tag manager account ID from command line.
  assert len(argv) == 2 and 'usage: gtm-api-hello-world.py <account_id>'
  account_id = str(argv[1])
  account_path = 'accounts/%s' % account_id

  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/tagmanager.edit.containers']

  # Authenticate and construct service.
  service = GetService('tagmanager', 'v2', scope, 'client_secrets.json')

  # Find the greetings container.
  container = FindGreetingsContainer(service, account_path)

  # Create a new workspace.
  workspace = CreateWorkspace(service, container)

  # Create the hello world tag.
  tag = CreateHelloWorldTag(
      service, workspace, 'UA-1234-5')

  # Create the hello world Trigger.
  trigger = CreateHelloWorldTrigger(
      service, workspace)

  # Update the hello world tag to fire based on the hello world tag.
  UpdateHelloWorldTagWithTrigger(service, tag, trigger)
if __name__ == '__main__':
  main(sys.argv)

Complete Example
Expand this section to see the complete code example of all steps in the guide.

Python
JavaScript

"""Access and manage a Google Tag Manager account."""

import argparse
import sys

import httplib2

from apiclient.discovery import build
from oauth2client import client
from oauth2client import file
from oauth2client import tools


def GetService(api_name, api_version, scope, client_secrets_path):
  """Get a service that communicates to a Google API.

  Args:
    api_name: string The name of the api to connect to.
    api_version: string The api version to connect to.
    scope: A list of strings representing the auth scopes to authorize for the
      connection.
    client_secrets_path: string A path to a valid client secrets file.

  Returns:
    A service that is connected to the specified API.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      client_secrets_path, scope=scope,
      message=tools.message_if_missing(client_secrets_path))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage(api_name + '.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service

def FindGreetingsContainer(service, account_path):
  """Find the greetings container.

  Args:
    service: the Tag Manager service object.
    account_path: the path of the Tag Manager account from which to retrieve the
      Greetings container.

  Returns:
    The greetings container if it exists, or None if it does not.
  """
  # Query the Tag Manager API to list all containers for the given account.
  container_wrapper = service.accounts().containers().list(
      parent=account_path).execute()

  # Find and return the Greetings container if it exists.
  for container in container_wrapper['container']:
    if container['name'] == 'Greetings':
      return container
  return None

def CreateWorkspace(service, container):
    """Creates a workspace named 'my workspace'.

    Args:
      service: the Tag Manager service object.
      container: the container to insert the workspace within.

    Returns:
      The created workspace.
    """
    return service.accounts().containers().workspaces().create(
        parent=container['path'],
        body={
            'name': 'my workspace',
        }).execute()

def CreateHelloWorldTag(service, workspace, tracking_id):
  """Create the Universal Analytics Hello World Tag.

  Args:
    service: the Tag Manager service object.
    workspace: the workspace to create a tag within.
    tracking_id: the Universal Analytics tracking ID to use.

  Returns:
    The created tag.
  """

  hello_world_tag = {
      'name': 'Universal Analytics Hello World',
      'type': 'ua',
      'parameter': [{
          'key': 'trackingId',
          'type': 'template',
          'value': str(tracking_id),
      }],
  }

  return service.accounts().containers().workspaces().tags().create(
      parent=workspace['path'],
      body=hello_world_tag).execute()


def CreateHelloWorldTrigger(service, workspace):
  """Create the Hello World Trigger.

  Args:
    service: the Tag Manager service object.
    workspace: the workspace to create the trigger within.

  Returns:
    The created trigger.
  """

  hello_world_trigger = {
      'name': 'Hello World Rule',
      'type': 'PAGEVIEW'
  }

  return service.accounts().containers().workspaces().triggers().create(
      parent=workspace['path'],
      body=hello_world_trigger).execute()

def UpdateHelloWorldTagWithTrigger(service, tag, trigger):
  """Update a Tag with a Trigger.

  Args:
    service: the Tag Manager service object.
    tag: the tag to associate with the trigger.
    trigger: the trigger to associate with the tag.
  """
  # Get the tag to update.
  tag = service.accounts().containers().workspaces().tags().get(
      path=tag['path']).execute()

  # Update the Firing Trigger for the Tag.
  tag['firingTriggerId'] = [trigger['triggerId']]

  # Update the Tag.
  response = service.accounts().containers().workspaces().tags().update(
      path=tag['path'],
      body=tag).execute()

def main(argv):
  # Get tag manager account ID from command line.
  assert len(argv) == 2 and 'usage: gtm-api-hello-world.py <account_id>'
  account_id = str(argv[1])
  account_path = 'accounts/%s' % account_id

  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/tagmanager.edit.containers']

  # Authenticate and construct service.
  service = GetService('tagmanager', 'v2', scope, 'client_secrets.json')

  # Find the greetings container.
  container = FindGreetingsContainer(service, account_path)

  # Create a new workspace.
  workspace = CreateWorkspace(service, container)

  # Create the hello world tag.
  tag = CreateHelloWorldTag(
      service, workspace, 'UA-1234-5')

  # Create the hello world Trigger.
  trigger = CreateHelloWorldTrigger(
      service, workspace)

  # Update the hello world tag to fire based on the hello world tag.
  UpdateHelloWorldTagWithTrigger(service, tag, trigger)

if __name__ == '__main__':
  main(sys.argv)


Next Steps
Now that you're familiar with how the API works, there are some additional resources for you:

API Reference – learn about the API interface and supported operations.
Parameter Reference – learn about setting parameters for tags and variables.
Review the Tag Dictionary Reference for a list of supported tags.
Review the Variable Dictionary Reference for a list of Variables that can be configured.