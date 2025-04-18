/**
 * Consolidated Google Tag Manager & Google Analytics 4 Configuration
 * Sets up GTM, GA4, custom event tracking, and user journey analytics for the portfolio site
 */

// Initialize dataLayer if it doesn't exist
window.dataLayer = window.dataLayer || [];

// Helper function to push events to dataLayer
function pushEvent(eventName, eventParams) {
  window.dataLayer.push({
    'event': eventName,
    ...eventParams
  });
  console.log('GTM Event:', eventName, eventParams);
}

// Get page category from meta tag or default to path
function getPageCategory() {
  return document.querySelector('meta[name="page-category"]')?.content || 
         document.querySelector('body').dataset.pageCategory || 
         window.location.pathname.replace(/\//g, '') || 
         'uncategorized';
}

// Calculate content group and subcategory
function getContentGrouping() {
  const pageCategory = getPageCategory();
  
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
  
  return { contentGroup, contentSubcategory };
}

// Initialize GA4 Configuration
function initializeGA4() {
  const { contentGroup, contentSubcategory } = getContentGrouping();
  
  // Push GA4 configuration to dataLayer
  window.dataLayer.push({
    'gtm.start': new Date().getTime(),
    'event': 'gtm.js',
    'google_analytics': {
      'measurement_id': 'G-3P8MK7MHQF', // GA4 measurement ID for analytics tracking
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
}

// Track page views with enhanced data
function trackPageView() {
  const pageCategory = getPageCategory();
  
  pushEvent('page_view', {
    'page_title': document.title,
    'page_location': window.location.href,
    'page_path': window.location.pathname,
    'page_category': pageCategory
  });
}

// Track portfolio project clicks
function trackProjectClicks() {
  // Project cards in projects section
  const projectCards = document.querySelectorAll('.card[id]');
  
  projectCards.forEach(card => {
    card.addEventListener('click', function(e) {
      if (e.target.tagName !== 'A') { // Don't double-count link clicks
        const projectTitle = this.querySelector('h2')?.textContent || 'Unknown Project';
        const projectId = this.id || '';
        
        pushEvent('project_card_view', {
          'project_name': projectTitle,
          'project_id': projectId,
          'project_type': 'portfolio'
        });
      }
    });
    
    // Track all links within project cards
    const projectLinks = card.querySelectorAll('a');
    projectLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        const projectTitle = card.querySelector('h2')?.textContent || 'Unknown Project';
        const linkText = this.textContent.trim();
        
        pushEvent('project_link_click', {
          'project_name': projectTitle,
          'project_id': card.id || '',
          'link_text': linkText,
          'link_url': this.href
        });
      });
    });
  });
  
  // General project links elsewhere on the site
  const otherProjectLinks = document.querySelectorAll('.project-link, a[data-project-type]');
  otherProjectLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const projectTitle = this.textContent.trim() || this.getAttribute('title') || 'Project Link';
      
      pushEvent('project_click', {
        'project_name': projectTitle,
        'project_url': this.href,
        'project_type': this.dataset.projectType || 'portfolio'
      });
    });
  });
}

// Track Tableau dashboard interactions
function trackTableauInteractions() {
  const tableauContainers = document.querySelectorAll('.tableau-container');
  const pageCategory = getPageCategory();
  
  tableauContainers.forEach(container => {
    // Track when Tableau visualization is loaded
    const observer = new MutationObserver((mutations) => {
      mutations.forEach(mutation => {
        if (mutation.addedNodes.length && mutation.addedNodes[0].tagName === 'IFRAME') {
          const tableauURL = container.dataset.tableauUrl || '';
          const containerId = container.id || '';
          const projectElement = container.closest('.card[id]');
          const projectName = projectElement ? projectElement.querySelector('h2')?.textContent : 'Unknown Project';
          
          pushEvent('tableau_view_loaded', {
            'tableau_url': tableauURL,
            'container_id': containerId,
            'project_name': projectName,
            'page_category': pageCategory
          });
          
          observer.disconnect(); // Only track the initial load
        }
      });
    });
    
    observer.observe(container, { childList: true, subtree: true });
    
    // Track clicks on the container (will likely lead to Tableau interactions)
    container.addEventListener('click', function(e) {
      const tableauURL = this.dataset.tableauUrl || '';
      const containerId = this.id || '';
      const projectElement = this.closest('.card[id]');
      const projectName = projectElement ? projectElement.querySelector('h2')?.textContent : 'Unknown Project';
      
      pushEvent('tableau_interaction', {
        'tableau_url': tableauURL,
        'container_id': containerId,
        'project_name': projectName,
        'interaction_type': 'click'
      });
    });
  });
}

