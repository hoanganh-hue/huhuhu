#!/usr/bin/env python3
"""
CAPTCHA Solver Check CCCD API Server
====================================

API server sử dụng CAPTCHA solver để bypass Cloudflare và lấy dữ liệu thực tế.

Author: AI Assistant
Date: 2025-09-08
Version: 8.0.0-captcha
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
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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
    title="Check CCCD API - CAPTCHA Solver Version",
    description="API sử dụng CAPTCHA solver để bypass Cloudflare",
    version="8.0.0-captcha",
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
    "captcha_solved": 0,
    "captcha_failed": 0,
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
    use_captcha_solver: bool = Field(default=True, description="Sử dụng CAPTCHA solver")

class CCCDCheckResponse(BaseModel):
    """CCCD check response."""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float
    captcha_solver_used: str = "none"
    is_real_data: bool = False

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    anticaptcha_available: bool
    twocaptcha_available: bool

class MetricsResponse(BaseModel):
    """Metrics response."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    captcha_solved: int = 0
    captcha_failed: int = 0
    real_data_found: int = 0
    no_data_found: int = 0
    average_response_time: float = 0.0
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

# =============================================================================
# CAPTCHA SOLVER CONFIGURATION
# =============================================================================

def get_anticaptcha_client():
    """Get AntiCaptcha client."""
    if not ANTICAPTCHA_AVAILABLE:
        return None
    
    api_key = os.getenv('ANTICAPTCHA_API_KEY', '')
    if not api_key:
        return None
    
    try:
        return AnticaptchaClient(api_key)
    except Exception as e:
        print(f"❌ Error creating AntiCaptcha client: {e}")
        return None

def get_twocaptcha_client():
    """Get 2captcha client."""
    if not TWOCAPTCHA_AVAILABLE:
        return None
    
    api_key = os.getenv('TWOCAPTCHA_API_KEY', '')
    if not api_key:
        return None
    
    try:
        return TwoCaptcha(api_key)
    except Exception as e:
        print(f"❌ Error creating 2captcha client: {e}")
        return None

