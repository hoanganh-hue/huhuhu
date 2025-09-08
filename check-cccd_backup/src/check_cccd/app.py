#!/usr/bin/env python3
"""
FastAPI application for Check CCCD API
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import logging

from .config import Settings
from .scraper import scrape_cccd_sync
from .store import Store
from .logging import logger, metrics

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="Check CCCD API",
    description="API để tra cứu thông tin CCCD từ masothue.com",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store
store = Store(settings.database_url)

# Request/Response models
class CCCDCheckRequest(BaseModel):
    cccd: str
    async_mode: bool = False

class CCCDCheckResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime: float

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting Check CCCD API")
    await store.initialize()
    logger.info("✅ Check CCCD API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Check CCCD API")
    await store.close()

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        uptime=0.0  # Simplified for now
    )

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return {
        "requests_total": metrics.get_counter("requests_total"),
        "errors_total": metrics.get_counter("errors_total"),
        "scraping_requests_total": metrics.get_counter("scraping_requests_total"),
        "scraping_errors_total": metrics.get_counter("scraping_errors_total")
    }

# Main check endpoint
@app.post("/api/v1/check", response_model=CCCDCheckResponse)
async def check_cccd(request: CCCDCheckRequest, background_tasks: BackgroundTasks):
    """Check CCCD information"""
    
    # Validate CCCD format
    if not request.cccd or len(request.cccd) != 12 or not request.cccd.isdigit():
        raise HTTPException(
            status_code=400,
            detail="CCCD phải có 12 chữ số"
        )
    
    # Update metrics
    metrics.increment_counter("requests_total")
    
    try:
        if request.async_mode:
            # Async mode - return immediately with request ID
            request_id = f"req_{datetime.utcnow().timestamp()}"
            background_tasks.add_task(process_cccd_async, request.cccd, request_id)
            
            return CCCDCheckResponse(
                status="accepted",
                request_id=request_id
            )
        else:
            # Sync mode - process immediately
            result = await process_cccd_sync(request.cccd)
            return CCCDCheckResponse(
                status="completed",
                result=result
            )
            
    except Exception as e:
        metrics.increment_counter("errors_total")
        logger.error(f"Error checking CCCD {request.cccd}: {str(e)}")
        
        return CCCDCheckResponse(
            status="error",
            error=str(e)
        )

async def process_cccd_sync(cccd: str) -> Dict[str, Any]:
    """Process CCCD synchronously"""
    try:
        # Check cache first
        cached_result = await store.get_cached_result(cccd)
        if cached_result:
            logger.info(f"Cache hit for CCCD {cccd}")
            return cached_result
        
        # Scrape from masothue.com
        logger.info(f"Scraping CCCD {cccd}")
        result = scrape_cccd_sync(cccd)
        
        # Cache the result
        await store.cache_result(cccd, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing CCCD {cccd}: {str(e)}")
        raise

async def process_cccd_async(cccd: str, request_id: str):
    """Process CCCD asynchronously"""
    try:
        result = await process_cccd_sync(cccd)
        await store.store_async_result(request_id, result)
        logger.info(f"Async processing completed for request {request_id}")
    except Exception as e:
        logger.error(f"Async processing failed for request {request_id}: {str(e)}")
        await store.store_async_result(request_id, {"error": str(e)})

# Get async result endpoint
@app.get("/api/v1/result/{request_id}")
async def get_async_result(request_id: str):
    """Get result of async request"""
    result = await store.get_async_result(request_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return result

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Check CCCD API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)