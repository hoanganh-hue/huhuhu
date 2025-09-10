#!/usr/bin/env python3
"""
Selenium-based Check CCCD API Server
====================================

API server sử dụng Selenium WebDriver để bypass Cloudflare và lấy dữ liệu thực tế.

Author: AI Assistant
Date: 2025-09-08
Version: 6.0.0-selenium
"""

import asyncio
import json
import random
import re
import time
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

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
    title="Check CCCD API - Selenium Version",
    description="API sử dụng Selenium WebDriver để bypass Cloudflare",
    version="6.0.0-selenium",
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
    "selenium_success": 0,
    "selenium_failed": 0,
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
    use_selenium: bool = Field(default=True, description="Sử dụng Selenium")

class CCCDCheckResponse(BaseModel):
    """CCCD check response."""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float
    selenium_used: bool = False
    is_real_data: bool = False

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    selenium_available: bool

class MetricsResponse(BaseModel):
    """Metrics response."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    selenium_success: int = 0
    selenium_failed: int = 0
    real_data_found: int = 0
    no_data_found: int = 0
    average_response_time: float = 0.0
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

# =============================================================================
# SELENIUM CONFIGURATION
# =============================================================================

def create_chrome_driver():
    """Create Chrome WebDriver with optimized settings."""
    try:
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        
        # Stealth options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Headless mode if enabled
        if os.getenv('HEADLESS_MODE', 'true').lower() == 'true':
            chrome_options.add_argument('--headless')
        
        # Window size
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Create service
        service = Service(ChromeDriverManager().install())
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    except Exception as e:
        print(f"❌ Error creating Chrome driver: {e}")
        return None

# =============================================================================
# SELENIUM SCRAPING FUNCTIONS
# =============================================================================

async def selenium_scrape_masothue(cccd: str) -> Dict[str, Any]:
    """Scrape masothue.com using Selenium WebDriver."""
    driver = None
    try:
        print(f"🤖 Selenium scraping for CCCD: {cccd}")
        metrics["selenium_success"] += 1
        
        # Create driver
        driver = create_chrome_driver()
        if not driver:
            return {
                "status": "error",
                "error": "Không thể tạo Chrome WebDriver",
                "selenium_used": True,
                "is_real_data": False
            }
        
        # Set timeout
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # Visit homepage first
        print("   🏠 Visiting homepage...")
        driver.get("https://masothue.com/")
        time.sleep(random.uniform(2, 4))
        
        # Try to find search box and search
        search_urls = [
            f"https://masothue.com/search?q={cccd}",
            f"https://masothue.com/Search/?q={cccd}",
            f"https://masothue.com/tim-kiem?q={cccd}"
        ]
        
        for search_url in search_urls:
            try:
                print(f"   🔍 Trying search URL: {search_url}")
                driver.get(search_url)
                
                # Wait for page to load
                time.sleep(random.uniform(3, 5))
                
                # Check if we got past Cloudflare
                page_source = driver.page_source
                if "Just a moment" in page_source or "Cloudflare" in page_source:
                    print(f"   ⚠️ Cloudflare detected on {search_url}")
                    continue
                
                # Look for results
                matches = []
                
                # Try different selectors for results
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
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements[:5]:  # Limit to first 5 results
                            try:
                                # Extract company name
                                name_selectors = ['h1', 'h2', 'h3', 'a', '.name', '.title', '.company-name']
                                name = "N/A"
                                for name_sel in name_selectors:
                                    try:
                                        name_elem = element.find_element(By.CSS_SELECTOR, name_sel)
                                        if name_elem and name_elem.text.strip():
                                            name = name_elem.text.strip()
                                            break
                                    except:
                                        continue
                                
                                # Extract tax code
                                tax_code = "N/A"
                                element_text = element.text
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
                                    try:
                                        addr_elem = element.find_element(By.CSS_SELECTOR, addr_sel)
                                        if addr_elem and addr_elem.text.strip():
                                            addr_text = addr_elem.text.strip()
                                            if len(addr_text) > 10:
                                                address = addr_text
                                                break
                                    except:
                                        continue
                                
                                # Extract role
                                role_selectors = ['.role', '.chucvu', '.position', '.title']
                                role = "N/A"
                                for role_sel in role_selectors:
                                    try:
                                        role_elem = element.find_element(By.CSS_SELECTOR, role_sel)
                                        if role_elem and role_elem.text.strip():
                                            role = role_elem.text.strip()
                                            break
                                    except:
                                        continue
                                
                                # Only add if we have meaningful data
                                if name != "N/A" and len(name) > 3:
                                    matches.append({
                                        "name": name,
                                        "tax_code": tax_code,
                                        "address": address,
                                        "role": role,
                                        "url": search_url,
                                        "raw_snippet": element.text[:300] + "...",
                                        "source": "selenium_masothue"
                                    })
                                    
                            except Exception as e:
                                print(f"   ⚠️ Error parsing element: {e}")
                                continue
                        
                        if matches:
                            break
                            
                    except Exception as e:
                        print(f"   ⚠️ Error with selector {selector}: {e}")
                        continue
                
                if matches:
                    metrics["real_data_found"] += 1
                    return {
                        "status": "found",
                        "matches": matches,
                        "fetched_at": datetime.now().isoformat(),
                        "search_url": search_url,
                        "note": f"Tìm thấy {len(matches)} kết quả thực tế bằng Selenium",
                        "selenium_used": True,
                        "is_real_data": True
                    }
                else:
                    print(f"   ℹ️ No results found on {search_url}")
                    
            except Exception as e:
                print(f"   ⚠️ Error with URL {search_url}: {e}")
                continue
        
        # If no results found
        metrics["no_data_found"] += 1
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "Không tìm thấy thông tin bằng Selenium - có thể bị chặn hoặc không có dữ liệu",
            "selenium_used": True,
            "is_real_data": False
        }
        
    except Exception as e:
        metrics["selenium_failed"] += 1
        return {
            "status": "error",
            "error": f"Selenium scraping failed: {e}",
            "selenium_used": True,
            "is_real_data": False
        }
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Test if Selenium is available
    selenium_available = False
    try:
        driver = create_chrome_driver()
        if driver:
            driver.quit()
            selenium_available = True
    except:
        pass
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=app.version,
        uptime=time.time() - start_time,
        selenium_available=selenium_available
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0.0
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        selenium_success=metrics["selenium_success"],
        selenium_failed=metrics["selenium_failed"],
        real_data_found=metrics["real_data_found"],
        no_data_found=metrics["no_data_found"],
        average_response_time=avg_time,
        uptime=time.time() - start_time
    )

@app.post("/api/v1/check", response_model=CCCDCheckResponse)
async def check_cccd_selenium(request: CCCDCheckRequest):
    """Selenium-based CCCD check."""
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
        
        print(f"🤖 Selenium check for CCCD: {request.cccd}")
        
        # Perform Selenium scraping
        result = await selenium_scrape_masothue(request.cccd)
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
            selenium_used=result.get("selenium_used", False),
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
    print("🤖 Selenium Check CCCD API Server starting...")
    print(f"📅 Started at: {datetime.now()}")
    print("🔧 Selenium WebDriver: ENABLED")
    print("🌐 Chrome Browser: ENABLED")
    print("🛡️ Cloudflare Bypass: ENABLED")
    print("📊 Real-time metrics: ENABLED")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("🛑 Selenium Check CCCD API Server shutting down...")
    print(f"📊 Final metrics: {metrics}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")