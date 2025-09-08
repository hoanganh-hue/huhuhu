#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check CCCD API Server - Mock Version for Demo
Tạo dữ liệu giả để demo hệ thống hoạt động
"""

import asyncio
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

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
    version: str = "1.0.0-mock"
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
    title="Check CCCD API - Mock Version",
    description="API để kiểm tra thông tin CCCD - Mock data for demo",
    version="1.0.0-mock",
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

# Mock data for demo
MOCK_NAMES = [
    "Nguyễn Thị Hoa", "Trần Thị Lan", "Lê Thị Mai", "Phạm Thị Hương",
    "Hoàng Thị Nga", "Vũ Thị Thu", "Đặng Thị Linh", "Bùi Thị Hạnh",
    "Đỗ Thị Quỳnh", "Ngô Thị Thảo", "Dương Thị Hồng", "Lý Thị Bích",
    "Tôn Thị Ngọc", "Đinh Thị Yến", "Võ Thị Trang", "Phan Thị Minh"
]

MOCK_COMPANIES = [
    "Công ty TNHH Thương mại", "Công ty Cổ phần Sản xuất", 
    "Doanh nghiệp Tư nhân", "Công ty TNHH Dịch vụ",
    "Công ty Cổ phần Xây dựng", "Công ty TNHH Nông nghiệp"
]

MOCK_ADDRESSES = [
    "Hải Phòng", "Quận Hồng Bàng, Hải Phòng", "Quận Ngô Quyền, Hải Phòng",
    "Quận Lê Chân, Hải Phòng", "Quận Hải An, Hải Phòng", "Quận Kiến An, Hải Phòng"
]

# =============================================================================
# MOCK FUNCTIONS
# =============================================================================

def generate_mock_cccd_data(cccd: str) -> Dict[str, Any]:
    """Generate mock CCCD data for demo."""
    
    # Simulate some CCCDs having data (30% chance)
    if random.random() < 0.3:
        name = random.choice(MOCK_NAMES)
        company = random.choice(MOCK_COMPANIES)
        address = random.choice(MOCK_ADDRESSES)
        tax_code = f"MST{cccd[:8]}"
        
        matches = [{
            "name": name,
            "tax_code": tax_code,
            "address": f"{address}",
            "url": f"https://masothue.com/{tax_code}",
            "role": "Giám đốc" if random.random() < 0.2 else "Nhân viên",
            "raw_snippet": f"{name} - {company} - {address}"
        }]
        
        return {
            "status": "found",
            "matches": matches,
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}"
        }
    else:
        return {
            "status": "not_found",
            "matches": [],
            "fetched_at": datetime.now().isoformat(),
            "search_url": f"https://masothue.com/search?q={cccd}"
        }

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Check CCCD API Server - Mock Version",
        "version": "1.0.0-mock",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "note": "This is a mock version for demo purposes"
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
    Check CCCD information - Mock version
    
    Args:
        request: Thông tin CCCD cần kiểm tra
        
    Returns:
        Kết quả kiểm tra CCCD (mock data)
    """
    start_time = time.time()
    
    try:
        # Update metrics
        metrics["total_requests"] += 1
        
        print(f"🔍 Mock check CCCD: {request.cccd}")
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Generate mock data
        result = generate_mock_cccd_data(request.cccd)
        
        processing_time = time.time() - start_time
        metrics["response_times"].append(processing_time)
        
        # Keep only last 100 response times for average calculation
        if len(metrics["response_times"]) > 100:
            metrics["response_times"] = metrics["response_times"][-100:]
        
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
    Batch check multiple CCCDs - Mock version
    
    Args:
        cccd_list: Danh sách CCCD cần kiểm tra
        
    Returns:
        Kết quả batch check (mock data)
    """
    results = []
    
    for cccd in cccd_list:
        try:
            result = generate_mock_cccd_data(cccd)
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
    print("🚀 Check CCCD API Server (Mock Version) đang khởi động...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("⚠️  Đây là phiên bản MOCK cho demo - dữ liệu không thật")
    print("✅ Server đã sẵn sàng!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    print("👋 Check CCCD API Server (Mock Version) đang tắt...")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function to run the server."""
    print("=" * 60)
    print("🔍 Check CCCD API Server - MOCK VERSION")
    print("=" * 60)
    print("🌐 Khởi động server trên http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("⚠️  ĐÂY LÀ PHIÊN BẢN MOCK CHO DEMO")
    print("=" * 60)
    print("Nhấn Ctrl+C để dừng server")
    print("=" * 60)
    
    uvicorn.run(
        "check_cccd_api_server_mock:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()