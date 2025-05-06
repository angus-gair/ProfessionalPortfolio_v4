import requests
import re
import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Color codes for terminal output
COLORS = {
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'BOLD': '\033[1m',
    'END': '\033[0m'
}

# GTM container ID to check for
GTM_CONTAINER_ID = 'GTM-PC9Q9VC3'

# Base URL of the website
BASE_URL = 'http://localhost:5000'

# URLs to check
URLS_TO_CHECK = [
    '/',
    '/projects',
    '/skills',
    '/experience',
    '/contact',
    '/architecture',
    '/optimisation',
    '/ecosystem',
    '/analytics-debug',
    '/listing.html',
    '/mmm_viz',
    '/interactive_chart',
    '/retail_loyalty_analytics'
]

# Regular expressions for GTM code patterns - updated for more flexible matching
GTM_HEAD_PATTERN = re.compile(r"googletagmanager\.com/gtm\.js.*?id=['\"]?" + GTM_CONTAINER_ID + r"['\"]?")
GTM_BODY_PATTERN = re.compile(r"googletagmanager\.com/ns\.html.*?id=['\"]?" + GTM_CONTAINER_ID + r"['\"]?")

# Alternative detection patterns
GTM_HEAD_ALT_PATTERN = re.compile(r"GTM-PC9Q9VC3")

def print_colored(text, color):
    """Print text with color"""
    print(f"{COLORS[color]}{text}{COLORS['END']}")

def check_gtm_implementation(url):
    """Check if GTM is correctly implemented on a page"""
    full_url = urljoin(BASE_URL, url)
    try:
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for GTM in head or anywhere in the document
        all_scripts = soup.find_all('script')
        
        # Safely get scripts in head
        head_scripts = []
        head = soup.find('head')
        if head and hasattr(head, 'find_all'):
            head_scripts = head.find_all('script')
        
        # Direct check for GTM in the HTML content
        html_content = response.text
        head_gtm_found = GTM_HEAD_PATTERN.search(html_content) is not None or GTM_HEAD_ALT_PATTERN.search(html_content) is not None
        body_gtm_found = GTM_BODY_PATTERN.search(html_content) is not None
        
        # Fallback checks with specific tag structures if direct checks fail
        if not head_gtm_found:
            head_gtm_found = (any(GTM_HEAD_PATTERN.search(str(script)) for script in head_scripts) or
                            any(GTM_HEAD_PATTERN.search(str(script)) for script in all_scripts) or
                            any(GTM_HEAD_ALT_PATTERN.search(str(script)) for script in all_scripts))
        
        if not body_gtm_found:
            all_noscript = soup.find_all('noscript')
            
            body_noscript = []
            body = soup.find('body')
            if body and hasattr(body, 'find_all'):
                body_noscript = body.find_all('noscript')
            
            body_gtm_found = (any(GTM_BODY_PATTERN.search(str(noscript)) for noscript in body_noscript) or
                             any(GTM_BODY_PATTERN.search(str(noscript)) for noscript in all_noscript) or
                             any(GTM_HEAD_ALT_PATTERN.search(str(noscript)) for noscript in all_noscript))
        
        # Check for consolidated script
        consolidated_script_found = bool(soup.find('script', {'src': re.compile(r'gtm-consolidated\.js')}))
        
        # Determine the overall result
        if head_gtm_found and body_gtm_found:
            result = 'PASSED'
            color = 'GREEN'
        elif head_gtm_found or body_gtm_found:
            result = 'PARTIAL'
            color = 'YELLOW'
        else:
            result = 'FAILED'
            color = 'RED'
            
        return {
            'url': url,
            'result': result,
            'color': color,
            'head_gtm': head_gtm_found,
            'body_gtm': body_gtm_found,
            'consolidated': consolidated_script_found
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'result': 'ERROR',
            'color': 'RED',
            'error': str(e),
            'head_gtm': False,
            'body_gtm': False,
            'consolidated': False
        }

def main():
    print_colored(f"\nChecking Google Tag Manager implementation ({GTM_CONTAINER_ID}) across all pages\n", 'BOLD')
    print_colored("URL".ljust(30) + "Status".ljust(10) + "Head GTM".ljust(15) + "Body GTM".ljust(15) + "Consolidated JS", 'BOLD')
    print("-" * 85)
    
    all_passed = True
    results = []
    
    for url in URLS_TO_CHECK:
        result = check_gtm_implementation(url)
        results.append(result)
        
        status_str = result['result'].ljust(10)
        head_gtm_str = ("✓" if result['head_gtm'] else "✗").ljust(15)
        body_gtm_str = ("✓" if result['body_gtm'] else "✗").ljust(15)
        consolidated_str = "✓" if result['consolidated'] else "✗"
        
        print_colored(
            f"{url.ljust(30)}{status_str}{head_gtm_str}{body_gtm_str}{consolidated_str}",
            result['color']
        )
        
        if result['result'] != 'PASSED':
            all_passed = False
    
    print("\nSummary:")
    if all_passed:
        print_colored("✅ GTM is correctly implemented on all pages!", 'GREEN')
    else:
        print_colored("❌ Some pages have GTM implementation issues.", 'RED')
        print_colored("   Please check the above results for details.", 'YELLOW')

if __name__ == "__main__":
    main()