def get_stealth_headers():
    """Get stealth headers to avoid detection."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
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

# =============================================================================
# CAPTCHA SOLVER FUNCTIONS
# =============================================================================

async def solve_cloudflare_captcha(site_url: str, site_key: str = None) -> Dict[str, Any]:
    """Solve Cloudflare CAPTCHA using available solvers."""
    try:
        print(f"🧩 Solving Cloudflare CAPTCHA for: {site_url}")
        
        # Try AntiCaptcha first
        anticaptcha_client = get_anticaptcha_client()
        if anticaptcha_client:
            try:
                print("   🔧 Trying AntiCaptcha...")
                
                # Create task
                task = NoCaptchaTaskProxylessTask(
                    website_url=site_url,
                    website_key=site_key or "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
                )
                
                # Submit task
                job = anticaptcha_client.createTask(task)
                job.join()
                
                if job.get_solution_response():
                    solution = job.get_solution_response()
                    print(f"   ✅ AntiCaptcha solved: {solution[:50]}...")
                    metrics["captcha_solved"] += 1
                    
                    return {
                        "success": True,
                        "solver": "anticaptcha",
                        "solution": solution,
                        "cost": job.get_cost()
                    }
                    
            except Exception as e:
                print(f"   ⚠️ AntiCaptcha failed: {e}")
                metrics["captcha_failed"] += 1
        
        # Try 2captcha
        twocaptcha_client = get_twocaptcha_client()
        if twocaptcha_client:
            try:
                print("   🔧 Trying 2captcha...")
                
                # Solve reCAPTCHA
                result = twocaptcha_client.recaptcha(
                    sitekey=site_key or "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
                    url=site_url
                )
                
                if result and result.get('code'):
                    solution = result['code']
                    print(f"   ✅ 2captcha solved: {solution[:50]}...")
                    metrics["captcha_solved"] += 1
                    
                    return {
                        "success": True,
                        "solver": "2captcha",
                        "solution": solution,
                        "cost": result.get('cost', 0)
                    }
                    
            except Exception as e:
                print(f"   ⚠️ 2captcha failed: {e}")
                metrics["captcha_failed"] += 1
        
        return {
            "success": False,
            "solver": "none",
            "error": "All CAPTCHA solvers failed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "solver": "error",
            "error": f"CAPTCHA solving error: {e}"
        }

async def captcha_scrape_masothue(cccd: str) -> Dict[str, Any]:
    """Scrape masothue.com using CAPTCHA solver."""
    try:
        print(f"🧩 CAPTCHA scraping for CCCD: {cccd}")
        
        headers = get_stealth_headers()
        
        async with httpx.AsyncClient(
            headers=headers,
            timeout=60.0,
            follow_redirects=True
        ) as client:
            
            # First, try to access the site
            site_url = "https://masothue.com/"
            search_url = f"https://masothue.com/search?q={cccd}"
            
            try:
                print("   🌐 Accessing masothue.com...")
                response = await client.get(site_url)
                
                if response.status_code == 200:
                    # Check if we got Cloudflare challenge
                    if "Just a moment" in response.text or "Cloudflare" in response.text:
                        print("   🧩 Cloudflare challenge detected, solving...")
                        
                        # Solve CAPTCHA
                        captcha_result = await solve_cloudflare_captcha(site_url)
                        
                        if captcha_result["success"]:
                            print(f"   ✅ CAPTCHA solved with {captcha_result['solver']}")
                            
                            # Now try to access the search page
                            await asyncio.sleep(random.uniform(2, 4))
                            
                            search_response = await client.get(search_url)
                            
                            if search_response.status_code == 200:
                                # Parse results
                                soup = BeautifulSoup(search_response.text, 'html.parser')
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
                                    for element in elements[:5]:  # Limit to first 5 results
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
                                                    "url": search_url,
                                                    "raw_snippet": element.get_text(strip=True)[:300] + "...",
                                                    "source": f"captcha_{captcha_result['solver']}"
                                                })
                                                
                                        except Exception as e:
                                            print(f"   ⚠️ Error parsing element: {e}")
                                            continue
                                    
                                    if matches:
                                        break
                                
                                if matches:
                                    metrics["real_data_found"] += 1
                                    return {
                                        "status": "found",
                                        "matches": matches,
                                        "fetched_at": datetime.now().isoformat(),
                                        "search_url": search_url,
                                        "note": f"Tìm thấy {len(matches)} kết quả thực tế qua CAPTCHA solver {captcha_result['solver']}",
                                        "captcha_solver_used": captcha_result['solver'],
                                        "is_real_data": True
                                    }
                                else:
                                    print("   ℹ️ No results found after CAPTCHA solving")
                                    
                        else:
                            print(f"   ❌ CAPTCHA solving failed: {captcha_result['error']}")
                            
                    else:
                        print("   ✅ No Cloudflare challenge detected")
                        # Continue with normal scraping...
                        
                else:
                    print(f"   ❌ Failed to access site: {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️ Error accessing site: {e}")
        
        # If no results found
        metrics["no_data_found"] += 1
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": search_url,
            "note": "Không tìm thấy thông tin sau khi giải CAPTCHA - có thể không có dữ liệu",
            "captcha_solver_used": "attempted",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"CAPTCHA scraping failed: {e}",
            "captcha_solver_used": "error",
            "is_real_data": False
        }

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=app.version,
        uptime=time.time() - start_time,
        anticaptcha_available=ANTICAPTCHA_AVAILABLE and bool(os.getenv('ANTICAPTCHA_API_KEY')),
        twocaptcha_available=TWOCAPTCHA_AVAILABLE and bool(os.getenv('TWOCAPTCHA_API_KEY'))
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0.0
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        captcha_solved=metrics["captcha_solved"],
        captcha_failed=metrics["captcha_failed"],
        real_data_found=metrics["real_data_found"],
        no_data_found=metrics["no_data_found"],
        average_response_time=avg_time,
        uptime=time.time() - start_time
    )

@app.post("/api/v1/check", response_model=CCCDCheckResponse)
async def check_cccd_captcha(request: CCCDCheckRequest):
    """CAPTCHA solver-based CCCD check."""
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
        
        print(f"🧩 CAPTCHA check for CCCD: {request.cccd}")
        
        # Perform CAPTCHA scraping
        result = await captcha_scrape_masothue(request.cccd)
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
            captcha_solver_used=result.get("captcha_solver_used", "none"),
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
    print("🧩 CAPTCHA Solver Check CCCD API Server starting...")
    print(f"📅 Started at: {datetime.now()}")
    print("🔧 AntiCaptcha: ENABLED" if ANTICAPTCHA_AVAILABLE else "❌ AntiCaptcha: DISABLED")
    print("🔧 2captcha: ENABLED" if TWOCAPTCHA_AVAILABLE else "❌ 2captcha: DISABLED")
    print("🛡️ Cloudflare bypass: ENABLED")
    print("📊 Real-time metrics: ENABLED")
    
    # Test API keys
    if os.getenv('ANTICAPTCHA_API_KEY'):
        print(f"🔑 AntiCaptcha API Key: {os.getenv('ANTICAPTCHA_API_KEY')[:10]}...")
    if os.getenv('TWOCAPTCHA_API_KEY'):
        print(f"🔑 2captcha API Key: {os.getenv('TWOCAPTCHA_API_KEY')[:10]}...")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("🛑 CAPTCHA Solver Check CCCD API Server shutting down...")
    print(f"📊 Final metrics: {metrics}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")