#!/usr/bin/env python3
"""
Tạo authorization URL cho Google Drive OAuth
"""

import json
from google_auth_oauthlib.flow import Flow

def create_authorization_url():
    """Tạo authorization URL"""
    try:
        print("🔐 TẠO AUTHORIZATION URL")
        print("=" * 50)
        
        # Scopes cần thiết
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        # Tạo flow
        flow = Flow.from_client_secrets_file(
            'credentials.json', SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # Tạo authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print(f"🔗 Authorization URL:")
        print(f"{auth_url}")
        print()
        print("📋 HƯỚNG DẪN:")
        print("1. Mở link trên trong browser")
        print("2. Đăng nhập Google account")
        print("3. Cho phép truy cập Google Drive")
        print("4. Copy authorization code")
        print("5. Paste code vào terminal")
        print()
        
        # Lưu flow để sử dụng sau
        with open('flow_data.json', 'w') as f:
            json.dump({
                'client_id': flow.client_config['client_id'],
                'client_secret': flow.client_config['client_secret'],
                'redirect_uri': flow.redirect_uri,
                'scopes': SCOPES
            }, f)
        
        print("✅ Flow data đã lưu vào flow_data.json")
        print("🔗 Authorization URL đã tạo thành công!")
        
        return auth_url
        
    except Exception as e:
        print(f"❌ Lỗi tạo authorization URL: {e}")
        return None

def main():
    """Hàm chính"""
    print("🚀 TẠO AUTHORIZATION URL CHO GOOGLE DRIVE")
    print("=" * 60)
    
    # Kiểm tra credentials
    if not os.path.exists('credentials.json'):
        print("❌ File credentials.json không tồn tại")
        return
    
    # Tạo authorization URL
    auth_url = create_authorization_url()
    
    if auth_url:
        print()
        print("🎯 AUTHORIZATION URL ĐÃ TẠO!")
        print(f"🔗 URL: {auth_url}")
        print()
        print("📋 BƯỚC TIẾP THEO:")
        print("1. Mở link trong browser")
        print("2. Đăng nhập Google account")
        print("3. Cho phép truy cập")
        print("4. Copy authorization code")
        print("5. Chạy script upload với code")
    else:
        print("❌ Không thể tạo authorization URL")

if __name__ == "__main__":
    import os
    main()