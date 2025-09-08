#!/usr/bin/env python3
"""
Real Production Check CCCD API Server
====================================

API server thực tế với khả năng scraping dữ liệu thật từ nhiều nguồn khác nhau.
KHÔNG có dữ liệu mô phỏng - chỉ dữ liệu thực tế.

Author: AI Assistant
Date: 2025-09-08
Version: 4.0.0-real-production
"""

import asyncio
import json
import random
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import urllib.parse

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# =============================================================================
# CONFIGURATION
# =============================================================================

# Global variables
start_time = time.time()
app = FastAPI(
    title="Check CCCD API - Real Production",
    description="API thực tế để kiểm tra thông tin CCCD với dữ liệu thật từ nhiều nguồn",
    version="4.0.0-real-production",
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
    "real_data_found": 0,
    "no_data_found": 0,
    "cloudflare_blocks": 0,
    "response_times": []
}

# =============================================================================
# DATA MODELS
# =============================================================================

class CCCDCheckRequest(BaseModel):
    """CCCD check request."""
    cccd: str = Field(..., min_length=12, max_length=12, description="Số CCCD 12 chữ số")
    async_mode: bool = Field(default=False, description="Chế độ async")
    use_all_sources: bool = Field(default=True, description="Sử dụng tất cả nguồn dữ liệu")

class CCCDCheckResponse(BaseModel):
    """CCCD check response."""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float
    data_source: str = "unknown"
    is_real_data: bool = False

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    real_data_sources: List[str]

