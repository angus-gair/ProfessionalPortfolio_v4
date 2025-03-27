Tag Manager API Authorization 

bookmark_border

The document describes how an application can gain authorization to make requests to the Tag Manager API.

Authorizing Requests
Before users can view their account information on any Google site, they must first log in with a Google Account. In the same way, when users first access your application, they need to authorize your application to access their data.

Every request your application sends to the Tag Manager API must include an authorization token. The token also identifies your application to Google.

About authorization protocols
Your application must use OAuth 2.0 to authorize requests. No other authorization protocols are supported. If your application uses Sign In With Google, some aspects of authorization are handled for you.

Authorizing requests with OAuth 2.0
All requests to the Tag Manager API must be authorized by an authenticated user.

The details of the authorization process, or "flow," for OAuth 2.0 vary somewhat depending on what kind of application you're writing. The following general process applies to all application types:

When you create your application, you register it using the Google API Console. Google then provides information you'll need later, such as a client ID and a client secret.
Activate the Tag Manager API in the Google API Console. (If the API isn't listed in the API Console, then skip this step.)
When your application needs access to user data, it asks Google for a particular scope of access.
Google displays a consent screen to the user, asking them to authorize your application to request some of their data.
If the user approves, then Google gives your application a short-lived access token.
Your application requests user data, attaching the access token to the request.
If Google determines that your request and the token are valid, it returns the requested data.
Some flows include additional steps, such as using refresh tokens to acquire new access tokens. For detailed information about flows for various types of applications, see Google's OAuth 2.0 documentation.

Here's the OAuth 2.0 scope information for the Tag Manager API:

Scope	Meaning
https://www.googleapis.com/auth/tagmanager.readonly	View your Google Tag Manager containers.
https://www.googleapis.com/auth/tagmanager.edit.containers	Manage your Google Tag Manager containers.
https://www.googleapis.com/auth/tagmanager.delete.containers	Delete your Google Tag Manager containers.
https://www.googleapis.com/auth/tagmanager.edit.containerversions	Manage your Google Tag Manager container versions.
https://www.googleapis.com/auth/tagmanager.publish	Publish your Google Tag Manager containers.
https://www.googleapis.com/auth/tagmanager.manage.users	Manage user permissions of your Google Tag Manager data.
https://www.googleapis.com/auth/tagmanager.manage.accounts	Manage your Google Tag Manager accounts.
To request access using OAuth 2.0, your application needs the scope information, as well as information that Google supplies when you register your application (such as the client ID and the client secret).

Getting Started
To get started using Tag Manager API, you need to first use the setup tool, which guides you through creating a project in the Google API Console, enabling the API, and creating credentials.

To set up a new service account, do the following:

Click Create credentials > Service account key.
Choose whether to download the service account's public/private key as a standard P12 file, or as a JSON file that can be loaded by a Google API client library.
Your new public/private key pair is generated and downloaded to your machine; it serves as the only copy of this key. You are responsible for storing it securely.

Common OAuth 2.0 Flows
The following guidelines outline common use cases for specific OAuth 2.0 flows:

Web Server
This flow is good for automated/offline/scheduled access of a user's Google Tag Manager account.

Example:
Automatically updating Tag Manager information from a server.
Note: The user has to complete a one-time auth flow to grant your application offline access to their Google Tag Manager data. Afterwards, a refresh token can be used to obtain a new access token.
Client-side
Ideal for when users interact directly with the application to access their Google Tag Manager Account within a browser. This flow eliminates the need for server-side capabilities, but it also makes it impractical for automated/offline/scheduled reporting.

Example:
A customized browser based configuration tool.
Installed Apps
For applications that are distributed as a package and installed by the user. It requires that the application or user have access to a browser to complete the authentication flow.

Examples:
A desktop widget on a PC or Mac.
A plugin for a content management system. The benefit of this flow compared to web server or client-side is that a single API Console project can be used for your application. This allows for a simpler installation for users.
Service Accounts
Useful for automated/offline/scheduled access your own Google Tag Manager account. For example, to build a custom tool to monitor your own Google Tag Manager account and share it with other users.

Troubleshooting
If your access_token has expired or you use the wrong scope for a particular API call you get a 401 status code in the response.

If the authorized user does not have access to the Google Tag Manager account or container you get a 403 status code in the response. Make sure you are authorized with the correct user and that you have been granted permissions to access the Tag Manager account or container.

OAuth 2.0 Playground
The OAuth 2.0 Playground allows you to go through the entire authorization flow through a web interface. The tool also displays all the HTTP request headers required for making an authorized query. If you can't get authorization to work in your own application, you should try to get it working through the OAuth 2.0 Playground. Then you can compare the HTTP headers and request from the playground to what your application is sending. This check is a simple way to ensure you are formatting your requests properly.

Invalid grant
If you receive an invalid_grant error response when attempting to use a refresh token, the error might be caused by one or both of the following things:

Your server's clock is not in sync with NTP.
You have exceeded the refresh token limit.
Applications can request multiple refresh tokens to access a single Google Tag Manager account. For example, this is useful in situations where a user wants to install an application on multiple machines and access the same Google Tag Manager account. In this case, two refresh tokens are required, one for each installation. When the number of refresh tokens exceeds the limit, older tokens become invalid. If the application attempts to use an invalidated refresh token, an invalid_grant error response is returned. Each unique client-ID/account combination can have up to 25 refresh tokens. (Note that this limit is subject to change.) If the application continues to request refresh tokens for the same Client-ID/account combination, once the 26th token is issued, the 1st refresh token that was issued becomes invalid. The 27th requested refresh token invalidates the 2nd issued token, and so on.