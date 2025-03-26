/**
 * DataLayer Initialization
 * This script must be loaded before GTM to ensure proper data capture
 */

// Initialize dataLayer
window.dataLayer = window.dataLayer || [];

// Basic page information for all pages
window.dataLayer.push({
  'pageCategory': document.querySelector('body').dataset.pageCategory || 'unspecified',
  'userStatus': 'visitor',
  'deviceType': /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
  'siteSection': window.location.pathname.split('/')[1] || 'home'
});

// Function to track page performance metrics
function trackPagePerformance() {
  if (window.performance && window.performance.timing) {
    setTimeout(function() {
      const timing = window.performance.timing;
      const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
      const domReadyTime = timing.domComplete - timing.domLoading;
      
      if (pageLoadTime > 0) {
        window.dataLayer.push({
          'event': 'page_performance',
          'pageLoadTime': pageLoadTime,
          'domReadyTime': domReadyTime,
          'networkLatency': timing.responseEnd - timing.fetchStart
        });
      }
    }, 0);
  }
}

// Track page performance after window loads
window.addEventListener('load', trackPagePerformance);

console.log('DataLayer initialized for GTM');