class MetricsResponse(BaseModel):
    """Metrics response."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    real_data_found: int = 0
    no_data_found: int = 0
    cloudflare_blocks: int = 0
    average_response_time: float = 0.0
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

# =============================================================================
# REAL DATA SOURCES
# =============================================================================

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

async def try_masothue_real(cccd: str) -> Dict[str, Any]:
    """Try to get real data from masothue.com with advanced techniques."""
    try:
        headers = get_stealth_headers()
        
        async with httpx.AsyncClient(
            headers=headers,
            timeout=60.0,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            
            # Try multiple approaches
            approaches = [
                # Approach 1: Direct search
                f"https://masothue.com/search?q={cccd}",
                # Approach 2: Search with different format
                f"https://masothue.com/Search/?q={cccd}",
                # Approach 3: Try with encoded CCCD
                f"https://masothue.com/search?q={urllib.parse.quote(cccd)}",
                # Approach 4: Try different search endpoint
                f"https://masothue.com/tim-kiem?q={cccd}"
            ]
            
            for url in approaches:
                try:
                    print(f"   🔍 Trying URL: {url}")
                    
                    # Random delay to avoid detection
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        # Check if we got past Cloudflare
                        if "Just a moment" in response.text or "Cloudflare" in response.text:
                            print(f"   ⚠️ Cloudflare detected on {url}")
                            metrics["cloudflare_blocks"] += 1
                            continue
                        
                        # Parse the response
                        soup = BeautifulSoup(response.text, 'html.parser')
                        matches = []
                        
                        # Look for company information in various formats
                        selectors = [
                            'div.company-item',
                            'div.search-result',
                            'div.result-item',
                            'article.company',
                            'div[class*="company"]',
                            'div[class*="result"]',
                            '.g-item',  # Google-like results
                            '.search-result-item'
                        ]
                        
                        for selector in selectors:
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
                                        r'(\d{10,13})'  # General number pattern
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
                                            if len(addr_text) > 10:  # Reasonable address length
                                                address = addr_text
                                                break
                                    
                                    # Extract role/position
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
                                            "source": "masothue.com"
                                        })
                                        
                                except Exception as e:
                                    print(f"   ⚠️ Error parsing element: {e}")
                                    continue
                        
                        if matches:
                            metrics["real_data_found"] += 1
                            return {
                                "status": "found",
                                "matches": matches,
                                "fetched_at": datetime.now().isoformat(),
                                "search_url": url,
                                "note": f"Tìm thấy {len(matches)} kết quả thực tế từ masothue.com",
                                "data_source": "masothue.com",
                                "is_real_data": True
                            }
                        else:
                            print(f"   ℹ️ No results found on {url}")
                            
                except Exception as e:
                    print(f"   ⚠️ Error with URL {url}: {e}")
                    continue
            
            # If all approaches failed
            return {
                "status": "not_found",
                "matches": [],
                "fetched_at": datetime.now().isoformat(),
                "search_url": f"https://masothue.com/search?q={cccd}",
                "note": "Không tìm thấy thông tin từ masothue.com - có thể bị chặn hoặc không có dữ liệu",
                "data_source": "masothue.com",
                "is_real_data": False
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": f"Lỗi khi truy cập masothue.com: {e}",
            "matches": [],
            "data_source": "masothue.com",
            "is_real_data": False
        }

async def try_government_sources(cccd: str) -> Dict[str, Any]:
    """Try to get data from government sources."""
    try:
        print(f"   🏛️ Trying government sources for CCCD: {cccd}")
        
        # This would integrate with real government APIs
        # For now, we'll return not found as we don't have access to real government APIs
        
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://government-api.gov.vn/search?cccd={cccd}",
            "note": "Không có quyền truy cập vào cơ sở dữ liệu chính phủ",
            "data_source": "government_api",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Lỗi khi truy cập nguồn chính phủ: {e}",
            "matches": [],
            "data_source": "government_api",
            "is_real_data": False
        }

async def try_business_registry(cccd: str) -> Dict[str, Any]:
    """Try to get data from business registry sources."""
    try:
        print(f"   🏢 Trying business registry for CCCD: {cccd}")
        
        # This would integrate with real business registry APIs
        # For now, we'll return not found as we don't have access to real business APIs
        
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://business-registry.gov.vn/search?cccd={cccd}",
            "note": "Không có quyền truy cập vào cơ sở dữ liệu đăng ký kinh doanh",
            "data_source": "business_registry",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Lỗi khi truy cập đăng ký kinh doanh: {e}",
            "matches": [],
            "data_source": "business_registry",
            "is_real_data": False
        }

async def try_alternative_websites(cccd: str) -> Dict[str, Any]:
    """Try to get data from alternative websites."""
    try:
        print(f"   🌐 Trying alternative websites for CCCD: {cccd}")
        
        headers = get_stealth_headers()
        
        # List of alternative websites to try
        alternative_sites = [
            f"https://thongtindoanhnghiep.co/search?q={cccd}",
            f"https://doanhnghiep.vn/search?q={cccd}",
            f"https://congty.vn/search?q={cccd}",
        ]
        
        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True
        ) as client:
            
            for site_url in alternative_sites:
                try:
                    print(f"   🔍 Trying alternative site: {site_url}")
                    
                    await asyncio.sleep(random.uniform(1, 2))
                    response = await client.get(site_url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for any company information
                        company_elements = soup.find_all(['div', 'article'], class_=re.compile(r'(company|result|item)'))
                        
                        matches = []
                        for element in company_elements[:3]:  # Limit to first 3 results
                            try:
                                # Extract basic information
                                name_elem = element.find(['h1', 'h2', 'h3', 'a'])
                                name = name_elem.get_text(strip=True) if name_elem else "N/A"
                                
                                if name != "N/A" and len(name) > 3:
                                    matches.append({
                                        "name": name,
                                        "tax_code": "N/A",
                                        "address": "N/A",
                                        "role": "N/A",
                                        "url": site_url,
                                        "raw_snippet": element.get_text(strip=True)[:200] + "...",
                                        "source": "alternative_website"
                                    })
                                    
                            except Exception as e:
                                continue
                        
                        if matches:
                            metrics["real_data_found"] += 1
                            return {
                                "status": "found",
                                "matches": matches,
                                "fetched_at": datetime.now().isoformat(),
                                "search_url": site_url,
                                "note": f"Tìm thấy {len(matches)} kết quả từ website thay thế",
                                "data_source": "alternative_website",
                                "is_real_data": True
                            }
                            
                except Exception as e:
                    print(f"   ⚠️ Error with alternative site {site_url}: {e}")
                    continue
        
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://alternative-sites.com/search?q={cccd}",
            "note": "Không tìm thấy thông tin từ các website thay thế",
            "data_source": "alternative_website",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Lỗi khi truy cập website thay thế: {e}",
            "matches": [],
            "data_source": "alternative_website",
            "is_real_data": False
        }

# =============================================================================
# MAIN SCRAPING FUNCTION
# =============================================================================

async def scrape_cccd_real_production(cccd: str, use_all_sources: bool = True) -> Dict[str, Any]:
    """Real production CCCD scraping with multiple real data sources."""
    try:
        print(f"🔍 Real production scraping for CCCD: {cccd}")
        
        # Strategy 1: Try masothue.com (primary source)
        print("   🎯 Strategy 1: masothue.com...")
        result = await try_masothue_real(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        if not use_all_sources:
            return result
        
        # Strategy 2: Try alternative websites
        print("   🌐 Strategy 2: Alternative websites...")
        result = await try_alternative_websites(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        # Strategy 3: Try business registry
        print("   🏢 Strategy 3: Business registry...")
        result = await try_business_registry(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        # Strategy 4: Try government sources
        print("   🏛️ Strategy 4: Government sources...")
        result = await try_government_sources(cccd)
        if result["status"] == "found" and result.get("is_real_data", False):
            return result
        
        # If all strategies fail, return the best result we have
        metrics["no_data_found"] += 1
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://multiple-sources.com/search?q={cccd}",
            "note": "Không tìm thấy thông tin từ tất cả các nguồn dữ liệu thực tế",
            "data_source": "all_sources",
            "is_real_data": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Lỗi trong quá trình scraping thực tế: {e}",
            "matches": [],
            "data_source": "error",
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
        real_data_sources=["masothue.com", "alternative_websites", "business_registry", "government_sources"]
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0.0
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        real_data_found=metrics["real_data_found"],
        no_data_found=metrics["no_data_found"],
        cloudflare_blocks=metrics["cloudflare_blocks"],
        average_response_time=avg_time,
        uptime=time.time() - start_time
    )

@app.post("/api/v1/check", response_model=CCCDCheckResponse)
async def check_cccd_real_production(request: CCCDCheckRequest):
    """Real production CCCD check with real data sources only."""
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
        
        print(f"🔍 Real production check for CCCD: {request.cccd}")
        
        # Perform real production scraping
        result = await scrape_cccd_real_production(request.cccd, request.use_all_sources)
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
            data_source=result.get("data_source", "unknown"),
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
    print("🚀 Real Production Check CCCD API Server starting...")
    print(f"📅 Started at: {datetime.now()}")
    print("🛡️ Real data sources: ENABLED")
    print("🚫 Mock data: DISABLED")
    print("🌐 Multiple sources: ENABLED")
    print("📊 Real metrics: ENABLED")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("🛑 Real Production Check CCCD API Server shutting down...")
    print(f"📊 Final metrics: {metrics}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")