// Track GitHub repository interactions
function trackGitHubInteractions() {
  // GitHub repository containers
  const repoCards = document.querySelectorAll('.github-repo-card, .repo-item');
  const pageCategory = getPageCategory();
  
  repoCards.forEach(card => {
    card.addEventListener('click', function(e) {
      if (e.target.tagName !== 'A') { // Don't double-count link clicks
        const repoName = this.querySelector('.repo-name, h3')?.textContent || 'Unknown Repository';
        
        pushEvent('github_repo_view', {
          'repo_name': repoName,
          'repo_id': this.dataset.repoId || '',
          'page_category': pageCategory
        });
      }
    });
    
    // Track repo link clicks
    const repoLinks = card.querySelectorAll('a');
    repoLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        const repoName = card.querySelector('.repo-name, h3')?.textContent || 'Unknown Repository';
        
        pushEvent('github_repo_click', {
          'repo_name': repoName,
          'repo_url': this.href,
          'link_text': this.textContent.trim(),
          'page_category': pageCategory
        });
      });
    });
    
    // Track GitHub repo view with IntersectionObserver
    const repoName = card.querySelector('.repo-name, h3')?.textContent || 'Unknown Repository';
    const observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          pushEvent('github_repo_impression', {
            'repo_name': repoName,
            'page_category': pageCategory,
            'visible_percent': Math.round(entry.intersectionRatio * 100)
          });
          observer.unobserve(card); // Only track once
        }
      });
    }, { threshold: 0.5 }); // At least 50% of the card must be visible
    observer.observe(card);
  });
}

// Track skill badges interactions
function trackSkillInteractions() {
  const skillBadges = document.querySelectorAll('.skill-badge');
  
  skillBadges.forEach(badge => {
    badge.addEventListener('click', function(e) {
      const skillName = this.textContent.trim();
      const skillCategory = this.classList.contains('bg-primary') ? 'data_analysis' :
                          this.classList.contains('bg-success') ? 'data_visualization' :
                          this.classList.contains('bg-info') ? 'machine_learning' :
                          this.classList.contains('bg-warning') ? 'cloud_tools' :
                          this.classList.contains('bg-secondary') ? 'soft_skills' : 'other';
      
      pushEvent('skill_badge_click', {
        'skill_name': skillName,
        'skill_category': skillCategory
      });
    });
  });
  
  // Make skill badges clickable with a cursor pointer
  const styleElement = document.createElement('style');
  styleElement.textContent = '.skill-badge { cursor: pointer; transition: transform 0.2s; } .skill-badge:hover { transform: scale(1.1); }';
  document.head.appendChild(styleElement);
}

// Track external link clicks (GitHub, LinkedIn, etc.)
function trackExternalLinks() {
  const externalLinks = document.querySelectorAll('a[target="_blank"]');
  
  externalLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const linkText = this.textContent.trim() || this.querySelector('i')?.className || 'Icon Link';
      const socialMatch = this.href.match(/github|linkedin|twitter|mailto/i);
      const linkType = socialMatch ? socialMatch[0].toLowerCase() : 'external';
      
      pushEvent('external_link_click', {
        'link_url': this.href,
        'link_text': linkText,
        'link_type': linkType
      });
    });
  });
}

// Track resume downloads
function trackResumeDownloads() {
  const resumeLinks = document.querySelectorAll('a[href*="resume"], a[download], #download-resume');
  
  resumeLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const format = this.href ? this.href.split('.').pop().toLowerCase() : 'pdf';
      
      pushEvent('resume_download', {
        'resume_format': format,
        'source_page': document.title,
        'button_text': this.textContent.trim()
      });
    });
  });
}

