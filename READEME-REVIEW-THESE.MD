Here's a list of things we need to review later:

1. **Notebook Handler Functions**

    - The serve\_notebook and get\_notebook\_content functions need further testing
    - Current 404 error for some notebook paths (e.g., dashboard\_analysis.ipynb)
    - Verify all fallback paths are working correctly
2. **Environment Variables**

    - Restore GitHub API configuration (username and token)
    - Ensure Tableau Public username is properly set
    - Check other environment variables removed during the reorganization
3. **Missing Dependencies**

    - Import statements like dotenv need to be restored
    - Review any other dependencies removed during file updates
4. **Routes Consistency**

    - Review active\_page parameter values across all routes for consistency
    - Verify architecture page is using 'projects' or 'architecture' as active\_page
5. **File Path Configuration**

    - Test all paths in the optimisation route
    - Review other file paths for any reorganization-related issues
6. **API Endpoints**

    - Test GitHub API integration
    - Verify Tableau views endpoint
    - Check analytics test endpoint
7. **Template References**

    - Ensure all templates correctly reference files in new locations
    - Check for any hardcoded paths that may need updating
8. **Google Analytics Configuration**

    - Verify the analytics-debug route is working
    - Test GA4 event tracking with the updated file structure

Would you like me to prioritize any specific item from this list to address next?