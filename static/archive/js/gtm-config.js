/**
 * Google Tag Manager Configuration
 * Sets up custom event tracking and user journey analytics for the portfolio site
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

// Track page views with enhanced data
document.addEventListener('DOMContentLoaded', function() {
  // Get page category from meta tag or default to path
  const pageCategory = document.querySelector('meta[name="page-category"]')?.content || 
                      window.location.pathname.replace(/\//g, '') || 'home';
                      
  pushEvent('page_view', {
    'page_title': document.title,
    'page_location': window.location.href,
    'page_path': window.location.pathname,
    'page_category': pageCategory
  });
});

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
            'project_name': projectName
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
  
  repoCards.forEach(card => {
    card.addEventListener('click', function(e) {
      if (e.target.tagName !== 'A') { // Don't double-count link clicks
        const repoName = this.querySelector('.repo-name, h3')?.textContent || 'Unknown Repository';
        
        pushEvent('github_repo_view', {
          'repo_name': repoName,
          'repo_id': this.dataset.repoId || ''
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
          'link_text': this.textContent.trim()
        });
      });
    });
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
  
  window.addEventListener('scroll', function() {
    const scrollPercentage = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    
    scrollMarks.forEach(mark => {
      if (scrollPercentage >= mark && !marks.has(mark)) {
        pushEvent('scroll_depth', {
          'scroll_percent': mark,
          'page_title': document.title,
          'page_path': window.location.pathname,
          'page_category': document.querySelector('meta[name="page-category"]')?.content || ''
        });
        marks.add(mark);
      }
    });
  });
}

// Track time spent on page
function trackTimeOnPage() {
  const startTime = new Date();
  let timeEventsSent = new Set();
  const timeMarks = [30, 60, 120, 300]; // seconds
  
  const interval = setInterval(() => {
    const timeSpent = Math.floor((new Date() - startTime) / 1000);
    
    timeMarks.forEach(mark => {
      if (timeSpent >= mark && !timeEventsSent.has(mark)) {
        pushEvent('time_on_page', {
          'time_seconds': mark,
          'page_title': document.title,
          'page_path': window.location.pathname
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
    const finalTimeSpent = Math.floor((new Date() - startTime) / 1000);
    pushEvent('page_exit', {
      'time_on_page_seconds': finalTimeSpent,
      'page_title': document.title,
      'page_path': window.location.pathname,
      'exit_percentage': (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
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
      category: document.querySelector('meta[name="page-category"]')?.content || '',
      timestamp: new Date().toISOString()
    }]));
  } else {
    // Add current page to journey
    try {
      const journey = JSON.parse(sessionStorage.getItem('user_journey'));
      journey.push({
        path: window.location.pathname,
        title: document.title,
        category: document.querySelector('meta[name="page-category"]')?.content || '',
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

// Initialize all tracking functions
document.addEventListener('DOMContentLoaded', function() {
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
});