// Track contact form interactions
function trackContactForm() {
  const contactForm = document.querySelector('form#contact-form');
  
  if (contactForm) {
    // Track form submissions
    contactForm.addEventListener('submit', function(e) {
      pushEvent('contact_form_submit', {
        'form_id': this.id || 'contact_form',
        'form_fields': contactForm.querySelectorAll('input, textarea').length
      });
    });
    
    // Track form field interactions
    const formFields = contactForm.querySelectorAll('input, textarea');
    formFields.forEach(field => {
      field.addEventListener('focus', function() {
        pushEvent('contact_form_field_focus', {
          'field_id': this.id,
          'field_type': this.tagName.toLowerCase()
        });
      });
    });
  }
  
  // Track FAQ interactions
  const faqButtons = document.querySelectorAll('.accordion-button');
  faqButtons.forEach(button => {
    button.addEventListener('click', function() {
      const faqQuestion = this.textContent.trim();
      const isExpanded = this.getAttribute('aria-expanded') === 'true';
      
      pushEvent('faq_interaction', {
        'question': faqQuestion,
        'action': isExpanded ? 'collapse' : 'expand'
      });
    });
  });
}

// Track scroll depth
function trackScrollDepth() {
  let scrollMarks = [25, 50, 75, 90];
  let marks = new Set();
  const pageCategory = getPageCategory();
  
  // Initialize max scroll depth
  window.scrollMaxDepth = 0;
  
  window.addEventListener('scroll', function() {
    const scrollPercentage = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    
    // Track maximum scroll depth
    if (scrollPercentage > window.scrollMaxDepth) {
      window.scrollMaxDepth = Math.round(scrollPercentage);
    }
    
    // Track scroll percentage milestones
    scrollMarks.forEach(mark => {
      if (scrollPercentage >= mark && !marks.has(mark)) {
        pushEvent('scroll_depth', {
          'scroll_percent': mark,
          'page_title': document.title,
          'page_path': window.location.pathname,
          'page_category': pageCategory
        });
        marks.add(mark);
      }
    });
  });
}

// Track time spent on page
function trackTimeOnPage() {
  window.startTime = new Date();
  let timeEventsSent = new Set();
  const timeMarks = [30, 60, 120, 300]; // seconds
  const pageCategory = getPageCategory();
  
  const interval = setInterval(() => {
    const timeSpent = Math.floor((new Date() - window.startTime) / 1000);
    
    timeMarks.forEach(mark => {
      if (timeSpent >= mark && !timeEventsSent.has(mark)) {
        pushEvent('time_on_page', {
          'time_seconds': mark,
          'page_title': document.title,
          'page_path': window.location.pathname,
          'page_category': pageCategory
        });
        timeEventsSent.add(mark);
      }
    });
    
    if (timeMarks.every(mark => timeEventsSent.has(mark))) {
      clearInterval(interval);
    }
  }, 5000);
  
  // Clean up interval when page is unloaded
  window.addEventListener('beforeunload', () => {
    clearInterval(interval);
    
    // Final time event on page exit
    const finalTimeSpent = Math.floor((new Date() - window.startTime) / 1000);
    pushEvent('page_exit', {
      'time_on_page_seconds': finalTimeSpent,
      'page_title': document.title,
      'page_path': window.location.pathname,
      'exit_percentage': window.scrollMaxDepth,
      'page_category': pageCategory
    });
  });
}

// Track user journey (page sequence)
function trackUserJourney() {
  // Store entry page
  if (sessionStorage.getItem('user_journey') === null) {
    sessionStorage.setItem('user_journey', JSON.stringify([{
      path: window.location.pathname,
      title: document.title,
      category: getPageCategory(),
      timestamp: new Date().toISOString()
    }]));
  } else {
    // Add current page to journey
    try {
      const journey = JSON.parse(sessionStorage.getItem('user_journey'));
      journey.push({
        path: window.location.pathname,
        title: document.title,
        category: getPageCategory(),
        timestamp: new Date().toISOString()
      });
      sessionStorage.setItem('user_journey', JSON.stringify(journey));
      
      // Push journey data to GTM after 3+ pages viewed
      if (journey.length >= 3) {
        pushEvent('user_journey', {
          'journey_steps': journey.length,
          'journey_paths': journey.map(step => step.path).join(' > '),
          'journey_categories': journey.map(step => step.category || 'unknown').join(' > '),
          'journey_duration': Math.round((new Date() - new Date(journey[0].timestamp)) / 1000)
        });
      }
    } catch (e) {
      console.error('Error tracking user journey:', e);
    }
  }
}

