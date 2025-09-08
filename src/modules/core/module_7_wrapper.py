#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 7 Wrapper - Tích hợp Advanced API Client với modules hiện có
Cung cấp interface đơn giản để các module khác sử dụng
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .module_7_advanced_api_client import AdvancedAPIClient, RequestResult, RequestStatus

logger = logging.getLogger(__name__)

class Module7Wrapper:
    """Wrapper để tích hợp Advanced API Client với modules hiện có"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        
        # Cấu hình từ config
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        self.proxy_file = config.get('proxy_file', 'config/proxies.txt')
        self.proxy_strategy = config.get('proxy_strategy', 'random')
        self.enable_dynamic_data = config.get('enable_dynamic_data', True)
        
        logger.info("✅ Module 7 Wrapper khởi tạo thành công")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = AdvancedAPIClient(
            timeout=self.timeout,
            max_retries=self.max_retries,
            proxy_file=self.proxy_file,
            proxy_strategy=self.proxy_strategy,
            enable_dynamic_data=self.enable_dynamic_data
        )
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def check_cccd_with_proxy(self, cccd: str) -> Dict[str, Any]:
        """Kiểm tra CCCD với proxy rotation"""
        logger.info(f"🔍 Kiểm tra CCCD {cccd} với proxy rotation")
        
        # Payload cho masothue.com
        payload = {
            "q": cccd,
            "type": "personal"
        }
        
        # Headers cho masothue.com
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/',
            'Origin': 'https://masothue.com'
        }
        
        try:
            # Thử GET request trước
            result = await self.client.request(
                method="GET",
                url="https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/",
                headers=headers
            )
            
            if result.status == RequestStatus.SUCCESS:
                logger.info("✅ Truy cập trang tìm kiếm thành công")
                
                # Thử POST request
                result = await self.client.request(
                    method="POST",
                    url="https://masothue.com/Search/",
                    json_body=payload,
                    headers=headers
                )
                
                if result.status == RequestStatus.SUCCESS:
                    logger.info("✅ Tìm kiếm CCCD thành công")
                    return self._parse_cccd_result(result, cccd)
                else:
                    logger.warning(f"⚠️ Tìm kiếm CCCD thất bại: {result.error_message}")
                    return self._create_fallback_result(cccd, result)
            else:
                logger.warning(f"⚠️ Truy cập trang tìm kiếm thất bại: {result.error_message}")
                return self._create_fallback_result(cccd, result)
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi kiểm tra CCCD: {str(e)}")
            return {
                "cccd": cccd,
                "status": "error",
                "message": f"Lỗi hệ thống: {str(e)}",
                "profiles": [],
                "timestamp": datetime.now().isoformat(),
                "proxy_used": None,
                "processing_time": 0.0
            }
    
    async def check_enterprise_with_proxy(self, enterprise_id: str) -> Dict[str, Any]:
        """Kiểm tra doanh nghiệp với proxy rotation"""
        logger.info(f"🏢 Kiểm tra doanh nghiệp {enterprise_id} với proxy rotation")
        
        # Payload cho thongtindoanhnghiep.co
        payload = {
            "id": enterprise_id,
            "type": "enterprise"
        }
        
        try:
            result = await self.client.request(
                method="GET",
                url=f"https://thongtindoanhnghiep.co/api/company/{enterprise_id}",
                json_body=payload
            )
            
            if result.status == RequestStatus.SUCCESS:
                logger.info("✅ Tìm kiếm doanh nghiệp thành công")
                return self._parse_enterprise_result(result, enterprise_id)
            else:
                logger.warning(f"⚠️ Tìm kiếm doanh nghiệp thất bại: {result.error_message}")
                return self._create_fallback_result(enterprise_id, result)
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi kiểm tra doanh nghiệp: {str(e)}")
            return {
                "enterprise_id": enterprise_id,
                "status": "error",
                "message": f"Lỗi hệ thống: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat(),
                "proxy_used": None,
                "processing_time": 0.0
            }
    
    async def check_bhxh_with_proxy(self, ssn: str) -> Dict[str, Any]:
        """Kiểm tra BHXH với proxy rotation"""
        logger.info(f"🏥 Kiểm tra BHXH {ssn} với proxy rotation")
        
        # Payload cho BHXH
        payload = {
            "ssn": ssn,
            "type": "bhxh"
        }
        
        try:
            result = await self.client.request(
                method="POST",
                url="https://api.bhxh.gov.vn/check",
                json_body=payload
            )
            
            if result.status == RequestStatus.SUCCESS:
                logger.info("✅ Tìm kiếm BHXH thành công")
                return self._parse_bhxh_result(result, ssn)
            else:
                logger.warning(f"⚠️ Tìm kiếm BHXH thất bại: {result.error_message}")
                return self._create_fallback_result(ssn, result)
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi kiểm tra BHXH: {str(e)}")
            return {
                "ssn": ssn,
                "status": "error",
                "message": f"Lỗi hệ thống: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat(),
                "proxy_used": None,
                "processing_time": 0.0
            }
    
    def _parse_cccd_result(self, result: RequestResult, cccd: str) -> Dict[str, Any]:
        """Parse kết quả CCCD"""
        try:
            response_data = result.response_data or {}
            
            # Tìm kiếm thông tin profile trong response
            profiles = []
            
            # Nếu có dữ liệu profile
            if isinstance(response_data, dict) and "profiles" in response_data:
                profiles = response_data["profiles"]
            elif isinstance(response_data, dict) and "data" in response_data:
                profiles = response_data["data"]
            
            return {
                "cccd": cccd,
                "status": "found" if profiles else "not_found",
                "message": f"Tìm thấy {len(profiles)} kết quả" if profiles else "Không tìm thấy thông tin",
                "profiles": profiles,
                "timestamp": datetime.now().isoformat(),
                "proxy_used": result.proxy_used.host if result.proxy_used else None,
                "processing_time": result.processing_time,
                "retry_count": result.retry_count
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi parse kết quả CCCD: {str(e)}")
            return self._create_fallback_result(cccd, result)
    
    def _parse_enterprise_result(self, result: RequestResult, enterprise_id: str) -> Dict[str, Any]:
        """Parse kết quả doanh nghiệp"""
        try:
            response_data = result.response_data or {}
            
            return {
                "enterprise_id": enterprise_id,
                "status": "found",
                "message": "Tìm thấy thông tin doanh nghiệp",
                "data": response_data,
                "timestamp": datetime.now().isoformat(),
                "proxy_used": result.proxy_used.host if result.proxy_used else None,
                "processing_time": result.processing_time,
                "retry_count": result.retry_count
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi parse kết quả doanh nghiệp: {str(e)}")
            return self._create_fallback_result(enterprise_id, result)
    
    def _parse_bhxh_result(self, result: RequestResult, ssn: str) -> Dict[str, Any]:
        """Parse kết quả BHXH"""
        try:
            response_data = result.response_data or {}
            
            return {
                "ssn": ssn,
                "status": "found",
                "message": "Tìm thấy thông tin BHXH",
                "data": response_data,
                "timestamp": datetime.now().isoformat(),
                "proxy_used": result.proxy_used.host if result.proxy_used else None,
                "processing_time": result.processing_time,
                "retry_count": result.retry_count
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi parse kết quả BHXH: {str(e)}")
            return self._create_fallback_result(ssn, result)
    
    def _create_fallback_result(self, identifier: str, result: RequestResult) -> Dict[str, Any]:
        """Tạo kết quả fallback"""
        status = "not_found"
        message = "Không tìm thấy thông tin"
        
        if result.status == RequestStatus.BLOCKED:
            status = "blocked"
            message = "Bị chặn bởi anti-bot protection"
        elif result.status == RequestStatus.ERROR:
            status = "error"
            message = f"Lỗi: {result.error_message}"
        elif result.status == RequestStatus.PROXY_ERROR:
            status = "proxy_error"
            message = "Lỗi proxy"
        
        return {
            "identifier": identifier,
            "status": status,
            "message": message,
            "profiles": [],
            "data": {},
            "timestamp": datetime.now().isoformat(),
            "proxy_used": result.proxy_used.host if result.proxy_used else None,
            "processing_time": result.processing_time,
            "retry_count": result.retry_count,
            "error_details": result.error_message
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê"""
        if self.client:
            return self.client.get_stats()
        return {"error": "Client not initialized"}

