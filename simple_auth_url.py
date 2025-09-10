#!/usr/bin/env python3
"""
Tạo authorization URL đơn giản
"""

import json
import urllib.parse

def create_simple_auth_url():
    """Tạo authorization URL đơn giản"""
    try:
        print("🔐 TẠO AUTHORIZATION URL MỚI")
        print("=" * 50)
        
        # Thông tin OAuth2
        client_id = "1094223905958-mbh6f5tpklu3tehrnv0bgajils19phs6.apps.googleusercontent.com"
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        scope = "https://www.googleapis.com/auth/drive.file"
        
        # Tạo authorization URL
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            f"scope={urllib.parse.quote(scope)}&"
            f"prompt=consent&"
            f"access_type=offline"
        )
        
        print(f"🔗 Authorization URL mới:")
        print(f"{auth_url}")
        print()
        print("📋 HƯỚNG DẪN:")
        print("1. Copy link trên")
        print("2. Mở trong browser mới")
        print("3. Đăng nhập Google account")
        print("4. Cho phép truy cập Google Drive")
        print("5. Copy authorization code")
        print("6. Chạy: python3 upload_with_code.py")
        print()
        
        # Lưu URL vào file
        with open('auth_url.txt', 'w') as f:
            f.write(auth_url)
        
        print("✅ URL đã lưu vào auth_url.txt")
        print("🔗 Authorization URL mới đã tạo thành công!")
        
        return auth_url
        
    except Exception as e:
        print(f"❌ Lỗi tạo URL: {e}")
        return None

def main():
    """Hàm chính"""
    print("🚀 TẠO AUTHORIZATION URL MỚI")
    print("=" * 60)
    
    # Tạo authorization URL
    auth_url = create_simple_auth_url()
    
    if auth_url:
        print()
        print("🎯 AUTHORIZATION URL MỚI ĐÃ TẠO!")
        print(f"🔗 URL: {auth_url}")
        print()
        print("📋 BƯỚC TIẾP THEO:")
        print("1. Copy link trên")
        print("2. Mở trong browser mới")
        print("3. Đăng nhập Google account")
        print("4. Cho phép truy cập")
        print("5. Copy authorization code")
        print("6. Chạy: python3 upload_with_code.py")
        print("7. Paste authorization code")
    else:
        print("❌ Không thể tạo authorization URL")

if __name__ == "__main__":
    main()