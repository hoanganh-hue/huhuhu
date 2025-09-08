#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 7: Advanced API Client với Proxy Management
Giải quyết vấn đề anti-bot protection và tăng tính ẩn danh

Tính năng:
- Proxy rotation (SOCKS5/HTTP) tự động
- Dynamic payload generation
- Retry logic với exponential backoff
- Session management
- Comprehensive logging
- Integration với modules hiện có
"""

import asyncio
import httpx
import itertools
import random
import json
import uuid
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

# Import Faker for dynamic data generation
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    print("⚠️ Faker not available. Install with: pip install faker")

# Import proxybroker for proxy management
try:
    from proxybroker import Broker
    PROXYBROKER_AVAILABLE = True
except ImportError:
    PROXYBROKER_AVAILABLE = False
    print("⚠️ ProxyBroker not available. Install with: pip install proxybroker")

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyType(Enum):
    """Loại proxy"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

class RequestStatus(Enum):
    """Trạng thái request"""
    SUCCESS = "success"
    ERROR = "error"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    PROXY_ERROR = "proxy_error"

@dataclass
class ProxyInfo:
    """Thông tin proxy"""
    url: str
    proxy_type: ProxyType
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    is_working: bool = True
    last_used: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0

@dataclass
class RequestResult:
    """Kết quả request"""
    url: str
    method: str
    status_code: int
    status: RequestStatus
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    proxy_used: Optional[ProxyInfo] = None
    processing_time: float = 0.0
    retry_count: int = 0
    timestamp: str = ""

