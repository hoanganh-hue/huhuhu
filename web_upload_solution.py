#!/usr/bin/env python3
"""
Giải pháp upload qua Web Interface
"""

import os
import webbrowser
import time

def open_google_drive():
    """Mở Google Drive để upload"""
    try:
        print("🌐 MỞ GOOGLE DRIVE ĐỂ UPLOAD")
        print("=" * 50)
        
        # URL Google Drive
        drive_url = "https://drive.google.com/"
        folder_url = "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
        
        print(f"🔗 Google Drive: {drive_url}")
        print(f"🎯 Target folder: {folder_url}")
        print()
        
        print("📋 HƯỚNG DẪN UPLOAD:")
        print("1. Đăng nhập Google account")
        print("2. Truy cập folder target")
        print("3. Kéo thả file cccd_project_complete.zip")
        print("4. Chờ upload hoàn tất")
        print()
        
        # Mở browser
        print("🔗 Đang mở browser...")
        webbrowser.open(drive_url)
        
        print("✅ Browser đã mở!")
        print("📋 Vui lòng làm theo hướng dẫn để upload file")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi mở browser: {e}")
        return False

def create_upload_guide():
    """Tạo hướng dẫn upload chi tiết"""
    print("📋 TẠO HƯỚNG DẪN UPLOAD")
    print("=" * 50)
    
    file_path = "cccd_project_complete.zip"
    folder_url = "https://drive.google.com/drive/folders/14AX0Qo41QW95eqFzEGqSym2HGz41PhNF"
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / (1024*1024)
        
        guide = f"""
# 📤 HƯỚNG DẪN UPLOAD FILE LÊN GOOGLE DRIVE

## 📁 THÔNG TIN FILE
- **Tên file:** {file_path}
- **Kích thước:** {file_size:.1f} MB
- **Vị trí:** {os.path.abspath(file_path)}

## 🎯 MỤC TIÊU UPLOAD
- **Google Drive:** https://drive.google.com/
- **Target folder:** {folder_url}
- **Folder ID:** 14AX0Qo41QW95eqFzEGqSym2HGz41PhNF

## 📋 HƯỚNG DẪN CHI TIẾT

### Bước 1: Mở Google Drive
1. Truy cập: https://drive.google.com/
2. Đăng nhập tài khoản Google của bạn

### Bước 2: Truy cập folder đích
1. Mở link: {folder_url}
2. Hoặc tìm folder "CCCD Project" trong Google Drive

### Bước 3: Upload file
1. Kéo thả file `{file_path}` vào folder
2. Hoặc click "New" → "File upload" → chọn file
3. Chờ upload hoàn tất ({file_size:.1f} MB)

### Bước 4: Xác nhận
1. Kiểm tra file đã xuất hiện trong folder
2. Click chuột phải → "Get link" để chia sẻ

## 🔗 LINKS HỮU ÍCH
- **Google Drive:** https://drive.google.com/
- **Target folder:** {folder_url}
- **Mobile app:** App Store / Google Play
- **Desktop app:** https://www.google.com/drive/download/

## ✅ KẾT QUẢ MONG ĐỢI
- File `{file_path}` xuất hiện trong Google Drive folder
- Có thể tải về và giải nén
- Tất cả tính năng hoạt động bình thường
- Dữ liệu và báo cáo đầy đủ

## 🎯 LƯU Ý
- Đảm bảo kết nối internet ổn định
- Đăng nhập đúng tài khoản Google
- Kiểm tra quyền truy cập folder
- Chờ upload hoàn tất trước khi đóng browser
"""
        
        # Lưu hướng dẫn
        with open('UPLOAD_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print("✅ Hướng dẫn đã lưu vào UPLOAD_GUIDE.md")
        print(f"📁 File: {file_path} ({file_size:.1f} MB)")
        print(f"🎯 Target: {folder_url}")
        
    else:
        print(f"❌ File không tồn tại: {file_path}")

def main():
    """Hàm chính"""
    print("🚀 GIẢI PHÁP UPLOAD QUA WEB INTERFACE")
    print("=" * 60)
    
    # Tạo hướng dẫn
    create_upload_guide()
    print()
    
    # Mở Google Drive
    print("🌐 MỞ GOOGLE DRIVE...")
    success = open_google_drive()
    
    if success:
        print()
        print("🎉 GIẢI PHÁP ĐÃ SẴN SÀNG!")
        print("📋 Làm theo hướng dẫn trong UPLOAD_GUIDE.md")
        print("🔗 Browser đã mở Google Drive")
        print("📁 File cccd_project_complete.zip sẵn sàng upload")
    else:
        print("❌ Không thể mở browser")
        print("📋 Vui lòng mở Google Drive thủ công")

if __name__ == "__main__":
    main()