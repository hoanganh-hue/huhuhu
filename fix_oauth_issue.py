#!/usr/bin/env python3
"""
Khắc phục vấn đề OAuth2 - Ứng dụng không hợp lệ
"""

import json
import urllib.parse

def analyze_oauth_issue():
    """Phân tích vấn đề OAuth2"""
    print("🔍 PHÂN TÍCH VẤN ĐỀ OAUTH2")
    print("=" * 50)
    
    # Đọc credentials
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        print("✅ Credentials đã đọc thành công")
        print(f"🔑 Client ID: {creds['web']['client_id']}")
        print("🔐 Client Secret: [Đã tải, không hiển thị]")
        print(f"🏢 Project ID: {creds['web']['project_id']}")
        print()
        
    except Exception as e:
        print(f"❌ Lỗi đọc credentials: {e}")
        return
    
    # Phân tích vấn đề
    print("📋 PHÂN TÍCH VẤN ĐỀ:")
    print("1. ❌ Ứng dụng chưa được verify bởi Google")
    print("2. ❌ Redirect URI 'urn:ietf:wg:oauth:2.0:oob' không được hỗ trợ")
    print("3. ❌ Client ID có thể chưa được cấu hình đúng")
    print("4. ❌ App chưa được publish hoặc test")
    print()

def create_fixed_auth_url():
    """Tạo authorization URL với cấu hình đã sửa"""
    try:
        print("🔧 TẠO AUTHORIZATION URL ĐÃ SỬA")
        print("=" * 50)
        
        # Đọc credentials
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        client_id = creds['web']['client_id']
        
        # Sử dụng redirect URI khác
        redirect_uri = "http://localhost:8080/callback"
        
        # Tạo authorization URL với cấu hình mới
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            f"scope={urllib.parse.quote('https://www.googleapis.com/auth/drive.file')}&"
            f"prompt=consent&"
            f"access_type=offline"
        )
        
        print(f"🔗 Authorization URL đã sửa:")
        print(f"{auth_url}")
        print()
        print("📋 THAY ĐỔI:")
        print("1. ✅ Sử dụng redirect_uri: http://localhost:8080/callback")
        print("2. ✅ Loại bỏ state parameter")
        print("3. ✅ Sử dụng scope đơn giản")
        print()
        
        # Lưu URL đã sửa
        with open('auth_url_fixed.txt', 'w') as f:
            f.write(auth_url)
        
        print("✅ URL đã sửa lưu vào auth_url_fixed.txt")
        
        return auth_url
        
    except Exception as e:
        print(f"❌ Lỗi tạo URL đã sửa: {e}")
        return None

def create_alternative_solution():
    """Tạo giải pháp thay thế"""
    print("🔄 GIẢI PHÁP THAY THẾ")
    print("=" * 50)
    
    print("📋 CÁC GIẢI PHÁP:")
    print()
    print("1️⃣ SỬ DỤNG WEB INTERFACE (Khuyến nghị)")
    print("   • Mở: https://drive.google.com/")
    print("   • Đăng nhập Google account")
    print("   • Kéo thả file cccd_project_complete.zip")
    print("   • Upload trực tiếp")
    print()
    print("2️⃣ SỬ DỤNG GOOGLE DRIVE API KEY")
    print("   • Tạo API Key trong Google Console")
    print("   • Sử dụng API Key thay vì OAuth2")
    print("   • Upload qua REST API")
    print()
    print("3️⃣ SỬ DỤNG SERVICE ACCOUNT")
    print("   • Tạo Service Account")
    print("   • Download service account key")
    print("   • Upload với service account")
    print()
    print("4️⃣ SỬ DỤNG GOOGLE DRIVE DESKTOP")
    print("   • Tải Google Drive for Desktop")
    print("   • Đăng nhập account")
    print("   • Copy file vào Google Drive folder")
    print()

def main():
    """Hàm chính"""
    print("🚀 KHẮC PHỤC VẤN ĐỀ OAUTH2")
    print("=" * 60)
    
    # Phân tích vấn đề
    analyze_oauth_issue()
    
    # Tạo URL đã sửa
    print("🔧 THỬ SỬA AUTHORIZATION URL...")
    fixed_url = create_fixed_auth_url()
    
    if fixed_url:
        print("✅ URL đã sửa tạo thành công!")
    else:
        print("❌ Không thể sửa URL")
    
    print()
    
    # Đề xuất giải pháp thay thế
    create_alternative_solution()
    
    print("🎯 KHUYẾN NGHỊ:")
    print("Sử dụng Web Interface để upload file trực tiếp!")
    print("Đây là cách đơn giản và hiệu quả nhất.")

if __name__ == "__main__":
    main()