class ProxyRotator:
    """Quản lý danh sách proxy và xoay proxy tự động"""
    
    def __init__(self, proxy_file: str = "config/proxies.txt"):
        self.proxy_file = Path(proxy_file)
        self.proxies: List[ProxyInfo] = []
        self._cycle = None
        self._current_index = 0
        
        # Load proxies từ file
        self._load_proxies()
        
        logger.info(f"✅ ProxyRotator khởi tạo với {len(self.proxies)} proxies")
    
    def _load_proxies(self):
        """Load proxies từ file"""
        if not self.proxy_file.exists():
            logger.warning(f"⚠️ File proxy không tồn tại: {self.proxy_file}")
            self._create_default_proxies()
            return
        
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            for line in lines:
                proxy_info = self._parse_proxy_line(line)
                if proxy_info:
                    self.proxies.append(proxy_info)
            
            if self.proxies:
                self._cycle = itertools.cycle(self.proxies)
                logger.info(f"✅ Loaded {len(self.proxies)} proxies từ {self.proxy_file}")
            else:
                logger.warning("⚠️ Không có proxy hợp lệ nào được load")
                self._create_default_proxies()
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi load proxies: {str(e)}")
            self._create_default_proxies()
    
    def _parse_proxy_line(self, line: str) -> Optional[ProxyInfo]:
        """Parse một dòng proxy"""
        try:
            # Format: http://user:pass@host:port hoặc socks5://host:port
            if '://' not in line:
                return None
            
            protocol, rest = line.split('://', 1)
            
            # Xử lý authentication
            if '@' in rest:
                auth_part, host_port = rest.split('@', 1)
                username, password = auth_part.split(':', 1)
            else:
                username, password = None, None
                host_port = rest
            
            # Xử lý host:port
            if ':' not in host_port:
                return None
            
            host, port = host_port.split(':', 1)
            port = int(port)
            
            # Xác định proxy type
            proxy_type = ProxyType.HTTP
            if protocol.lower() == 'https':
                proxy_type = ProxyType.HTTPS
            elif protocol.lower() == 'socks4':
                proxy_type = ProxyType.SOCKS4
            elif protocol.lower() == 'socks5':
                proxy_type = ProxyType.SOCKS5
            
            return ProxyInfo(
                url=line,
                proxy_type=proxy_type,
                host=host,
                port=port,
                username=username,
                password=password
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Không thể parse proxy line: {line} - {str(e)}")
            return None
    
    def _create_default_proxies(self):
        """Tạo danh sách proxy mặc định (free proxies)"""
        default_proxies = [
            "http://8.210.83.33:80",
            "http://47.74.152.29:8888",
            "http://103.152.112.145:80",
            "http://185.162.251.76:80",
            "http://103.152.112.162:80"
        ]
        
        for proxy_url in default_proxies:
            proxy_info = self._parse_proxy_line(proxy_url)
            if proxy_info:
                self.proxies.append(proxy_info)
        
        if self.proxies:
            self._cycle = itertools.cycle(self.proxies)
            logger.info(f"✅ Tạo {len(self.proxies)} default proxies")
    
    def get_proxy(self, strategy: str = "random") -> Optional[ProxyInfo]:
        """Lấy proxy theo strategy"""
        if not self.proxies:
            logger.warning("⚠️ Không có proxy nào available")
            return None
        
        if strategy == "random":
            return random.choice(self.proxies)
        elif strategy == "round_robin":
            if self._cycle:
                return next(self._cycle)
        elif strategy == "best_performance":
            # Chọn proxy có success rate cao nhất
            working_proxies = [p for p in self.proxies if p.is_working]
            if working_proxies:
                return max(working_proxies, key=lambda p: p.success_count / max(1, p.success_count + p.error_count))
        
        return random.choice(self.proxies)
    
    def mark_proxy_success(self, proxy: ProxyInfo):
        """Đánh dấu proxy thành công"""
        proxy.success_count += 1
        proxy.last_used = datetime.now()
        proxy.is_working = True
    
    def mark_proxy_error(self, proxy: ProxyInfo):
        """Đánh dấu proxy lỗi"""
        proxy.error_count += 1
        proxy.last_used = datetime.now()
        
        # Nếu error rate quá cao, đánh dấu không working
        total_requests = proxy.success_count + proxy.error_count
        if total_requests > 5 and proxy.error_count / total_requests > 0.8:
            proxy.is_working = False
            logger.warning(f"⚠️ Proxy {proxy.url} bị đánh dấu không working")
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê proxy"""
        total = len(self.proxies)
        working = len([p for p in self.proxies if p.is_working])
        
        return {
            "total_proxies": total,
            "working_proxies": working,
            "broken_proxies": total - working,
            "success_rate": sum(p.success_count for p in self.proxies) / max(1, sum(p.success_count + p.error_count for p in self.proxies))
        }

class DynamicDataGenerator:
    """Tạo dữ liệu động cho payload"""
    
    def __init__(self, locale: str = "vi_VN"):
        self.locale = locale
        if FAKER_AVAILABLE:
            self.faker = Faker(locale)
        else:
            self.faker = None
            logger.warning("⚠️ Faker không available, sử dụng random data")
    
    def generate_info(self) -> Dict[str, Any]:
        """Tạo thông tin động"""
        if self.faker:
            return {
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "session_id": str(uuid.uuid4())[:8],
                "user_agent": self.faker.user_agent(),
                "fullname": self.faker.name(),
                "address": self.faker.address(),
                "phone": self.faker.phone_number(),
                "email": self.faker.email(),
                "company": self.faker.company(),
                "extra_data": self.faker.sentence(nb_words=8),
                "random_number": random.randint(1000, 9999),
                "browser_fingerprint": self._generate_browser_fingerprint()
            }
        else:
            return {
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "session_id": str(uuid.uuid4())[:8],
                "random_string": f"data_{random.randint(10000, 99999)}",
                "random_number": random.randint(1000, 9999),
                "extra_data": f"dynamic_content_{int(time.time())}"
            }
    
    def _generate_browser_fingerprint(self) -> Dict[str, Any]:
        """Tạo browser fingerprint"""
        if not self.faker:
            return {"type": "fallback"}
        
        return {
            "screen_resolution": f"{random.randint(1024, 1920)}x{random.randint(768, 1080)}",
            "timezone": self.faker.timezone(),
            "language": "vi-VN",
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "cookie_enabled": True,
            "do_not_track": random.choice([True, False])
        }

class AdvancedAPIClient:
    """Advanced API Client với proxy management và dynamic payload"""
    
    def __init__(self, 
                 timeout: int = 30,
                 max_retries: int = 3,
                 proxy_file: str = "config/proxies.txt",
                 proxy_strategy: str = "random",
                 enable_dynamic_data: bool = True):
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.proxy_strategy = proxy_strategy
        self.enable_dynamic_data = enable_dynamic_data
        
        # Khởi tạo components
        self.proxy_rotator = ProxyRotator(proxy_file)
        self.data_generator = DynamicDataGenerator()
        
        # HTTP client
        self.client = None
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "proxy_rotations": 0,
            "average_response_time": 0.0
        }
        
        logger.info("✅ AdvancedAPIClient khởi tạo thành công")
        logger.info(f"🔧 Timeout: {timeout}s, Max Retries: {max_retries}")
        logger.info(f"🔄 Proxy Strategy: {proxy_strategy}")
        logger.info(f"📊 Dynamic Data: {'Enabled' if enable_dynamic_data else 'Disabled'}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    async def request(self,
                     method: str,
                     url: str,
                     json_body: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     params: Optional[Dict[str, Any]] = None,
                     **extra) -> RequestResult:
        """Thực hiện request với proxy rotation và dynamic payload"""
        
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        # Tạo headers mặc định
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        if headers:
            default_headers.update(headers)
        
        # Thêm dynamic data vào payload
        if json_body and self.enable_dynamic_data:
            json_body = json_body.copy()
            json_body["dynamic_info"] = self.data_generator.generate_info()
        
        # Thực hiện request với retry logic
        last_error = None
        proxy_used = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Lấy proxy
                proxy = self.proxy_rotator.get_proxy(self.proxy_strategy)
                if not proxy:
                    raise Exception("Không có proxy available")
                
                proxy_used = proxy
                self.stats["proxy_rotations"] += 1
                
                logger.info(f"🔄 [{attempt+1}/{self.max_retries+1}] Request {method} {url} via proxy {proxy.host}:{proxy.port}")
                
                # Tạo client mới với proxy cho mỗi request
                proxies = {
                    "http://": proxy.url,
                    "https://": proxy.url
                }
                
                # Tạo client với proxy
                proxy_client = httpx.AsyncClient(timeout=self.timeout, proxies=proxies)
                try:
                    # Thực hiện request
                    response = await proxy_client.request(
                        method=method,
                        url=url,
                        json=json_body,
                        headers=default_headers,
                        params=params,
                        **extra
                    )
                finally:
                    await proxy_client.aclose()
                
                processing_time = time.time() - start_time
                
                # Đánh dấu proxy thành công
                self.proxy_rotator.mark_proxy_success(proxy)
                
                # Cập nhật stats
                self.stats["successful_requests"] += 1
                self._update_average_response_time(processing_time)
                
                # Parse response
                try:
                    response_data = response.json()
                except:
                    response_data = {"text": response.text}
                
                logger.info(f"✅ Request thành công: {response.status_code} - {processing_time:.2f}s")
                
                return RequestResult(
                    url=url,
                    method=method,
                    status_code=response.status_code,
                    status=RequestStatus.SUCCESS,
                    response_data=response_data,
                    proxy_used=proxy,
                    processing_time=processing_time,
                    retry_count=attempt,
                    timestamp=datetime.now().isoformat()
                )
                
            except httpx.HTTPStatusError as e:
                processing_time = time.time() - start_time
                last_error = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                
                if proxy_used:
                    self.proxy_rotator.mark_proxy_error(proxy_used)
                
                if e.response.status_code == 403:
                    logger.warning(f"🚫 Request bị chặn (403): {url}")
                    if attempt == self.max_retries:
                        self.stats["failed_requests"] += 1
                        return RequestResult(
                            url=url,
                            method=method,
                            status_code=e.response.status_code,
                            status=RequestStatus.BLOCKED,
                            error_message=last_error,
                            proxy_used=proxy_used,
                            processing_time=processing_time,
                            retry_count=attempt,
                            timestamp=datetime.now().isoformat()
                        )
                else:
                    logger.warning(f"⚠️ HTTP Error {e.response.status_code}: {url}")
                    if attempt == self.max_retries:
                        self.stats["failed_requests"] += 1
                        return RequestResult(
                            url=url,
                            method=method,
                            status_code=e.response.status_code,
                            status=RequestStatus.ERROR,
                            error_message=last_error,
                            proxy_used=proxy_used,
                            processing_time=processing_time,
                            retry_count=attempt,
                            timestamp=datetime.now().isoformat()
                        )
                
            except httpx.RequestError as e:
                processing_time = time.time() - start_time
                last_error = f"Request Error: {str(e)}"
                
                if proxy_used:
                    self.proxy_rotator.mark_proxy_error(proxy_used)
                
                logger.warning(f"⚠️ Request Error: {str(e)}")
                if attempt == self.max_retries:
                    self.stats["failed_requests"] += 1
                    return RequestResult(
                        url=url,
                        method=method,
                        status_code=0,
                        status=RequestStatus.PROXY_ERROR,
                        error_message=last_error,
                        proxy_used=proxy_used,
                        processing_time=processing_time,
                        retry_count=attempt,
                        timestamp=datetime.now().isoformat()
                    )
            
            except Exception as e:
                processing_time = time.time() - start_time
                last_error = f"Unexpected Error: {str(e)}"
                
                if proxy_used:
                    self.proxy_rotator.mark_proxy_error(proxy_used)
                
                logger.error(f"❌ Unexpected Error: {str(e)}")
                if attempt == self.max_retries:
                    self.stats["failed_requests"] += 1
                    return RequestResult(
                        url=url,
                        method=method,
                        status_code=0,
                        status=RequestStatus.ERROR,
                        error_message=last_error,
                        proxy_used=proxy_used,
                        processing_time=processing_time,
                        retry_count=attempt,
                        timestamp=datetime.now().isoformat()
                    )
            
            # Delay trước khi retry
            if attempt < self.max_retries:
                delay = (2 ** attempt) + random.uniform(0, 1)
                logger.info(f"⏳ Chờ {delay:.1f}s trước khi retry...")
                await asyncio.sleep(delay)
        
        # Nếu đến đây thì tất cả retry đều thất bại
        processing_time = time.time() - start_time
        self.stats["failed_requests"] += 1
        
        return RequestResult(
            url=url,
            method=method,
            status_code=0,
            status=RequestStatus.ERROR,
            error_message=f"Tất cả {self.max_retries + 1} attempts đều thất bại: {last_error}",
            proxy_used=proxy_used,
            processing_time=processing_time,
            retry_count=self.max_retries,
            timestamp=datetime.now().isoformat()
        )
    
    def _update_average_response_time(self, new_time: float):
        """Cập nhật thời gian response trung bình"""
        total_successful = self.stats["successful_requests"]
        if total_successful == 1:
            self.stats["average_response_time"] = new_time
        else:
            current_avg = self.stats["average_response_time"]
            self.stats["average_response_time"] = (current_avg * (total_successful - 1) + new_time) / total_successful
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê client"""
        proxy_stats = self.proxy_rotator.get_stats()
        
        return {
            "client_stats": self.stats,
            "proxy_stats": proxy_stats,
            "success_rate": self.stats["successful_requests"] / max(1, self.stats["total_requests"]) * 100
        }
    
    async def test_proxy(self, proxy: ProxyInfo, test_url: str = "https://httpbin.org/ip") -> bool:
        """Test proxy có hoạt động không"""
        try:
            proxies = {
                "http://": proxy.url,
                "https://": proxy.url
            }
            
            response = await self.client.get(test_url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Proxy {proxy.host}:{proxy.port} hoạt động tốt")
                return True
            else:
                logger.warning(f"⚠️ Proxy {proxy.host}:{proxy.port} trả về {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Proxy {proxy.host}:{proxy.port} lỗi: {str(e)}")
            return False

class ProxyManager:
    """Quản lý proxy pool và tự động refresh"""
    
    def __init__(self, proxy_file: str = "config/proxies.txt"):
        self.proxy_file = Path(proxy_file)
        self.proxy_file.parent.mkdir(parents=True, exist_ok=True)
    
    async def fetch_free_proxies(self, limit: int = 50) -> List[str]:
        """Lấy proxy miễn phí từ proxybroker"""
        if not PROXYBROKER_AVAILABLE:
            logger.warning("⚠️ ProxyBroker không available, sử dụng default proxies")
            return self._get_default_proxies()
        
        logger.info(f"🔄 Đang tìm {limit} proxy miễn phí...")
        
        try:
            broker = Broker()
            proxies = []
            
            async def collector():
                async for proxy in broker:
                    if proxy.host and proxy.port:
                        # Chỉ lấy HTTPS và SOCKS5
                        if proxy.types & {'HTTPS', 'SOCKS5'}:
                            line = f"{proxy.schema}://{proxy.host}:{proxy.port}"
                            proxies.append(line)
                            logger.info(f"✔ Tìm thấy proxy: {line}")
                        if len(proxies) >= limit:
                            break
            
            # Tìm proxy trong 60s
            task = asyncio.create_task(
                broker.find(types=['HTTPS', 'SOCKS5'], limit=limit, timeout=60)
            )
            await asyncio.gather(task, collector())
            
            logger.info(f"✅ Tìm thấy {len(proxies)} proxy miễn phí")
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi tìm proxy: {str(e)}")
            return self._get_default_proxies()
    
    def _get_default_proxies(self) -> List[str]:
        """Lấy danh sách proxy mặc định"""
        return [
            "http://8.210.83.33:80",
            "http://47.74.152.29:8888",
            "http://103.152.112.145:80",
            "http://185.162.251.76:80",
            "http://103.152.112.162:80",
            "http://47.74.152.29:8888",
            "http://103.152.112.145:80",
            "http://185.162.251.76:80"
        ]
    
    async def save_proxies(self, proxies: List[str]):
        """Lưu danh sách proxy vào file"""
        try:
            with open(self.proxy_file, 'w', encoding='utf-8') as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            
            logger.info(f"💾 Đã lưu {len(proxies)} proxy vào {self.proxy_file}")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi lưu proxy: {str(e)}")
    
    async def refresh_proxies(self, limit: int = 50):
        """Refresh danh sách proxy"""
        logger.info("🔄 Bắt đầu refresh proxy pool...")
        
        proxies = await self.fetch_free_proxies(limit)
        await self.save_proxies(proxies)
        
        logger.info("✅ Hoàn thành refresh proxy pool")

# Utility functions
async def create_api_client(proxy_file: str = "config/proxies.txt") -> AdvancedAPIClient:
    """Tạo API client với cấu hình mặc định"""
    return AdvancedAPIClient(proxy_file=proxy_file)

async def refresh_proxy_pool(proxy_file: str = "config/proxies.txt", limit: int = 50):
    """Refresh proxy pool"""
    manager = ProxyManager(proxy_file)
    await manager.refresh_proxies(limit)

# Example usage
async def main():
    """Ví dụ sử dụng AdvancedAPIClient"""
    
    # Tạo API client
    async with AdvancedAPIClient() as client:
        
        # Test với masothue.com
        result = await client.request(
            method="GET",
            url="https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/",
            json_body={"test": "data"}
        )
        
        print(f"Status: {result.status.value}")
        print(f"Status Code: {result.status_code}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        print(f"Proxy Used: {result.proxy_used.host if result.proxy_used else 'None'}")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
        
        # In stats
        stats = client.get_stats()
        print(f"\nStats: {json.dumps(stats, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())