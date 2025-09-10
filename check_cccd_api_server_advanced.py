#!/usr/bin/env python3
"""
Advanced Check CCCD API Server with Cloudflare Bypass
====================================================

API server để kiểm tra thông tin CCCD với khả năng bypass Cloudflare
và sử dụng đúng format URL tìm kiếm.

Author: AI Assistant
Date: 2025-09-08
Version: 2.0.0-advanced
"""

import asyncio
import json
import random
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

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
    title="Check CCCD API - Advanced Version",
    description="API để kiểm tra thông tin CCCD với khả năng bypass Cloudflare",
    version="2.0.0-advanced",
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
    "cloudflare_bypass_attempts": 0,
    "cloudflare_bypass_success": 0,
    "response_times": []
}

# =============================================================================
# DATA MODELS
# =============================================================================

class CCCDCheckRequest(BaseModel):
    """CCCD check request."""
    cccd: str = Field(..., min_length=12, max_length=12, description="Số CCCD 12 chữ số")
    async_mode: bool = Field(default=False, description="Chế độ async")
    bypass_cloudflare: bool = Field(default=True, description="Bypass Cloudflare protection")

class CCCDCheckResponse(BaseModel):
    """CCCD check response."""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float
    cloudflare_bypassed: bool = False

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    cloudflare_status: str

class MetricsResponse(BaseModel):
    """Metrics response."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cloudflare_bypass_attempts: int = 0
    cloudflare_bypass_success: int = 0
    average_response_time: float = 0.0
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

# =============================================================================
# CLOUDFLARE BYPASS FUNCTIONS
# =============================================================================

def get_advanced_headers():
    """Get advanced headers to bypass Cloudflare."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        'Sec-GPC': '1'
    }

def generate_search_token():
    """Generate a search token for masothue.com."""
    # This is a simplified token generation
    # In real implementation, you might need to extract this from the homepage
    return "shDrRznWij"

async def bypass_cloudflare_challenge(client: httpx.AsyncClient, url: str) -> bool:
    """Attempt to bypass Cloudflare challenge."""
    try:
        metrics["cloudflare_bypass_attempts"] += 1
        
        # Try different approaches
        approaches = [
            # Approach 1: Wait and retry
            lambda: asyncio.sleep(random.uniform(5, 10)),
            
            # Approach 2: Use different headers
            lambda: client.headers.update(get_advanced_headers()),
            
            # Approach 3: Simulate browser behavior
            lambda: asyncio.sleep(random.uniform(2, 5))
        ]
        
        for approach in approaches:
            await approach()
            
            response = await client.get(url)
            if response.status_code == 200 and "Just a moment" not in response.text:
                metrics["cloudflare_bypass_success"] += 1
                return True
                
        return False
        
    except Exception as e:
        print(f"❌ Cloudflare bypass failed: {e}")
        return False

# =============================================================================
# SCRAPING FUNCTIONS
# =============================================================================

