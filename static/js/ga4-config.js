/**
 * Google Analytics 4 Configuration via GTM
 * Initializes GA4 measurement ID and configuration for enhanced analytics tracking
 */

// This script enhances the GA4 configuration capabilities beyond basic settings
// While these settings can be managed in GTM interface, this provides additional flexibility
// and ensures consistent configuration across environments
document.addEventListener('DOMContentLoaded', function() {
  // Create the dataLayer if it doesn't exist
  window.dataLayer = window.dataLayer || [];
  
  // Get page category from meta tag for consistent categorization
  const pageCategory = document.querySelector('meta[name="page-category"]')?.content || 
                      document.querySelector('body').dataset.pageCategory || 
                      'uncategorized';
  
  // Enhanced content grouping based on page category or URL path
  const path = window.location.pathname;
  let contentGroup = pageCategory;
  
  // Fallback logic if page category is not explicitly set
  if (contentGroup === 'uncategorized') {
    if (path === '/' || path === '/index' || path === '/index.html') {
      contentGroup = 'home';
    } else if (path.includes('project')) {
      contentGroup = 'projects';
    } else if (path.includes('skill')) {
      contentGroup = 'skills';
    } else if (path.includes('experience')) {
      contentGroup = 'experience';
    } else if (path.includes('contact')) {
      contentGroup = 'contact';
    } else {
      contentGroup = 'other';
    }
  }
  
  // Determine content subcategory for more granular reporting
  let contentSubcategory = 'general';
  const pageTitle = document.title.toLowerCase();
  
  if (contentGroup === 'projects') {
    if (pageTitle.includes('machine learning') || pageTitle.includes('ml') || 
        document.querySelector('.badge:not(.skill-badge)')?.textContent.includes('Machine Learning')) {
      contentSubcategory = 'machine_learning';
    } else if (pageTitle.includes('dashboard') || pageTitle.includes('visualization') || 
               document.querySelector('.badge:not(.skill-badge)')?.textContent.includes('Tableau')) {
      contentSubcategory = 'data_visualization';
    } else if (pageTitle.includes('sql') || pageTitle.includes('database')) {
      contentSubcategory = 'database';
    }
  } else if (contentGroup === 'skills') {
    // Determine which skills section is currently in view (if available)
    const skillSections = document.querySelectorAll('.card h3.card-title');
    if (skillSections.length > 0) {
      const firstSection = skillSections[0].textContent.toLowerCase();
      if (firstSection.includes('data analysis')) {
        contentSubcategory = 'analysis_skills';
      } else if (firstSection.includes('visualization')) {
        contentSubcategory = 'visualization_skills';
      } else if (firstSection.includes('machine learning')) {
        contentSubcategory = 'ml_skills';
      }
    }
  }
  
  // Push GA4 configuration to dataLayer
  window.dataLayer.push({
    'gtm.start': new Date().getTime(),
    'event': 'gtm.js',
    'google_analytics': {
      'measurement_id': 'G-XXXXXXXXXX', // Replace with your actual GA4 measurement ID when available
      'config': {
        'cookie_domain': 'auto',
        'send_page_view': false, // We'll handle this manually for better control
        'anonymize_ip': true,    // Enhanced privacy
        'page_title': document.title,
        'page_location': window.location.href,
        'content_group': contentGroup
      }
    }
  });
  
  // Custom dimensions and metrics for enhanced reporting
  window.dataLayer.push({
    'user_properties': {
      'user_type': 'portfolio_visitor',
      'arrival_date': new Date().toISOString().split('T')[0],
      'visit_hour': new Date().getHours(),
      'visit_day': ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][new Date().getDay()],
      'device_category': /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
      'viewport_width': window.innerWidth,
      'viewport_height': window.innerHeight
    }
  });
  
  // Enhanced content grouping for better content analysis
  window.dataLayer.push({
    'event': 'content_view',
    'content_group': contentGroup,
    'content_subcategory': contentSubcategory,
    'page_type': contentGroup,
    'page_section': contentGroup,
    'page_language': document.documentElement.lang || 'en',
    'page_template': 'portfolio_template'
  });
  
  // Set custom dimensions for engagement tracking
  window.scrollMaxDepth = 0;
  window.startTime = new Date();
  
  // Track maximum scroll depth
  window.addEventListener('scroll', function() {
    const scrollPercentage = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    if (scrollPercentage > window.scrollMaxDepth) {
      window.scrollMaxDepth = Math.round(scrollPercentage);
    }
  });
  
  // Track time on page and max scroll depth on page exit
  window.addEventListener('beforeunload', function() {
    const timeSpent = Math.round((new Date() - window.startTime) / 1000);
    
    window.dataLayer.push({
      'event': 'engagement_metrics',
      'time_on_page': timeSpent,
      'max_scroll_depth': window.scrollMaxDepth,
      'page_category': pageCategory
    });
  });
  
  // Set up interaction tracking for rich media content
  const setupRichMediaTracking = function() {
    // Track Tableau visualizations 
    document.querySelectorAll('.tableau-container').forEach(function(container) {
      // Use MutationObserver to detect when Tableau iframe is loaded
      const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          if (mutation.addedNodes.length && mutation.addedNodes[0].tagName === 'IFRAME') {
            window.dataLayer.push({
              'event': 'tableau_load',
              'tableau_url': container.dataset.tableauUrl || '',
              'tableau_id': container.id || '',
              'page_category': pageCategory
            });
            observer.disconnect(); // Only track initial load
          }
        });
      });
      observer.observe(container, { childList: true, subtree: true });
    });
    
    // Track GitHub repository card views
    document.querySelectorAll('.github-repo-card, .repo-item').forEach(function(card) {
      const repoName = card.querySelector('.repo-name, h3')?.textContent || 'Unknown Repository';
      const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            window.dataLayer.push({
              'event': 'github_repo_view',
              'repo_name': repoName,
              'page_category': pageCategory
            });
            observer.unobserve(card); // Only track once
          }
        });
      }, { threshold: 0.5 }); // At least 50% of the card must be visible
      observer.observe(card);
    });
  };
  
  // Setup rich media tracking after a slight delay to ensure DOM is fully processed
  setTimeout(setupRichMediaTracking, 1000);
  
  console.log('Enhanced GA4 Configuration initialized via GTM');
});