#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Cài Đặt Tự Động cho Hệ Thống Tích Hợp
Hệ Thống Tự Động Hóa Tra Cứu và Tổng Hợp Thông Tin
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Đưa ra banner thông tin hệ thống"""
    banner = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   Hệ THỐNG TỰCH HỢP TRA CỨU THÔNG TIN TỰ ĐỘNG                   ┃
┃                                                            ┃
┃   🗺️ Module 1: Phân tích CCCD Nội bộ                          ┃
┃   🏢 Module 2: Tra cứu thông tin Doanh nghiệp               ┃
┃   📋 Module 3: Tra cứu thông tin BHXH                       ┃
┃                                                            ┃
┃   ⚡ Tự động hóa quy trình 5 bước                         ┃
┃   📄 Xuất báo cáo Excel chuẩn định dạng                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """
    print(banner)

def check_system_requirements():
    """
Kiểm tra yêu cầu hệ thống
    """
    print("\n🔍 Kiểm tra yêu cầu hệ thống...")
    
    # Kiểm tra Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Lỗi: Cần Python 3.8 trở lên")
        print(f"🐍 Phiên bản hiện tại: {python_version.major}.{python_version.minor}")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor} - OK")
    
    # Kiểm tra Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            node_version = result.stdout.strip()
            print(f"✅ Node.js {node_version} - OK")
        else:
            print("❌ Lỗi: Không tìm thấy Node.js")
            return False
    except FileNotFoundError:
        print("❌ Lỗi: Node.js chưa được cài đặt")
        return False
    
    # Kiểm tra NPM
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            npm_version = result.stdout.strip()
            print(f"✅ NPM {npm_version} - OK")
        else:
            print("❌ Lỗi: NPM không hoạt động")
            return False
    except FileNotFoundError:
        print("❌ Lỗi: NPM chưa được cài đặt")
        return False
    
    return True

def install_python_dependencies():
    """
Cài đặt Python dependencies
    """
    print("\n🐍 Cài đặt Python dependencies...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Đã cài đặt thành công Python packages")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt Python packages: {e}")
        return False

def install_nodejs_dependencies():
    """
Cài đặt Node.js dependencies
    """
    print("\n📦 Cài đặt Node.js dependencies...")
    try:
        result = subprocess.run(
            ['npm', 'install'],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Đã cài đặt thành công Node.js packages")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt Node.js packages: {e}")
        return False

def copy_modules():
    """
Sao chép các module vào thư mục modules
    """
    print("\n📁 Sao chép các module...")
    
    current_dir = Path.cwd()
    modules_dir = current_dir / "modules"
    
    # Sao chép các module
    modules_to_copy = [
        (current_dir.parent / "cccd", "cccd"),
        (current_dir.parent / "API-tongcucthue", "doanh-nghiep"),
        (current_dir.parent / "bhxh-tool-enhanced", "bhxh")
    ]
    
    for src, dst_name in modules_to_copy:
        dst = modules_dir / dst_name
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"✅ Đã sao chép {src.name} → modules/{dst_name}")
        else:
            print(f"⚠️ Không tìm thấy thư mục: {src}")
    
    return True

def setup_environment():
    """
Thiết lập file environment
    """
    print("\n⚙️ Thiết lập environment...")
    
    env_template = Path(".env.template")
    env_file = Path(".env")
    
    if not env_file.exists() and env_template.exists():
        shutil.copy(env_template, env_file)
        print("✅ Đã tạo file .env từ template")
        print("⚠️ Lưu ý: Vui lòng sửa file .env và điền thông tin cần thiết")
    elif env_file.exists():
        print("✅ File .env đã tồn tại")
    
    return True

def create_directories():
    """
Tạo các thư mục cần thiết
    """
    print("\n📁 Tạo cấu trúc thư mục...")
    
    directories = ['output', 'logs', 'modules', 'config']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Đã tạo thư mục: {directory}")
    
    return True

def main():
    """
Hàm chính của script cài đặt
    """
    print_banner()
    
    # Kiểm tra yêu cầu hệ thống
    if not check_system_requirements():
        print("\n❌ Cài đặt thất bại do không đảm bảo yêu cầu hệ thống")
        sys.exit(1)
    
    # Tạo thư mục
    if not create_directories():
        print("\n❌ Không thể tạo cấu trúc thư mục")
        sys.exit(1)
    
    # Cài đặt dependencies
    if not install_python_dependencies():
        print("\n❌ Cài đặt Python dependencies thất bại")
        sys.exit(1)
    
    if not install_nodejs_dependencies():
        print("\n❌ Cài đặt Node.js dependencies thất bại")
        sys.exit(1)
    
    # Sao chép modules
    if not copy_modules():
        print("\n❌ Sao chép modules thất bại")
        sys.exit(1)
    
    # Thiết lập environment
    if not setup_environment():
        print("\n❌ Thiết lập environment thất bại")
        sys.exit(1)
    
    # Thông báo hoàn tất
    success_message = """

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ CÀI ĐẶT THÀNH CÔNG!                              ┃
┃                                                    ┃
┃  Bước tiếp theo:                                  ┃
┃                                                    ┃
┃  1. Sửa file .env và điền thông tin cần thiết      ┃
┃  2. Chạy hệ thống: python main.py                 ┃
┃                                                    ┃
┃  📝 Lưu ý quan trọng:                              ┃
┃  - Cần API key của 2captcha cho module BHXH      ┃
┃  - Kiểm tra kết nối internet                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """
    print(success_message)

if __name__ == "__main__":
    main()
