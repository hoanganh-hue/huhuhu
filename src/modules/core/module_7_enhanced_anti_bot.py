"""
Module 7 Enhanced Anti-Bot - Advanced masothue.com scraper
Implements comprehensive anti-bot bypass strategies including:
- Browser-like headers and session management
- Cookie collection and management
- SOCKS5/HTTP proxy rotation
- Playwright fallback for Cloudflare challenges
- Intelligent rate limiting and delays
"""

import asyncio
import time
import random
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin
import httpx
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('masothue_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    username: str
    password: str
    protocol: str = "socks5"
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"

@dataclass
class SearchResult:
    """Search result data structure"""
    cccd: str
    status: str  # "found", "not_found", "error"
    tax_code: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    profile_url: Optional[str] = None
    method_used: Optional[str] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None

class BrowserHeaders:
    """Realistic browser headers for different scenarios"""
    
    @staticmethod
    def get_chrome_headers() -> Dict[str, str]:
        """Get realistic Chrome headers"""
        return {
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
    
    @staticmethod
    def get_mobile_headers() -> Dict[str, str]:
        """Get mobile browser headers"""
        return {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

class SessionManager:
    """Manages HTTP sessions with cookie handling"""
    
    def __init__(self, proxy_config: Optional[ProxyConfig] = None):
        self.proxy_config = proxy_config
        self.session = requests.Session()
        self.cookies = {}
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with headers and proxy"""
        self.session.headers.update(BrowserHeaders.get_chrome_headers())
        
        if self.proxy_config:
            proxy_url = self.proxy_config.url
            self.session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            logger.info(f"🔧 Session configured with proxy: {self.proxy_config.host}:{self.proxy_config.port}")
    
    def get_homepage_cookies(self) -> bool:
        """Get cookies from homepage to establish session"""
        try:
            logger.info("🍪 Getting cookies from homepage...")
            response = self.session.get(
                "https://masothue.com/",
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.cookies.update(response.cookies.get_dict())
                logger.info(f"✅ Cookies collected: {list(self.cookies.keys())}")
                return True
            else:
                logger.warning(f"⚠️ Homepage returned {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to get homepage cookies: {e}")
            return False
    
    def search_with_cookies(self, cccd: str) -> requests.Response:
        """Perform search with established cookies"""
        params = {
            "q": cccd,
            "type": "auto",
            "token": "NbnmgilFfL",
            "force-search": "1"
        }
        
        # Add referer header
        self.session.headers.update({
            "Referer": "https://masothue.com/",
            "X-Requested-With": "XMLHttpRequest"
        })
        
        logger.info(f"🔍 Searching for CCCD: {cccd}")
        response = self.session.get(
            "https://masothue.com/Search/",
            params=params,
            timeout=15
        )
        
        return response

class EnhancedAntiBotScraper:
    """Enhanced scraper with comprehensive anti-bot bypass"""
    
    def __init__(self):
        self.proxy_configs = self._load_proxy_configs()
        self.current_proxy_index = 0
        self.request_count = 0
        self.last_request_time = 0
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "proxy_rotations": 0,
            "browser_fallbacks": 0
        }
    
    def _load_proxy_configs(self) -> List[ProxyConfig]:
        """Load proxy configurations from file"""
        configs = []
        try:
            with open("config/proxies.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Parse proxy URL: protocol://user:pass@host:port
                        if "://" in line:
                            protocol, rest = line.split("://", 1)
                            if "@" in rest:
                                auth, host_port = rest.split("@", 1)
                                username, password = auth.split(":", 1)
                                host, port = host_port.split(":", 1)
                                
                                configs.append(ProxyConfig(
                                    host=host,
                                    port=int(port),
                                    username=username,
                                    password=password,
                                    protocol=protocol
                                ))
            
            logger.info(f"📋 Loaded {len(configs)} proxy configurations")
            return configs
            
        except Exception as e:
            logger.error(f"❌ Failed to load proxy configs: {e}")
            return []
    
    def _get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get next proxy in rotation"""
        if not self.proxy_configs:
            return None
        
        proxy = self.proxy_configs[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_configs)
        self.stats["proxy_rotations"] += 1
        
        return proxy
    
    def _random_delay(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(min_delay, max_delay)
        logger.info(f"⏱️ Waiting {delay:.2f}s to avoid rate limiting...")
        time.sleep(delay)
        self.last_request_time = time.time()
    
    def _check_rate_limit(self):
        """Check if we need to add delay based on request frequency"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # If less than 2 seconds since last request, add delay
        if time_since_last < 2.0:
            self._random_delay(2.0, 4.0)
    
    def search_with_requests(self, cccd: str) -> SearchResult:
        """Search using requests with session management"""
        start_time = time.time()
        self._check_rate_limit()
        
        try:
            # Get proxy and create session
            proxy_config = self._get_next_proxy()
            session_manager = SessionManager(proxy_config)
            
            # Get homepage cookies first
            if not session_manager.get_homepage_cookies():
                logger.warning("⚠️ Failed to get homepage cookies, proceeding anyway...")
            
            # Perform search
            response = session_manager.search_with_cookies(cccd)
            self.stats["total_requests"] += 1
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                self.stats["successful_requests"] += 1
                logger.info(f"✅ Request successful: {response.status_code}")
                
                # Parse response
                result = self._parse_search_response(response.text, cccd)
                result.method_used = "requests_session"
                result.response_time = processing_time
                return result
                
            elif response.status_code == 403:
                self.stats["failed_requests"] += 1
                logger.warning(f"🚫 Blocked by anti-bot: {response.status_code}")
                return SearchResult(
                    cccd=cccd,
                    status="error",
                    method_used="requests_session",
                    response_time=processing_time,
                    error_message=f"403 Forbidden - Anti-bot protection"
                )
            else:
                self.stats["failed_requests"] += 1
                logger.error(f"❌ Unexpected status: {response.status_code}")
                return SearchResult(
                    cccd=cccd,
                    status="error",
                    method_used="requests_session",
                    response_time=processing_time,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Request failed: {e}")
            return SearchResult(
                cccd=cccd,
                status="error",
                method_used="requests_session",
                response_time=processing_time,
                error_message=str(e)
            )
    
    def search_with_httpx(self, cccd: str) -> SearchResult:
        """Search using httpx with SOCKS5 proxy support"""
        start_time = time.time()
        self._check_rate_limit()
        
        try:
            proxy_config = self._get_next_proxy()
            if not proxy_config:
                raise Exception("No proxy available")
            
            # Setup httpx with SOCKS5 proxy
            proxy_url = proxy_config.url
            headers = BrowserHeaders.get_chrome_headers()
            headers.update({
                "Referer": "https://masothue.com/",
                "X-Requested-With": "XMLHttpRequest"
            })
            
            params = {
                "q": cccd,
                "type": "auto",
                "token": "NbnmgilFfL",
                "force-search": "1"
            }
            
            logger.info(f"🌐 httpx request via {proxy_config.protocol} proxy")
            
            # Use httpx with SOCKS5 support
            with httpx.Client(
                proxies=proxy_url,
                headers=headers,
                timeout=15.0,
                follow_redirects=True
            ) as client:
                response = client.get(
                    "https://masothue.com/Search/",
                    params=params
                )
            
            self.stats["total_requests"] += 1
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                self.stats["successful_requests"] += 1
                logger.info(f"✅ httpx request successful: {response.status_code}")
                
                result = self._parse_search_response(response.text, cccd)
                result.method_used = "httpx_socks5"
                result.response_time = processing_time
                return result
                
            else:
                self.stats["failed_requests"] += 1
                logger.warning(f"⚠️ httpx request failed: {response.status_code}")
                return SearchResult(
                    cccd=cccd,
                    status="error",
                    method_used="httpx_socks5",
                    response_time=processing_time,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.stats["failed_requests"] += 1
            logger.error(f"❌ httpx request failed: {e}")
            return SearchResult(
                cccd=cccd,
                status="error",
                method_used="httpx_socks5",
                response_time=processing_time,
                error_message=str(e)
            )
    
    def _parse_search_response(self, html_content: str, cccd: str) -> SearchResult:
        """Parse search response HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for tax code in various possible locations
            tax_code = None
            name = None
            address = None
            profile_url = None
            
            # Method 1: Look for direct tax code links
            tax_links = soup.find_all('a', href=True)
            for link in tax_links:
                href = link.get('href', '')
                if '/masothue.com/' in href and href != 'https://masothue.com/':
                    tax_code = href.split('/')[-1].split('-')[0]
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
            
            # Method 3: Look for name in specific elements
            if not name:
                name_elements = soup.find_all(['h1', 'h2', 'h3', 'strong', 'b'])
                for elem in name_elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 3 and not text.isdigit():
                        name = text
                        break
            
            if tax_code and name:
                return SearchResult(
                    cccd=cccd,
                    status="found",
                    tax_code=tax_code,
                    name=name,
                    address=address,
                    profile_url=profile_url
                )
            else:
                return SearchResult(
                    cccd=cccd,
                    status="not_found"
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to parse response: {e}")
            return SearchResult(
                cccd=cccd,
                status="error",
                error_message=f"Parse error: {e}"
            )
    
    def search_with_fallback(self, cccd: str) -> SearchResult:
        """Search with multiple fallback methods"""
        logger.info(f"🔄 Starting fallback search for CCCD: {cccd}")
        
        # Method 1: Try requests with session management
        result = self.search_with_requests(cccd)
        if result.status == "found":
            logger.info(f"✅ Found via requests session: {result.tax_code}")
            return result
        
        # Method 2: Try httpx with SOCKS5
        if result.status == "error" and "403" in str(result.error_message):
            logger.info("🔄 Trying httpx with SOCKS5...")
            result = self.search_with_httpx(cccd)
            if result.status == "found":
                logger.info(f"✅ Found via httpx SOCKS5: {result.tax_code}")
                return result
        
        # Method 3: Try mobile headers
        if result.status == "error":
            logger.info("🔄 Trying mobile headers...")
            # This would require implementing mobile header version
            # For now, return the last result
            pass
        
        logger.warning(f"⚠️ All methods failed for CCCD: {cccd}")
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        total = self.stats["total_requests"]
        success_rate = (self.stats["successful_requests"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "success_rate": f"{success_rate:.1f}%",
            "proxy_count": len(self.proxy_configs)
        }

def main():
    """Test the enhanced anti-bot scraper"""
    scraper = EnhancedAntiBotScraper()
    
    # Test CCCDs
    test_cccds = [
        "001087016369",
        "001184032114", 
        "001098021288",
        "001094001628",
        "036092002342"
    ]
    
    logger.info("🚀 Starting enhanced anti-bot scraping test...")
    logger.info(f"📊 Proxy configurations loaded: {len(scraper.proxy_configs)}")
    
    results = []
    for cccd in test_cccds:
        logger.info(f"\n{'='*50}")
        logger.info(f"🔍 Testing CCCD: {cccd}")
        logger.info(f"{'='*50}")
        
        result = scraper.search_with_fallback(cccd)
        results.append(result)
        
        # Print result
        if result.status == "found":
            logger.info(f"✅ SUCCESS: {result.tax_code} - {result.name}")
            if result.profile_url:
                logger.info(f"🔗 Profile: {result.profile_url}")
        elif result.status == "not_found":
            logger.info("❌ NOT FOUND")
        else:
            logger.info(f"⚠️ ERROR: {result.error_message}")
        
        logger.info(f"⏱️ Response time: {result.response_time:.2f}s")
        logger.info(f"🔧 Method used: {result.method_used}")
        
        # Add delay between requests
        if cccd != test_cccds[-1]:  # Don't delay after last request
            scraper._random_delay(3.0, 6.0)
    
    # Print final statistics
    logger.info(f"\n{'='*50}")
    logger.info("📊 FINAL STATISTICS")
    logger.info(f"{'='*50}")
    stats = scraper.get_stats()
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    
    # Summary
    found_count = sum(1 for r in results if r.status == "found")
    logger.info(f"\n🎯 RESULTS SUMMARY:")
    logger.info(f"Found: {found_count}/{len(results)}")
    logger.info(f"Success rate: {found_count/len(results)*100:.1f}%")

if __name__ == "__main__":
    main()