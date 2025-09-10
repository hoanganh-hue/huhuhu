#!/usr/bin/env python3
"""
Alternative upload method using requests
"""

import requests
import os
import json
from urllib.parse import urlparse, parse_qs

def upload_via_web_interface():
    """Hướng dẫn upload qua web interface"""
    print("🌐 UPLOAD QUA WEB INTERFACE")
    print("=" * 50)
    
    file_path = "cccd_project_complete.zip"
    folder_url = "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    print(f"📁 File: {file_path}")
    print(f"📊 Size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    print(f"🎯 Target folder: {folder_url}")
    print()
    
    print("📋 HƯỚNG DẪN UPLOAD:")
    print("1. Mở Google Drive: https://drive.google.com/")
    print("2. Đăng nhập tài khoản Google của bạn")
    print("3. Truy cập folder: https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF")
    print("4. Kéo thả file 'cccd_project_complete.zip' vào folder")
    print("5. Chờ upload hoàn tất")
    print()
    
    print("🔗 LINKS HỮU ÍCH:")
    print(f"📂 Target folder: {folder_url}")
    print("🌐 Google Drive: https://drive.google.com/")
    print("📱 Mobile app: Tải Google Drive app")
    print()
    
    print("📊 THÔNG TIN FILE:")
    print(f"📁 Tên file: {file_path}")
    print(f"📊 Kích thước: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    print(f"📅 Ngày tạo: {os.path.getctime(file_path)}")
    print(f"📝 Loại file: ZIP Archive")
    print()
    
    print("✅ FILE SẴN SÀNG UPLOAD!")
    print("📋 Vui lòng làm theo hướng dẫn trên để upload file")

def create_upload_info():
    """Tạo file thông tin upload"""
    info = {
        "file_name": "cccd_project_complete.zip",
        "file_size_mb": round(os.path.getsize("cccd_project_complete.zip") / (1024*1024), 1),
        "target_folder": "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF",
        "upload_instructions": [
            "Mở Google Drive: https://drive.google.com/",
            "Đăng nhập tài khoản Google",
            "Truy cập folder target",
            "Kéo thả file vào folder",
            "Chờ upload hoàn tất"
        ],
        "project_info": {
            "name": "CCCD Project Complete",
            "version": "1.0",
            "description": "Dự án tra cứu CCCD với anti-bot protection",
            "features": [
                "Tạo CCCD tối ưu",
                "Anti-bot protection",
                "Proxy support",
                "Excel export",
                "GUI interface"
            ]
        }
    }
    
    with open("upload_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print("📄 Đã tạo file upload_info.json")
    return info

def main():
    """Hàm chính"""
    print("🚀 ALTERNATIVE UPLOAD METHOD")
    print("=" * 50)
    
    # Kiểm tra file tồn tại
    if not os.path.exists("cccd_project_complete.zip"):
        print("❌ File cccd_project_complete.zip không tồn tại")
        return
    
    # Tạo thông tin upload
    info = create_upload_info()
    
    # Hiển thị hướng dẫn
    upload_via_web_interface()
    
    print()
    print("🎯 KẾT LUẬN:")
    print("✅ File đã sẵn sàng upload")
    print("📋 Làm theo hướng dẫn để upload lên Google Drive")
    print("🔗 Link folder: https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF")

if __name__ == "__main__":
    main()