# Utility functions
async def check_cccd_with_proxy(cccd: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Kiểm tra CCCD với proxy (standalone function)"""
    if config is None:
        config = {}
    
    async with Module7Wrapper(config) as wrapper:
        return await wrapper.check_cccd_with_proxy(cccd)

async def check_enterprise_with_proxy(enterprise_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Kiểm tra doanh nghiệp với proxy (standalone function)"""
    if config is None:
        config = {}
    
    async with Module7Wrapper(config) as wrapper:
        return await wrapper.check_enterprise_with_proxy(enterprise_id)

async def check_bhxh_with_proxy(ssn: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Kiểm tra BHXH với proxy (standalone function)"""
    if config is None:
        config = {}
    
    async with Module7Wrapper(config) as wrapper:
        return await wrapper.check_bhxh_with_proxy(ssn)

# Example usage
async def main():
    """Ví dụ sử dụng Module 7 Wrapper"""
    
    config = {
        'timeout': 30,
        'max_retries': 3,
        'proxy_strategy': 'random',
        'enable_dynamic_data': True
    }
    
    async with Module7Wrapper(config) as wrapper:
        
        # Test CCCD
        result = await wrapper.check_cccd_with_proxy("037178000015")
        print(f"CCCD Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Test Enterprise
        result = await wrapper.check_enterprise_with_proxy("0101234567")
        print(f"Enterprise Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Test BHXH
        result = await wrapper.check_bhxh_with_proxy("0123456789")
        print(f"BHXH Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Stats
        stats = wrapper.get_stats()
        print(f"Stats: {json.dumps(stats, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())