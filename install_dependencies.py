#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cài đặt dependencies cho Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Cài đặt dependencies từ requirements.txt"""
    
    print("🚀 Cài đặt dependencies cho Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH")
    print("=" * 80)
    
    # Kiểm tra file requirements.txt
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ Không tìm thấy file requirements.txt")
        return False
    
    try:
        print("📦 Đang cài đặt dependencies...")
        
        # Cài đặt từ requirements.txt
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True, check=True)
        
        print("✅ Cài đặt dependencies thành công!")
        print("\n📋 Dependencies đã cài đặt:")
        
        # Hiển thị danh sách packages đã cài đặt
        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"   - {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Lỗi không mong đợi: {e}")
        return False

def check_installation():
    """Kiểm tra cài đặt"""
    
    print("\n🔍 Kiểm tra cài đặt...")
    
    required_modules = [
        'rich', 'click', 'requests', 'pandas', 'openpyxl', 
        'fastapi', 'uvicorn', 'beautifulsoup4', 'lxml'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Thiếu modules: {', '.join(missing_modules)}")
        return False
    else:
        print("\n🎉 Tất cả modules đã được cài đặt thành công!")
        return True

def main():
    """Hàm chính"""
    
    print("🎯 HỆ THỐNG TỰ ĐỘNG HÓA TRA CỨU THÔNG TIN BHXH")
    print("📦 Script Cài Đặt Dependencies")
    print("=" * 80)
    
    # Cài đặt dependencies
    if install_requirements():
        # Kiểm tra cài đặt
        if check_installation():
            print("\n🚀 Sẵn sàng chạy hệ thống!")
            print("\nCác lệnh để chạy:")
            print("   python main.py          # Command line")
            print("   python gui_main.py      # GUI interface")
            print("   ./run_linux_mac.sh      # Linux/Mac script")
            print("   run_windows.bat         # Windows script")
        else:
            print("\n❌ Có lỗi trong quá trình cài đặt")
            sys.exit(1)
    else:
        print("\n❌ Không thể cài đặt dependencies")
        sys.exit(1)

if __name__ == "__main__":
    main()