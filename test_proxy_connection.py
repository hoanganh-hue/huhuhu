#!/usr/bin/env python3
"""
Test SOCKS5 proxy connection to verify it's working
"""

import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_proxy_connection():
    """Test SOCKS5 proxy connection"""
    
    # SOCKS5 proxy configuration
    proxy_config = {
        'http': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
        'https': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
    }
    
    # Test URLs
    test_urls = [
        "http://httpbin.org/ip",
        "https://httpbin.org/ip",
        "https://masothue.com/",
        "https://www.google.com/"
    ]
    
    logger.info("🔧 Testing SOCKS5 proxy connection...")
    logger.info(f"Proxy: socks5://beba111:***@ip.mproxy.vn:12301")
    
    for i, url in enumerate(test_urls, 1):
        logger.info(f"\n📡 Test {i}/{len(test_urls)}: {url}")
        logger.info("-" * 50)
        
        try:
            start_time = time.time()
            
            # Make request with proxy
            response = requests.get(
                url,
                proxies=proxy_config,
                timeout=15,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                }
            )
            
            response_time = time.time() - start_time
            
            logger.info(f"✅ Status: {response.status_code}")
            logger.info(f"⏱️ Response time: {response_time:.2f}s")
            logger.info(f"📏 Content length: {len(response.content)} bytes")
            
            # Show IP if it's httpbin.org/ip
            if "httpbin.org/ip" in url:
                try:
                    import json
                    ip_data = response.json()
                    logger.info(f"🌐 IP Address: {ip_data.get('origin', 'Unknown')}")
                except:
                    logger.info("📄 Response preview: " + response.text[:100] + "...")
            else:
                logger.info("📄 Response preview: " + response.text[:100] + "...")
                
        except requests.exceptions.ProxyError as e:
            logger.error(f"❌ Proxy Error: {e}")
        except requests.exceptions.ConnectTimeout as e:
            logger.error(f"❌ Connection Timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request Error: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected Error: {e}")
        
        # Add delay between tests
        if i < len(test_urls):
            logger.info("⏳ Waiting 3s before next test...")
            time.sleep(3)
    
    logger.info("\n🏁 Proxy connection test completed!")

if __name__ == "__main__":
    test_proxy_connection()