#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doanh Nghiệp Wrapper - Tra cứu thông tin doanh nghiệp
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


class DoanhNghiepWrapper:
    """Wrapper cho doanh nghiệp lookup"""
    
    def __init__(self):
        pass
    
    def test_cccd_list_with_api(self, cccd_list: List[str]) -> pd.DataFrame:
        """Test CCCD list với API doanh nghiệp"""
        
        results = []
        
        for cccd in cccd_list:
            # Mock data - trong thực tế sẽ gọi API thongtindoanhnghiep.co
            result = {
                'cccd': cccd,
                'company_name': f'Công ty TNHH {cccd[-4:]}',
                'representative': f'Nguyễn Văn {cccd[-3:]}',
                'address': f'Địa chỉ mẫu cho CCCD {cccd}',
                'phone': f'0{cccd[-9:]}',
                'mst': f'0{cccd[-9:]}',
                'status': 'Hoạt động',
                'api_response_status': 'Success',
                'fetched_at': datetime.now().isoformat()
            }
            
            results.append(result)
        
        return pd.DataFrame(results)