#!/usr/bin/env python3
"""
Test masothue.com search with the specific URL format from the analysis
"""

import requests
import time
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_masothue_search():
    """Test masothue.com search with specific URL format"""
    
    # SOCKS5 proxy configuration
    proxy_config = {
        'http': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
        'https': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
    }
    
    # Test CCCDs
    test_cccds = [
        "001087016369",
        "001184032114", 
        "001098021288",
        "001094001628",
        "036092002342"
    ]
    
    # Browser-like headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    
    logger.info("🔧 Testing masothue.com search with SOCKS5 proxy...")
    logger.info("="*60)
    
    # First, get cookies from homepage
    logger.info("🍪 Getting cookies from homepage...")
    session = requests.Session()
    session.proxies.update(proxy_config)
    session.headers.update(headers)
    
    try:
        homepage_response = session.get("https://masothue.com/", timeout=15)
        logger.info(f"✅ Homepage: {homepage_response.status_code}")
        logger.info(f"📊 Cookies: {list(session.cookies.keys())}")
    except Exception as e:
        logger.error(f"❌ Homepage error: {e}")
        return
    
    # Test each CCCD
    for i, cccd in enumerate(test_cccds, 1):
        logger.info(f"\n🔍 Test {i}/{len(test_cccds)}: {cccd}")
        logger.info("-" * 40)
        
        try:
            # Use the exact URL format from the analysis
            search_url = f"https://masothue.com/Search/?q={cccd}&type=auto&token=NbnmgilFfL&force-search=1"
            
            # Add referer header
            search_headers = headers.copy()
            search_headers.update({
                "Referer": "https://masothue.com/",
                "X-Requested-With": "XMLHttpRequest"
            })
            
            start_time = time.time()
            response = session.get(search_url, headers=search_headers, timeout=15)
            response_time = time.time() - start_time
            
            logger.info(f"✅ Status: {response.status_code}")
            logger.info(f"⏱️ Response time: {response_time:.2f}s")
            logger.info(f"📏 Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # Parse the response
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for tax code and name
                tax_code = None
                name = None
                profile_url = None
                
                # Method 1: Look for tax code links
                tax_links = soup.find_all('a', href=True)
                for link in tax_links:
                    href = link.get('href', '')
                    if '/masothue.com/' in href and href != 'https://masothue.com/':
                        # Extract tax code from URL
                        url_parts = href.split('/')
                        if len(url_parts) > 0:
                            last_part = url_parts[-1]
                            if '-' in last_part:
                                tax_code = last_part.split('-')[0]
                            else:
                                tax_code = last_part
                            
                            name = link.get_text(strip=True)
                            profile_url = href
                            break
                
                # Method 2: Look for tax code in text content
                if not tax_code:
                    text_content = soup.get_text()
                    import re
                    # Look for 10-digit tax code pattern
                    tax_pattern = r'\b\d{10}\b'
                    matches = re.findall(tax_pattern, text_content)
                    if matches:
                        tax_code = matches[0]
                
                # Method 3: Look for name in headings
                if not name:
                    name_elements = soup.find_all(['h1', 'h2', 'h3', 'strong', 'b', 'span'])
                    for elem in name_elements:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 3 and not text.isdigit() and not text.startswith('http'):
                            # Check if it looks like a Vietnamese name
                            if any(char in text for char in ['Lê', 'Nguyễn', 'Trần', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Võ']):
                                name = text
                                break
                
                if tax_code and name:
                    logger.info(f"🎯 FOUND: {tax_code} - {name}")
                    if profile_url:
                        logger.info(f"🔗 Profile: {profile_url}")
                else:
                    logger.info("❌ NOT FOUND - No tax code or name detected")
                    # Show a preview of the content
                    logger.info("📄 Content preview: " + response.text[:200] + "...")
            
            elif response.status_code == 403:
                logger.warning("🚫 403 Forbidden - Anti-bot protection")
            else:
                logger.warning(f"⚠️ Unexpected status: {response.status_code}")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        # Add delay between tests
        if i < len(test_cccds):
            delay = 5
            logger.info(f"⏳ Waiting {delay}s before next test...")
            time.sleep(delay)
    
    logger.info("\n🏁 masothue.com search test completed!")

if __name__ == "__main__":
    test_masothue_search()