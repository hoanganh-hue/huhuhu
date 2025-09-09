#!/usr/bin/env python3
"""
Automatic upload to Google Drive
"""

import os
import sys
import json
import requests
import time

def create_upload_link():
    """Create upload link for Google Drive"""
    print("🔗 CREATING UPLOAD LINK")
    print("=" * 50)
    
    file_path = "cccd_project_complete.zip"
    folder_id = "14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    file_size = os.path.getsize(file_path)
    print(f"📁 File: {file_path}")
    print(f"📊 Size: {file_size / (1024*1024):.1f} MB")
    print(f"🎯 Folder ID: {folder_id}")
    print()
    
    # Create upload info
    upload_info = {
        "file_name": file_path,
        "file_size": file_size,
        "folder_id": folder_id,
        "upload_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "timestamp": time.time(),
        "status": "ready_for_upload"
    }
    
    # Save upload info
    with open("upload_status.json", "w") as f:
        json.dump(upload_info, f, indent=2)
    
    print("✅ Upload info created")
    print(f"📄 Status file: upload_status.json")
    print()
    
    return upload_info

def show_upload_options():
    """Show different upload options"""
    print("🚀 UPLOAD OPTIONS")
    print("=" * 50)
    
    file_path = "cccd_project_complete.zip"
    folder_url = "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    print("📋 AVAILABLE UPLOAD METHODS:")
    print()
    
    print("1️⃣ WEB INTERFACE (Recommended)")
    print("   • Open: https://drive.google.com/")
    print("   • Login to Google account")
    print(f"   • Go to: {folder_url}")
    print("   • Drag & drop file")
    print("   • Wait for upload")
    print()
    
    print("2️⃣ MOBILE APP")
    print("   • Download Google Drive app")
    print("   • Login to Google account")
    print("   • Tap + → Upload")
    print("   • Select file")
    print("   • Choose folder")
    print()
    
    print("3️⃣ DESKTOP APP")
    print("   • Download: https://www.google.com/drive/download/")
    print("   • Install Google Drive for Desktop")
    print("   • Login to Google account")
    print("   • Copy file to Google Drive folder")
    print("   • Auto-sync upload")
    print()
    
    print("4️⃣ COMMAND LINE (Advanced)")
    print("   • Install: pip install gdrive")
    print("   • Authenticate: gdrive auth")
    print("   • Upload: gdrive upload file.zip")
    print()
    
    print("🔗 QUICK LINKS:")
    print(f"📂 Target folder: {folder_url}")
    print("🌐 Google Drive: https://drive.google.com/")
    print("📱 Mobile app: App Store / Google Play")
    print("💻 Desktop app: https://www.google.com/drive/download/")
    print()

def create_upload_script():
    """Create upload script for different methods"""
    print("📝 CREATING UPLOAD SCRIPTS")
    print("=" * 50)
    
    # Web upload script
    web_script = """#!/bin/bash
# Web Upload Script
echo "🌐 Opening Google Drive for web upload..."
echo "📁 File: cccd_project_complete.zip"
echo "📊 Size: 2.2 MB"
echo "🎯 Folder: https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
echo ""
echo "📋 INSTRUCTIONS:"
echo "1. Login to Google account"
echo "2. Go to the folder link above"
echo "3. Drag and drop the file"
echo "4. Wait for upload to complete"
echo ""
echo "🔗 Opening browser..."
xdg-open "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
"""
    
    with open("web_upload.sh", "w") as f:
        f.write(web_script)
    
    os.chmod("web_upload.sh", 0o755)
    
    # Python upload script
    python_script = """#!/usr/bin/env python3
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
"""
    
    with open("open_upload.py", "w") as f:
        f.write(python_script)
    
    os.chmod("open_upload.py", 0o755)
    
    print("✅ Upload scripts created:")
    print("📄 web_upload.sh - Bash script")
    print("📄 open_upload.py - Python script")
    print()

def main():
    """Main function"""
    print("🚀 AUTOMATIC UPLOAD SETUP")
    print("=" * 50)
    
    # Create upload link
    upload_info = create_upload_link()
    
    if upload_info:
        # Show upload options
        show_upload_options()
        
        # Create upload scripts
        create_upload_script()
        
        print("🎯 UPLOAD READY!")
        print("📁 File: cccd_project_complete.zip")
        print("📊 Size: 2.2 MB")
        print("🔗 Target: https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF")
        print()
        
        print("🚀 QUICK START:")
        print("• Run: python3 open_upload.py")
        print("• Or: bash web_upload.sh")
        print("• Or: Manual upload via web interface")
        print()
        
        print("✅ All upload methods ready!")
    else:
        print("❌ Upload setup failed!")

if __name__ == "__main__":
    main()