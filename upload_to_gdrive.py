#!/usr/bin/env python3
"""
Script upload file lên Google Drive
"""

import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Scopes cần thiết cho Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    """Xác thực với Google Drive API"""
    creds = None
    
    # Kiểm tra token đã lưu
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Nếu không có credentials hợp lệ, yêu cầu user login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("❌ Cần xác thực Google Drive API")
            print("📋 Hướng dẫn:")
            print("1. Truy cập: https://console.developers.google.com/")
            print("2. Tạo project mới hoặc chọn project hiện có")
            print("3. Enable Google Drive API")
            print("4. Tạo OAuth 2.0 credentials")
            print("5. Download credentials.json")
            print("6. Đặt file credentials.json vào thư mục hiện tại")
            return None
        
        # Lưu credentials cho lần sau
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(service, file_path, folder_id, file_name=None):
    """Upload file lên Google Drive folder"""
    try:
        if not file_name:
            file_name = os.path.basename(file_path)
        
        print(f"📁 Uploading {file_name}...")
        print(f"📊 File size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
        
        # Tạo metadata cho file
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Tạo media upload
        media = MediaFileUpload(file_path, resumable=True)
        
        # Upload file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Upload thành công!")
        print(f"🔗 File ID: {file.get('id')}")
        print(f"🌐 Link: https://drive.google.com/file/d/{file.get('id')}/view")
        
        return file.get('id')
        
    except Exception as e:
        print(f"❌ Lỗi upload: {e}")
        return None

def main():
    """Hàm chính"""
    print("🚀 UPLOAD FILE LÊN GOOGLE DRIVE")
    print("=" * 50)
    
    # Thông tin file và folder
    file_path = "cccd_project_complete.zip"
    folder_id = "14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    folder_url = "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    # Kiểm tra file tồn tại
    if not os.path.exists(file_path):
        print(f"❌ File không tồn tại: {file_path}")
        return
    
    print(f"📁 File: {file_path}")
    print(f"📊 Size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    print(f"🎯 Target folder: {folder_url}")
    print()
    
    # Xác thực Google Drive
    print("🔐 Đang xác thực Google Drive API...")
    service = authenticate_google_drive()
    
    if not service:
        print("❌ Không thể xác thực Google Drive API")
        print("📋 Vui lòng làm theo hướng dẫn trên để cấu hình API")
        return
    
    print("✅ Xác thực thành công!")
    print()
    
    # Upload file
    print("📤 Đang upload file...")
    file_id = upload_file_to_drive(service, file_path, folder_id)
    
    if file_id:
        print()
        print("🎉 UPLOAD HOÀN TẤT!")
        print(f"📁 File: {file_path}")
        print(f"🔗 Link: https://drive.google.com/file/d/{file_id}/view")
        print(f"📂 Folder: {folder_url}")
    else:
        print("❌ Upload thất bại!")

if __name__ == "__main__":
    main()