async def scrape_masothue_advanced(cccd: str, bypass_cf: bool = True) -> Dict[str, Any]:
    """Advanced scraping from masothue.com with Cloudflare bypass."""
    try:
        print(f"🔍 Advanced scraping for CCCD: {cccd}")
        
        headers = get_advanced_headers()
        
        async with httpx.AsyncClient(
            headers=headers,
            timeout=60.0,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            
            # Step 1: Try the correct search URL format
            search_url = f"https://masothue.com/Search/?q={cccd}&type=auto&token={generate_search_token()}&force-search=1"
            print(f"   📡 Trying advanced search URL: {search_url}")
            
            # Step 2: Attempt to bypass Cloudflare if enabled
            if bypass_cf:
                print("   🛡️ Attempting Cloudflare bypass...")
                if await bypass_cloudflare_challenge(client, search_url):
                    print("   ✅ Cloudflare bypass successful!")
                else:
                    print("   ⚠️ Cloudflare bypass failed, trying direct access...")
            
            # Step 3: Make the request
            response = await client.get(search_url)
            
            if response.status_code == 200:
                # Check if we got past Cloudflare
                if "Just a moment" in response.text:
                    return {
                        "status": "cloudflare_blocked",
                        "matches": [],
                        "fetched_at": datetime.now().isoformat(),
                        "search_url": search_url,
                        "note": "Bị chặn bởi Cloudflare protection. Cần giải pháp bypass nâng cao hơn."
                    }
                
                # Parse the response
                soup = BeautifulSoup(response.text, 'html.parser')
                matches = []
                
                # Look for company information
                company_divs = soup.find_all('div', class_=re.compile(r'(company|result|item|search-result)'))
                
                for div in company_divs[:5]:  # Limit to first 5 results
                    try:
                        # Extract company name
                        name_elem = div.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'(name|title|company)'))
                        name = name_elem.get_text(strip=True) if name_elem else "N/A"
                        
                        # Extract tax code
                        tax_elem = div.find(['span', 'div'], class_=re.compile(r'(tax|code|mst)'))
                        tax_code = tax_elem.get_text(strip=True) if tax_elem else "N/A"
                        
                        # Extract address
                        addr_elem = div.find(['p', 'div', 'span'], class_=re.compile(r'(address|diachi|location)'))
                        address = addr_elem.get_text(strip=True) if addr_elem else "N/A"
                        
                        # Extract role
                        role_elem = div.find(['span', 'div'], class_=re.compile(r'(role|chucvu|position)'))
                        role = role_elem.get_text(strip=True) if role_elem else "N/A"
                        
                        if name != "N/A" and tax_code != "N/A":
                            matches.append({
                                "name": name,
                                "tax_code": tax_code,
                                "address": address,
                                "role": role,
                                "url": search_url,
                                "raw_snippet": div.get_text(strip=True)[:200] + "..."
                            })
                            
                    except Exception as e:
                        print(f"   ⚠️ Error parsing company div: {e}")
                        continue
                
                if matches:
                    return {
                        "status": "found",
                        "matches": matches,
                        "fetched_at": datetime.now().isoformat(),
                        "search_url": search_url,
                        "note": f"Tìm thấy {len(matches)} kết quả từ masothue.com"
                    }
                else:
                    return {
                        "status": "not_found",
                        "matches": [],
                        "fetched_at": datetime.now().isoformat(),
                        "search_url": search_url,
                        "note": "Không tìm thấy thông tin từ masothue.com"
                    }
            else:
                return {
                    "status": "error",
                    "matches": [],
                    "fetched_at": datetime.now().isoformat(),
                    "search_url": search_url,
                    "note": f"Lỗi HTTP: {response.status_code}",
                    "error": f"HTTP {response.status_code}"
                }
                
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            return {
                "status": "cloudflare_blocked",
                "matches": [],
                "fetched_at": datetime.now().isoformat(),
                "search_url": search_url,
                "note": "Bị chặn bởi Cloudflare (HTTP 403). Cần giải pháp bypass nâng cao hơn.",
                "error": str(e)
            }
        return {
            "status": "error",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": search_url,
            "note": f"Lỗi HTTP: {e.response.status_code}",
            "error": str(e)
        }
    except httpx.RequestError as e:
        return {
            "status": "error",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": search_url,
            "note": f"Lỗi kết nối: {e}",
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": search_url,
            "note": f"Lỗi không xác định: {e}",
            "error": str(e)
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
        cloudflare_status="bypass_available"
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0.0
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        cloudflare_bypass_attempts=metrics["cloudflare_bypass_attempts"],
        cloudflare_bypass_success=metrics["cloudflare_bypass_success"],
        average_response_time=avg_time,
        uptime=time.time() - start_time
    )

@app.post("/api/v1/check", response_model=CCCDCheckResponse)
async def check_cccd_advanced(request: CCCDCheckRequest):
    """Advanced CCCD check with Cloudflare bypass."""
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
        
        print(f"🔍 Advanced check for CCCD: {request.cccd}")
        
        # Perform advanced scraping
        result = await scrape_masothue_advanced(request.cccd, request.bypass_cloudflare)
        processing_time = time.time() - start_time
        
        # Update metrics
        if result.get("status") == "error":
            metrics["failed_requests"] += 1
        else:
            metrics["successful_requests"] += 1
        
        metrics["response_times"].append(processing_time)
        
        # Check if Cloudflare was bypassed
        cloudflare_bypassed = result.get("status") not in ["cloudflare_blocked", "error"]
        
        return CCCDCheckResponse(
            status="completed",
            result=result,
            error=result.get("error"),
            processing_time=processing_time,
            cloudflare_bypassed=cloudflare_bypassed
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
    print("🚀 Advanced Check CCCD API Server starting...")
    print(f"📅 Started at: {datetime.now()}")
    print("🛡️ Cloudflare bypass: ENABLED")
    print("🔧 Advanced scraping: ENABLED")
    print("📊 Metrics tracking: ENABLED")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("🛑 Advanced Check CCCD API Server shutting down...")
    print(f"📊 Final metrics: {metrics}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")