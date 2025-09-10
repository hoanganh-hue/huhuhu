#!/usr/bin/env python3
"""
Monitor tiến độ chạy toàn bộ 10,000 CCCD tối ưu
"""

import time
import re
import os
from datetime import datetime

def monitor_progress():
    """Monitor tiến độ"""
    print("🚀 MONITORING FULL OPTIMIZED CCCD LOOKUP (10,000 RECORDS)")
    print("=" * 60)
    
    last_processed = 0
    start_time = datetime.now()
    
    while True:
        try:
            # Đọc log file
            if os.path.exists('logs/system.log'):
                with open('logs/system.log', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Tìm số CCCD đã xử lý
                processing_matches = re.findall(r'Processing (\d+)/1000:', content)
                if processing_matches:
                    current_processed = int(processing_matches[-1])
                    
                    if current_processed > last_processed:
                        last_processed = current_processed
                        
                        # Tính toán tiến độ
                        progress_percent = (current_processed / 1000) * 100
                        elapsed_time = datetime.now() - start_time
                        
                        # Ước tính thời gian còn lại
                        if current_processed > 0:
                            avg_time_per_cccd = elapsed_time.total_seconds() / current_processed
                            remaining_cccd = 1000 - current_processed
                            estimated_remaining = remaining_cccd * avg_time_per_cccd
                            
                            print(f"📊 Progress: {current_processed}/1000 ({progress_percent:.1f}%)")
                            print(f"⏱️ Elapsed: {elapsed_time}")
                            print(f"🕐 Estimated remaining: {estimated_remaining/60:.1f} minutes")
                            print(f"📈 Average speed: {60/avg_time_per_cccd:.1f} CCCD/minute")
                            
                            # Thống kê lỗi
                            error_403 = content.count('403 Forbidden')
                            no_data = content.count('No company data found')
                            success = content.count('"status": "success"')
                            
                            print(f"🔍 Results: Success={success}, No data={no_data}, 403 errors={error_403}")
                            print("-" * 60)
                
                # Kiểm tra xem có hoàn thành không
                if 'FULL OPTIMIZED PROJECT COMPLETED' in content:
                    print("🎉 PROJECT COMPLETED!")
                    break
                    
        except Exception as e:
            print(f"❌ Error monitoring: {e}")
        
        time.sleep(30)  # Cập nhật mỗi 30 giây

if __name__ == "__main__":
    monitor_progress()