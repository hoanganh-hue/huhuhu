#!/usr/bin/env python3
"""
Test masothue.com search with proper Brotli decompression
"""

import requests
import time
import logging
import brotli
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_masothue_brotli():
    """Test masothue.com search with Brotli decompression"""
    
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
    
    logger.info("🔧 Testing masothue.com search with Brotli decompression...")
    logger.info("="*60)
    
    # Create session
    session = requests.Session()
    session.proxies.update(proxy_config)
    session.headers.update(headers)
    
    # Get homepage first
    logger.info("🍪 Getting homepage...")
    try:
        homepage_response = session.get("https://masothue.com/", timeout=15)
        logger.info(f"✅ Homepage: {homepage_response.status_code}")
        
        # Manually decompress if needed
        if homepage_response.headers.get('Content-Encoding') == 'br':
            try:
                decompressed_content = brotli.decompress(homepage_response.content)
                homepage_text = decompressed_content.decode('utf-8')
                logger.info("✅ Homepage decompressed successfully")
                logger.info(f"📄 Homepage preview: {homepage_text[:200]}...")
            except Exception as e:
                logger.error(f"❌ Homepage decompression error: {e}")
                homepage_text = homepage_response.text
        else:
            homepage_text = homepage_response.text
            
    except Exception as e:
        logger.error(f"❌ Homepage error: {e}")
        return
    
    # Test each CCCD
    for i, cccd in enumerate(test_cccds, 1):
        logger.info(f"\n🔍 Test {i}/{len(test_cccds)}: {cccd}")
        logger.info("-" * 40)
        
        try:
            # Use the exact URL format
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
            logger.info(f"📊 Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
            logger.info(f"📊 Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # Handle Brotli decompression
                if response.headers.get('Content-Encoding') == 'br':
                    try:
                        decompressed_content = brotli.decompress(response.content)
                        html_content = decompressed_content.decode('utf-8')
                        logger.info("✅ Content decompressed successfully")
                    except Exception as e:
                        logger.error(f"❌ Decompression error: {e}")
                        html_content = response.text
                else:
                    html_content = response.text
                
                # Parse the response
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look for tax code and name
                tax_code = None
                name = None
                profile_url = None
                
                # Method 1: Look for tax code links
                tax_links = soup.find_all('a', href=True)
                logger.info(f"📄 Found {len(tax_links)} links")
                
                for link in tax_links:
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)
                    
                    # Log all links for debugging
                    if href and link_text:
                        logger.info(f"  🔗 Link: {href} - {link_text}")
                    
                    if '/masothue.com/' in href and href != 'https://masothue.com/':
                        # Extract tax code from URL
                        url_parts = href.split('/')
                        if len(url_parts) > 0:
                            last_part = url_parts[-1]
                            if '-' in last_part:
                                tax_code = last_part.split('-')[0]
                            else:
                                tax_code = last_part
                            
                            name = link_text
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
                        logger.info(f"📄 Found tax code in text: {tax_code}")
                
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
                
                # Method 4: Look for any meaningful text
                if not name and not tax_code:
                    all_text = soup.get_text()
                    logger.info(f"📄 All text content (first 1000 chars): {all_text[:1000]}")
                    
                    # Look for any Vietnamese text patterns
                    import re
                    vietnamese_pattern = r'[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ\s]+'
                    matches = re.findall(vietnamese_pattern, all_text)
                    if matches:
                        logger.info(f"📄 Found Vietnamese text patterns: {matches[:5]}")
                
                if tax_code and name:
                    logger.info(f"🎯 FOUND: {tax_code} - {name}")
                    if profile_url:
                        logger.info(f"🔗 Profile: {profile_url}")
                else:
                    logger.info("❌ NOT FOUND - No tax code or name detected")
            
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
    
    logger.info("\n🏁 masothue.com search test with Brotli completed!")

if __name__ == "__main__":
    test_masothue_brotli()