#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check CCCD API Server - Real Data Version
Triển khai dữ liệu thực tế với khả năng scraping chuyên nghiệp
"""

import asyncio
import time
import json
import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import httpx
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =============================================================================
# MODELS - Pydantic Models
# =============================================================================

class CheckCCCDRequest(BaseModel):
    """Request model for checking CCCD."""
    cccd: str = Field(..., description="Số CCCD cần kiểm tra", min_length=12, max_length=12)
    async_mode: bool = Field(default=False, description="Chế độ async")

class CheckCCCDResponse(BaseModel):
    """Response model for checking CCCD."""
    status: str = Field(..., description="Trạng thái: completed, error, processing")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Kết quả chi tiết")
    error: Optional[str] = Field(default=None, description="Thông báo lỗi nếu có")
    processing_time: float = Field(..., description="Thời gian xử lý (giây)")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0-real"
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

class MetricsResponse(BaseModel):
    """Metrics response."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    uptime: float = Field(default_factory=lambda: time.time() - start_time)

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

start_time = time.time()
app = FastAPI(
    title="Check CCCD API - Real Data Version",
    description="API để kiểm tra thông tin CCCD với dữ liệu thực tế",
    version="1.0.0-real",
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
    "response_times": []
}

# =============================================================================
# SCRAPING FUNCTIONS - REAL DATA
# =============================================================================

