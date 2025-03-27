# Google Tag Manager Manual Setup Guide

## Issue with Programmatic Configuration

We attempted to automatically configure your Google Tag Manager container using the GTM API, but encountered the following issue:

**The service account (`replit@gair-com-au.iam.gserviceaccount.com`) doesn't have access to the GTM container (GTM-PC9Q9VC3)**

To resolve this issue and set up GTM properly, you have two options:

1. **Grant API Access** to the service account (recommended for future automation)
2. **Configure GTM Manually** following the steps below

## How to Grant API Access (Optional)

If you want to enable programmatic configuration:

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Select the container with ID `GTM-PC9Q9VC3`
3. Click on **Admin** > **User Management**
4. Click **+ Add Users**
5. Enter the service account email: `replit@gair-com-au.iam.gserviceaccount.com`
6. Select at least **Read, Edit, Approve, Publish** permissions
7. Click **Confirm**

After granting access, run the script again:
```
python gtm_configurator.py
```

## Manual GTM Configuration Guide

If you prefer to configure GTM manually, follow these detailed steps:

### Step 1: Set Up Google Analytics 4 Configuration Tag

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Navigate to your container (GTM-PC9Q9VC3)
3. Click on **Tags** in the left sidebar
4. Click **New** to create a new tag
5. Name it **GA4 Configuration**
6. Click the tag configuration block and select **Google Analytics: GA4 Configuration**
7. Enter your Measurement ID: **G-3P8MK7MHQF**
8. Uncheck **Send a page view event when this configuration loads**
9. Under **Advanced Settings** > **Tag Firing Options**, select **Once per page**
10. In the Triggering section, select **All Pages**
11. Click **Save**

### Step 2: Enable Built-in Variables

1. Click on **Variables** in the left sidebar
2. Under **Built-in Variables**, click **Configure**
3. Enable the following variable categories:
   - **Page Variables**: Page URL, Page Hostname, Page Path, Referrer
   - **Utility Variables**: Event, Container ID, Debug Mode
   - **Click Variables**: Click Element, Click Classes, Click ID, Click Target, Click URL, Click Text
   - **Form Variables**: Form Element, Form Classes, Form ID, Form Target, Form URL, Form Text
4. Click **Save**

### Step 3: Create Custom Variables

Create the following **Data Layer Variables**:

1. Click **Variables** > **New** (under User-Defined Variables)
2. Name it **dlv_project_name**
3. Click the variable configuration block and select **Data Layer Variable**
4. Enter **project_name** as the Data Layer Variable Name
5. Leave Version as **Version 2**
6. Click **Save**

Repeat the process for these additional variables:
- **dlv_page_category** (Data Layer name: pageCategory)
- **dlv_link_url** (Data Layer name: link_url)
- **dlv_link_text** (Data Layer name: link_text)
- **dlv_form_name** (Data Layer name: form_name)
- **dlv_event_category** (Data Layer name: event_category)
- **dlv_event_label** (Data Layer name: event_label)
- **dlv_device_type** (Data Layer name: deviceType)
- **dlv_browser** (Data Layer name: browser)

### Step 4: Create Custom Event Triggers

Create the following triggers for custom events:

1. Click **Triggers** > **New**
2. Name it **CE - Page View**
3. Click the trigger configuration block and select **Custom Event**
4. Enter **page_view** as the Event name
5. Leave **This trigger fires on** as **All Custom Events**
6. Click **Save**

Repeat for these additional triggers:
- **CE - Project Click** (Event name: project_click)
- **CE - External Link Click** (Event name: external_link_click)
- **CE - Form Submission** (Event name: form_submission)
- **CE - Tableau View Loaded** (Event name: tableau_view_loaded)
- **CE - GitHub Repo View** (Event name: github_repo_view)
- **CE - Tableau Interaction** (Event name: tableau_interaction)
- **CE - GitHub Repo Click** (Event name: github_repo_click)
- **CE - Skill Badge Click** (Event name: skill_badge_click)
- **CE - Resume Download** (Event name: resume_download)
- **CE - Scroll Depth** (Event name: scroll_depth)
- **CE - Time On Page** (Event name: time_on_page)
- **CE - Debug Event** (Event name: debug_test_event)

