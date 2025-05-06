/**
 * Google Tag Manager Verification Script
 * This script helps verify that Google Tag Manager is correctly loaded and dataLayer is working
 */

// Wait for the DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if dataLayer exists
    if (typeof dataLayer !== 'undefined') {
        console.log('%c✓ DataLayer exists', 'color: green; font-weight: bold');
        console.log('DataLayer contents:', dataLayer);
        
        // Check if GTM script is loaded
        const gtmScripts = document.querySelectorAll('script[src*="googletagmanager.com/gtm.js"]');
        if (gtmScripts.length > 0) {
            console.log('%c✓ GTM script found', 'color: green; font-weight: bold');
            console.log('GTM script:', gtmScripts[0].src);
            
            // Extract GTM container ID
            const gtmIdMatch = gtmScripts[0].src.match(/id=GTM-([\w\d]+)/);
            if (gtmIdMatch) {
                console.log('%c✓ GTM Container ID:', 'color: green; font-weight: bold', 'GTM-' + gtmIdMatch[1]);
            } else {
                console.warn('⚠️ Could not extract GTM Container ID from script src');
            }
        } else {
            console.warn('⚠️ GTM script not found in the page');
        }
        
        // Check for GTM noscript iframe
        const gtmNoscript = document.querySelectorAll('noscript iframe[src*="googletagmanager.com/ns.html"]');
        if (gtmNoscript.length > 0) {
            console.log('%c✓ GTM noscript iframe found', 'color: green; font-weight: bold');
        } else {
            console.warn('⚠️ GTM noscript iframe not found');
        }
        
        // Check for consolidated script
        const consolidatedScript = document.querySelector('script[src*="gtm-consolidated.js"]');
        if (consolidatedScript) {
            console.log('%c✓ GTM consolidated script found', 'color: green; font-weight: bold');
        } else {
            console.warn('⚠️ GTM consolidated script not found');
        }
        
        // Push a test event to verify dataLayer functionality
        try {
            dataLayer.push({
                'event': 'gtm_verification_test',
                'test_timestamp': new Date().toISOString(),
                'page_url': window.location.href
            });
            console.log('%c✓ Test event pushed to dataLayer', 'color: green; font-weight: bold');
        } catch (e) {
            console.error('❌ Error pushing test event to dataLayer:', e);
        }
    } else {
        console.error('❌ DataLayer not found! Google Tag Manager might not be properly implemented.');
    }
});