// Track page performance metrics
function trackPagePerformance() {
  // Use more modern Performance API methods when available
  if (window.performance) {
    try {
      // Use newer Performance API if available
      if (window.performance.getEntriesByType && window.performance.getEntriesByType("navigation").length > 0) {
        const navEntry = window.performance.getEntriesByType("navigation")[0];
        const paintEntries = window.performance.getEntriesByType("paint");
        
        let firstPaint = 0;
        let firstContentfulPaint = 0;
        
        // Extract painting metrics
        paintEntries.forEach(entry => {
          if (entry.name === "first-paint") {
            firstPaint = entry.startTime;
          } else if (entry.name === "first-contentful-paint") {
            firstContentfulPaint = entry.startTime;
          }
        });
        
        pushEvent('page_performance', {
          'pageLoadTime': navEntry.loadEventEnd,
          'domContentLoaded': navEntry.domContentLoadedEventEnd,
          'domInteractive': navEntry.domInteractive,
          'firstPaint': firstPaint,
          'firstContentfulPaint': firstContentfulPaint,
          'networkLatency': navEntry.responseEnd - navEntry.requestStart,
          'serverResponseTime': navEntry.responseEnd - navEntry.responseStart,
          'redirectTime': navEntry.redirectEnd - navEntry.redirectStart,
          'domParsingTime': navEntry.domComplete - navEntry.domInteractive,
          'navigationType': navEntry.type
        });
      } 
      // Fallback to older API
      else if (window.performance.timing) {
        const timing = window.performance.timing;
        const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
        const domReadyTime = timing.domComplete - timing.domLoading;
        
        if (pageLoadTime > 0) {
          pushEvent('page_performance', {
            'pageLoadTime': pageLoadTime,
            'domReadyTime': domReadyTime,
            'networkLatency': timing.responseEnd - timing.fetchStart,
            'serverResponseTime': timing.responseEnd - timing.requestStart,
            'redirectTime': timing.redirectEnd - timing.redirectStart,
            'domParsingTime': timing.domComplete - timing.domInteractive
          });
        }
      }
    } catch (e) {
      console.error('Error capturing performance metrics:', e);
    }
  }
}

// Initialize all tracking functions
document.addEventListener('DOMContentLoaded', function() {
  // Initialize GA4 first
  initializeGA4();
  
  // Track page view
  trackPageView();
  
  // Initialize all tracking handlers
  trackProjectClicks();
  trackTableauInteractions();
  trackGitHubInteractions();
  trackSkillInteractions();
  trackExternalLinks();
  trackResumeDownloads();
  trackContactForm();
  trackScrollDepth();
  trackTimeOnPage();
  trackUserJourney();
  
  // Tracking performance metrics after a slight delay
  setTimeout(trackPagePerformance, 1000);
  
  console.log('Consolidated GTM and GA4 configuration initialized');
});

// Output debug information to console
console.group('%c🔍 GTM & GA4 Initialization', 'color: #4285f4; font-weight: bold; font-size: 14px;');
console.log('%cPage Category:', 'font-weight: bold;', getPageCategory());
console.log('%cContent Group:', 'font-weight: bold;', getContentGrouping().contentGroup);
console.log('%cContent Subcategory:', 'font-weight: bold;', getContentGrouping().contentSubcategory);
console.log('%cDataLayer Object:', 'font-weight: bold;', window.dataLayer);
console.groupEnd();

// For non-dev environments, this could be set to only show when a debug parameter is present
if (window.location.search.includes('gtm_debug=true')) {
  window.gtmDebug = true;
  console.log('%c🔄 GTM Debug Mode Enabled', 'color: #4285f4; font-weight: bold;');
} 