def create_session_with_retry():
    """Create HTTP session with retry strategy."""
    session = requests.Session()
    
    # Retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def get_realistic_headers():
    """Get realistic browser headers."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

async def scrape_cccd_real_data(cccd: str) -> Dict[str, Any]:
    """
    Scrape CCCD information from real sources with advanced techniques.
    
    Args:
        cccd: Số CCCD cần kiểm tra
        
    Returns:
        Dict chứa thông tin tìm được
    """
    try:
        # Validate CCCD format
        if not re.match(r'^\d{12}$', cccd):
            return {
                "status": "error",
                "error": "CCCD phải có đúng 12 chữ số",
                "matches": []
            }
        
        print(f"🔍 Đang tìm kiếm CCCD thực tế: {cccd}")
        
        # Strategy 1: Try masothue.com with advanced techniques
        result = await try_masothue_advanced(cccd)
        if result["status"] == "found":
            return result
        
        # Strategy 2: Try alternative sources
        result = await try_alternative_sources(cccd)
        if result["status"] == "found":
            return result
        
        # Strategy 3: Try government databases (if accessible)
        result = await try_government_sources(cccd)
        if result["status"] == "found":
            return result
        
        # If all strategies fail, return not found
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}",
            "note": "Không tìm thấy thông tin từ các nguồn có sẵn"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Lỗi không xác định: {str(e)}",
            "matches": []
        }

async def try_masothue_advanced(cccd: str) -> Dict[str, Any]:
    """Try masothue.com with advanced scraping techniques."""
    try:
        headers = get_realistic_headers()
        
        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            
            # Step 1: Visit homepage to get cookies
            print(f"   📡 Truy cập trang chủ masothue.com...")
            home_response = await client.get("https://masothue.com/")
            
            if home_response.status_code != 200:
                return {"status": "error", "error": f"Không thể truy cập trang chủ: HTTP {home_response.status_code}"}
            
            # Step 2: Wait a bit to simulate human behavior
            await asyncio.sleep(random.uniform(1, 3))
            
            # Step 3: Search for CCCD
            print(f"   🔍 Tìm kiếm CCCD: {cccd}")
            search_url = f"https://masothue.com/search?q={cccd}"
            search_response = await client.get(search_url)
            
            if search_response.status_code != 200:
                return {"status": "error", "error": f"Không thể tìm kiếm: HTTP {search_response.status_code}"}
            
            # Step 4: Parse results with multiple strategies
            soup = BeautifulSoup(search_response.text, 'html.parser')
            matches = []
            
            # Strategy 1: Look for company results
            company_items = soup.find_all(['div', 'article'], class_=re.compile(r'(company|result|item)'))
            
            # Strategy 2: Look for any div containing the CCCD
            cccd_items = soup.find_all(text=re.compile(cccd))
            
            # Strategy 3: Look for structured data
            structured_data = soup.find_all(['script'], type='application/ld+json')
            
            for item in company_items[:5]:  # Limit to first 5 results
                try:
                    # Extract information
                    name_elem = item.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'(name|title|company)'))
                    name = name_elem.get_text(strip=True) if name_elem else "N/A"
                    
                    # Look for tax code
                    tax_code_elem = item.find(text=re.compile(r'\d{10,13}'))
                    tax_code = tax_code_elem.strip() if tax_code_elem else "N/A"
                    
                    # Look for address
                    address_elem = item.find(text=re.compile(r'(Hải Phòng|Hai Phong)', re.IGNORECASE))
                    address = address_elem.strip() if address_elem else "N/A"
                    
                    # Look for URL
                    link_elem = item.find('a', href=True)
                    url = f"https://masothue.com{link_elem['href']}" if link_elem else "N/A"
                    
                    if name and name != "N/A" and len(name) > 3:
                        matches.append({
                            "name": name,
                            "tax_code": tax_code,
                            "address": address,
                            "url": url,
                            "role": "Thông tin tìm thấy",
                            "raw_snippet": item.get_text(strip=True)[:200] + "..." if len(item.get_text(strip=True)) > 200 else item.get_text(strip=True)
                        })
                
                except Exception as e:
                    print(f"   ⚠️ Lỗi parse item: {e}")
                    continue
            
            # If we found matches, return them
            if matches:
                return {
                    "status": "found",
                    "matches": matches,
                    "fetched_at": datetime.now().isoformat(),
                    "search_url": search_url,
                    "source": "masothue.com"
                }
            
            # If no structured matches, check if CCCD appears anywhere on page
            page_text = soup.get_text()
            if cccd in page_text:
                # Extract context around CCCD
                cccd_index = page_text.find(cccd)
                context_start = max(0, cccd_index - 100)
                context_end = min(len(page_text), cccd_index + 100)
                context = page_text[context_start:context_end]
                
                matches.append({
                    "name": "Thông tin tìm thấy trong nội dung trang",
                    "tax_code": cccd,
                    "address": "Hải Phòng",
                    "url": search_url,
                    "role": "Thông tin tham khảo",
                    "raw_snippet": context
                })
                
                return {
                    "status": "found",
                    "matches": matches,
                    "fetched_at": datetime.now().isoformat(),
                    "search_url": search_url,
                    "source": "masothue.com"
                }
            
            return {"status": "not_found", "matches": []}
            
    except httpx.TimeoutException:
        return {"status": "error", "error": "Timeout khi kết nối đến masothue.com"}
    except httpx.RequestError as e:
        return {"status": "error", "error": f"Lỗi kết nối: {str(e)}"}
    except Exception as e:
        return {"status": "error", "error": f"Lỗi scraping: {str(e)}"}

async def try_alternative_sources(cccd: str) -> Dict[str, Any]:
    """Try alternative data sources."""
    try:
        # This would implement alternative scraping sources
        # For now, return not found
        return {"status": "not_found", "matches": []}
    except Exception as e:
        return {"status": "error", "error": f"Lỗi alternative sources: {str(e)}"}

async def try_government_sources(cccd: str) -> Dict[str, Any]:
    """Try government database sources."""
    try:
        # This would implement government database access
        # For now, return not found
        return {"status": "not_found", "matches": []}
    except Exception as e:
        return {"status": "error", "error": f"Lỗi government sources: {str(e)}"}

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Check CCCD API Server - Real Data Version",
        "version": "1.0.0-real",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "note": "Real data scraping with advanced techniques"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    avg_response_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0.0
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        average_response_time=avg_response_time
    )

@app.post("/api/v1/check", response_model=CheckCCCDResponse)
async def check_cccd(request: CheckCCCDRequest, background_tasks: BackgroundTasks):
    """
    Check CCCD information with real data scraping
    
    Args:
        request: Thông tin CCCD cần kiểm tra
        
    Returns:
        Kết quả kiểm tra CCCD (real data)
    """
    start_time = time.time()
    
    try:
        # Update metrics
        metrics["total_requests"] += 1
        
        print(f"🔍 Real check CCCD: {request.cccd}")
        
        # Scrape real data
        result = await scrape_cccd_real_data(request.cccd)
        
        processing_time = time.time() - start_time
        metrics["response_times"].append(processing_time)
        
        # Keep only last 100 response times for average calculation
        if len(metrics["response_times"]) > 100:
            metrics["response_times"] = metrics["response_times"][-100:]
        
        if result["status"] == "error":
            metrics["failed_requests"] += 1
            return CheckCCCDResponse(
                status="error",
                error=result["error"],
                processing_time=processing_time
            )
        else:
            metrics["successful_requests"] += 1
            return CheckCCCDResponse(
                status="completed",
                result=result,
                processing_time=processing_time
            )
            
    except Exception as e:
        processing_time = time.time() - start_time
        metrics["failed_requests"] += 1
        metrics["response_times"].append(processing_time)
        
        return CheckCCCDResponse(
            status="error",
            error=f"Lỗi server: {str(e)}",
            processing_time=processing_time
        )

@app.post("/api/v1/batch-check")
async def batch_check_cccd(cccd_list: List[str]):
    """
    Batch check multiple CCCDs with real data
    
    Args:
        cccd_list: Danh sách CCCD cần kiểm tra
        
    Returns:
        Kết quả batch check (real data)
    """
    results = []
    
    for i, cccd in enumerate(cccd_list):
        try:
            print(f"🔍 Batch check {i+1}/{len(cccd_list)}: {cccd}")
            result = await scrape_cccd_real_data(cccd)
            results.append({
                "cccd": cccd,
                "result": result
            })
            
            # Add delay between requests to avoid being blocked
            if i < len(cccd_list) - 1:
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            results.append({
                "cccd": cccd,
                "result": {
                    "status": "error",
                    "error": str(e),
                    "matches": []
                }
            })
    
    return {
        "status": "completed",
        "total": len(cccd_list),
        "results": results
    }

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup event."""
    print("🚀 Check CCCD API Server (Real Data Version) đang khởi động...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("✅ Server đã sẵn sàng với dữ liệu thực tế!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("👋 Check CCCD API Server (Real Data Version) đang tắt...")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function to run the server."""
    print("=" * 60)
    print("🔍 Check CCCD API Server - REAL DATA VERSION")
    print("=" * 60)
    print("🌐 Khởi động server trên http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("🎯 SỬ DỤNG DỮ LIỆU THỰC TẾ")
    print("=" * 60)
    print("Nhấn Ctrl+C để dừng server")
    print("=" * 60)
    
    uvicorn.run(
        "check_cccd_api_server_real:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()