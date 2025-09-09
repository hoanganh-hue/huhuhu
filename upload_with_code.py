#!/usr/bin/env python3
"""
Upload file với authorization code
"""

import os
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_with_authorization_code(auth_code):
    """Upload file với authorization code"""
    try:
        print("🔐 XỬ LÝ AUTHORIZATION CODE")
        print("=" * 50)
        
        # Scopes cần thiết
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        # Tạo flow
        flow = Flow.from_client_secrets_file(
            'credentials.json', SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # Lấy token từ authorization code
        print("🔄 Đang lấy access token...")
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        print("✅ Access token đã lấy thành công!")
        
        # Tạo service
        service = build('drive', 'v3', credentials=creds)
        
        # Upload file
        file_path = "cccd_project_complete.zip"
        folder_id = "14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
        
        if not os.path.exists(file_path):
            print(f"❌ File không tồn tại: {file_path}")
            return None
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024*1024)
        
        print(f"📁 Uploading: {file_name}")
        print(f"📊 Size: {file_size:.1f} MB")
        print(f"🎯 Target folder: {folder_id}")
        
        # Tạo metadata
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Tạo media upload
        media = MediaFileUpload(file_path, resumable=True)
        
        print("📤 Đang upload file...")
        
        # Upload file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,webViewLink,size'
        ).execute()
        
        print(f"✅ Upload thành công!")
        print(f"📁 File ID: {file.get('id')}")
        print(f"📝 File name: {file.get('name')}")
        print(f"📊 File size: {int(file.get('size', 0)) / (1024*1024):.1f} MB")
        print(f"🔗 Link: {file.get('webViewLink')}")
        
        # Lưu token để sử dụng sau
        import pickle
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Token đã lưu vào token.pickle")
        
        return file
        
    except Exception as e:
        print(f"❌ Lỗi upload: {e}")
        return None

def main():
    """Hàm chính"""
    print("🚀 UPLOAD VỚI AUTHORIZATION CODE")
    print("=" * 50)
    
    # Lấy authorization code từ user
    print("📋 Nhập authorization code từ Google OAuth:")
    auth_code = input("🔑 Authorization code: ").strip()
    
    if not auth_code:
        print("❌ Không có authorization code")
        return
    
    print()
    print("🔄 Bắt đầu upload...")
    
    # Upload file
    result = upload_with_authorization_code(auth_code)
    
    if result:
        print()
        print("🎉 UPLOAD HOÀN TẤT!")
        print(f"📁 File: {result.get('name')}")
        print(f"🔗 Link: {result.get('webViewLink')}")
        print(f"📊 Size: {os.path.getsize('cccd_project_complete.zip') / (1024*1024):.1f} MB")
        print()
        print("✅ File đã được upload thành công lên Google Drive!")
    else:
        print("❌ Upload thất bại!")

if __name__ == "__main__":
    main()