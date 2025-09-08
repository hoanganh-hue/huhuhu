#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 2 Enhanced: Check CCCD - Tích hợp với masothue.com với khả năng chống bot
Tìm kiếm thông tin mã số thuế cá nhân từ số CCCD với proxy và anti-bot

Tính năng:
- Tích hợp với https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/
- Hỗ trợ SOCKS5 và HTTP proxy
- Anti-bot protection với browser simulation
- Trích xuất thông tin thực tế từ HTML
- Xử lý Brotli compression
- Logging chi tiết
"""

import re
import time
import json
import requests
import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass, field
import os
import random

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Kết quả tìm kiếm CCCD"""
    cccd: str
    status: str
    tax_code: Optional[str] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    business_type: Optional[str] = None
    business_status: Optional[str] = None
    registration_date: Optional[str] = None
    profile_url: Optional[str] = None
    error: Optional[str] = None
    method: Optional[str] = None
    response_time: Optional[float] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

class Module2CheckCCCDEnhanced:
    """Module kiểm tra CCCD nâng cao với khả năng chống bot và proxy"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Khởi tạo module
        
        Args:
            config: Cấu hình module
        """
        self.config = config
        self.base_url = "https://masothue.com"
        self.search_url = "https://masothue.com/Search/"
        
        # Cấu hình request
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = 1.0
        
        # Proxy configuration
        self.proxy_config = self._load_proxy_config()
        
        # Browser-like headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "proxy_rotations": 0
        }
        
        logger.info("✅ Module 2 Check CCCD Enhanced - Khởi tạo thành công")
        logger.info(f"🔗 Base URL: {self.base_url}")
        logger.info(f"🌐 Proxy enabled: {self.proxy_config.get('enabled', False)}")
        if self.proxy_config.get('enabled', False):
            logger.info(f"🔗 Proxy type: {self.proxy_config.get('type', 'none')}")
            if self.proxy_config.get('type') == 'socks5':
                socks5_config = self.proxy_config.get('socks5', {})
                logger.info(f"🌐 SOCKS5: {socks5_config.get('host', 'N/A')}:{socks5_config.get('port', 'N/A')}")
    
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
    
    def _get_session(self) -> requests.Session:
        """Tạo session với proxy configuration"""
        session = requests.Session()
        session.headers.update(self.headers)
        
        if self.proxy_config.get('enabled', False):
            proxy_type = self.proxy_config.get('type', 'socks5')
            
            if proxy_type == 'socks5':
                proxy_info = self.proxy_config['socks5']
                if proxy_info['host'] and proxy_info['port']:
                    if proxy_info['username'] and proxy_info['password']:
                        proxy_url = f"socks5://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
                    else:
                        proxy_url = f"socks5://{proxy_info['host']}:{proxy_info['port']}"
                    
                    session.proxies = {"http": proxy_url, "https": proxy_url}
                    logger.info(f"🌐 SOCKS5 Proxy: {proxy_info['host']}:{proxy_info['port']}")
            
            elif proxy_type == 'http':
                proxy_info = self.proxy_config['http']
                if proxy_info['host'] and proxy_info['port']:
                    if proxy_info['username'] and proxy_info['password']:
                        proxy_url = f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
                    else:
                        proxy_url = f"http://{proxy_info['host']}:{proxy_info['port']}"
                    
                    session.proxies = {"http": proxy_url, "https": proxy_url}
                    logger.info(f"🌐 HTTP Proxy: {proxy_info['host']}:{proxy_info['port']}")
        
        return session
    
    def _random_delay(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """Random delay để tránh bị phát hiện"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _get_homepage_cookies(self, session: requests.Session) -> bool:
        """Lấy cookies từ homepage"""
        try:
            logger.info("🍪 Getting cookies from homepage...")
            response = session.get("https://masothue.com/", timeout=15)
            response.raise_for_status()
            logger.info(f"✅ Cookies collected: {len(response.cookies)} cookies")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to get homepage cookies: {e}")
            return False
    
    def check_cccd(self, cccd: str) -> SearchResult:
        """
        Kiểm tra CCCD và tìm kiếm thông tin mã số thuế cá nhân
        
        Args:
            cccd: Số CCCD cần kiểm tra
            
        Returns:
            SearchResult chứa thông tin kết quả
        """
        logger.info(f"🔍 Starting enhanced search for CCCD: {cccd}")
        
        self.stats["total_requests"] += 1
        
        try:
            # Validate CCCD format
            if not self._validate_cccd(cccd):
                return SearchResult(
                    cccd=cccd,
                    status="error",
                    error="Số CCCD không hợp lệ"
                )
            
            # Thực hiện tìm kiếm với retry logic
            result = self._search_with_retry(cccd)
            
            if result.status == "found":
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            logger.info(f"✅ Completed search for CCCD: {cccd} - Status: {result.status}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error checking CCCD {cccd}: {str(e)}")
            self.stats["failed_requests"] += 1
            return SearchResult(
                cccd=cccd,
                status="error",
                error=str(e)
            )
    
    def _validate_cccd(self, cccd: str) -> bool:
        """Validate format của số CCCD"""
        # CCCD phải có 12 chữ số
        if not re.match(r'^\d{12}$', cccd):
            return False
        return True
    
    def _search_with_retry(self, cccd: str) -> SearchResult:
        """Tìm kiếm với retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{self.max_retries} for CCCD: {cccd}")
                
                # Tạo session mới cho mỗi lần thử
                session = self._get_session()
                
                # Lấy cookies từ homepage
                self._get_homepage_cookies(session)
                
                # Thực hiện tìm kiếm
                result = self._perform_search(session, cccd)
                
                if result.status != "error":
                    return result
                    
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"⏳ Waiting {delay}s before retry...")
                    time.sleep(delay)
        
        # Tất cả lần thử đều thất bại
        return SearchResult(
            cccd=cccd,
            status="error",
            error=f"Failed after {self.max_retries} attempts: {str(last_error)}"
        )
    
    def _perform_search(self, session: requests.Session, cccd: str) -> SearchResult:
        """Thực hiện tìm kiếm thực tế"""
        start_time = time.time()
        
        try:
            # Random delay
            self._random_delay(1.0, 3.0)
            
            # Search parameters
            params = {
                "q": cccd,
                "type": "auto",
                "token": "NbnmgilFfL",
                "force-search": "1",
            }
            
            # Add search-specific headers
            search_headers = self.headers.copy()
            search_headers.update({
                "Referer": "https://masothue.com/",
                "X-Requested-With": "XMLHttpRequest"
            })
            
            logger.info(f"🔍 Searching for CCCD: {cccd}")
            response = session.get(self.search_url, params=params, headers=search_headers, timeout=15)
            response.raise_for_status()
            
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.info(f"✅ Request successful: {response.status_code}")
            logger.info(f"⏱️ Response time: {response_time:.2f}s")
            logger.info(f"📊 Content length: {len(response.content)} bytes")
            
            # Parse HTML to extract data
            result = self._parse_masothue_response(response.text, cccd)
            result.response_time = response_time
            result.method = "enhanced_requests"
            
            return result
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            logger.error(f"❌ Request failed: {e}")
            return SearchResult(
                cccd=cccd,
                status="error",
                error=str(e),
                response_time=end_time - start_time
            )
    
    def _parse_masothue_response(self, html_content: str, cccd: str) -> SearchResult:
        """Parse kết quả từ masothue.com"""
        logger.info("📄 Parsing HTML content...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all text content
        all_text = soup.get_text()
        logger.info(f"📄 Total text content length: {len(all_text)} characters")
        
        # Initialize result
        result = SearchResult(cccd=cccd, status="not_found")
        
        # Method 1: Look for tax code and name in links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check for tax code profile links
            if '/masothue.com/' in href and href != 'https://masothue.com/':
                # Extract tax code from URL
                url_parts = href.split('/')
                if len(url_parts) > 0:
                    last_part = url_parts[-1]
                    if '-' in last_part:
                        potential_tax_code = last_part.split('-')[0]
                        if potential_tax_code.isdigit() and len(potential_tax_code) == 10:
                            result.tax_code = potential_tax_code
                            result.name = text
                            result.profile_url = href
                            result.status = "found"
                            logger.info(f"🎯 Found tax code: {potential_tax_code}")
                            logger.info(f"👤 Found name: {text}")
                            logger.info(f"🔗 Profile URL: {href}")
                            break
        
        # Method 2: Look for tax code in text content
        if not result.tax_code:
            tax_pattern = r'\b\d{10}\b'
            matches = re.findall(tax_pattern, all_text)
            if matches:
                result.tax_code = matches[0]
                logger.info(f"🎯 Found tax code in text: {matches[0]}")
        
        # Method 3: Look for Vietnamese names
        if not result.name:
            # Vietnamese name patterns
            vietnamese_patterns = [
                r'[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ\s]+',
                r'[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*'
            ]
            
            for pattern in vietnamese_patterns:
                matches = re.findall(pattern, all_text)
                for match in matches:
                    match = match.strip()
                    if len(match) > 5 and len(match) < 50:
                        # Check if it looks like a Vietnamese name
                        if any(char in match for char in ['Lê', 'Nguyễn', 'Trần', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Võ', 'Đỗ', 'Bùi', 'Đặng', 'Ngô', 'Dương', 'Lý']):
                            result.name = match
                            result.status = "found"
                            logger.info(f"👤 Found Vietnamese name: {match}")
                            break
                if result.name:
                    break
        
        # Method 4: Look for address information
        address_keywords = ['phường', 'quận', 'huyện', 'tỉnh', 'thành phố', 'xã', 'thị trấn', 'đường', 'phố']
        address_elements = soup.find_all(['p', 'div', 'span', 'td'])
        
        for elem in address_elements:
            text = elem.get_text(strip=True)
            if text and len(text) > 20:
                if any(keyword in text.lower() for keyword in address_keywords):
                    result.address = text
                    logger.info(f"🏠 Found address: {text}")
                    break
        
        # Method 5: Look for business information
        business_keywords = ['công ty', 'doanh nghiệp', 'tổ chức', 'cá nhân', 'hộ kinh doanh']
        for elem in soup.find_all(['p', 'div', 'span', 'td']):
            text = elem.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in business_keywords):
                result.business_type = text
                logger.info(f"🏢 Found business type: {text}")
                break
        
        # Method 6: Look for status information
        status_keywords = ['hoạt động', 'ngừng hoạt động', 'đang hoạt động', 'tạm nghỉ']
        for elem in soup.find_all(['p', 'div', 'span', 'td']):
            text = elem.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in status_keywords):
                result.business_status = text
                logger.info(f"📊 Found business status: {text}")
                break
        
        # Method 7: Look for dates
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        date_matches = re.findall(date_pattern, all_text)
        if date_matches:
            result.registration_date = date_matches[0]
            logger.info(f"📅 Found date: {date_matches[0]}")
        
        # Method 8: Extract additional structured data
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        result.additional_info[key] = value
        
        # Method 9: Look for specific data in divs with classes
        data_divs = soup.find_all('div', class_=re.compile(r'info|data|detail|profile'))
        for div in data_divs:
            text = div.get_text(strip=True)
            if text and len(text) > 5:
                result.additional_info[f"div_content_{len(result.additional_info)}"] = text
        
        logger.info(f"📊 Extracted {len(result.additional_info)} additional data fields")
        
        return result
    
    def batch_check(self, cccd_list: List[str]) -> List[SearchResult]:
        """
        Kiểm tra hàng loạt nhiều CCCD
        
        Args:
            cccd_list: Danh sách số CCCD cần kiểm tra
            
        Returns:
            List các kết quả
        """
        logger.info(f"🔄 Starting batch check for {len(cccd_list)} CCCDs")
        
        results = []
        for i, cccd in enumerate(cccd_list, 1):
            logger.info(f"📋 [{i}/{len(cccd_list)}] Checking: {cccd}")
            
            result = self.check_cccd(cccd)
            results.append(result)
            
            # Thêm delay giữa các request để tránh bị block
            if i < len(cccd_list):
                self._random_delay(3.0, 7.0)
        
        logger.info(f"✅ Completed batch check: {len(results)} results")
        return results
    
    def save_results(self, results: List[SearchResult], output_file: str = None):
        """
        Lưu kết quả vào file
        
        Args:
            results: Danh sách kết quả
            output_file: Đường dẫn file output
        """
        if not output_file:
            output_file = self.config.get('output_file', 'module_2_check_cccd_enhanced_output.txt')
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("MODULE 2 ENHANCED: CHECK CCCD - KẾT QUẢ TÌM KIẾM MÃ SỐ THUẾ CÁ NHÂN\n")
                f.write("=" * 80 + "\n")
                f.write(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Tổng số CCCD kiểm tra: {len(results)}\n")
                f.write(f"Proxy enabled: {self.proxy_config.get('enabled', False)}\n")
                f.write(f"Proxy type: {self.proxy_config.get('type', 'none')}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"📋 CCCD #{i}: {result.cccd}\n")
                    f.write(f"   Trạng thái: {result.status}\n")
                    f.write(f"   Phương pháp: {result.method or 'N/A'}\n")
                    f.write(f"   Thời gian phản hồi: {result.response_time:.2f}s\n")
                    
                    if result.status == 'found':
                        if result.tax_code:
                            f.write(f"   Mã số thuế: {result.tax_code}\n")
                        if result.name:
                            f.write(f"   Tên: {result.name}\n")
                        if result.address:
                            f.write(f"   Địa chỉ: {result.address}\n")
                        if result.business_type:
                            f.write(f"   Loại hình: {result.business_type}\n")
                        if result.business_status:
                            f.write(f"   Trạng thái: {result.business_status}\n")
                        if result.registration_date:
                            f.write(f"   Ngày đăng ký: {result.registration_date}\n")
                        if result.profile_url:
                            f.write(f"   URL: {result.profile_url}\n")
                        
                        if result.additional_info:
                            f.write(f"   Thông tin bổ sung:\n")
                            for key, value in result.additional_info.items():
                                f.write(f"     {key}: {value}\n")
                    
                    elif result.status == 'not_found':
                        f.write(f"   Thông báo: Không tìm thấy thông tin\n")
                    elif result.status == 'error':
                        f.write(f"   Lỗi: {result.error}\n")
                    
                    f.write("\n" + "-" * 60 + "\n\n")
            
            logger.info(f"💾 Saved results to file: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê hoạt động"""
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": (self.stats["successful_requests"] / max(1, self.stats["total_requests"])) * 100,
            "proxy_enabled": self.proxy_config.get('enabled', False),
            "proxy_type": self.proxy_config.get('type', 'none')
        }


def main():
    """Hàm test module"""
    # Cấu hình test
    config = {
        'timeout': 30,
        'max_retries': 3,
        'output_file': 'module_2_check_cccd_enhanced_output.txt'
    }
    
    # Khởi tạo module
    module = Module2CheckCCCDEnhanced(config)
    
    # Test với CCCD thực tế
    test_cccd = "031089011929"
    logger.info(f"🧪 Testing with CCCD: {test_cccd}")
    
    # Thực hiện kiểm tra
    result = module.check_cccd(test_cccd)
    
    # In kết quả
    print("\n" + "=" * 60)
    print("KẾT QUẢ TEST MODULE 2 CHECK CCCD ENHANCED")
    print("=" * 60)
    print(f"CCCD: {result.cccd}")
    print(f"Status: {result.status}")
    print(f"Tax Code: {result.tax_code}")
    print(f"Name: {result.name}")
    print(f"Address: {result.address}")
    print(f"Business Type: {result.business_type}")
    print(f"Profile URL: {result.profile_url}")
    print(f"Response Time: {result.response_time:.2f}s")
    print(f"Method: {result.method}")
    if result.error:
        print(f"Error: {result.error}")
    print("=" * 60)
    
    # Lưu kết quả
    module.save_results([result])
    
    # In thống kê
    stats = module.get_statistics()
    print("\n📊 THỐNG KÊ:")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Successful: {stats['successful_requests']}")
    print(f"Failed: {stats['failed_requests']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print(f"Proxy enabled: {stats['proxy_enabled']}")


if __name__ == "__main__":
    main()