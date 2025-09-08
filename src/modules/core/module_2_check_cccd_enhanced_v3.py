"""
Module 2 Enhanced V3 - Check CCCD với Smart Anti-bot Protection
Tích hợp với masothue.com với adaptive delay thông minh
"""

import requests
import time
import random
import logging
import json
import os
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Kết quả tra cứu CCCD"""
    cccd: str
    status: str  # "found", "not_found", "error"
    tax_code: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    business_type: Optional[str] = None
    business_status: Optional[str] = None
    registration_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    representative: Optional[str] = None
    error: Optional[str] = None
    response_time: Optional[float] = None
    source: str = "masothue.com"
    additional_info: Dict[str, Any] = field(default_factory=dict)

class Module2CheckCCCDEnhancedV3:
    """Module 2 Enhanced V3 - Tra cứu CCCD với smart anti-bot protection"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.masothue_url = "https://masothue.com"
        self.max_retries = config.get('max_retries', 3)
        self.delay_range = (2, 4)  # Delay cơ bản
        self.proxy_config = self._load_proxy_config()
        self.user_agents = self._load_user_agents()
        self.current_ua_index = 0
        self.request_count = 0
        self.last_request_time = 0
        self.consecutive_403_count = 0
        self.session = self._create_session()
        logger.info("✅ Module 2 Enhanced V3 initialized with smart anti-bot protection")
    
    def _load_user_agents(self) -> List[str]:
        """Load danh sách User-Agent để rotate"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
        ]
    
    def _load_proxy_config(self) -> Dict[str, Any]:
        """Load proxy configuration from config object, environment or config file"""
        proxy_config = {
            'enabled': False,
            'type': 'socks5',
            'socks5': {'host': '', 'port': '', 'username': '', 'password': ''},
            'http': {'host': '', 'port': '', 'username': '', 'password': ''}
        }
        
        try:
            # First, try to load from config object (passed during initialization)
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
            
            # If not found in config object, try to load from config file
            elif os.path.exists('config/proxy_config.json'):
                with open('config/proxy_config.json', 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    proxy_config.update(file_config)
            
            # Finally, override with environment variables
            if os.getenv('PROXY_ENABLED', '').lower() == 'true':
                proxy_config['enabled'] = True
                proxy_config['type'] = os.getenv('PROXY_TYPE', 'socks5')
                
                # SOCKS5 config
                proxy_config['socks5']['host'] = os.getenv('PROXY_SOCKS5_HOST', '')
                proxy_config['socks5']['port'] = os.getenv('PROXY_SOCKS5_PORT', '')
                proxy_config['socks5']['username'] = os.getenv('PROXY_SOCKS5_USERNAME', '')
                proxy_config['socks5']['password'] = os.getenv('PROXY_SOCKS5_PASSWORD', '')
                
                # HTTP config
                proxy_config['http']['host'] = os.getenv('PROXY_HTTP_HOST', '')
                proxy_config['http']['port'] = os.getenv('PROXY_HTTP_PORT', '')
                proxy_config['http']['username'] = os.getenv('PROXY_HTTP_USERNAME', '')
                proxy_config['http']['password'] = os.getenv('PROXY_HTTP_PASSWORD', '')
            
        except Exception as e:
            logger.warning(f"⚠️ Không thể load proxy config: {e}")
        
        return proxy_config
    
    def _create_session(self) -> requests.Session:
        """Tạo session với smart anti-bot headers và proxy"""
        session = requests.Session()
        
        # Rotate User-Agent
        user_agent = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        
        # Smart browser-like headers
        session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        })
        
        # Configure proxy if enabled
        if self.proxy_config['enabled']:
            if self.proxy_config['type'] == 'socks5':
                proxy_url = f"socks5://{self.proxy_config['socks5']['username']}:{self.proxy_config['socks5']['password']}@{self.proxy_config['socks5']['host']}:{self.proxy_config['socks5']['port']}"
                session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                logger.info(f"🔒 SOCKS5 proxy configured: {self.proxy_config['socks5']['host']}:{self.proxy_config['socks5']['port']}")
            elif self.proxy_config['type'] == 'http':
                proxy_url = f"http://{self.proxy_config['http']['username']}:{self.proxy_config['http']['password']}@{self.proxy_config['http']['host']}:{self.proxy_config['http']['port']}"
                session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                logger.info(f"🔒 HTTP proxy configured: {self.proxy_config['http']['host']}:{self.proxy_config['http']['port']}")
        
        return session
    
    def _smart_delay(self):
        """Smart delay based on request patterns and errors"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Base delay
        base_delay = random.uniform(*self.delay_range)
        
        # Increase delay if consecutive 403 errors
        if self.consecutive_403_count > 0:
            base_delay += self.consecutive_403_count * random.uniform(2, 4)
        
        # Increase delay if requests are too frequent
        if time_since_last < 1.5:
            base_delay += random.uniform(1, 3)
        
        # Add random jitter
        jitter = random.uniform(0.5, 1.5)
        total_delay = base_delay + jitter
        
        logger.info(f"⏱️ Smart delay: {total_delay:.2f}s (403_count: {self.consecutive_403_count})")
        time.sleep(total_delay)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _rotate_session(self):
        """Rotate session để tránh detection"""
        logger.info("🔄 Rotating session to avoid detection")
        self.session.close()
        self.session = self._create_session()
        time.sleep(random.uniform(1, 2))
    
    def _get_cookies(self) -> bool:
        """Lấy cookies từ trang chủ masothue.com với smart retry"""
        for attempt in range(2):
            try:
                # Rotate session every 30 requests
                if self.request_count % 30 == 0 and self.request_count > 0:
                    self._rotate_session()
                
                response = self.session.get(self.masothue_url, timeout=15)
                if response.status_code == 200:
                    logger.info("✅ Successfully got cookies from masothue.com")
                    return True
                else:
                    logger.warning(f"⚠️ Failed to get cookies: {response.status_code}")
                    if attempt < 1:
                        time.sleep(random.uniform(2, 4))
                        continue
                    return False
            except Exception as e:
                logger.error(f"❌ Error getting cookies: {e}")
                if attempt < 1:
                    time.sleep(random.uniform(2, 4))
                    continue
                return False
        return False
    
    def _parse_search_results(self, html_content: str) -> SearchResult:
        """Parse kết quả tìm kiếm từ HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        result = SearchResult(cccd="", status="not_found")
        
        try:
            # Tìm thông tin trong tax-listing
            tax_listing = soup.find('div', class_='tax-listing')
            if tax_listing:
                # Lấy công ty đầu tiên
                first_company = tax_listing.find('div', attrs={'data-prefetch': True})
                if first_company:
                    # Trích xuất tên công ty
                    name_elem = first_company.find('h3')
                    if name_elem:
                        result.name = name_elem.get_text().strip()
                    
                    # Trích xuất mã số thuế
                    tax_code_elem = first_company.find('a', href=re.compile(r'/\d{10,13}-'))
                    if tax_code_elem:
                        tax_code_match = re.search(r'/(\d{10,13})-', tax_code_elem.get('href', ''))
                        if tax_code_match:
                            result.tax_code = tax_code_match.group(1)
                    
                    # Trích xuất người đại diện
                    rep_elem = first_company.find('em')
                    if rep_elem:
                        result.representative = rep_elem.get_text().strip()
                    
                    # Trích xuất địa chỉ
                    address_elem = first_company.find('address')
                    if address_elem:
                        result.address = address_elem.get_text().strip()
                    
                    # Xác định loại hình doanh nghiệp từ tên
                    if result.name:
                        if 'TNHH' in result.name.upper():
                            result.business_type = 'Công ty TNHH'
                        elif 'CỔ PHẦN' in result.name.upper():
                            result.business_type = 'Công ty cổ phần'
                        elif 'TƯ NHÂN' in result.name.upper():
                            result.business_type = 'Doanh nghiệp tư nhân'
                        else:
                            result.business_type = 'Khác'
                    
                    if result.tax_code:
                        result.status = "found"
                        logger.info(f"✅ Parsed tax info: {result.tax_code} - {result.name}")
                    else:
                        result.error = "No tax code found in parsed data"
                        logger.warning("⚠️ No tax code found in parsed data")
                else:
                    result.error = "No company data found in tax-listing"
                    logger.warning("⚠️ No company data found in tax-listing")
            else:
                result.error = "No tax-listing found in HTML"
                logger.warning("⚠️ No tax-listing found in HTML")
                
        except Exception as e:
            result.error = f"Parse error: {str(e)}"
            logger.error(f"❌ Error parsing search results: {e}")
        
        return result
    
    def check_cccd(self, cccd: str) -> SearchResult:
        """Tra cứu thông tin CCCD từ masothue.com với smart anti-bot"""
        result = SearchResult(cccd=cccd, status="not_found")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔍 Looking up CCCD: {cccd} (attempt {attempt + 1}/{self.max_retries})")
                
                # Smart delay
                self._smart_delay()
                
                # Lấy cookies trước
                if not self._get_cookies():
                    if attempt < self.max_retries - 1:
                        continue
                    result.error = "Failed to get cookies"
                    return result
                
                # Thực hiện tìm kiếm
                params = {
                    "q": cccd,
                    "type": "auto",
                    "token": "NbnmgilFfL",
                    "force-search": "1",
                }
                
                search_url = f"{self.masothue_url}/Search/"
                start_time = time.time()
                
                response = self.session.get(search_url, params=params, timeout=20)
                result.response_time = time.time() - start_time
                
                if response.status_code == 200:
                    logger.info(f"✅ Got response for {cccd}: {response.status_code}")
                    parsed_result = self._parse_search_results(response.text)
                    parsed_result.cccd = cccd
                    parsed_result.response_time = result.response_time
                    
                    # Reset consecutive 403 count on success
                    self.consecutive_403_count = 0
                    
                    return parsed_result
                    
                elif response.status_code == 403:
                    logger.warning(f"⚠️ 403 Forbidden for {cccd} - anti-bot protection")
                    result.error = f"403 Forbidden - anti-bot protection"
                    
                    # Increase consecutive 403 count
                    self.consecutive_403_count += 1
                    
                    # Rotate session on 403
                    self._rotate_session()
                    
                    if attempt < self.max_retries - 1:
                        # Smart delay based on consecutive 403 count
                        delay = min(15 + (self.consecutive_403_count * 5), 60)
                        logger.info(f"⏱️ Waiting {delay}s before retry due to 403")
                        time.sleep(delay)
                        continue
                    return result
                    
                else:
                    logger.warning(f"⚠️ Unexpected status code for {cccd}: {response.status_code}")
                    result.error = f"HTTP {response.status_code}"
                    if attempt < self.max_retries - 1:
                        self._smart_delay()
                        continue
                    return result
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request error for {cccd}: {e}")
                result.error = str(e)
                if attempt < self.max_retries - 1:
                    self._smart_delay()
                    continue
                return result
                
            except Exception as e:
                logger.error(f"❌ Unexpected error for {cccd}: {e}")
                result.error = str(e)
                if attempt < self.max_retries - 1:
                    self._smart_delay()
                    continue
                return result
        
        return result
    
    def batch_check(self, cccd_list: List[str]) -> List[SearchResult]:
        """Tra cứu hàng loạt CCCD với smart anti-bot protection"""
        results = []
        total = len(cccd_list)
        
        logger.info(f"🔄 Starting batch check for {total} CCCD records with smart anti-bot protection")
        
        for i, cccd in enumerate(cccd_list, 1):
            logger.info(f"🔄 Processing {i}/{total}: {cccd}")
            result = self.check_cccd(cccd)
            results.append(result)
            
            # Smart delay between requests
            if i < total:
                self._smart_delay()
        
        logger.info(f"✅ Batch check completed: {len(results)} results")
        return results
    
    def save_results(self, results: List[SearchResult], output_file: str = "cccd_lookup_results_v3.json"):
        """Lưu kết quả tra cứu"""
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / output_file
        
        try:
            # Convert dataclass to dict for JSON serialization
            results_data = []
            for result in results:
                result_dict = {
                    'cccd': result.cccd,
                    'status': result.status,
                    'tax_code': result.tax_code,
                    'name': result.name,
                    'address': result.address,
                    'business_type': result.business_type,
                    'business_status': result.business_status,
                    'registration_date': result.registration_date,
                    'phone': result.phone,
                    'email': result.email,
                    'representative': result.representative,
                    'error': result.error,
                    'response_time': result.response_time,
                    'source': result.source,
                    'additional_info': result.additional_info
                }
                results_data.append(result_dict)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Saved {len(results)} results to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")

if __name__ == "__main__":
    # Test configuration
    test_config = {
        'max_retries': 2,
        'proxy_enabled': False
    }
    
    # Initialize module
    module = Module2CheckCCCDEnhancedV3(test_config)
    
    # Test with sample CCCD
    test_cccd = "037178000015"
    result = module.check_cccd(test_cccd)
    
    print(f"Test result for {test_cccd}:")
    print(f"Status: {result.status}")
    print(f"Tax Code: {result.tax_code}")
    print(f"Name: {result.name}")
    print(f"Error: {result.error}")