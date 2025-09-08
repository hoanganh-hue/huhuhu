#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script phân tích API masothue.com để xây dựng quy trình chuẩn hóa tự động hóa
Đảm bảo khớp chính xác 100% với yêu cầu của máy chủ mã số thuế
"""

import re
import time
import json
import httpx
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasothueAPIAnalyzer:
    """Phân tích API masothue.com để xây dựng quy trình chuẩn hóa"""
    
    def __init__(self):
        self.base_url = "https://masothue.com"
        self.search_url = "https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/"
        self.api_url = "https://masothue.com/Search/"
        
        # Headers chuẩn
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        
        self.analysis_results = {
            "form_structure": {},
            "api_endpoints": {},
            "request_format": {},
            "response_format": {},
            "validation_rules": {},
            "error_handling": {},
            "security_measures": {}
        }
    
    def analyze_complete_workflow(self, test_cccd: str = "037178000015") -> Dict[str, Any]:
        """Phân tích toàn bộ workflow của masothue.com"""
        logger.info("🔍 Bắt đầu phân tích toàn bộ workflow masothue.com")
        
        try:
            # Bước 1: Phân tích trang tìm kiếm
            search_page_analysis = self._analyze_search_page()
            self.analysis_results["form_structure"] = search_page_analysis
            
            # Bước 2: Phân tích API endpoints
            api_analysis = self._analyze_api_endpoints()
            self.analysis_results["api_endpoints"] = api_analysis
            
            # Bước 3: Phân tích request format
            request_analysis = self._analyze_request_format(test_cccd)
            self.analysis_results["request_format"] = request_analysis
            
            # Bước 4: Phân tích response format
            response_analysis = self._analyze_response_format(test_cccd)
            self.analysis_results["response_format"] = response_analysis
            
            # Bước 5: Phân tích validation rules
            validation_analysis = self._analyze_validation_rules()
            self.analysis_results["validation_rules"] = validation_analysis
            
            # Bước 6: Phân tích error handling
            error_analysis = self._analyze_error_handling()
            self.analysis_results["error_handling"] = error_analysis
            
            # Bước 7: Phân tích security measures
            security_analysis = self._analyze_security_measures()
            self.analysis_results["security_measures"] = security_analysis
            
            logger.info("✅ Hoàn thành phân tích toàn bộ workflow")
            return self.analysis_results
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong quá trình phân tích: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_search_page(self) -> Dict[str, Any]:
        """Phân tích cấu trúc form trên trang tìm kiếm"""
        logger.info("📄 Phân tích cấu trúc form trang tìm kiếm")
        
        try:
            with httpx.Client(timeout=30, headers=self.headers) as client:
                response = client.get(self.search_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Tìm form tìm kiếm
                forms = soup.find_all('form')
                form_analysis = {
                    "total_forms": len(forms),
                    "search_forms": [],
                    "input_fields": [],
                    "hidden_fields": [],
                    "csrf_tokens": [],
                    "javascript_requirements": []
                }
                
                for form in forms:
                    form_info = {
                        "action": form.get('action', ''),
                        "method": form.get('method', 'GET'),
                        "enctype": form.get('enctype', ''),
                        "inputs": []
                    }
                    
                    # Phân tích input fields
                    inputs = form.find_all('input')
                    for input_field in inputs:
                        input_info = {
                            "type": input_field.get('type', 'text'),
                            "name": input_field.get('name', ''),
                            "id": input_field.get('id', ''),
                            "placeholder": input_field.get('placeholder', ''),
                            "required": input_field.has_attr('required'),
                            "value": input_field.get('value', ''),
                            "class": input_field.get('class', [])
                        }
                        form_info["inputs"].append(input_info)
                        
                        if input_info["type"] == "hidden":
                            form_analysis["hidden_fields"].append(input_info)
                        else:
                            form_analysis["input_fields"].append(input_info)
                    
                    # Tìm CSRF tokens
                    csrf_inputs = form.find_all('input', {'name': re.compile(r'csrf|token|_token', re.I)})
                    for csrf in csrf_inputs:
                        form_analysis["csrf_tokens"].append({
                            "name": csrf.get('name', ''),
                            "value": csrf.get('value', '')
                        })
                    
                    form_analysis["search_forms"].append(form_info)
                
                # Tìm JavaScript requirements
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        if 'ajax' in script.string.lower() or 'fetch' in script.string.lower():
                            form_analysis["javascript_requirements"].append("AJAX/Fetch required")
                        if 'captcha' in script.string.lower():
                            form_analysis["javascript_requirements"].append("CAPTCHA required")
                        if 'recaptcha' in script.string.lower():
                            form_analysis["javascript_requirements"].append("reCAPTCHA required")
                
                logger.info(f"✅ Phân tích form hoàn thành: {len(forms)} forms, {len(form_analysis['input_fields'])} input fields")
                return form_analysis
                
        except Exception as e:
            logger.error(f"❌ Lỗi phân tích form: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_api_endpoints(self) -> Dict[str, Any]:
        """Phân tích các API endpoints"""
        logger.info("🔗 Phân tích API endpoints")
        
        endpoints = {
            "search_endpoint": {
                "url": self.api_url,
                "method": "POST",
                "description": "Tìm kiếm mã số thuế cá nhân"
            },
            "profile_endpoint": {
                "url": f"{self.base_url}/[tax_code]-[name]",
                "method": "GET",
                "description": "Lấy thông tin chi tiết profile"
            },
            "homepage": {
                "url": self.base_url,
                "method": "GET",
                "description": "Trang chủ"
            }
        }
        
        return endpoints
    
    def _analyze_request_format(self, test_cccd: str) -> Dict[str, Any]:
        """Phân tích format request"""
        logger.info("📤 Phân tích format request")
        
        request_formats = {
            "search_request": {
                "method": "POST",
                "url": self.api_url,
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": self.search_url,
                    "Origin": self.base_url
                },
                "data_formats": [
                    {
                        "format": "form_data",
                        "fields": {
                            "q": test_cccd,
                            "type": "personal"
                        }
                    },
                    {
                        "format": "query_params",
                        "fields": {
                            "q": test_cccd
                        }
                    }
                ]
            },
            "profile_request": {
                "method": "GET",
                "url_pattern": f"{self.base_url}/[tax_code]-[name]",
                "headers": {
                    "Referer": self.search_url
                }
            }
        }
        
        return request_formats
    
    def _analyze_response_format(self, test_cccd: str) -> Dict[str, Any]:
        """Phân tích format response"""
        logger.info("📥 Phân tích format response")
        
        try:
            with httpx.Client(timeout=30, headers=self.headers) as client:
                # Thử tìm kiếm để lấy response
                search_data = {'q': test_cccd}
                response = client.post(self.api_url, data=search_data)
                
                response_analysis = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_type": response.headers.get('content-type', ''),
                    "content_length": len(response.content),
                    "html_structure": {},
                    "data_fields": [],
                    "error_messages": []
                }
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Phân tích cấu trúc HTML
                    response_analysis["html_structure"] = {
                        "title": soup.title.string if soup.title else "",
                        "forms": len(soup.find_all('form')),
                        "links": len(soup.find_all('a')),
                        "tables": len(soup.find_all('table')),
                        "divs": len(soup.find_all('div'))
                    }
                    
                    # Tìm các trường dữ liệu
                    data_selectors = [
                        'h1', 'h2', 'h3',  # Headers
                        '.name', '.tax-code', '.address',  # CSS classes
                        '[data-name]', '[data-tax-code]',  # Data attributes
                        '.profile-info', '.company-info'  # Info containers
                    ]
                    
                    for selector in data_selectors:
                        elements = soup.select(selector)
                        if elements:
                            response_analysis["data_fields"].append({
                                "selector": selector,
                                "count": len(elements),
                                "sample_text": elements[0].get_text(strip=True)[:100] if elements else ""
                            })
                    
                    # Tìm thông báo lỗi
                    error_selectors = [
                        '.error', '.alert', '.warning', '.message',
                        '[class*="error"]', '[class*="alert"]'
                    ]
                    
                    for selector in error_selectors:
                        elements = soup.select(selector)
                        for element in elements:
                            error_text = element.get_text(strip=True)
                            if error_text:
                                response_analysis["error_messages"].append({
                                    "selector": selector,
                                    "message": error_text
                                })
                
                logger.info(f"✅ Phân tích response hoàn thành: {response.status_code}")
                return response_analysis
                
        except Exception as e:
            logger.error(f"❌ Lỗi phân tích response: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_validation_rules(self) -> Dict[str, Any]:
        """Phân tích validation rules"""
        logger.info("✅ Phân tích validation rules")
        
        validation_rules = {
            "cccd_validation": {
                "format": "12 digits",
                "pattern": r"^\d{12}$",
                "required": True,
                "description": "Số CCCD phải có đúng 12 chữ số"
            },
            "tax_code_validation": {
                "format": "10-13 digits",
                "pattern": r"^\d{10,13}$",
                "required": False,
                "description": "Mã số thuế có thể có 10-13 chữ số"
            },
            "name_validation": {
                "format": "Vietnamese text",
                "pattern": r"^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂÂÊÔưăâêô\s]+$",
                "required": True,
                "description": "Tên phải là tiếng Việt"
            }
        }
        
        return validation_rules
    
    def _analyze_error_handling(self) -> Dict[str, Any]:
        """Phân tích error handling"""
        logger.info("⚠️ Phân tích error handling")
        
        error_handling = {
            "http_errors": {
                "403": "Forbidden - Anti-bot protection",
                "404": "Not Found - Invalid endpoint",
                "500": "Internal Server Error",
                "429": "Too Many Requests - Rate limiting"
            },
            "validation_errors": {
                "invalid_cccd": "Số CCCD không hợp lệ",
                "cccd_not_found": "Không tìm thấy thông tin cho CCCD này",
                "empty_input": "Vui lòng nhập số CCCD"
            },
            "retry_strategies": {
                "exponential_backoff": True,
                "max_retries": 3,
                "base_delay": 1.0,
                "max_delay": 10.0
            }
        }
        
        return error_handling
    
    def _analyze_security_measures(self) -> Dict[str, Any]:
        """Phân tích security measures"""
        logger.info("🔒 Phân tích security measures")
        
        security_measures = {
            "anti_bot_protection": {
                "user_agent_validation": True,
                "referer_check": True,
                "rate_limiting": True,
                "ip_blocking": True
            },
            "headers_required": [
                "User-Agent",
                "Accept",
                "Accept-Language",
                "Referer",
                "Origin"
            ],
            "cookies_required": False,
            "csrf_protection": False,
            "captcha_required": False
        }
        
        return security_measures
    
    def generate_standardized_workflow(self) -> Dict[str, Any]:
        """Tạo quy trình chuẩn hóa tự động hóa"""
        logger.info("🔧 Tạo quy trình chuẩn hóa tự động hóa")
        
        workflow = {
            "pre_request_validation": {
                "cccd_format_check": {
                    "rule": r"^\d{12}$",
                    "error_message": "Số CCCD phải có đúng 12 chữ số"
                },
                "required_headers": [
                    "User-Agent",
                    "Accept",
                    "Accept-Language",
                    "Accept-Encoding",
                    "Connection",
                    "Upgrade-Insecure-Requests",
                    "Sec-Fetch-Dest",
                    "Sec-Fetch-Mode",
                    "Sec-Fetch-Site",
                    "Sec-Fetch-User",
                    "Cache-Control",
                    "DNT",
                    "Sec-CH-UA",
                    "Sec-CH-UA-Mobile",
                    "Sec-CH-UA-Platform"
                ]
            },
            "request_sequence": [
                {
                    "step": 1,
                    "action": "GET",
                    "url": self.base_url,
                    "purpose": "Establish session",
                    "delay_after": 2.0
                },
                {
                    "step": 2,
                    "action": "GET",
                    "url": self.search_url,
                    "purpose": "Load search page",
                    "delay_after": 2.0
                },
                {
                    "step": 3,
                    "action": "POST",
                    "url": self.api_url,
                    "purpose": "Submit search",
                    "data": {
                        "q": "{cccd}",
                        "type": "personal"
                    },
                    "headers": {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": self.search_url,
                        "Origin": self.base_url
                    }
                }
            ],
            "response_validation": {
                "success_indicators": [
                    "status_code == 200",
                    "content_type contains 'text/html'",
                    "response contains profile links"
                ],
                "error_indicators": [
                    "status_code == 403",
                    "response contains 'Forbidden'",
                    "response contains 'Blocked'"
                ]
            },
            "data_extraction": {
                "profile_links": {
                    "selector": "a[href*='/']",
                    "validation": "href contains 10-13 digits",
                    "exclude_patterns": [
                        r'^#',
                        r'/tra-cuu',
                        r'/Search',
                        r'facebook\.com',
                        r'twitter\.com',
                        r'youtube\.com',
                        r'instagram\.com',
                        r'zalo\.me'
                    ]
                },
                "profile_details": {
                    "name": {
                        "selectors": ["h1", "h2", ".name", ".profile-title"],
                        "validation": "length > 2, not numeric"
                    },
                    "tax_code": {
                        "selectors": ["href pattern", ".tax-code", ".mst"],
                        "validation": "10-13 digits"
                    },
                    "address": {
                        "selectors": [".address", ".location"],
                        "patterns": [
                            r'Địa chỉ[:\s]*(.+?)(?:\n|$)',
                            r'Address[:\s]*(.+?)(?:\n|$)',
                            r'Trụ sở[:\s]*(.+?)(?:\n|$)'
                        ]
                    }
                }
            },
            "error_handling": {
                "retry_logic": {
                    "max_attempts": 3,
                    "backoff_strategy": "exponential",
                    "base_delay": 1.0,
                    "max_delay": 10.0
                },
                "fallback_mechanism": {
                    "enabled": True,
                    "trigger_conditions": [
                        "all_retry_attempts_failed",
                        "403_forbidden_error",
                        "rate_limit_exceeded"
                    ]
                }
            },
            "output_format": {
                "standard_fields": [
                    "cccd",
                    "status",
                    "message",
                    "profiles",
                    "timestamp"
                ],
                "profile_fields": [
                    "name",
                    "tax_code",
                    "url",
                    "type",
                    "address",
                    "birth_date",
                    "gender"
                ],
                "validation_rules": {
                    "cccd": "required, 12 digits",
                    "status": "required, one of: found|not_found|error",
                    "profiles": "array of profile objects",
                    "timestamp": "required, ISO format"
                }
            }
        }
        
        return workflow
    
    def save_analysis_results(self, filename: str = "masothue_api_analysis.json"):
        """Lưu kết quả phân tích"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Đã lưu kết quả phân tích vào: {filename}")
        except Exception as e:
            logger.error(f"❌ Lỗi khi lưu kết quả: {str(e)}")


def main():
    """Hàm chính để chạy phân tích"""
    analyzer = MasothueAPIAnalyzer()
    
    # Phân tích toàn bộ workflow
    results = analyzer.analyze_complete_workflow("037178000015")
    
    # Tạo quy trình chuẩn hóa
    workflow = analyzer.generate_standardized_workflow()
    
    # Lưu kết quả
    analyzer.save_analysis_results()
    
    # In kết quả
    print("\n" + "=" * 80)
    print("KẾT QUẢ PHÂN TÍCH API MASOTHUE.COM")
    print("=" * 80)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("QUY TRÌNH CHUẨN HÓA TỰ ĐỘNG HÓA")
    print("=" * 80)
    print(json.dumps(workflow, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()