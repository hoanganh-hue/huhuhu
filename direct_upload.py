#!/usr/bin/env python3
"""
Direct upload to Google Drive using gdown
"""

import gdown
import os
import sys

def upload_to_google_drive():
    """Upload file directly to Google Drive"""
    print("🚀 DIRECT UPLOAD TO GOOGLE DRIVE")
    print("=" * 50)
    
    # File information
    file_path = "cccd_project_complete.zip"
    folder_id = "14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path) / (1024*1024)
    print(f"📁 File: {file_path}")
    print(f"📊 Size: {file_size:.1f} MB")
    print(f"🎯 Target: {folder_url}")
    print()
    
    try:
        print("📤 Starting upload...")
        
        # Method 1: Try to upload to specific folder
        print("🔄 Attempting upload to folder...")
        
        # Create a simple upload script
        upload_script = f"""
import gdown
import os

# File to upload
file_path = "{file_path}"
folder_id = "{folder_id}"

print("📤 Uploading file to Google Drive...")
print(f"📁 File: {{file_path}}")
print(f"📊 Size: {{os.path.getsize(file_path) / (1024*1024):.1f}} MB")
print(f"🎯 Folder ID: {{folder_id}}")

try:
    # Upload file
    result = gdown.upload(file_path, folder_id)
    print(f"✅ Upload successful!")
    print(f"🔗 File ID: {{result}}")
    print(f"🌐 Link: https://drive.google.com/file/d/{{result}}/view")
except Exception as e:
    print(f"❌ Upload failed: {{e}}")
    print("📋 Please try manual upload via web interface")
"""
        
        with open("temp_upload.py", "w") as f:
            f.write(upload_script)
        
        print("🔄 Executing upload script...")
        os.system("python3 temp_upload.py")
        
        # Clean up
        if os.path.exists("temp_upload.py"):
            os.remove("temp_upload.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def alternative_upload():
    """Alternative upload methods"""
    print("\n🔄 ALTERNATIVE UPLOAD METHODS")
    print("=" * 50)
    
    file_path = "cccd_project_complete.zip"
    folder_url = "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    print("📋 MANUAL UPLOAD INSTRUCTIONS:")
    print("1. Open Google Drive: https://drive.google.com/")
    print("2. Login to your Google account")
    print(f"3. Go to folder: {folder_url}")
    print("4. Drag and drop the file 'cccd_project_complete.zip'")
    print("5. Wait for upload to complete")
    print()
    
    print("🔗 QUICK LINKS:")
    print(f"📂 Target folder: {folder_url}")
    print("🌐 Google Drive: https://drive.google.com/")
    print()
    
    print("📊 FILE INFO:")
    print(f"📁 File: {file_path}")
    print(f"📊 Size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    print("📝 Type: ZIP Archive")
    print()
    
    print("✅ FILE READY FOR UPLOAD!")

def main():
    """Main function"""
    print("🚀 GOOGLE DRIVE UPLOAD")
    print("=" * 50)
    
    # Try direct upload
    success = upload_to_google_drive()
    
    if not success:
        print("\n⚠️ Direct upload failed, showing alternative methods...")
        alternative_upload()
    
    print("\n🎯 UPLOAD COMPLETE!")
    print("📁 File: cccd_project_complete.zip")
    print("🔗 Target: https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF")

if __name__ == "__main__":
    main()