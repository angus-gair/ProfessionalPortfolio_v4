/**
 * Google Analytics 4 Configuration via GTM
 * Initializes GA4 measurement ID and configuration
 */

// This script enhances the GA4 configuration capabilities
// These settings can be managed in GTM, but this provides additional flexibility
document.addEventListener('DOMContentLoaded', function() {
  // Create the dataLayer if it doesn't exist
  window.dataLayer = window.dataLayer || [];
  
  // Push GA4 configuration to dataLayer
  window.dataLayer.push({
    'gtm.start': new Date().getTime(),
    'event': 'gtm.js',
    'google_analytics': {
      'measurement_id': 'G-XXXXXXXXXX', // Replace with your actual GA4 measurement ID when available
      'config': {
        'cookie_domain': 'auto',
        'send_page_view': false // We'll handle this manually for better control
      }
    }
  });
  
  // Custom dimensions for enhanced reporting
  window.dataLayer.push({
    'user_properties': {
      'user_type': 'portfolio_visitor',
      'arrival_date': new Date().toISOString().split('T')[0]
    }
  });
  
  // Set up content groups based on page sections
  const path = window.location.pathname;
  let contentGroup = 'other';
  
  if (path === '/' || path === '/index') {
    contentGroup = 'home';
  } else if (path.includes('project')) {
    contentGroup = 'projects';
  } else if (path.includes('skill')) {
    contentGroup = 'skills';
  } else if (path.includes('experience')) {
    contentGroup = 'experience';
  } else if (path.includes('contact')) {
    contentGroup = 'contact';
  }
  
  // Push content grouping
  window.dataLayer.push({
    'content_group': contentGroup,
    'page_type': contentGroup
  });
  
  console.log('GA4 Configuration initialized via GTM');
});