### Step 5: Create GA4 Event Tags

Now create tags for each event that will send data to GA4:

#### Page View Tag

1. Click **Tags** > **New**
2. Name it **GA4 Event - Page View**
3. Click the tag configuration block and select **Google Analytics: GA4 Event**
4. Enter **page_view** as the Event Name
5. Under **Event Parameters**:
   - Click **+ Add Row**
   - Parameter Name: **page_title**
   - Value: **{{Page Title}}**
   - Add additional parameters:
     - **page_location**: {{Page URL}}
     - **page_path**: {{Page Path}}
     - **page_category**: {{dlv_page_category}}
6. Under **Configuration Tag**, select your **GA4 Configuration** tag
7. In the **Triggering** section, select **CE - Page View** or **All Pages**
8. Click **Save**

#### Project Click Tag

1. Click **Tags** > **New**
2. Name it **GA4 Event - Project Click**
3. Click the tag configuration block and select **Google Analytics: GA4 Event**
4. Enter **project_click** as the Event Name
5. Under **Event Parameters**:
   - **project_name**: {{dlv_project_name}}
   - **page_location**: {{Page URL}}
6. Under **Configuration Tag**, select your **GA4 Configuration** tag
7. In the **Triggering** section, select **CE - Project Click**
8. Click **Save**

#### External Link Click Tag

1. Click **Tags** > **New**
2. Name it **GA4 Event - External Link Click**
3. Click the tag configuration block and select **Google Analytics: GA4 Event**
4. Enter **outbound_click** as the Event Name
5. Under **Event Parameters**:
   - **link_url**: {{dlv_link_url}}
   - **link_text**: {{dlv_link_text}}
6. Under **Configuration Tag**, select your **GA4 Configuration** tag
7. In the **Triggering** section, select **CE - External Link Click**
8. Click **Save**

#### Form Submission Tag

1. Click **Tags** > **New**
2. Name it **GA4 Event - Form Submission**
3. Click the tag configuration block and select **Google Analytics: GA4 Event**
4. Enter **form_submit** as the Event Name
5. Under **Event Parameters**:
   - **form_name**: {{dlv_form_name}}
6. Under **Configuration Tag**, select your **GA4 Configuration** tag
7. In the **Triggering** section, select **CE - Form Submission**
8. Click **Save**

Create similar tags for the other events following the same pattern.

### Step 6: Test Your Setup

1. Click the **Preview** button in the top right
2. Enter your website URL and click **Start**
3. Navigate to your website in the preview window
4. Check the GTM Debug panel to see if tags are firing correctly
5. Visit the `/analytics-debug` page on your website
6. Use the testing buttons to verify event tracking

### Step 7: Publish Your Container

1. When you're satisfied with your configuration, click **Submit** in GTM
2. Add a version name (e.g., "Initial GTM Setup with GA4 Events")
3. Add a description of the changes
4. Click **Publish**

## Verifying Your Setup

After publishing, use these methods to verify that everything is working:

1. **GTM Debug Mode**: Enable preview mode in GTM and navigate through your site
2. **Analytics Debug Page**: Visit the `/analytics-debug` page on your website
3. **GA4 DebugView**: In Google Analytics, go to Admin > DebugView to see real-time events
4. **Real-Time Reports**: Check the Real-Time section in Google Analytics to see current users and events

## Troubleshooting Common Issues

- **No data in GA4**: Remember that data can take 24-48 hours to appear in standard reports
- **Events not firing**: Check browser console for JavaScript errors
- **Missing data in events**: Verify that dataLayer variables are being populated correctly
- **Privacy blockers**: Ad blockers and privacy extensions may block GTM from loading

## Next Steps

1. Visit your GTM container at [Google Tag Manager](https://tagmanager.google.com/)
2. Complete the setup following the steps above
3. Test your setup using the `/analytics-debug` page
4. If everything works correctly, your website will now properly track user behavior in Google Analytics