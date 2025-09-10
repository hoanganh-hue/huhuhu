#!/usr/bin/env python3
"""
Google Drive OAuth Upload với credentials thực tế
"""

import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Scopes cần thiết
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    """Xác thực Google Drive với OAuth"""
    creds = None
    
    # Kiểm tra token đã lưu
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Nếu không có credentials hợp lệ
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Đang xác thực OAuth...")
            print("📋 Mở browser để đăng nhập...")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Lưu credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(service, file_path, folder_id=None):
    """Upload file lên Google Drive"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ File không tồn tại: {file_path}")
            return None
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024*1024)
        
        print(f"📁 Uploading: {file_name}")
        print(f"📊 Size: {file_size:.1f} MB")
        
        # Tạo metadata
        file_metadata = {
            'name': file_name
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
            print(f"🎯 Target folder: {folder_id}")
        
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
        
        return file
        
    except Exception as e:
        print(f"❌ Lỗi upload: {e}")
        return None

def list_drive_files(service, folder_id=None):
    """Liệt kê files trong Google Drive"""
    try:
        print("📋 Đang liệt kê files...")
        
        query = ""
        if folder_id:
            query = f"'{folder_id}' in parents"
        
        results = service.files().list(
            q=query,
            fields="files(id,name,size,createdTime,webViewLink)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("📁 Không có files nào")
        else:
            print(f"📁 Tìm thấy {len(files)} files:")
            for file in files:
                size = int(file.get('size', 0)) / (1024*1024) if file.get('size') else 0
                print(f"  📄 {file.get('name')} ({size:.1f} MB) - {file.get('id')}")
        
        return files
        
    except Exception as e:
        print(f"❌ Lỗi liệt kê files: {e}")
        return []

def main():
    """Hàm chính"""
    print("🚀 GOOGLE DRIVE OAUTH UPLOAD FINAL")
    print("=" * 60)
    
    # Thông tin file và folder
    file_path = "cccd_project_complete.zip"
    folder_id = "14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    print(f"📁 File: {file_path}")
    print(f"🎯 Folder ID: {folder_id}")
    print()
    
    # Xác thực
    print("🔐 Đang xác thực Google Drive...")
    service = authenticate_google_drive()
    
    if not service:
        print("❌ Không thể xác thực Google Drive")
        return
    
    print("✅ Xác thực thành công!")
    print()
    
    # Liệt kê files hiện có
    print("📋 Kiểm tra files hiện có trong folder...")
    existing_files = list_drive_files(service, folder_id)
    print()
    
    # Upload file
    print("📤 Bắt đầu upload file...")
    result = upload_file_to_drive(service, file_path, folder_id)
    
    if result:
        print()
        print("🎉 UPLOAD HOÀN TẤT!")
        print(f"📁 File: {result.get('name')}")
        print(f"🔗 Link: {result.get('webViewLink')}")
        print(f"📊 Size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
        print()
        print("✅ File đã được upload thành công lên Google Drive!")
        
        # Kiểm tra lại files
        print()
        print("📋 Kiểm tra files sau khi upload...")
        updated_files = list_drive_files(service, folder_id)
        
    else:
        print("❌ Upload thất bại!")

if __name__ == "__main__":
    main()