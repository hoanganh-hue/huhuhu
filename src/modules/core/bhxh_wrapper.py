#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BHXH Wrapper - Tra cứu thông tin BHXH
"""

from typing import List, Dict, Any
from datetime import datetime


class BHXHWrapper:
    """Wrapper cho BHXH lookup"""
    
    def __init__(self, captcha_api_key: str = None):
        self.captcha_api_key = captcha_api_key
    
    def lookup_bhxh_info(self, input_data: List[Dict]) -> Dict[str, Any]:
        """Tra cứu thông tin BHXH"""
        
        if not self.captcha_api_key or self.captcha_api_key == "your_2captcha_api_key_here":
            return {
                'success': False,
                'error': 'CAPTCHA API key chưa được cấu hình',
                'data': [],
                'processed_count': 0
            }
        
        # Mock data - trong thực tế sẽ gọi API BHXH
        bhxh_data = []
        
        for item in input_data:
            cccd = item.get('cccd', '')
            name = item.get('name', '')
            
            # Tạo mock BHXH data
            mock_bhxh = {
                'cccd': cccd,
                'name': name,
                'bhxh_number': f"BHXH{cccd[-6:]}",
                'phone': f"0{cccd[-9:]}",
                'source': 'bhxh.gov.vn (mock)',
                'fetched_at': datetime.now().isoformat()
            }
            
            bhxh_data.append(mock_bhxh)
        
        return {
            'success': True,
            'data': bhxh_data,
            'processed_count': len(bhxh_data)
        }