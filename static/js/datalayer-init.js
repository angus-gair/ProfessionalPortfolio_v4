/**
 * DataLayer Initialization
 * This script must be loaded before GTM to ensure proper data capture
 */

// Initialize dataLayer
window.dataLayer = window.dataLayer || [];

// Get page category from meta tag
const pageCategory = document.querySelector('meta[name="page-category"]')?.content || 
                   document.querySelector('body').dataset.pageCategory || 
                   window.location.pathname.replace(/\//g, '') || 
                   'uncategorized';

// Detect browser information
function getBrowserInfo() {
  const ua = navigator.userAgent;
  let browser = "unknown";
  let browserVersion = "unknown";
  
  // Detect browser
  if (ua.indexOf("Firefox") > -1) {
    browser = "Firefox";
    browserVersion = ua.match(/Firefox\/([0-9.]+)/)[1];
  } else if (ua.indexOf("Chrome") > -1 && ua.indexOf("Edg") === -1 && ua.indexOf("OPR") === -1) {
    browser = "Chrome";
    browserVersion = ua.match(/Chrome\/([0-9.]+)/)[1];
  } else if (ua.indexOf("Safari") > -1 && ua.indexOf("Chrome") === -1) {
    browser = "Safari";
    const versionMatch = ua.match(/Version\/([0-9.]+).*Safari/);
    browserVersion = versionMatch ? versionMatch[1] : "unknown";
  } else if (ua.indexOf("Edg") > -1) {
    browser = "Edge";
    browserVersion = ua.match(/Edg\/([0-9.]+)/)[1];
  } else if (ua.indexOf("OPR") > -1 || ua.indexOf("Opera") > -1) {
    browser = "Opera";
    browserVersion = ua.match(/(?:OPR|Opera)\/([0-9.]+)/)[1];
  } else if (ua.indexOf("Trident") > -1) {
    browser = "Internet Explorer";
    browserVersion = ua.match(/rv:([0-9.]+)/)[1];
  }
  
  return { browser, browserVersion };
}

// Detect device type and screen info
function getDeviceInfo() {
  const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  const isTablet = /Tablet|iPad/i.test(navigator.userAgent) || (isMobile && Math.min(window.screen.width, window.screen.height) > 480);
  
  let deviceType = "desktop";
  if (isTablet) deviceType = "tablet";
  else if (isMobile) deviceType = "mobile";
  
  return {
    deviceType,
    screenWidth: window.screen.width,
    screenHeight: window.screen.height,
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
    devicePixelRatio: window.devicePixelRatio || 1
  };
}

// Get the site section based on URL path
function getSiteSection() {
  const path = window.location.pathname;
  let section = path.split('/')[1] || 'home';
  
  // Special case for index page
  if (path === '/' || path === '/index' || path === '/index.html') {
    section = 'home';
  }
  
  return section;
}

// Get referrer information
function getReferrerInfo() {
  if (!document.referrer) return { referrer: 'direct', referrerDomain: 'direct' };
  
  try {
    const referrerURL = new URL(document.referrer);
    const currentURL = new URL(window.location.href);
    
    // Check if referrer is from the same domain
    if (referrerURL.hostname === currentURL.hostname) {
      return {
        referrer: 'internal',
        referrerDomain: referrerURL.hostname,
        referrerPath: referrerURL.pathname
      };
    }
    
    // External referrer
    return {
      referrer: 'external',
      referrerDomain: referrerURL.hostname,
      referrerProtocol: referrerURL.protocol.replace(':', '')
    };
  } catch (e) {
    return { referrer: 'unknown', referrerDomain: 'unknown' };
  }
}

// Get session information
function getSessionInfo() {
  let isNewSession = false;
  let sessionCount = 1;
  
  // Check if this is a new session
  if (!sessionStorage.getItem('session_established')) {
    isNewSession = true;
    sessionStorage.setItem('session_established', 'true');
    
    // Update session count in localStorage
    if (localStorage.getItem('session_count')) {
      sessionCount = parseInt(localStorage.getItem('session_count')) + 1;
      localStorage.setItem('session_count', sessionCount.toString());
    } else {
      localStorage.setItem('session_count', '1');
    }
  } else {
    sessionCount = parseInt(localStorage.getItem('session_count')) || 1;
  }
  
  return {
    isNewSession,
    sessionCount,
    sessionId: sessionStorage.getItem('session_id') || generateSessionId()
  };
}

// Generate a unique session ID
function generateSessionId() {
  const sessionId = 'ss_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  sessionStorage.setItem('session_id', sessionId);
  return sessionId;
}

// Combine all information for the dataLayer
const browserInfo = getBrowserInfo();
const deviceInfo = getDeviceInfo();
const sessionInfo = getSessionInfo();
const referrerInfo = getReferrerInfo();

// Push comprehensive data to dataLayer
window.dataLayer.push({
  // Page Information
  'pageCategory': pageCategory,
  'siteSection': getSiteSection(),
  'pageLanguage': document.documentElement.lang || 'en',
  'pageTitle': document.title,
  'pageUrl': window.location.href,
  'pagePath': window.location.pathname,
  'pageQuery': window.location.search,
  'pageHash': window.location.hash,
  
  // Session Information
  'isNewSession': sessionInfo.isNewSession,
  'sessionCount': sessionInfo.sessionCount,
  'sessionId': sessionInfo.sessionId,
  
  // User & Device Information
  'userStatus': 'visitor',
  'deviceType': deviceInfo.deviceType,
  'screenWidth': deviceInfo.screenWidth,
  'screenHeight': deviceInfo.screenHeight,
  'viewportWidth': deviceInfo.viewportWidth,
  'viewportHeight': deviceInfo.viewportHeight,
  'devicePixelRatio': deviceInfo.devicePixelRatio,
  'browser': browserInfo.browser,
  'browserVersion': browserInfo.browserVersion,
  
  // Referrer Information
  'referrer': referrerInfo.referrer,
  'referrerDomain': referrerInfo.referrerDomain,
  'referrerPath': referrerInfo.referrerPath,
  
  // Time Information
  'timestamp': new Date().toISOString(),
  'localDate': new Date().toLocaleDateString(),
  'localTime': new Date().toLocaleTimeString()
});

// Function to track page performance metrics
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
        
        window.dataLayer.push({
          'event': 'page_performance',
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
          window.dataLayer.push({
            'event': 'page_performance',
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

// Track page performance after window loads
window.addEventListener('load', function() {
  // Delay performance tracking slightly to ensure accurate measurements
  setTimeout(trackPagePerformance, 0);
});

// Track client-side errors
window.addEventListener('error', function(event) {
  window.dataLayer.push({
    'event': 'javascript_error',
    'errorMessage': event.message,
    'errorSource': event.filename,
    'errorLine': event.lineno,
    'errorColumn': event.colno,
    'pageUrl': window.location.href
  });
});

// Output debug information to console
console.group('%c🔍 GTM DataLayer Initialization', 'color: #4285f4; font-weight: bold; font-size: 14px;');
console.log('%cPage Category:', 'font-weight: bold;', pageCategory);
console.log('%cBrowser:', 'font-weight: bold;', browserInfo.browser, browserInfo.browserVersion);
console.log('%cDevice:', 'font-weight: bold;', deviceInfo.deviceType, `${deviceInfo.screenWidth}x${deviceInfo.screenHeight}`);
console.log('%cReferrer:', 'font-weight: bold;', referrerInfo.referrer, referrerInfo.referrerDomain || '');
console.log('%cSession:', 'font-weight: bold;', `#${sessionInfo.sessionCount}`, sessionInfo.isNewSession ? '(New)' : '(Returning)');
console.log('%cDataLayer Object:', 'font-weight: bold;', window.dataLayer);
console.groupEnd();

// For non-dev environments, this could be set to only show when a debug parameter is present
// e.g., ?gtm_debug=true
if (window.location.search.includes('gtm_debug=true')) {
  window.gtmDebug = true;
  console.log('%c🔄 GTM Debug Mode Enabled', 'color: #4285f4; font-weight: bold;');
}

console.log('DataLayer initialized for GTM with comprehensive tracking data');