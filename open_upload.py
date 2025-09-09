#!/usr/bin/env python3
import webbrowser
import os

def open_upload_page():
    print("🚀 OPENING GOOGLE DRIVE UPLOAD PAGE")
    print("=" * 50)
    
    file_path = "cccd_project_complete.zip"
    folder_url = "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / (1024*1024)
        print(f"📁 File: {file_path}")
        print(f"📊 Size: {file_size:.1f} MB")
        print(f"🎯 Target: {folder_url}")
        print()
        
        print("📋 UPLOAD INSTRUCTIONS:")
        print("1. Login to your Google account")
        print("2. Go to the folder link above")
        print("3. Drag and drop the file")
        print("4. Wait for upload to complete")
        print()
        
        print("🔗 Opening browser...")
        webbrowser.open(folder_url)
        print("✅ Browser opened!")
        
    else:
        print(f"❌ File not found: {file_path}")

if __name__ == "__main__":
    open_upload_page()
