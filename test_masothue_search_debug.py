#!/usr/bin/env python3
"""
Debug masothue.com search response to understand the content format
"""

import requests
import time
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_masothue_search_debug():
    """Debug masothue.com search response"""
    
    # SOCKS5 proxy configuration
    proxy_config = {
        'http': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
        'https': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
    }
    
    # Test with one CCCD first
    cccd = "001087016369"
    
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
    
    logger.info("🔧 Debugging masothue.com search response...")
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
        logger.info(f"📊 Content-Type: {homepage_response.headers.get('Content-Type', 'Unknown')}")
        logger.info(f"📊 Content-Encoding: {homepage_response.headers.get('Content-Encoding', 'None')}")
        logger.info(f"📊 Content-Length: {len(homepage_response.content)} bytes")
        
        # Check if homepage content is readable
        homepage_text = homepage_response.text
        logger.info(f"📄 Homepage preview: {homepage_text[:200]}...")
        
    except Exception as e:
        logger.error(f"❌ Homepage error: {e}")
        return
    
    # Test search
    logger.info(f"\n🔍 Testing search for CCCD: {cccd}")
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
        logger.info(f"📊 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        logger.info(f"📊 Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
        logger.info(f"📊 Content-Length: {len(response.content)} bytes")
        
        # Check all response headers
        logger.info("📋 Response Headers:")
        for key, value in response.headers.items():
            logger.info(f"  {key}: {value}")
        
        # Try different ways to decode the content
        logger.info("\n🔍 Content Analysis:")
        
        # Method 1: Direct text
        try:
            text_content = response.text
            logger.info(f"📄 Text content (first 500 chars): {text_content[:500]}")
        except Exception as e:
            logger.error(f"❌ Text decode error: {e}")
        
        # Method 2: Raw content
        raw_content = response.content
        logger.info(f"📄 Raw content (first 100 bytes): {raw_content[:100]}")
        
        # Method 3: Try to detect if it's compressed
        if response.headers.get('Content-Encoding') == 'gzip':
            logger.info("🗜️ Content appears to be gzip compressed")
            try:
                import gzip
                decompressed = gzip.decompress(raw_content)
                logger.info(f"📄 Decompressed content: {decompressed.decode('utf-8', errors='ignore')[:500]}")
            except Exception as e:
                logger.error(f"❌ Decompression error: {e}")
        
        # Method 4: Try BeautifulSoup parsing
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info(f"📄 Parsed HTML title: {soup.title.string if soup.title else 'No title'}")
            
            # Look for any text content
            all_text = soup.get_text()
            logger.info(f"📄 All text content (first 500 chars): {all_text[:500]}")
            
            # Look for specific elements
            links = soup.find_all('a', href=True)
            logger.info(f"📄 Found {len(links)} links")
            for i, link in enumerate(links[:5]):  # Show first 5 links
                logger.info(f"  Link {i+1}: {link.get('href')} - {link.get_text(strip=True)}")
            
        except Exception as e:
            logger.error(f"❌ BeautifulSoup parsing error: {e}")
        
        # Method 5: Check if it's JSON
        try:
            import json
            json_data = response.json()
            logger.info(f"📄 JSON response: {json_data}")
        except:
            logger.info("📄 Not JSON format")
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
    
    logger.info("\n🏁 Debug completed!")

if __name__ == "__main__":
    test_masothue_search_debug()