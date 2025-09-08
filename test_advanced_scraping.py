#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test với các phương pháp advanced scraping
Để bypass anti-bot protection và lấy dữ liệu thực tế
"""

import httpx
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedScraper:
    """Advanced scraper với nhiều phương pháp bypass anti-bot"""
    
    def __init__(self):
        self.base_url = "https://masothue.com"
        self.search_url = "https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/"
        self.api_url = "https://masothue.com/Search/"
        
        # Nhiều User-Agent khác nhau
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Test CCCDs
        self.test_cccds = [
            "001087016369",
            "001184032114", 
            "001098021288",
            "001094001628",
            "036092002342"
        ]
    
    def get_random_headers(self) -> Dict[str, str]:
        """Tạo headers ngẫu nhiên"""
        user_agent = random.choice(self.user_agents)
        
        return {
            'User-Agent': user_agent,
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
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"'
        }
    
    def method_1_session_based(self, cccd: str) -> Dict[str, Any]:
        """Phương pháp 1: Session-based với cookies"""
        logger.info(f"🔄 Method 1: Session-based cho CCCD {cccd}")
        
        try:
            with httpx.Client(timeout=30, headers=self.get_random_headers()) as client:
                # Bước 1: Truy cập homepage
                logger.info("🌐 Bước 1: Truy cập homepage")
                homepage_response = client.get(self.base_url)
                logger.info(f"Homepage status: {homepage_response.status_code}")
                
                if homepage_response.status_code == 200:
                    time.sleep(random.uniform(2, 4))
                    
                    # Bước 2: Truy cập search page
                    logger.info("🔍 Bước 2: Truy cập search page")
                    search_response = client.get(self.search_url)
                    logger.info(f"Search page status: {search_response.status_code}")
                    
                    if search_response.status_code == 200:
                        time.sleep(random.uniform(2, 4))
                        
                        # Bước 3: Thực hiện search
                        logger.info("📤 Bước 3: Thực hiện search")
                        search_data = {'q': cccd, 'type': 'personal'}
                        post_headers = self.get_random_headers()
                        post_headers.update({
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Referer': self.search_url,
                            'Origin': self.base_url
                        })
                        
                        api_response = client.post(self.api_url, data=search_data, headers=post_headers)
                        logger.info(f"API response status: {api_response.status_code}")
                        
                        if api_response.status_code == 200:
                            return self.parse_response(api_response.text, cccd)
                        else:
                            return {"status": "error", "message": f"API error: {api_response.status_code}"}
                    else:
                        return {"status": "error", "message": f"Search page error: {search_response.status_code}"}
                else:
                    return {"status": "error", "message": f"Homepage error: {homepage_response.status_code}"}
                    
        except Exception as e:
            return {"status": "error", "message": f"Method 1 error: {str(e)}"}
    
    def method_2_direct_api(self, cccd: str) -> Dict[str, Any]:
        """Phương pháp 2: Direct API call"""
        logger.info(f"🔄 Method 2: Direct API cho CCCD {cccd}")
        
        try:
            with httpx.Client(timeout=30, headers=self.get_random_headers()) as client:
                # Thử GET request trực tiếp
                search_url = f"{self.api_url}?q={cccd}"
                response = client.get(search_url)
                logger.info(f"Direct API status: {response.status_code}")
                
                if response.status_code == 200:
                    return self.parse_response(response.text, cccd)
                else:
                    return {"status": "error", "message": f"Direct API error: {response.status_code}"}
                    
        except Exception as e:
            return {"status": "error", "message": f"Method 2 error: {str(e)}"}
    
    def method_3_mobile_headers(self, cccd: str) -> Dict[str, Any]:
        """Phương pháp 3: Mobile headers"""
        logger.info(f"🔄 Method 3: Mobile headers cho CCCD {cccd}")
        
        try:
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            with httpx.Client(timeout=30, headers=mobile_headers) as client:
                # Truy cập search page
                search_response = client.get(self.search_url)
                logger.info(f"Mobile search page status: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    time.sleep(random.uniform(1, 3))
                    
                    # Thực hiện search
                    search_data = {'q': cccd}
                    post_headers = mobile_headers.copy()
                    post_headers.update({
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': self.search_url
                    })
                    
                    api_response = client.post(self.api_url, data=search_data, headers=post_headers)
                    logger.info(f"Mobile API status: {api_response.status_code}")
                    
                    if api_response.status_code == 200:
                        return self.parse_response(api_response.text, cccd)
                    else:
                        return {"status": "error", "message": f"Mobile API error: {api_response.status_code}"}
                else:
                    return {"status": "error", "message": f"Mobile search page error: {search_response.status_code}"}
                    
        except Exception as e:
            return {"status": "error", "message": f"Method 3 error: {str(e)}"}
    
    def method_4_curl_headers(self, cccd: str) -> Dict[str, Any]:
        """Phương pháp 4: Curl-like headers"""
        logger.info(f"🔄 Method 4: Curl-like headers cho CCCD {cccd}")
        
        try:
            curl_headers = {
                'User-Agent': 'curl/7.68.0',
                'Accept': '*/*',
                'Accept-Language': 'vi-VN,vi;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            with httpx.Client(timeout=30, headers=curl_headers) as client:
                # Thử GET request
                search_url = f"{self.api_url}?q={cccd}"
                response = client.get(search_url)
                logger.info(f"Curl API status: {response.status_code}")
                
                if response.status_code == 200:
                    return self.parse_response(response.text, cccd)
                else:
                    return {"status": "error", "message": f"Curl API error: {response.status_code}"}
                    
        except Exception as e:
            return {"status": "error", "message": f"Method 4 error: {str(e)}"}
    
    def parse_response(self, html: str, cccd: str) -> Dict[str, Any]:
        """Parse response HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Tìm kiếm các link profile
            profile_links = []
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if href and self.is_profile_link(href):
                    profile_info = self.extract_profile_info(link, href)
                    if profile_info:
                        profile_links.append(profile_info)
            
            if profile_links:
                return {
                    "cccd": cccd,
                    "status": "found",
                    "message": f"Tìm thấy {len(profile_links)} kết quả",
                    "profiles": profile_links,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "cccd": cccd,
                    "status": "not_found",
                    "message": "Không tìm thấy thông tin mã số thuế",
                    "profiles": [],
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "cccd": cccd,
                "status": "error",
                "message": f"Parse error: {str(e)}",
                "profiles": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def is_profile_link(self, href: str) -> bool:
        """Kiểm tra link profile"""
        if not href:
            return False
        
        # Loại bỏ các link không phải profile
        exclude_patterns = [
            r'^#', r'/tra-cuu', r'/Search',
            r'facebook\.com', r'twitter\.com', r'youtube\.com',
            r'instagram\.com', r'zalo\.me'
        ]
        
        import re
        for pattern in exclude_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
        
        # Kiểm tra xem có chứa mã số thuế không
        return bool(re.search(r'\d{10,13}', href))
    
    def extract_profile_info(self, link_element, href: str) -> Dict[str, Any]:
        """Trích xuất thông tin profile"""
        try:
            name = link_element.get_text(strip=True)
            if not name or len(name) < 2:
                return None
            
            import re
            tax_code_match = re.search(r'(\d{10,13})', href)
            tax_code = tax_code_match.group(1) if tax_code_match else None
            
            # Chuẩn hóa URL
            if href.startswith('/'):
                url = f"{self.base_url}{href}"
            elif href.startswith('http'):
                url = href
            else:
                url = f"{self.base_url}/{href}"
            
            return {
                "name": name,
                "tax_code": tax_code or "",
                "url": url,
                "type": "personal"
            }
            
        except Exception as e:
            logger.warning(f"Lỗi extract profile: {str(e)}")
            return None
    
    def test_all_methods(self, cccd: str) -> Dict[str, Any]:
        """Test tất cả phương pháp cho một CCCD"""
        logger.info(f"🧪 Test tất cả phương pháp cho CCCD: {cccd}")
        
        methods = [
            ("method_1_session_based", self.method_1_session_based),
            ("method_2_direct_api", self.method_2_direct_api),
            ("method_3_mobile_headers", self.method_3_mobile_headers),
            ("method_4_curl_headers", self.method_4_curl_headers)
        ]
        
        results = {}
        
        for method_name, method_func in methods:
            try:
                logger.info(f"🔄 Thử {method_name}")
                result = method_func(cccd)
                results[method_name] = result
                
                if result.get("status") == "found":
                    logger.info(f"✅ {method_name} thành công!")
                    break
                else:
                    logger.info(f"❌ {method_name} thất bại: {result.get('message', 'Unknown error')}")
                
                # Delay giữa các phương pháp
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"❌ {method_name} error: {str(e)}")
                results[method_name] = {"status": "error", "message": str(e)}
        
        return results
    
    def run_comprehensive_test(self):
        """Chạy test toàn diện"""
        logger.info("🚀 Bắt đầu test toàn diện với advanced scraping")
        logger.info("=" * 80)
        
        all_results = {}
        
        for i, cccd in enumerate(self.test_cccds, 1):
            logger.info(f"\n📋 [{i}/{len(self.test_cccds)}] Test CCCD: {cccd}")
            logger.info("-" * 60)
            
            results = self.test_all_methods(cccd)
            all_results[cccd] = results
            
            # Delay giữa các CCCD
            if i < len(self.test_cccds):
                delay = random.uniform(5, 8)
                logger.info(f"⏳ Chờ {delay:.1f}s trước khi test CCCD tiếp theo...")
                time.sleep(delay)
        
        # In tổng kết
        self.print_summary(all_results)
        
        # Lưu kết quả
        self.save_results(all_results)
        
        return all_results
    
    def print_summary(self, all_results: Dict[str, Any]):
        """In tổng kết"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 TỔNG KẾT ADVANCED SCRAPING TEST")
        logger.info("=" * 80)
        
        total_cccds = len(all_results)
        successful_cccds = 0
        total_profiles = 0
        
        for cccd, methods_results in all_results.items():
            logger.info(f"\n📋 CCCD: {cccd}")
            found_any = False
            
            for method_name, result in methods_results.items():
                status = result.get("status", "error")
                if status == "found":
                    found_any = True
                    profiles_count = len(result.get("profiles", []))
                    total_profiles += profiles_count
                    logger.info(f"   ✅ {method_name}: {profiles_count} profiles")
                else:
                    logger.info(f"   ❌ {method_name}: {result.get('message', 'Failed')}")
            
            if found_any:
                successful_cccds += 1
        
        success_rate = (successful_cccds / total_cccds) * 100
        
        logger.info(f"\n📊 TỔNG KẾT:")
        logger.info(f"   Tổng số CCCD: {total_cccds}")
        logger.info(f"   Thành công: {successful_cccds}")
        logger.info(f"   Tỷ lệ thành công: {success_rate:.1f}%")
        logger.info(f"   Tổng số profiles: {total_profiles}")
        
        if success_rate >= 80:
            logger.info("✅ KẾT QUẢ: Xuất sắc - Advanced scraping hiệu quả!")
        elif success_rate >= 60:
            logger.info("⚠️ KẾT QUẢ: Tốt - Advanced scraping hoạt động ổn định")
        elif success_rate >= 40:
            logger.info("⚠️ KẾT QUẢ: Trung bình - Cần cải thiện")
        else:
            logger.info("❌ KẾT QUẢ: Kém - Anti-bot protection quá mạnh")
        
        logger.info("=" * 80)
    
    def save_results(self, all_results: Dict[str, Any]):
        """Lưu kết quả"""
        try:
            with open('advanced_scraping_results.json', 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info("💾 Đã lưu kết quả vào: advanced_scraping_results.json")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi lưu kết quả: {str(e)}")


def main():
    """Hàm chính"""
    print("🧪 ADVANCED SCRAPING TEST")
    print("🎯 Test với nhiều phương pháp bypass anti-bot protection")
    print("=" * 80)
    
    scraper = AdvancedScraper()
    results = scraper.run_comprehensive_test()
    
    # Kết luận
    total_cccds = len(results)
    successful_cccds = sum(1 for cccd_results in results.values() 
                          if any(result.get("status") == "found" 
                                for result in cccd_results.values()))
    
    success_rate = (successful_cccds / total_cccds) * 100
    
    print(f"\n🎉 KẾT LUẬN:")
    if success_rate >= 80:
        print("✅ Advanced scraping thành công!")
        print("✅ Tìm thấy nhiều mã số thuế thực tế")
    elif success_rate >= 60:
        print("⚠️ Advanced scraping hoạt động tốt")
        print("⚠️ Tìm thấy một số mã số thuế")
    elif success_rate >= 40:
        print("⚠️ Advanced scraping hoạt động trung bình")
        print("⚠️ Tìm thấy ít mã số thuế")
    else:
        print("❌ Advanced scraping cũng bị chặn")
        print("❌ Anti-bot protection quá mạnh")
    
    print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")


if __name__ == "__main__":
    main()