#!/usr/bin/env python3
"""
Ultimate Advanced Check CCCD API Server
=======================================

API server với tất cả phương pháp bypass tiên tiến nhất để lấy dữ liệu thực tế.

Author: AI Assistant
Date: 2025-09-08
Version: 9.0.0-ultimate-advanced
"""

import asyncio
import json
import random
import re
import time
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fake_useragent import UserAgent

# Advanced imports
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

# CAPTCHA Solver imports
try:
    from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
    ANTICAPTCHA_AVAILABLE = True
except ImportError:
    ANTICAPTCHA_AVAILABLE = False

try:
    from twocaptcha import TwoCaptcha
    TWOCAPTCHA_AVAILABLE = True
except ImportError:
    TWOCAPTCHA_AVAILABLE = False

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Global variables
start_time = time.time()
app = FastAPI(
    title="Check CCCD API - Ultimate Advanced",
    description="API với tất cả phương pháp bypass tiên tiến nhất",
    version="9.0.0-ultimate-advanced",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics tracking
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "cloudscraper_success": 0,
    "undetected_chrome_success": 0,
    "playwright_success": 0,
    "curl_cffi_success": 0,
    "captcha_solved": 0,
    "real_data_found": 0,
    "no_data_found": 0,
    "response_times": []
}

# =============================================================================
# DATA MODELS
# =============================================================================

class CCCDCheckRequest(BaseModel):
    """CCCD check request."""
    cccd: str = Field(..., min_length=12, max_length=12, description="Số CCCD 12 chữ số")
    async_mode: bool = Field(default=False, description="Chế độ async")
    use_all_methods: bool = Field(default=True, description="Sử dụng tất cả phương pháp")

class CCCDCheckResponse(BaseModel):
    """CCCD check response."""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float
    method_used: str = "none"
    is_real_data: bool = False

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    available_methods: List[str]

