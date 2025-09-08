"""
Module 7 Playwright Fallback - Browser automation for Cloudflare challenges
Handles JavaScript challenges and CAPTCHAs that regular HTTP requests cannot solve
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class PlaywrightConfig:
    """Playwright browser configuration"""
    headless: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    viewport: Dict[str, int] = None
    proxy_server: Optional[str] = None
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}

class PlaywrightScraper:
    """Playwright-based scraper for handling Cloudflare challenges"""
    
    def __init__(self, config: Optional[PlaywrightConfig] = None):
        self.config = config or PlaywrightConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.stats = {
            "browser_launches": 0,
            "challenges_solved": 0,
            "successful_requests": 0,
            "failed_requests": 0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()
    
    async def start_browser(self):
        """Start Playwright browser"""
        try:
            playwright = await async_playwright().start()
            
            # Launch browser with options
            browser_options = {
                "headless": self.config.headless,
                "args": [
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            }
            
            # Add proxy if configured
            if self.config.proxy_server:
                browser_options["proxy"] = {"server": self.config.proxy_server}
                logger.info(f"🌐 Browser configured with proxy: {self.config.proxy_server}")
            
            self.browser = await playwright.chromium.launch(**browser_options)
            
            # Create context with realistic settings
            context_options = {
                "user_agent": self.config.user_agent,
                "viewport": self.config.viewport,
                "locale": "vi-VN",
                "timezone_id": "Asia/Ho_Chi_Minh",
                "extra_http_headers": {
                    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
            }
            
            self.context = await self.browser.new_context(**context_options)
            self.stats["browser_launches"] += 1
            
            logger.info("🚀 Playwright browser started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            raise
    
    async def close_browser(self):
        """Close Playwright browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("🔒 Browser closed successfully")
        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")
    
    async def solve_cloudflare_challenge(self, page: Page) -> bool:
        """Attempt to solve Cloudflare challenge"""
        try:
            logger.info("🛡️ Detected Cloudflare challenge, attempting to solve...")
            
            # Wait for challenge to appear
            await page.wait_for_timeout(3000)
            
            # Check if challenge is present
            challenge_selectors = [
                "[data-ray]",
                ".cf-browser-verification",
                "#cf-challenge-stage",
                ".cf-challenge-running"
            ]
            
            challenge_found = False
            for selector in challenge_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        challenge_found = True
                        logger.info(f"🎯 Found challenge element: {selector}")
                        break
                except:
                    continue
            
            if not challenge_found:
                logger.info("✅ No challenge detected, proceeding...")
                return True
            
            # Wait for challenge to complete automatically
            logger.info("⏳ Waiting for Cloudflare challenge to complete...")
            await page.wait_for_timeout(10000)  # Wait up to 10 seconds
            
            # Check if we're past the challenge
            current_url = page.url
            if "masothue.com" in current_url and "challenge" not in current_url.lower():
                logger.info("✅ Cloudflare challenge solved successfully")
                self.stats["challenges_solved"] += 1
                return True
            else:
                logger.warning("⚠️ Cloudflare challenge may not be fully solved")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error solving Cloudflare challenge: {e}")
            return False
    
    async def search_with_browser(self, cccd: str) -> Dict[str, Any]:
        """Search using browser automation"""
        start_time = time.time()
        
        try:
            if not self.context:
                await self.start_browser()
            
            # Create new page
            page = await self.context.new_page()
            
            # Navigate to homepage first to establish session
            logger.info("🏠 Navigating to homepage...")
            await page.goto("https://masothue.com/", wait_until="networkidle", timeout=30000)
            
            # Check for and solve Cloudflare challenge
            await self.solve_cloudflare_challenge(page)
            
            # Navigate to search page
            search_url = f"https://masothue.com/Search/?q={cccd}&type=auto&token=NbnmgilFfL&force-search=1"
            logger.info(f"🔍 Navigating to search: {cccd}")
            
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            
            # Check for additional challenges
            await self.solve_cloudflare_challenge(page)
            
            # Get page content
            content = await page.content()
            processing_time = time.time() - start_time
            
            # Close page
            await page.close()
            
            # Parse results
            result = self._parse_browser_response(content, cccd)
            result["method_used"] = "playwright_browser"
            result["response_time"] = processing_time
            
            self.stats["successful_requests"] += 1
            logger.info(f"✅ Browser search completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Browser search failed: {e}")
            
            return {
                "cccd": cccd,
                "status": "error",
                "method_used": "playwright_browser",
                "response_time": processing_time,
                "error_message": str(e)
            }
    
    def _parse_browser_response(self, html_content: str, cccd: str) -> Dict[str, Any]:
        """Parse browser response HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for tax code and name
            tax_code = None
            name = None
            address = None
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
            
            # Method 3: Look for name in headings or strong elements
            if not name:
                name_elements = soup.find_all(['h1', 'h2', 'h3', 'strong', 'b', 'span'])
                for elem in name_elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 3 and not text.isdigit() and not text.startswith('http'):
                        # Check if it looks like a Vietnamese name
                        if any(char in text for char in ['Lê', 'Nguyễn', 'Trần', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Võ']):
                            name = text
                            break
            
            # Method 4: Look for address information
            address_elements = soup.find_all(['p', 'div', 'span'])
            for elem in address_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 20 and any(keyword in text.lower() for keyword in ['phường', 'quận', 'huyện', 'tỉnh', 'thành phố']):
                    address = text
                    break
            
            if tax_code and name:
                return {
                    "cccd": cccd,
                    "status": "found",
                    "tax_code": tax_code,
                    "name": name,
                    "address": address,
                    "profile_url": profile_url
                }
            else:
                return {
                    "cccd": cccd,
                    "status": "not_found"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to parse browser response: {e}")
            return {
                "cccd": cccd,
                "status": "error",
                "error_message": f"Parse error: {e}"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get browser automation statistics"""
        total = self.stats["successful_requests"] + self.stats["failed_requests"]
        success_rate = (self.stats["successful_requests"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "success_rate": f"{success_rate:.1f}%"
        }

async def test_playwright_scraper():
    """Test the Playwright scraper"""
    config = PlaywrightConfig(
        headless=True,
        proxy_server="socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301"
    )
    
    async with PlaywrightScraper(config) as scraper:
        test_cccds = [
            "001087016369",
            "001184032114", 
            "001098021288",
            "001094001628",
            "036092002342"
        ]
        
        logger.info("🚀 Starting Playwright browser test...")
        
        results = []
        for cccd in test_cccds:
            logger.info(f"\n{'='*50}")
            logger.info(f"🔍 Testing CCCD: {cccd}")
            logger.info(f"{'='*50}")
            
            result = await scraper.search_with_browser(cccd)
            results.append(result)
            
            # Print result
            if result["status"] == "found":
                logger.info(f"✅ SUCCESS: {result['tax_code']} - {result['name']}")
                if result.get("profile_url"):
                    logger.info(f"🔗 Profile: {result['profile_url']}")
            elif result["status"] == "not_found":
                logger.info("❌ NOT FOUND")
            else:
                logger.info(f"⚠️ ERROR: {result.get('error_message', 'Unknown error')}")
            
            logger.info(f"⏱️ Response time: {result.get('response_time', 0):.2f}s")
            logger.info(f"🔧 Method used: {result.get('method_used', 'unknown')}")
            
            # Add delay between requests
            if cccd != test_cccds[-1]:
                await asyncio.sleep(3)
        
        # Print final statistics
        logger.info(f"\n{'='*50}")
        logger.info("📊 PLAYWRIGHT STATISTICS")
        logger.info(f"{'='*50}")
        stats = scraper.get_stats()
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
        
        # Summary
        found_count = sum(1 for r in results if r["status"] == "found")
        logger.info(f"\n🎯 PLAYWRIGHT RESULTS SUMMARY:")
        logger.info(f"Found: {found_count}/{len(results)}")
        logger.info(f"Success rate: {found_count/len(results)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_playwright_scraper())