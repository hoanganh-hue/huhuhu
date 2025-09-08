#!/usr/bin/env python3
"""
Script monitor tiến trình xử lý 10,000 CCCD
"""

import time
import re
from pathlib import Path

def get_current_progress():
    """Lấy tiến trình hiện tại từ log"""
    log_file = Path("logs/system.log")
    
    if not log_file.exists():
        return 0, 0, "Log file not found"
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tìm số CCCD đã xử lý
        processing_matches = re.findall(r'Processing (\d+)/10000:', content)
        if processing_matches:
            current = int(processing_matches[-1])
        else:
            current = 0
        
        # Tìm số lỗi 403
        error_403_matches = re.findall(r'403 Forbidden', content)
        error_403_count = len(error_403_matches)
        
        # Tìm số thành công
        success_matches = re.findall(r'Parsed tax info:', content)
        success_count = len(success_matches)
        
        # Tìm số not found
        not_found_matches = re.findall(r'No company data found', content)
        not_found_count = len(not_found_matches)
        
        return current, error_403_count, {
            'success': success_count,
            'not_found': not_found_count,
            'error_403': error_403_count
        }
        
    except Exception as e:
        return 0, 0, f"Error reading log: {e}"

def estimate_completion_time(current, start_time):
    """Ước tính thời gian hoàn thành"""
    if current == 0:
        return "Unknown"
    
    elapsed = time.time() - start_time
    rate = current / elapsed  # CCCD per second
    remaining = 10000 - current
    eta_seconds = remaining / rate if rate > 0 else 0
    
    hours = int(eta_seconds // 3600)
    minutes = int((eta_seconds % 3600) // 60)
    
    return f"{hours}h {minutes}m"

def format_time(seconds):
    """Format thời gian"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

def main():
    """Monitor chính"""
    print("🔍 Monitor tiến trình xử lý 10,000 CCCD")
    print("=" * 60)
    
    start_time = time.time()
    last_progress = 0
    
    while True:
        try:
            current, error_403, stats = get_current_progress()
            
            if isinstance(stats, str):
                print(f"❌ Error: {stats}")
                time.sleep(10)
                continue
            
            # Tính toán
            progress_percent = (current / 10000) * 100
            elapsed = time.time() - start_time
            eta = estimate_completion_time(current, start_time)
            
            # Tính tốc độ
            if current > last_progress:
                rate = (current - last_progress) / 10  # CCCD per 10 seconds
                last_progress = current
            
            # Hiển thị thông tin
            print(f"\r📊 Progress: {current:,}/10,000 ({progress_percent:.1f}%) | "
                  f"⏱️ Elapsed: {format_time(elapsed)} | "
                  f"🎯 ETA: {eta} | "
                  f"✅ Success: {stats['success']} | "
                  f"❌ Not Found: {stats['not_found']} | "
                  f"🚫 403 Errors: {stats['error_403']}", end="", flush=True)
            
            # Kiểm tra hoàn thành
            if current >= 10000:
                print(f"\n\n🎉 HOÀN THÀNH! Đã xử lý {current:,} CCCD")
                print(f"⏱️ Tổng thời gian: {format_time(elapsed)}")
                print(f"📊 Thống kê cuối cùng:")
                print(f"  ✅ Thành công: {stats['success']}")
                print(f"  ❌ Không tìm thấy: {stats['not_found']}")
                print(f"  🚫 403 Errors: {stats['error_403']}")
                break
            
            time.sleep(10)  # Update mỗi 10 giây
            
        except KeyboardInterrupt:
            print(f"\n\n⏸️ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()