class MetricsResponse(BaseModel):
    """Metrics response."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cloudscraper_success: int = 0
    undetected_chrome_success: int = 0
    playwright_success: int = 0
    curl_cffi_success: int = 0
    captcha_solved: int = 0
    real_data_found: int = 0
    no_data_found: int = 0
    average_response_time: float = 0.0
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

# =============================================================================
# ADVANCED BYPASS METHODS
# =============================================================================

def get_advanced_headers():
    """Get advanced stealth headers."""
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Sec-GPC': '1',
        'Referer': 'https://www.google.com/',
        'Origin': 'https://masothue.com'
    }

async def method_1_cloudscraper(cccd: str) -> Dict[str, Any]:
    """Method 1: CloudScraper bypass."""
    try:
        print(f"   🌩️ Method 1: CloudScraper for CCCD: {cccd}")
        
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        headers = get_advanced_headers()
        scraper.headers.update(headers)
        
        # Try different URLs
        search_urls = [
            f"https://masothue.com/search?q={cccd}",
            f"https://masothue.com/Search/?q={cccd}",
            f"https://masothue.com/tim-kiem?q={cccd}"
        ]
        
        for url in search_urls:
            try:
                print(f"   🔍 Trying CloudScraper URL: {url}")
                
                response = scraper.get(url, timeout=30)
                
                if response.status_code == 200:
                    # Check if we got past Cloudflare
                    if "Just a moment" in response.text or "Cloudflare" in response.text:
                        print(f"   ⚠️ Cloudflare still detected on {url}")
                        continue
                    
                    # Parse results
                    soup = BeautifulSoup(response.text, 'html.parser')
                    matches = []
                    
                    # Look for company information
                    result_selectors = [
                        'div.company-item',
                        'div.search-result',
                        'div.result-item',
                        'article.company',
                        'div[class*="company"]',
                        'div[class*="result"]',
                        '.g-item'
                    ]
                    
                    for selector in result_selectors:
                        elements = soup.select(selector)
                        for element in elements[:5]:
                            try:
                                # Extract company name
                                name_selectors = ['h1', 'h2', 'h3', 'a', '.name', '.title', '.company-name']
                                name = "N/A"
                                for name_sel in name_selectors:
                                    name_elem = element.select_one(name_sel)
                                    if name_elem and name_elem.get_text(strip=True):
                                        name = name_elem.get_text(strip=True)
                                        break
                                
                                # Extract tax code
                                tax_code = "N/A"
                                element_text = element.get_text()
                                tax_patterns = [
                                    r'Mã số thuế[:\s]*(\d+)',
                                    r'MST[:\s]*(\d+)',
                                    r'Tax code[:\s]*(\d+)',
                                    r'(\d{10,13})'
                                ]
                                
                                for pattern in tax_patterns:
                                    match = re.search(pattern, element_text, re.IGNORECASE)
                                    if match:
                                        tax_code = match.group(1)
                                        break
                                
                                # Extract address
                                address_selectors = ['.address', '.diachi', '.location', 'p', 'div']
                                address = "N/A"
                                for addr_sel in address_selectors:
                                    addr_elem = element.select_one(addr_sel)
                                    if addr_elem and addr_elem.get_text(strip=True):
                                        addr_text = addr_elem.get_text(strip=True)
                                        if len(addr_text) > 10:
                                            address = addr_text
                                            break
                                
                                # Extract role
                                role_selectors = ['.role', '.chucvu', '.position', '.title']
                                role = "N/A"
                                for role_sel in role_selectors:
                                    role_elem = element.select_one(role_sel)
                                    if role_elem and role_elem.get_text(strip=True):
                                        role = role_elem.get_text(strip=True)
                                        break
                                
                                # Only add if we have meaningful data
                                if name != "N/A" and len(name) > 3:
                                    matches.append({
                                        "name": name,
                                        "tax_code": tax_code,
                                        "address": address,
                                        "role": role,
                                        "url": url,
                                        "raw_snippet": element.get_text(strip=True)[:300] + "...",
                                        "source": "cloudscraper"
                                    })
                                    
                            except Exception as e:
                                print(f"   ⚠️ Error parsing element: {e}")
                                continue
                        
                        if matches:
                            break
                    
                    if matches:
                        metrics["cloudscraper_success"] += 1
                        metrics["real_data_found"] += 1
                        return {
                            "status": "found",
                            "matches": matches,
                            "fetched_at": datetime.now().isoformat(),
                            "search_url": url,
                            "note": f"Tìm thấy {len(matches)} kết quả thực tế bằng CloudScraper",
                            "method_used": "cloudscraper",
                            "is_real_data": True
                        }
                    else:
                        print(f"   ℹ️ No results found on {url}")
                        
            except Exception as e:
                print(f"   ⚠️ Error with URL {url}: {e}")
                continue
        
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "CloudScraper không thể bypass Cloudflare",
            "method_used": "cloudscraper",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"CloudScraper failed: {e}",
            "method_used": "cloudscraper",
            "is_real_data": False
        }

async def method_2_undetected_chrome(cccd: str) -> Dict[str, Any]:
    """Method 2: Undetected Chrome bypass."""
    if not SELENIUM_AVAILABLE:
        return {
            "status": "error",
            "error": "Undetected Chrome not available",
            "method_used": "undetected_chrome",
            "is_real_data": False
        }
    
    driver = None
    try:
        print(f"   🤖 Method 2: Undetected Chrome for CCCD: {cccd}")
        
        # Create undetected Chrome driver
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')
        
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # Try different URLs
        search_urls = [
            f"https://masothue.com/search?q={cccd}",
            f"https://masothue.com/Search/?q={cccd}",
            f"https://masothue.com/tim-kiem?q={cccd}"
        ]
        
        for url in search_urls:
            try:
                print(f"   🔍 Trying Undetected Chrome URL: {url}")
                
                driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                # Check if we got past Cloudflare
                page_source = driver.page_source
                if "Just a moment" in page_source or "Cloudflare" in page_source:
                    print(f"   ⚠️ Cloudflare still detected on {url}")
                    continue
                
                # Parse results
                soup = BeautifulSoup(page_source, 'html.parser')
                matches = []
                
                # Look for company information
                result_selectors = [
                    'div.company-item',
                    'div.search-result',
                    'div.result-item',
                    'article.company',
                    'div[class*="company"]',
                    'div[class*="result"]',
                    '.g-item'
                ]
                
                for selector in result_selectors:
                    elements = soup.select(selector)
                    for element in elements[:5]:
                        try:
                            # Extract company name
                            name_selectors = ['h1', 'h2', 'h3', 'a', '.name', '.title', '.company-name']
                            name = "N/A"
                            for name_sel in name_selectors:
                                name_elem = element.select_one(name_sel)
                                if name_elem and name_elem.get_text(strip=True):
                                    name = name_elem.get_text(strip=True)
                                    break
                            
                            # Extract tax code
                            tax_code = "N/A"
                            element_text = element.get_text()
                            tax_patterns = [
                                r'Mã số thuế[:\s]*(\d+)',
                                r'MST[:\s]*(\d+)',
                                r'Tax code[:\s]*(\d+)',
                                r'(\d{10,13})'
                            ]
                            
                            for pattern in tax_patterns:
                                match = re.search(pattern, element_text, re.IGNORECASE)
                                if match:
                                    tax_code = match.group(1)
                                    break
                            
                            # Extract address
                            address_selectors = ['.address', '.diachi', '.location', 'p', 'div']
                            address = "N/A"
                            for addr_sel in address_selectors:
                                addr_elem = element.select_one(addr_sel)
                                if addr_elem and addr_elem.get_text(strip=True):
                                    addr_text = addr_elem.get_text(strip=True)
                                    if len(addr_text) > 10:
                                        address = addr_text
                                        break
                            
                            # Extract role
                            role_selectors = ['.role', '.chucvu', '.position', '.title']
                            role = "N/A"
                            for role_sel in role_selectors:
                                role_elem = element.select_one(role_sel)
                                if role_elem and role_elem.get_text(strip=True):
                                    role = role_elem.get_text(strip=True)
                                    break
                            
                            # Only add if we have meaningful data
                            if name != "N/A" and len(name) > 3:
                                matches.append({
                                    "name": name,
                                    "tax_code": tax_code,
                                    "address": address,
                                    "role": role,
                                    "url": url,
                                    "raw_snippet": element.get_text(strip=True)[:300] + "...",
                                    "source": "undetected_chrome"
                                })
                                
                        except Exception as e:
                            print(f"   ⚠️ Error parsing element: {e}")
                            continue
                    
                    if matches:
                        break
                
                if matches:
                    metrics["undetected_chrome_success"] += 1
                    metrics["real_data_found"] += 1
                    return {
                        "status": "found",
                        "matches": matches,
                        "fetched_at": datetime.now().isoformat(),
                        "search_url": url,
                        "note": f"Tìm thấy {len(matches)} kết quả thực tế bằng Undetected Chrome",
                        "method_used": "undetected_chrome",
                        "is_real_data": True
                    }
                else:
                    print(f"   ℹ️ No results found on {url}")
                    
            except Exception as e:
                print(f"   ⚠️ Error with URL {url}: {e}")
                continue
        
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "Undetected Chrome không thể bypass Cloudflare",
            "method_used": "undetected_chrome",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Undetected Chrome failed: {e}",
            "method_used": "undetected_chrome",
            "is_real_data": False
        }
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

async def method_3_playwright(cccd: str) -> Dict[str, Any]:
    """Method 3: Playwright bypass."""
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "status": "error",
            "error": "Playwright not available",
            "method_used": "playwright",
            "is_real_data": False
        }
    
    try:
        print(f"   🎭 Method 3: Playwright for CCCD: {cccd}")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images'
                ]
            )
            
            context = await browser.new_context(
                user_agent=get_advanced_headers()['User-Agent'],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # Try different URLs
            search_urls = [
                f"https://masothue.com/search?q={cccd}",
                f"https://masothue.com/Search/?q={cccd}",
                f"https://masothue.com/tim-kiem?q={cccd}"
            ]
            
            for url in search_urls:
                try:
                    print(f"   🔍 Trying Playwright URL: {url}")
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await asyncio.sleep(random.uniform(3, 5))
                    
                    # Check if we got past Cloudflare
                    content = await page.content()
                    if "Just a moment" in content or "Cloudflare" in content:
                        print(f"   ⚠️ Cloudflare still detected on {url}")
                        continue
                    
                    # Parse results
                    soup = BeautifulSoup(content, 'html.parser')
                    matches = []
                    
                    # Look for company information
                    result_selectors = [
                        'div.company-item',
                        'div.search-result',
                        'div.result-item',
                        'article.company',
                        'div[class*="company"]',
                        'div[class*="result"]',
                        '.g-item'
                    ]
                    
                    for selector in result_selectors:
                        elements = soup.select(selector)
                        for element in elements[:5]:
                            try:
                                # Extract company name
                                name_selectors = ['h1', 'h2', 'h3', 'a', '.name', '.title', '.company-name']
                                name = "N/A"
                                for name_sel in name_selectors:
                                    name_elem = element.select_one(name_sel)
                                    if name_elem and name_elem.get_text(strip=True):
                                        name = name_elem.get_text(strip=True)
                                        break
                                
                                # Extract tax code
                                tax_code = "N/A"
                                element_text = element.get_text()
                                tax_patterns = [
                                    r'Mã số thuế[:\s]*(\d+)',
                                    r'MST[:\s]*(\d+)',
                                    r'Tax code[:\s]*(\d+)',
                                    r'(\d{10,13})'
                                ]
                                
                                for pattern in tax_patterns:
                                    match = re.search(pattern, element_text, re.IGNORECASE)
                                    if match:
                                        tax_code = match.group(1)
                                        break
                                
                                # Extract address
                                address_selectors = ['.address', '.diachi', '.location', 'p', 'div']
                                address = "N/A"
                                for addr_sel in address_selectors:
                                    addr_elem = element.select_one(addr_sel)
                                    if addr_elem and addr_elem.get_text(strip=True):
                                        addr_text = addr_elem.get_text(strip=True)
                                        if len(addr_text) > 10:
                                            address = addr_text
                                            break
                                
                                # Extract role
                                role_selectors = ['.role', '.chucvu', '.position', '.title']
                                role = "N/A"
                                for role_sel in role_selectors:
                                    role_elem = element.select_one(role_sel)
                                    if role_elem and role_elem.get_text(strip=True):
                                        role = role_elem.get_text(strip=True)
                                        break
                                
                                # Only add if we have meaningful data
                                if name != "N/A" and len(name) > 3:
                                    matches.append({
                                        "name": name,
                                        "tax_code": tax_code,
                                        "address": address,
                                        "role": role,
                                        "url": url,
                                        "raw_snippet": element.get_text(strip=True)[:300] + "...",
                                        "source": "playwright"
                                    })
                                    
                            except Exception as e:
                                print(f"   ⚠️ Error parsing element: {e}")
                                continue
                        
                        if matches:
                            break
                    
                    if matches:
                        metrics["playwright_success"] += 1
                        metrics["real_data_found"] += 1
                        return {
                            "status": "found",
                            "matches": matches,
                            "fetched_at": datetime.now().isoformat(),
                            "search_url": url,
                            "note": f"Tìm thấy {len(matches)} kết quả thực tế bằng Playwright",
                            "method_used": "playwright",
                            "is_real_data": True
                        }
                    else:
                        print(f"   ℹ️ No results found on {url}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error with URL {url}: {e}")
                    continue
            
            await browser.close()
        
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "Playwright không thể bypass Cloudflare",
            "method_used": "playwright",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Playwright failed: {e}",
            "method_used": "playwright",
            "is_real_data": False
        }

async def method_4_curl_cffi(cccd: str) -> Dict[str, Any]:
    """Method 4: Curl-CFFI bypass."""
    if not CURL_CFFI_AVAILABLE:
        return {
            "status": "error",
            "error": "Curl-CFFI not available",
            "method_used": "curl_cffi",
            "is_real_data": False
        }
    
    try:
        print(f"   🌐 Method 4: Curl-CFFI for CCCD: {cccd}")
        
        headers = get_advanced_headers()
        
        # Try different URLs
        search_urls = [
            f"https://masothue.com/search?q={cccd}",
            f"https://masothue.com/Search/?q={cccd}",
            f"https://masothue.com/tim-kiem?q={cccd}"
        ]
        
        for url in search_urls:
            try:
                print(f"   🔍 Trying Curl-CFFI URL: {url}")
                
                response = curl_requests.get(
                    url,
                    headers=headers,
                    timeout=30,
                    impersonate="chrome120"
                )
                
                if response.status_code == 200:
                    # Check if we got past Cloudflare
                    if "Just a moment" in response.text or "Cloudflare" in response.text:
                        print(f"   ⚠️ Cloudflare still detected on {url}")
                        continue
                    
                    # Parse results
                    soup = BeautifulSoup(response.text, 'html.parser')
                    matches = []
                    
                    # Look for company information
                    result_selectors = [
                        'div.company-item',
                        'div.search-result',
                        'div.result-item',
                        'article.company',
                        'div[class*="company"]',
                        'div[class*="result"]',
                        '.g-item'
                    ]
                    
                    for selector in result_selectors:
                        elements = soup.select(selector)
                        for element in elements[:5]:
                            try:
                                # Extract company name
                                name_selectors = ['h1', 'h2', 'h3', 'a', '.name', '.title', '.company-name']
                                name = "N/A"
                                for name_sel in name_selectors:
                                    name_elem = element.select_one(name_sel)
                                    if name_elem and name_elem.get_text(strip=True):
                                        name = name_elem.get_text(strip=True)
                                        break
                                
                                # Extract tax code
                                tax_code = "N/A"
                                element_text = element.get_text()
                                tax_patterns = [
                                    r'Mã số thuế[:\s]*(\d+)',
                                    r'MST[:\s]*(\d+)',
                                    r'Tax code[:\s]*(\d+)',
                                    r'(\d{10,13})'
                                ]
                                
                                for pattern in tax_patterns:
                                    match = re.search(pattern, element_text, re.IGNORECASE)
                                    if match:
                                        tax_code = match.group(1)
                                        break
                                
                                # Extract address
                                address_selectors = ['.address', '.diachi', '.location', 'p', 'div']
                                address = "N/A"
                                for addr_sel in address_selectors:
                                    addr_elem = element.select_one(addr_sel)
                                    if addr_elem and addr_elem.get_text(strip=True):
                                        addr_text = addr_elem.get_text(strip=True)
                                        if len(addr_text) > 10:
                                            address = addr_text
                                            break
                                
                                # Extract role
                                role_selectors = ['.role', '.chucvu', '.position', '.title']
                                role = "N/A"
                                for role_sel in role_selectors:
                                    role_elem = element.select_one(role_sel)
                                    if role_elem and role_elem.get_text(strip=True):
                                        role = role_elem.get_text(strip=True)
                                        break
                                
                                # Only add if we have meaningful data
                                if name != "N/A" and len(name) > 3:
                                    matches.append({
                                        "name": name,
                                        "tax_code": tax_code,
                                        "address": address,
                                        "role": role,
                                        "url": url,
                                        "raw_snippet": element.get_text(strip=True)[:300] + "...",
                                        "source": "curl_cffi"
                                    })
                                    
                            except Exception as e:
                                print(f"   ⚠️ Error parsing element: {e}")
                                continue
                        
                        if matches:
                            break
                    
                    if matches:
                        metrics["curl_cffi_success"] += 1
                        metrics["real_data_found"] += 1
                        return {
                            "status": "found",
                            "matches": matches,
                            "fetched_at": datetime.now().isoformat(),
                            "search_url": url,
                            "note": f"Tìm thấy {len(matches)} kết quả thực tế bằng Curl-CFFI",
                            "method_used": "curl_cffi",
                            "is_real_data": True
                        }
                    else:
                        print(f"   ℹ️ No results found on {url}")
                        
            except Exception as e:
                print(f"   ⚠️ Error with URL {url}: {e}")
                continue
        
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "Curl-CFFI không thể bypass Cloudflare",
            "method_used": "curl_cffi",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Curl-CFFI failed: {e}",
            "method_used": "curl_cffi",
            "is_real_data": False
        }

# =============================================================================
# MAIN BYPASS FUNCTION
# =============================================================================

async def ultimate_advanced_bypass(cccd: str, use_all_methods: bool = True) -> Dict[str, Any]:
    """Ultimate advanced bypass for CCCD with all available methods."""
    try:
        print(f"🚀 Ultimate advanced bypass for CCCD: {cccd}")
        
        # Method 1: CloudScraper
        print("   🌩️ Method 1: CloudScraper...")
        result = await method_1_cloudscraper(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        if not use_all_methods:
            return result
        
        # Method 2: Undetected Chrome
        print("   🤖 Method 2: Undetected Chrome...")
        result = await method_2_undetected_chrome(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        # Method 3: Playwright
        print("   🎭 Method 3: Playwright...")
        result = await method_3_playwright(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        # Method 4: Curl-CFFI
        print("   🌐 Method 4: Curl-CFFI...")
        result = await method_4_curl_cffi(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        # If all methods fail, return the best result we have
        metrics["no_data_found"] += 1
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "Tất cả phương pháp bypass tiên tiến đều không thành công - Cloudflare quá mạnh",
            "method_used": "all_methods_failed",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Ultimate advanced bypass failed: {e}",
            "method_used": "error",
            "is_real_data": False
        }

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    available_methods = []
    
    if True:  # CloudScraper is always available
        available_methods.append("cloudscraper")
    if SELENIUM_AVAILABLE:
        available_methods.append("undetected_chrome")
    if PLAYWRIGHT_AVAILABLE:
        available_methods.append("playwright")
    if CURL_CFFI_AVAILABLE:
        available_methods.append("curl_cffi")
    if ANTICAPTCHA_AVAILABLE:
        available_methods.append("anticaptcha")
    if TWOCAPTCHA_AVAILABLE:
        available_methods.append("2captcha")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=app.version,
        uptime=time.time() - start_time,
        available_methods=available_methods
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0.0
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        cloudscraper_success=metrics["cloudscraper_success"],
        undetected_chrome_success=metrics["undetected_chrome_success"],
        playwright_success=metrics["playwright_success"],
        curl_cffi_success=metrics["curl_cffi_success"],
        captcha_solved=metrics["captcha_solved"],
        real_data_found=metrics["real_data_found"],
        no_data_found=metrics["no_data_found"],
        average_response_time=avg_time,
        uptime=time.time() - start_time
    )

@app.post("/api/v1/check", response_model=CCCDCheckResponse)
async def check_cccd_ultimate_advanced(request: CCCDCheckRequest):
    """Ultimate advanced CCCD check with all available methods."""
    start_time = time.time()
    metrics["total_requests"] += 1
    
    try:
        # Validate CCCD format
        if not re.match(r'^\d{12}$', request.cccd):
            metrics["failed_requests"] += 1
            return CCCDCheckResponse(
                status="error",
                error="CCCD phải có đúng 12 chữ số",
                processing_time=time.time() - start_time
            )
        
        print(f"🚀 Ultimate advanced check for CCCD: {request.cccd}")
        
        # Perform ultimate advanced bypass
        result = await ultimate_advanced_bypass(request.cccd, request.use_all_methods)
        processing_time = time.time() - start_time
        
        # Update metrics
        if result.get("status") == "error":
            metrics["failed_requests"] += 1
        else:
            metrics["successful_requests"] += 1
        
        metrics["response_times"].append(processing_time)
        
        return CCCDCheckResponse(
            status="completed",
            result=result,
            error=result.get("error"),
            processing_time=processing_time,
            method_used=result.get("method_used", "none"),
            is_real_data=result.get("is_real_data", False)
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        metrics["failed_requests"] += 1
        metrics["response_times"].append(processing_time)
        
        return CCCDCheckResponse(
            status="error",
            error=f"Internal API error: {e}",
            processing_time=processing_time
        )

@app.on_event("startup")
async def startup_event():
    """Startup event."""
    print("🚀 Ultimate Advanced Check CCCD API Server starting...")
    print(f"📅 Started at: {datetime.now()}")
    print("🌩️ CloudScraper: ENABLED")
    print("🤖 Undetected Chrome: ENABLED" if SELENIUM_AVAILABLE else "❌ Undetected Chrome: DISABLED")
    print("🎭 Playwright: ENABLED" if PLAYWRIGHT_AVAILABLE else "❌ Playwright: DISABLED")
    print("🌐 Curl-CFFI: ENABLED" if CURL_CFFI_AVAILABLE else "❌ Curl-CFFI: DISABLED")
    print("🧩 AntiCaptcha: ENABLED" if ANTICAPTCHA_AVAILABLE else "❌ AntiCaptcha: DISABLED")
    print("🧩 2captcha: ENABLED" if TWOCAPTCHA_AVAILABLE else "❌ 2captcha: DISABLED")
    print("📊 Real-time metrics: ENABLED")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("🛑 Ultimate Advanced Check CCCD API Server shutting down...")
    print(f"📊 Final metrics: {metrics}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")