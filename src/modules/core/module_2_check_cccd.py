#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 2: Check CCCD from masothue.com
"""

import requests
import time
from typing import List, Dict, Any

class Module2CheckCCCD:
    """Module for checking CCCD from masothue.com API."""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_base_url = config.get('api_base_url', 'http://localhost:8000')
        self.api_key = config.get('api_key', 'dev-api-key-123')
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        self.output_file = config.get('output_file', 'module_2_check_cccd_output.txt')
        
        # Remove trailing slash from API URL
        self.api_base_url = self.api_base_url.rstrip('/')
        self.check_endpoint = f"{self.api_base_url}/api/v1/check"
    
    def run_module(self, input_data: List[str]) -> Dict[str, Any]:
        """Run the check CCCD module."""
        
        results = []
        stats = {
            'total': len(input_data),
            'found_matches': 0,
            'success_rate': 0.0,
            'match_rate': 0.0
        }
        
        print(f"🔍 Module 2: Checking {len(input_data)} CCCD from {self.api_base_url}")
        
        for i, cccd in enumerate(input_data):
            try:
                print(f"   {i+1:3d}. Checking CCCD: {cccd}", end=" ... ")
                
                # Make API request
                payload = {
                    "cccd": cccd,
                    "async_mode": False
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "BHXH-Tools/2.0"
                }
                
                response = requests.post(
                    self.check_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results.append({
                        'cccd': cccd,
                        'result': result
                    })
                    
                    # Update stats
                    if result.get('status') == 'completed':
                        api_result = result.get('result', {})
                        if api_result.get('status') == 'found':
                            stats['found_matches'] += 1
                    
                    print("✅")
                else:
                    results.append({
                        'cccd': cccd,
                        'error': f"HTTP {response.status_code}: {response.text}"
                    })
                    print("❌")
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                results.append({
                    'cccd': cccd,
                    'error': str(e)
                })
                print("❌")
        
        # Calculate final stats
        successful_requests = len([r for r in results if 'error' not in r])
        stats['success_rate'] = (successful_requests / len(input_data)) * 100 if input_data else 0
        stats['match_rate'] = (stats['found_matches'] / len(input_data)) * 100 if input_data else 0
        
        return {
            'status': 'completed',
            'results': results,
            'stats': stats,
            'api_available': True,
            'module_available': True
        }