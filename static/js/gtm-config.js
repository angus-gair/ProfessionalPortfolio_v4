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
  pushEvent('page_view', {
    'page_title': document.title,
    'page_location': window.location.href,
    'page_path': window.location.pathname
  });
});

// Track portfolio project clicks
function trackProjectClicks() {
  const projectLinks = document.querySelectorAll('.project-card a, .project-link');
  
  projectLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const projectTitle = this.closest('.project-card, .project-item')?.querySelector('h3, .project-title')?.textContent || 'Unknown Project';
      
      pushEvent('project_click', {
        'project_name': projectTitle,
        'project_url': this.href,
        'project_type': this.dataset.projectType || 'portfolio'
      });
    });
  });
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
  const resumeLinks = document.querySelectorAll('a[href*="resume"], a[download]');
  
  resumeLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      pushEvent('resume_download', {
        'resume_format': this.href.split('.').pop().toLowerCase()
      });
    });
  });
}

// Track contact form submissions
function trackContactForm() {
  const contactForm = document.querySelector('form');
  
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      pushEvent('contact_form_submit', {
        'form_id': this.id || 'contact_form'
      });
    });
  }
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
          'page_path': window.location.pathname
        });
        marks.add(mark);
      }
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
      timestamp: new Date().toISOString()
    }]));
  } else {
    // Add current page to journey
    try {
      const journey = JSON.parse(sessionStorage.getItem('user_journey'));
      journey.push({
        path: window.location.pathname,
        title: document.title,
        timestamp: new Date().toISOString()
      });
      sessionStorage.setItem('user_journey', JSON.stringify(journey));
      
      // Push journey data to GTM after 3+ pages viewed
      if (journey.length >= 3) {
        pushEvent('user_journey', {
          'journey_steps': journey.length,
          'journey_paths': journey.map(step => step.path).join(' > '),
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
  trackExternalLinks();
  trackResumeDownloads();
  trackContactForm();
  trackScrollDepth();
  trackUserJourney();
});