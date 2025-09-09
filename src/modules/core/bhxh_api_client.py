"""
Module BHXH API Client - Tra cứu thông tin Bảo hiểm Xã hội
Dựa trên Module 7 Advanced API Client với proxy management
"""

import asyncio
import httpx
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class BHXHResult:
    """Kết quả tra cứu BHXH"""
    ma_dinh_danh: str
    status: str  # "found", "not_found", "error", "blocked"
    ho_ten: Optional[str] = None
    dia_chi: Optional[str] = None
    ma_so_thue: Optional[str] = None
    dien_thoai: Optional[str] = None
    nguoi_dai_dien: Optional[str] = None
    tinh_trang: Optional[str] = None
    loai_hinh_dn: Optional[str] = None
    ngay_hoat_dong: Optional[str] = None
    co_quan_thue: Optional[str] = None
    ngay_thay_doi: Optional[str] = None
    ghi_chu: Optional[str] = None
    error: Optional[str] = None
    source: str = "bhxh_api"
    proxy_used: Optional[str] = None
    processing_time: float = 0.0
    retry_count: int = 0
    timestamp: str = ""
    additional_info: Dict[str, Any] = field(default_factory=dict)

class BHXHAPIClient:
    """Client tra cứu BHXH với proxy support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        self.proxy_config = self._load_proxy_config()
        self.session = None
        logger.info("✅ BHXH API Client initialized")
    
    def _load_proxy_config(self) -> Dict[str, Any]:
        """Load proxy configuration"""
        proxy_config = {
            'enabled': False,
            'type': 'socks5',
            'socks5': {'host': '', 'port': '', 'username': '', 'password': ''},
            'http': {'host': '', 'port': '', 'username': '', 'password': ''}
        }
        
        try:
            # Load from config object
            if self.config.get('proxy_enabled'):
                proxy_config['enabled'] = True
                proxy_config['type'] = self.config.get('proxy_type', 'socks5')
                
                if proxy_config['type'] == 'socks5':
                    proxy_config['socks5']['host'] = self.config.get('proxy_socks5_host', '')
                    proxy_config['socks5']['port'] = self.config.get('proxy_socks5_port', '')
                    proxy_config['socks5']['username'] = self.config.get('proxy_socks5_username', '')
                    proxy_config['socks5']['password'] = self.config.get('proxy_socks5_password', '')
                elif proxy_config['type'] == 'http':
                    proxy_config['http']['host'] = self.config.get('proxy_http_host', '')
                    proxy_config['http']['port'] = self.config.get('proxy_http_port', '')
                    proxy_config['http']['username'] = self.config.get('proxy_http_username', '')
                    proxy_config['http']['password'] = self.config.get('proxy_http_password', '')
            
            # Load from environment variables
            import os
            if os.getenv('PROXY_ENABLED', '').lower() == 'true':
                proxy_config['enabled'] = True
                proxy_config['type'] = os.getenv('PROXY_TYPE', 'socks5')
                
                proxy_config['socks5']['host'] = os.getenv('PROXY_SOCKS5_HOST', '')
                proxy_config['socks5']['port'] = os.getenv('PROXY_SOCKS5_PORT', '')
                proxy_config['socks5']['username'] = os.getenv('PROXY_SOCKS5_USERNAME', '')
                proxy_config['socks5']['password'] = os.getenv('PROXY_SOCKS5_PASSWORD', '')
                
                proxy_config['http']['host'] = os.getenv('PROXY_HTTP_HOST', '')
                proxy_config['http']['port'] = os.getenv('PROXY_HTTP_PORT', '')
                proxy_config['http']['username'] = os.getenv('PROXY_HTTP_USERNAME', '')
                proxy_config['http']['password'] = os.getenv('PROXY_HTTP_PASSWORD', '')
            
        except Exception as e:
            logger.warning(f"⚠️ Không thể load proxy config: {e}")
        
        return proxy_config
    
    def _create_session(self) -> httpx.AsyncClient:
        """Tạo session với proxy configuration"""
        proxy = None
        
        if self.proxy_config['enabled']:
            if self.proxy_config['type'] == 'socks5':
                proxy_url = f"socks5://{self.proxy_config['socks5']['username']}:{self.proxy_config['socks5']['password']}@{self.proxy_config['socks5']['host']}:{self.proxy_config['socks5']['port']}"
                proxy = proxy_url
                logger.info(f"🔒 SOCKS5 proxy configured: {self.proxy_config['socks5']['host']}:{self.proxy_config['socks5']['port']}")
            elif self.proxy_config['type'] == 'http':
                proxy_url = f"http://{self.proxy_config['http']['username']}:{self.proxy_config['http']['password']}@{self.proxy_config['http']['host']}:{self.proxy_config['http']['port']}"
                proxy = proxy_url
                logger.info(f"🔒 HTTP proxy configured: {self.proxy_config['http']['host']}:{self.proxy_config['http']['port']}")
        
        # Headers cho BHXH API
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        return httpx.AsyncClient(
            proxy=proxy,
            headers=headers,
            timeout=self.timeout,
            follow_redirects=True
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def lookup_bhxh(self, ma_dinh_danh: str) -> BHXHResult:
        """Tra cứu thông tin BHXH"""
        result = BHXHResult(
            ma_dinh_danh=ma_dinh_danh,
            status="not_found",
            timestamp=datetime.now().isoformat()
        )
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔍 Looking up BHXH: {ma_dinh_danh} (attempt {attempt + 1}/{self.max_retries})")
                
                start_time = time.time()
                
                # Thử nhiều endpoint BHXH
                endpoints = [
                    f"https://api.bhxh.gov.vn/api/check/{ma_dinh_danh}",
                    f"https://bhxh.gov.vn/api/lookup/{ma_dinh_danh}",
                    f"https://api.social-insurance.gov.vn/check/{ma_dinh_danh}",
                    f"https://tra-cuu-bhxh.gov.vn/api/search/{ma_dinh_danh}"
                ]
                
                for endpoint in endpoints:
                    try:
                        response = await self.session.get(endpoint)
                        result.processing_time = time.time() - start_time
                        result.retry_count = attempt
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                return self._parse_bhxh_response(data, result)
                            except json.JSONDecodeError:
                                # Thử parse HTML response
                                return self._parse_html_response(response.text, result)
                        elif response.status_code == 403:
                            result.status = "blocked"
                            result.error = "403 Forbidden - Anti-bot protection"
                            logger.warning(f"⚠️ 403 Forbidden for {ma_dinh_danh}")
                        elif response.status_code == 404:
                            result.status = "not_found"
                            result.error = "404 Not Found"
                        else:
                            result.status = "error"
                            result.error = f"HTTP {response.status_code}"
                            
                    except httpx.RequestError as e:
                        logger.warning(f"⚠️ Request error for {endpoint}: {e}")
                        continue
                
                # Nếu tất cả endpoints đều thất bại, thử fallback
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                result.status = "error"
                result.error = "All endpoints failed"
                
            except Exception as e:
                logger.error(f"❌ Error looking up BHXH {ma_dinh_danh}: {e}")
                result.error = str(e)
                result.status = "error"
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
        
        return result
    
    def _parse_bhxh_response(self, data: Dict[str, Any], result: BHXHResult) -> BHXHResult:
        """Parse JSON response từ BHXH API"""
        try:
            if data.get('success') or data.get('status') == 'success':
                result.status = "found"
                
                # Parse các trường thông tin
                profile = data.get('data', {}) or data.get('profile', {}) or data
                
                result.ho_ten = profile.get('ho_ten') or profile.get('full_name') or profile.get('name')
                result.dia_chi = profile.get('dia_chi') or profile.get('address') or profile.get('address_full')
                result.ma_so_thue = profile.get('ma_so_thue') or profile.get('tax_code') or profile.get('mst')
                result.dien_thoai = profile.get('dien_thoai') or profile.get('phone') or profile.get('mobile')
                result.nguoi_dai_dien = profile.get('nguoi_dai_dien') or profile.get('representative') or profile.get('representative_name')
                result.tinh_trang = profile.get('tinh_trang') or profile.get('status') or profile.get('business_status')
                result.loai_hinh_dn = profile.get('loai_hinh_dn') or profile.get('business_type') or profile.get('company_type')
                result.ngay_hoat_dong = profile.get('ngay_hoat_dong') or profile.get('start_date') or profile.get('operation_date')
                result.co_quan_thue = profile.get('co_quan_thue') or profile.get('tax_office') or profile.get('tax_authority')
                result.ngay_thay_doi = profile.get('ngay_thay_doi') or profile.get('last_updated') or profile.get('update_date')
                result.ghi_chu = profile.get('ghi_chu') or profile.get('note') or profile.get('description')
                
                # Thêm thông tin bổ sung
                result.additional_info = {
                    'raw_data': data,
                    'api_endpoint': 'bhxh_api',
                    'response_format': 'json'
                }
                
                logger.info(f"✅ Found BHXH info for {result.ma_dinh_danh}: {result.ho_ten}")
                
            else:
                result.status = "not_found"
                result.error = data.get('message', 'No data found')
                
        except Exception as e:
            logger.error(f"❌ Error parsing BHXH response: {e}")
            result.status = "error"
            result.error = f"Parse error: {str(e)}"
        
        return result
    
    def _parse_html_response(self, html_content: str, result: BHXHResult) -> BHXHResult:
        """Parse HTML response từ BHXH website"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Tìm kiếm thông tin trong HTML
            name_elem = soup.find('span', class_='name') or soup.find('div', class_='full-name') or soup.find('h3')
            if name_elem:
                result.ho_ten = name_elem.get_text().strip()
                result.status = "found"
            
            address_elem = soup.find('span', class_='address') or soup.find('div', class_='address')
            if address_elem:
                result.dia_chi = address_elem.get_text().strip()
            
            tax_elem = soup.find('span', class_='tax-code') or soup.find('div', class_='mst')
            if tax_elem:
                result.ma_so_thue = tax_elem.get_text().strip()
            
            phone_elem = soup.find('span', class_='phone') or soup.find('div', class_='phone')
            if phone_elem:
                result.dien_thoai = phone_elem.get_text().strip()
            
            if result.status == "found":
                result.additional_info = {
                    'raw_html': html_content[:1000],  # Lưu 1000 ký tự đầu
                    'api_endpoint': 'bhxh_website',
                    'response_format': 'html'
                }
                logger.info(f"✅ Found BHXH info from HTML for {result.ma_dinh_danh}: {result.ho_ten}")
            else:
                result.status = "not_found"
                result.error = "No information found in HTML"
                
        except Exception as e:
            logger.error(f"❌ Error parsing HTML response: {e}")
            result.status = "error"
            result.error = f"HTML parse error: {str(e)}"
        
        return result
    
    async def batch_lookup(self, identifiers: List[str]) -> List[BHXHResult]:
        """Tra cứu hàng loạt mã định danh"""
        results = []
        
        logger.info(f"🔄 Starting batch BHXH lookup for {len(identifiers)} identifiers")
        
        for i, identifier in enumerate(identifiers, 1):
            logger.info(f"🔄 Processing {i}/{len(identifiers)}: {identifier}")
            result = await self.lookup_bhxh(identifier)
            results.append(result)
            
            # Delay giữa các requests
            if i < len(identifiers):
                await asyncio.sleep(1)
        
        logger.info(f"✅ Batch BHXH lookup completed: {len(results)} results")
        return results
    
    def save_results(self, results: List[BHXHResult], output_file: str = "bhxh_api_results.json"):
        """Lưu kết quả tra cứu BHXH"""
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / output_file
        
        try:
            # Convert dataclass to dict for JSON serialization
            results_data = []
            for result in results:
                result_dict = {
                    'ma_dinh_danh': result.ma_dinh_danh,
                    'status': result.status,
                    'ho_ten': result.ho_ten,
                    'dia_chi': result.dia_chi,
                    'ma_so_thue': result.ma_so_thue,
                    'dien_thoai': result.dien_thoai,
                    'nguoi_dai_dien': result.nguoi_dai_dien,
                    'tinh_trang': result.tinh_trang,
                    'loai_hinh_dn': result.loai_hinh_dn,
                    'ngay_hoat_dong': result.ngay_hoat_dong,
                    'co_quan_thue': result.co_quan_thue,
                    'ngay_thay_doi': result.ngay_thay_doi,
                    'ghi_chu': result.ghi_chu,
                    'error': result.error,
                    'source': result.source,
                    'proxy_used': result.proxy_used,
                    'processing_time': result.processing_time,
                    'retry_count': result.retry_count,
                    'timestamp': result.timestamp,
                    'additional_info': result.additional_info
                }
                results_data.append(result_dict)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Saved {len(results)} BHXH results to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving BHXH results: {e}")

# Utility functions
async def lookup_bhxh_async(ma_dinh_danh: str, config: Dict[str, Any] = None) -> BHXHResult:
    """Tra cứu BHXH (standalone function)"""
    if config is None:
        config = {}
    
    async with BHXHAPIClient(config) as client:
        return await client.lookup_bhxh(ma_dinh_danh)

async def batch_lookup_bhxh_async(identifiers: List[str], config: Dict[str, Any] = None) -> List[BHXHResult]:
    """Tra cứu hàng loạt BHXH (standalone function)"""
    if config is None:
        config = {}
    
    async with BHXHAPIClient(config) as client:
        return await client.batch_lookup(identifiers)

if __name__ == "__main__":
    # Test configuration
    test_config = {
        'timeout': 30,
        'max_retries': 2,
        'proxy_enabled': False
    }
    
    async def test_bhxh():
        async with BHXHAPIClient(test_config) as client:
            result = await client.lookup_bhxh("8087485671")
            print(f"Test result for 8087485671:")
            print(f"Status: {result.status}")
            print(f"Họ tên: {result.ho_ten}")
            print(f"Địa chỉ: {result.dia_chi}")
            print(f"Error: {result.error}")
    
    asyncio.run(test_bhxh())