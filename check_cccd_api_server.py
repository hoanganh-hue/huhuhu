#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check CCCD API Server - Simple FastAPI Implementation
Khắc phục lỗi hệ thống không thể kết nối đến API server
"""

import asyncio
import time
import json
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
    version: str = "1.0.0"
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
    title="Check CCCD API",
    description="API để kiểm tra thông tin CCCD từ masothue.com",
    version="1.0.0",
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
# SCRAPING FUNCTIONS
# =============================================================================

async def scrape_cccd_from_masothue(cccd: str) -> Dict[str, Any]:
    """
    Scrape CCCD information from masothue.com
    
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
        
        # Headers để giả lập browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True
        ) as client:
            
            # Bước 1: Truy cập trang chủ để lấy session
            print(f"🔍 Đang truy cập trang chủ masothue.com...")
            home_response = await client.get("https://masothue.com/")
            
            if home_response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Không thể truy cập trang chủ: HTTP {home_response.status_code}",
                    "matches": []
                }
            
            # Bước 2: Tìm kiếm CCCD
            print(f"🔍 Đang tìm kiếm CCCD: {cccd}")
            search_url = f"https://masothue.com/search?q={cccd}"
            search_response = await client.get(search_url)
            
            if search_response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Không thể tìm kiếm: HTTP {search_response.status_code}",
                    "matches": []
                }
            
            # Bước 3: Parse kết quả
            soup = BeautifulSoup(search_response.text, 'html.parser')
            matches = []
            
            # Tìm các kết quả tìm kiếm
            result_items = soup.find_all('div', class_='search-result-item')
            
            if not result_items:
                # Thử tìm với selector khác
                result_items = soup.find_all('div', class_='company-item')
            
            if not result_items:
                # Thử tìm với selector khác nữa
                result_items = soup.find_all('div', class_='result-item')
            
            for item in result_items:
                try:
                    # Extract thông tin từ mỗi item
                    name_elem = item.find('h3') or item.find('h2') or item.find('a', class_='company-name')
                    name = name_elem.get_text(strip=True) if name_elem else "N/A"
                    
                    # Tìm mã số thuế
                    tax_code_elem = item.find('span', class_='tax-code') or item.find('div', class_='tax-code')
                    tax_code = tax_code_elem.get_text(strip=True) if tax_code_elem else "N/A"
                    
                    # Tìm địa chỉ
                    address_elem = item.find('div', class_='address') or item.find('span', class_='address')
                    address = address_elem.get_text(strip=True) if address_elem else "N/A"
                    
                    # Tìm URL
                    link_elem = item.find('a', href=True)
                    url = f"https://masothue.com{link_elem['href']}" if link_elem else "N/A"
                    
                    # Tìm chức vụ/role
                    role_elem = item.find('span', class_='role') or item.find('div', class_='role')
                    role = role_elem.get_text(strip=True) if role_elem else "N/A"
                    
                    if name and name != "N/A":
                        matches.append({
                            "name": name,
                            "tax_code": tax_code,
                            "address": address,
                            "url": url,
                            "role": role,
                            "raw_snippet": item.get_text(strip=True)[:200] + "..." if len(item.get_text(strip=True)) > 200 else item.get_text(strip=True)
                        })
                
                except Exception as e:
                    print(f"⚠️ Lỗi parse item: {e}")
                    continue
            
            # Nếu không tìm thấy kết quả cụ thể, thử tìm trong toàn bộ page
            if not matches:
                page_text = soup.get_text()
                if cccd in page_text:
                    # Có thể có thông tin nhưng không parse được
                    matches.append({
                        "name": "Thông tin tìm thấy nhưng không parse được",
                        "tax_code": "N/A",
                        "address": "N/A", 
                        "url": search_url,
                        "role": "N/A",
                        "raw_snippet": page_text[:500] + "..." if len(page_text) > 500 else page_text
                    })
            
            return {
                "status": "found" if matches else "not_found",
                "matches": matches,
                "fetched_at": datetime.now().isoformat(),
                "search_url": search_url
            }
            
    except httpx.TimeoutException:
        return {
            "status": "error",
            "error": "Timeout khi kết nối đến masothue.com",
            "matches": []
        }
    except httpx.RequestError as e:
        return {
            "status": "error", 
            "error": f"Lỗi kết nối: {str(e)}",
            "matches": []
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Lỗi không xác định: {str(e)}",
            "matches": []
        }

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Check CCCD API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
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
    Check CCCD information from masothue.com
    
    Args:
        request: Thông tin CCCD cần kiểm tra
        
    Returns:
        Kết quả kiểm tra CCCD
    """
    start_time = time.time()
    
    try:
        # Update metrics
        metrics["total_requests"] += 1
        
        print(f"🔍 Nhận request check CCCD: {request.cccd}")
        
        # Scrape thông tin
        result = await scrape_cccd_from_masothue(request.cccd)
        
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
    Batch check multiple CCCDs
    
    Args:
        cccd_list: Danh sách CCCD cần kiểm tra
        
    Returns:
        Kết quả batch check
    """
    results = []
    
    for cccd in cccd_list:
        try:
            result = await scrape_cccd_from_masothue(cccd)
            results.append({
                "cccd": cccd,
                "result": result
            })
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
    print("🚀 Check CCCD API Server đang khởi động...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("✅ Server đã sẵn sàng!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("👋 Check CCCD API Server đang tắt...")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function to run the server."""
    print("=" * 60)
    print("🔍 Check CCCD API Server")
    print("=" * 60)
    print("🌐 Khởi động server trên http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("=" * 60)
    print("Nhấn Ctrl+C để dừng server")
    print("=" * 60)
    
    uvicorn.run(
        "check_cccd_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()