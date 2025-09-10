#!/usr/bin/env python3
"""
Proxy-based Check CCCD API Server
=================================

API server sử dụng proxy rotation để bypass Cloudflare và lấy dữ liệu thực tế.

Author: AI Assistant
Date: 2025-09-08
Version: 7.0.0-proxy
"""

import asyncio
import json
import random
import re
import time
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
import aiohttp
from bs4 import BeautifulSoup
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
    title="Check CCCD API - Proxy Version",
    description="API sử dụng proxy rotation để bypass Cloudflare",
    version="7.0.0-proxy",
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
    "proxy_success": 0,
    "proxy_failed": 0,
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
    use_proxy: bool = Field(default=True, description="Sử dụng proxy")

class CCCDCheckResponse(BaseModel):
    """CCCD check response."""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float
    proxy_used: str = "none"
    is_real_data: bool = False

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    proxy_available: bool

class MetricsResponse(BaseModel):
    """Metrics response."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    proxy_success: int = 0
    proxy_failed: int = 0
    real_data_found: int = 0
    no_data_found: int = 0
    average_response_time: float = 0.0
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

# =============================================================================
# PROXY CONFIGURATION
# =============================================================================

def get_proxy_list():
    """Get list of proxy servers from environment."""
    proxy_list_str = os.getenv('PROXY_LIST', '')
    if not proxy_list_str:
        # Default free proxy servers (in production, use paid proxies)
        return [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "http://proxy3.example.com:8080"
        ]
    
    return [proxy.strip() for proxy in proxy_list_str.split(',') if proxy.strip()]

def get_proxy_auth():
    """Get proxy authentication from environment."""
    username = os.getenv('PROXY_USERNAME', '')
    password = os.getenv('PROXY_PASSWORD', '')
    
    if username and password:
        return (username, password)
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
# PROXY SCRAPING FUNCTIONS
# =============================================================================

async def proxy_scrape_masothue(cccd: str) -> Dict[str, Any]:
    """Scrape masothue.com using proxy rotation."""
    try:
        print(f"🔄 Proxy scraping for CCCD: {cccd}")
        
        proxy_list = get_proxy_list()
        proxy_auth = get_proxy_auth()
        headers = get_stealth_headers()
        
        # Try each proxy
        for proxy_url in proxy_list:
            try:
                print(f"   🔄 Trying proxy: {proxy_url}")
                metrics["proxy_success"] += 1
                
                # Parse proxy URL
                parsed_proxy = urlparse(proxy_url)
                proxy_host = parsed_proxy.hostname
                proxy_port = parsed_proxy.port
                proxy_scheme = parsed_proxy.scheme
                
                # Configure proxy
                proxy_config = {
                    f"{proxy_scheme}://": f"{proxy_scheme}://{proxy_host}:{proxy_port}"
                }
                
                # Add authentication if available
                if proxy_auth:
                    username, password = proxy_auth
                    proxy_config[f"{proxy_scheme}://"] = f"{proxy_scheme}://{username}:{password}@{proxy_host}:{proxy_port}"
                
                # Create HTTP client with proxy
                async with httpx.AsyncClient(
                    headers=headers,
                    proxies=proxy_config,
                    timeout=30.0,
                    follow_redirects=True
                ) as client:
                    
                    # Try different search URLs
                    search_urls = [
                        f"https://masothue.com/search?q={cccd}",
                        f"https://masothue.com/Search/?q={cccd}",
                        f"https://masothue.com/tim-kiem?q={cccd}"
                    ]
                    
                    for search_url in search_urls:
                        try:
                            print(f"   🔍 Trying URL: {search_url}")
                            
                            # Random delay
                            await asyncio.sleep(random.uniform(1, 3))
                            
                            response = await client.get(search_url)
                            
                            if response.status_code == 200:
                                # Check if we got past Cloudflare
                                if "Just a moment" in response.text or "Cloudflare" in response.text:
                                    print(f"   ⚠️ Cloudflare detected on {search_url}")
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
                                                    "source": f"proxy_{proxy_host}"
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
                                        "note": f"Tìm thấy {len(matches)} kết quả thực tế qua proxy {proxy_host}",
                                        "proxy_used": proxy_host,
                                        "is_real_data": True
                                    }
                                else:
                                    print(f"   ℹ️ No results found on {search_url}")
                            
                        except Exception as e:
                            print(f"   ⚠️ Error with URL {search_url}: {e}")
                            continue
                    
            except Exception as e:
                print(f"   ⚠️ Proxy {proxy_url} failed: {e}")
                metrics["proxy_failed"] += 1
                continue
        
        # If all proxies failed
        metrics["no_data_found"] += 1
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "Tất cả proxy đều không thành công - cần cài đặt proxy servers thực tế",
            "proxy_used": "all_failed",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Proxy scraping failed: {e}",
            "proxy_used": "error",
            "is_real_data": False
        }

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Test if proxy is available
    proxy_available = len(get_proxy_list()) > 0
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=app.version,
        uptime=time.time() - start_time,
        proxy_available=proxy_available
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0.0
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        proxy_success=metrics["proxy_success"],
        proxy_failed=metrics["proxy_failed"],
        real_data_found=metrics["real_data_found"],
        no_data_found=metrics["no_data_found"],
        average_response_time=avg_time,
        uptime=time.time() - start_time
    )

@app.post("/api/v1/check", response_model=CCCDCheckResponse)
async def check_cccd_proxy(request: CCCDCheckRequest):
    """Proxy-based CCCD check."""
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
        
        print(f"🔄 Proxy check for CCCD: {request.cccd}")
        
        # Perform proxy scraping
        result = await proxy_scrape_masothue(request.cccd)
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
            proxy_used=result.get("proxy_used", "none"),
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
    print("🔄 Proxy Check CCCD API Server starting...")
    print(f"📅 Started at: {datetime.now()}")
    print("🌐 Proxy rotation: ENABLED")
    print("🛡️ Cloudflare bypass: ENABLED")
    print("📊 Real-time metrics: ENABLED")
    print(f"🔧 Proxy list: {get_proxy_list()}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("🛑 Proxy Check CCCD API Server shutting down...")
    print(f"📊 Final metrics: {metrics}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")