#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 2: Check CCCD - Wrapper cho scraper masothue.com
Thay thế cho API server bị thiếu, sử dụng trực tiếp scraper
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add check_cccd to path
current_dir = Path(__file__).parent.parent.parent.parent
check_cccd_path = current_dir / "check_cccd" / "src"
sys.path.insert(0, str(check_cccd_path))

try:
    from check_cccd.scraper_fixed import scrape_cccd_sync
except ImportError:
    # Fallback nếu không import được scraper
    scrape_cccd_sync = None


class Module2CheckCCCD:
    """
    Module 2: Check CCCD từ masothue.com
    Sử dụng trực tiếp scraper thay vì API server
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Khởi tạo module
        
        Args:
            config: Cấu hình module
        """
        self.config = config
        self.api_base_url = config.get('api_base_url', 'http://localhost:8000')
        self.api_key = config.get('api_key', '')
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        self.output_file = config.get('output_file', 'module_2_check_cccd_output.txt')
        
        # Kiểm tra scraper có sẵn không
        self.scraper_available = scrape_cccd_sync is not None
        
        if not self.scraper_available:
            print("⚠️ Warning: Scraper không khả dụng, sẽ trả về dữ liệu giả")
    
    def run_module(self, input_data: List[str]) -> Dict[str, Any]:
        """
        Chạy module check CCCD
        
        Args:
            input_data: Danh sách số CCCD cần check
            
        Returns:
            Kết quả check CCCD
        """
        print(f"🔍 Module 2: Check CCCD - Xử lý {len(input_data)} CCCD")
        
        if not input_data:
            return {
                'status': 'completed',
                'results': [],
                'stats': {
                    'total': 0,
                    'found_matches': 0,
                    'success_rate': 0.0,
                    'match_rate': 0.0
                },
                'api_available': False,
                'module_available': True
            }
        
        results = []
        stats = {
            'total': len(input_data),
            'found_matches': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'success_rate': 0.0,
            'match_rate': 0.0
        }
        
        for i, cccd in enumerate(input_data):
            print(f"   {i+1:3d}. Checking CCCD: {cccd}", end=" ... ")
            
            try:
                if self.scraper_available:
                    # Sử dụng scraper thật
                    result = self._check_cccd_with_scraper(cccd)
                else:
                    # Sử dụng dữ liệu giả
                    result = self._check_cccd_mock(cccd)
                
                results.append(result)
                
                if result.get('error'):
                    stats['failed_requests'] += 1
                    print("❌")
                else:
                    stats['successful_requests'] += 1
                    api_result = result.get('result', {})
                    if api_result.get('status') == 'found':
                        stats['found_matches'] += 1
                    print("✅")
                
            except Exception as e:
                error_result = {
                    'cccd': cccd,
                    'error': str(e),
                    'result': None
                }
                results.append(error_result)
                stats['failed_requests'] += 1
                print("❌")
        
        # Tính toán thống kê
        stats['success_rate'] = (stats['successful_requests'] / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['match_rate'] = (stats['found_matches'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        return {
            'status': 'completed',
            'results': results,
            'stats': stats,
            'api_available': self.scraper_available,
            'module_available': True
        }
    
    def _check_cccd_with_scraper(self, cccd: str) -> Dict[str, Any]:
        """
        Check CCCD sử dụng scraper thật
        
        Args:
            cccd: Số CCCD cần check
            
        Returns:
            Kết quả check
        """
        try:
            # Gọi scraper
            scraper_result = scrape_cccd_sync(cccd)
            
            # Chuyển đổi format để tương thích với API
            api_result = {
                'status': 'completed',
                'result': {
                    'status': scraper_result.get('status', 'error'),
                    'matches': scraper_result.get('matches', []),
                    'fetched_at': scraper_result.get('fetched_at', datetime.utcnow().isoformat() + 'Z'),
                    'source': scraper_result.get('source', 'masothue.com')
                }
            }
            
            return {
                'cccd': cccd,
                'result': api_result,
                'error': None
            }
            
        except Exception as e:
            return {
                'cccd': cccd,
                'result': None,
                'error': str(e)
            }
    
    def _check_cccd_mock(self, cccd: str) -> Dict[str, Any]:
        """
        Check CCCD sử dụng dữ liệu giả (mock)
        
        Args:
            cccd: Số CCCD cần check
            
        Returns:
            Kết quả check giả
        """
        # Tạo dữ liệu giả dựa trên CCCD
        # Mô phỏng tỷ lệ tìm thấy ~10%
        import random
        random.seed(hash(cccd) % 1000)  # Deterministic random
        
        if random.random() < 0.1:  # 10% chance of finding
            mock_match = {
                'type': 'person_or_company',
                'name': f'Nguyễn Văn {cccd[-3:]}',
                'tax_code': f'0{cccd[-9:]}',
                'url': f'https://masothue.com/{cccd}',
                'address': f'Địa chỉ mẫu cho CCCD {cccd}',
                'role': 'Giám đốc',
                'raw_snippet': f'Thông tin mẫu cho CCCD {cccd}'
            }
            
            api_result = {
                'status': 'completed',
                'result': {
                    'status': 'found',
                    'matches': [mock_match],
                    'fetched_at': datetime.utcnow().isoformat() + 'Z',
                    'source': 'masothue.com (mock)'
                }
            }
        else:
            api_result = {
                'status': 'completed',
                'result': {
                    'status': 'not_found',
                    'matches': [],
                    'fetched_at': datetime.utcnow().isoformat() + 'Z',
                    'source': 'masothue.com (mock)'
                }
            }
        
        return {
            'cccd': cccd,
            'result': api_result,
            'error': None
        }