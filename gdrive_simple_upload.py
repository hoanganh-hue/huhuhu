#!/usr/bin/env python3
"""
Google Drive Simple Upload với API Key
"""

import requests
import os
import json

# API Key của bạn
API_KEY = "AIzaSyAUnuPqbJfbcnIaTMjQvEXC4pqgoN3H3dU"

def upload_file_simple(file_path, folder_id=None):
    """Upload file đơn giản với API Key"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ File không tồn tại: {file_path}")
            return None
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024*1024)
        
        print(f"📁 File: {file_name}")
        print(f"📊 Size: {file_size:.1f} MB")
        print(f"🔑 API Key: {API_KEY[:20]}...")
        
        # URL endpoint
        url = "https://www.googleapis.com/upload/drive/v3/files"
        
        # Headers
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Metadata
        metadata = {
            'name': file_name
        }
        
        if folder_id:
            metadata['parents'] = [folder_id]
        
        print("📤 Đang upload file...")
        
        # Upload file
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'metadata': json.dumps(metadata)}
            
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload thành công!")
            print(f"📁 File ID: {result.get('id')}")
            print(f"📝 File name: {result.get('name')}")
            return result
        else:
            print(f"❌ Lỗi upload: {response.status_code}")
            print(f"📋 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Lỗi upload: {e}")
        return None

def test_api_connection():
    """Test kết nối API"""
    try:
        print("🔐 Đang test kết nối API...")
        
        url = "https://www.googleapis.com/drive/v3/about"
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Kết nối API thành công!")
            return True
        else:
            print(f"❌ Lỗi kết nối: {response.status_code}")
            print(f"📋 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi test kết nối: {e}")
        return False

def main():
    """Hàm chính"""
    print("🚀 GOOGLE DRIVE SIMPLE UPLOAD")
    print("=" * 50)
    
    # Thông tin file và folder
    file_path = "cccd_project_complete.zip"
    folder_id = "14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    print(f"📁 File: {file_path}")
    print(f"🎯 Folder ID: {folder_id}")
    print()
    
    # Test kết nối
    if not test_api_connection():
        print("❌ Không thể kết nối API")
        return
    
    print()
    
    # Upload file
    print("📤 Bắt đầu upload file...")
    result = upload_file_simple(file_path, folder_id)
    
    if result:
        print()
        print("🎉 UPLOAD HOÀN TẤT!")
        print(f"📁 File: {result.get('name')}")
        print(f"📊 Size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
        print()
        print("✅ File đã được upload thành công lên Google Drive!")
    else:
        print("❌ Upload thất bại!")

if __name__ == "__main__":
    main()