#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chạy hệ thống với 2000 CCCD nữ Hải Phòng (1965-1975)
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Main function to run the system."""
    print("=" * 80)
    print("🚀 HỆ THỐNG BHXH DATA TOOLS - HẢI PHÒNG 2000 CCCD")
    print("=" * 80)
    print("📋 Cấu hình:")
    print("   - Tỉnh/Thành: Hải Phòng (31)")
    print("   - Giới tính: Nữ")
    print("   - Năm sinh: 1965-1975")
    print("   - Số lượng: 2000 CCCD")
    print("=" * 80)
    
    start_time = datetime.now()
    print(f"⏰ Bắt đầu: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import và chạy hệ thống
        from main import IntegratedLookupSystem
        
        # Tạo instance hệ thống
        system = IntegratedLookupSystem()
        
        # Hiển thị cấu hình
        system.config.print_configuration_summary()
        
        # Kiểm tra cấu hình
        if not system.validate_system_configuration():
            print("\n❌ Cấu hình hệ thống không hợp lệ. Vui lòng kiểm tra lại.")
            return False
        
        print("\n" + "="*80)
        print("🚀 BẮT ĐẦU WORKFLOW TỰ ĐỘNG HÓA")
        print("📋 Quy trình sẽ thực hiện 6 bước:")
        print("   1. Tạo danh sách 2000 số CCCD Hải Phòng nữ (1965-1975)")
        print("   2. Check CCCD từ masothue.com")
        print("   3. Tra cứu thông tin Doanh nghiệp")
        print("   4. Tra cứu thông tin BHXH")
        print("   5. Tổng hợp và chuẩn hóa dữ liệu")
        print("   6. Xuất báo cáo Excel")
        print("="*80)
        
        # Chạy workflow
        print("\n🎯 Bắt đầu thực hiện workflow...\n")
        
        success = system.run_complete_workflow()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if success:
            print("\n" + "="*80)
            print("🎉 HOÀN THÀNH THÀNH CÔNG!")
            print(f"⏱️  Tổng thời gian: {duration.total_seconds():.2f} giây")
            print(f"📁 Kiểm tra kết quả trong thư mục: {system.config.output_path}")
            print(f"📊 File báo cáo Excel: {system.config.excel_output_file}")
            print(f"📝 File log: {system.config.get_log_file_path()}")
            print("="*80)
            
            # Thống kê cuối cùng
            print("\n📊 THỐNG KÊ CUỐI CÙNG:")
            print(f"   - Tổng CCCD tạo: {system.stats['total_cccd_generated']}")
            print(f"   - Check CCCD tìm thấy: {system.stats['check_cccd_found']}")
            print(f"   - Doanh nghiệp tìm thấy: {system.stats['doanh_nghiep_found']}")
            print(f"   - BHXH tìm thấy: {system.stats['bhxh_found']}")
            print(f"   - Records cuối cùng: {system.stats['final_records']}")
            print(f"   - Số lỗi: {len(system.stats['errors'])}")
            
            return True
        else:
            print("\n" + "="*80)
            print("❌ WORKFLOW THẤT BẠI!")
            print("🔍 Kiểm tra log để biết thêm chi tiết.")
            print("="*80)
            return False
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Đã dừng thực hiện theo yêu cầu người dùng.")
        return False
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        print("🔍 Kiểm tra log để biết thêm chi tiết.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)