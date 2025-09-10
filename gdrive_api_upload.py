#!/usr/bin/env python3
"""
Google Drive API Upload với API Key
"""

import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import json

# API Key của bạn
API_KEY = "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU"

def create_drive_service():
    """Tạo Google Drive service với API Key"""
    try:
        print("🔐 Đang kết nối Google Drive API...")
        
        # Tạo service với API Key
        service = build('drive', 'v3', developerKey=API_KEY)
        
        print("✅ Kết nối Google Drive API thành công!")
        return service
        
    except Exception as e:
        print(f"❌ Lỗi kết nối API: {e}")
        return None

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
        
        # Tạo metadata cho file
        file_metadata = {
            'name': file_name
        }
        
        # Nếu có folder_id, thêm vào parents
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
            fields='id,name,webViewLink'
        ).execute()
        
        print(f"✅ Upload thành công!")
        print(f"📁 File ID: {file.get('id')}")
        print(f"📝 File name: {file.get('name')}")
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
    print("🚀 GOOGLE DRIVE API UPLOAD")
    print("=" * 50)
    
    # Thông tin file và folder
    file_path = "cccd_project_complete.zip"
    folder_id = "14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"  # Folder ID từ link
    
    print("🔑 API Key has been loaded.")
    print(f"📁 File: {file_path}")
    print(f"🎯 Folder ID: {folder_id}")
    print()
    
    # Tạo service
    service = create_drive_service()
    if not service:
        print("❌ Không thể kết nối Google Drive API")
        return
    
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
    else:
        print("❌ Upload thất bại!")

if __name__ == "__main__":
    main()