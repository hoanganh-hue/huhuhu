#!/usr/bin/env python3
"""
Test CCCD 031089011929 using Module 2 enhanced anti-bot capabilities
Collect all displayed data fields from masothue.com
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CCCDChecker:
    """Enhanced CCCD checker with anti-bot capabilities"""
    
    def __init__(self):
        # SOCKS5 proxy configuration
        self.proxy_config = {
            'http': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
            'https': 'socks5://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
        }
        
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
    
    def check_cccd(self, cccd: str) -> Dict[str, Any]:
        """Check CCCD and collect all data fields"""
        logger.info(f"🔍 Checking CCCD: {cccd}")
        logger.info("="*60)
        
        # Create session
        session = requests.Session()
        session.proxies.update(self.proxy_config)
        session.headers.update(self.headers)
        
        try:
            # Step 1: Get homepage to establish session
            logger.info("🍪 Getting homepage to establish session...")
            homepage_response = session.get("https://masothue.com/", timeout=15)
            logger.info(f"✅ Homepage status: {homepage_response.status_code}")
            
            # Step 2: Perform search
            logger.info(f"🔍 Searching for CCCD: {cccd}")
            search_url = f"https://masothue.com/Search/?q={cccd}&type=auto&token=NbnmgilFfL&force-search=1"
            
            # Add search-specific headers
            search_headers = self.headers.copy()
            search_headers.update({
                "Referer": "https://masothue.com/",
                "X-Requested-With": "XMLHttpRequest"
            })
            
            start_time = time.time()
            response = session.get(search_url, headers=search_headers, timeout=15)
            response_time = time.time() - start_time
            
            logger.info(f"✅ Search status: {response.status_code}")
            logger.info(f"⏱️ Response time: {response_time:.2f}s")
            logger.info(f"📊 Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # Parse and extract all data
                result = self._extract_all_data(response.text, cccd)
                result["response_time"] = response_time
                result["status"] = "success"
                return result
            else:
                return {
                    "cccd": cccd,
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return {
                "cccd": cccd,
                "status": "error",
                "error": str(e)
            }
    
    def _extract_all_data(self, html_content: str, cccd: str) -> Dict[str, Any]:
        """Extract all possible data fields from HTML content"""
        logger.info("📄 Parsing HTML content...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize result structure
        result = {
            "cccd": cccd,
            "tax_code": None,
            "name": None,
            "full_name": None,
            "address": None,
            "province": None,
            "district": None,
            "ward": None,
            "business_type": None,
            "business_status": None,
            "registration_date": None,
            "profile_url": None,
            "additional_info": {},
            "all_links": [],
            "all_text_content": "",
            "raw_html": html_content
        }
        
        # Extract all text content
        all_text = soup.get_text()
        result["all_text_content"] = all_text
        logger.info(f"📄 Total text content length: {len(all_text)} characters")
        
        # Extract all links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href and text:
                result["all_links"].append({
                    "url": href,
                    "text": text
                })
        
        logger.info(f"🔗 Found {len(result['all_links'])} links")
        
        # Method 1: Look for tax code and name in links
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
                            result["tax_code"] = potential_tax_code
                            result["name"] = text
                            result["profile_url"] = href
                            logger.info(f"🎯 Found tax code: {potential_tax_code}")
                            logger.info(f"👤 Found name: {text}")
                            logger.info(f"🔗 Profile URL: {href}")
                            break
        
        # Method 2: Look for tax code in text content
        if not result["tax_code"]:
            tax_pattern = r'\b\d{10}\b'
            matches = re.findall(tax_pattern, all_text)
            if matches:
                result["tax_code"] = matches[0]
                logger.info(f"🎯 Found tax code in text: {matches[0]}")
        
        # Method 3: Look for Vietnamese names
        if not result["name"]:
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
                            result["name"] = match
                            logger.info(f"👤 Found Vietnamese name: {match}")
                            break
                if result["name"]:
                    break
        
        # Method 4: Look for address information
        address_keywords = ['phường', 'quận', 'huyện', 'tỉnh', 'thành phố', 'xã', 'thị trấn', 'đường', 'phố']
        address_elements = soup.find_all(['p', 'div', 'span', 'td'])
        
        for elem in address_elements:
            text = elem.get_text(strip=True)
            if text and len(text) > 20:
                if any(keyword in text.lower() for keyword in address_keywords):
                    result["address"] = text
                    logger.info(f"🏠 Found address: {text}")
                    break
        
        # Method 5: Look for business information
        business_keywords = ['công ty', 'doanh nghiệp', 'tổ chức', 'cá nhân', 'hộ kinh doanh']
        for elem in soup.find_all(['p', 'div', 'span', 'td']):
            text = elem.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in business_keywords):
                result["business_type"] = text
                logger.info(f"🏢 Found business type: {text}")
                break
        
        # Method 6: Look for status information
        status_keywords = ['hoạt động', 'ngừng hoạt động', 'đang hoạt động', 'tạm nghỉ']
        for elem in soup.find_all(['p', 'div', 'span', 'td']):
            text = elem.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in status_keywords):
                result["business_status"] = text
                logger.info(f"📊 Found business status: {text}")
                break
        
        # Method 7: Look for dates
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        date_matches = re.findall(date_pattern, all_text)
        if date_matches:
            result["registration_date"] = date_matches[0]
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
                        result["additional_info"][key] = value
        
        # Method 9: Look for specific data in divs with classes
        data_divs = soup.find_all('div', class_=re.compile(r'info|data|detail|profile'))
        for div in data_divs:
            text = div.get_text(strip=True)
            if text and len(text) > 5:
                result["additional_info"][f"div_content_{len(result['additional_info'])}"] = text
        
        logger.info(f"📊 Extracted {len(result['additional_info'])} additional data fields")
        
        return result

def main():
    """Main function to test CCCD 031089011929"""
    cccd = "031089011929"
    
    logger.info("🚀 Starting CCCD check for Module 2")
    logger.info(f"Target CCCD: {cccd}")
    logger.info("="*60)
    
    checker = CCCDChecker()
    result = checker.check_cccd(cccd)
    
    # Display results
    logger.info("\n" + "="*60)
    logger.info("📊 KẾT QUẢ KIỂM TRA CCCD")
    logger.info("="*60)
    
    logger.info(f"CCCD: {result['cccd']}")
    logger.info(f"Trạng thái: {result['status']}")
    
    if result['status'] == 'success':
        logger.info(f"⏱️ Thời gian phản hồi: {result.get('response_time', 0):.2f}s")
        
        if result.get('tax_code'):
            logger.info(f"🎯 Mã số thuế: {result['tax_code']}")
        else:
            logger.info("🎯 Mã số thuế: Không tìm thấy")
        
        if result.get('name'):
            logger.info(f"👤 Tên: {result['name']}")
        else:
            logger.info("👤 Tên: Không tìm thấy")
        
        if result.get('address'):
            logger.info(f"🏠 Địa chỉ: {result['address']}")
        else:
            logger.info("🏠 Địa chỉ: Không tìm thấy")
        
        if result.get('business_type'):
            logger.info(f"🏢 Loại hình: {result['business_type']}")
        else:
            logger.info("🏢 Loại hình: Không tìm thấy")
        
        if result.get('business_status'):
            logger.info(f"📊 Trạng thái: {result['business_status']}")
        else:
            logger.info("📊 Trạng thái: Không tìm thấy")
        
        if result.get('registration_date'):
            logger.info(f"📅 Ngày đăng ký: {result['registration_date']}")
        else:
            logger.info("📅 Ngày đăng ký: Không tìm thấy")
        
        if result.get('profile_url'):
            logger.info(f"🔗 Link profile: {result['profile_url']}")
        else:
            logger.info("🔗 Link profile: Không tìm thấy")
        
        # Display additional information
        if result.get('additional_info'):
            logger.info(f"\n📋 THÔNG TIN BỔ SUNG ({len(result['additional_info'])} trường):")
            for key, value in result['additional_info'].items():
                logger.info(f"  {key}: {value}")
        
        # Display all links found
        if result.get('all_links'):
            logger.info(f"\n🔗 TẤT CẢ LINKS TÌM THẤY ({len(result['all_links'])} links):")
            for i, link in enumerate(result['all_links'][:10], 1):  # Show first 10 links
                logger.info(f"  {i}. {link['text']} -> {link['url']}")
            if len(result['all_links']) > 10:
                logger.info(f"  ... và {len(result['all_links']) - 10} links khác")
        
        # Save detailed results to file
        import json
        with open(f"cccd_{cccd}_detailed_results.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"\n💾 Kết quả chi tiết đã lưu vào: cccd_{cccd}_detailed_results.json")
        
    else:
        logger.error(f"❌ Lỗi: {result.get('error', 'Unknown error')}")
    
    logger.info("\n🏁 Hoàn thành kiểm tra CCCD")

if __name__ == "__main__":
    main()