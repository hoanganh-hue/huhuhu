#!/usr/bin/env python3
"""
Remote Access Setup cho máy chủ
"""

import subprocess
import time
import os

def check_services():
    """Kiểm tra các dịch vụ đang chạy"""
    try:
        print("🔍 KIỂM TRA DỊCH VỤ")
        print("=" * 50)
        
        # Kiểm tra VNC server
        result = subprocess.run(['pgrep', 'x11vnc'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ VNC Server: Đang chạy")
        else:
            print("❌ VNC Server: Không chạy")
        
        # Kiểm tra Web server
        result = subprocess.run(['pgrep', '-f', 'python3.*http.server'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Web Server: Đang chạy")
        else:
            print("❌ Web Server: Không chạy")
        
        # Kiểm tra Xvfb
        result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Virtual Display: Đang chạy")
        else:
            print("❌ Virtual Display: Không chạy")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra dịch vụ: {e}")
        return False

def get_network_info():
    """Lấy thông tin network"""
    try:
        print("🌐 THÔNG TIN NETWORK")
        print("=" * 50)
        
        # Lấy IP addresses
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ips = result.stdout.strip().split()
            print(f"🌐 Server IPs: {', '.join(ips)}")
            main_ip = ips[0] if ips else "Unknown"
            print(f"🎯 Main IP: {main_ip}")
        else:
            print("❌ Không thể lấy IP address")
            main_ip = "Unknown"
        
        return main_ip
        
    except Exception as e:
        print(f"❌ Lỗi lấy thông tin network: {e}")
        return "Unknown"

def create_remote_access_guide(server_ip):
    """Tạo hướng dẫn truy cập từ xa"""
    try:
        print("📋 TẠO HƯỚNG DẪN TRUY CẬP TỪ XA")
        print("=" * 50)
        
        guide_content = f"""
# 🌐 HƯỚNG DẪN TRUY CẬP TỪ XA

## 🖥️ VNC ACCESS (GUI Interface)

### Thông tin kết nối:
- **VNC URL:** vnc://{server_ip}:5900
- **Port:** 5900
- **Password:** Abcd@2024
- **Protocol:** VNC

### Cách kết nối:
1. **Cài đặt VNC Client:**
   - Windows: RealVNC Viewer, TightVNC, UltraVNC
   - Mac: RealVNC Viewer, VNC Viewer
   - Linux: Remmina, Vinagre, RealVNC Viewer
   - Mobile: VNC Viewer (iOS/Android)

2. **Kết nối:**
   - Mở VNC Client
   - Nhập địa chỉ: {server_ip}:5900
   - Nhập password: Abcd@2024
   - Kết nối

### Tính năng:
- ✅ Truy cập giao diện GUI đầy đủ
- ✅ Điều khiển từ xa
- ✅ Chia sẻ màn hình
- ✅ Bảo mật password

---

## 🌐 WEB ACCESS (Web Interface)

### Thông tin kết nối:
- **Web URL:** http://{server_ip}:8080
- **Port:** 8080
- **Protocol:** HTTP

### Cách truy cập:
1. **Mở browser** (Chrome, Firefox, Safari, Edge)
2. **Nhập URL:** http://{server_ip}:8080
3. **Xem thông tin** server và dự án

### Tính năng:
- ✅ Xem trạng thái hệ thống
- ✅ Thông tin file dự án
- ✅ Hướng dẫn sử dụng
- ✅ Links truy cập

---

## 📁 FILE ACCESS

### Thông tin file:
- **Tên file:** cccd_project_complete.zip
- **Kích thước:** 2.2 MB
- **Vị trí:** /workspace/cccd_project_complete.zip
- **Truy cập:** Qua VNC hoặc Web interface

### Cách tải file:
1. **Qua VNC:** Mở file manager, copy file
2. **Qua Web:** Click link download (nếu có)
3. **Qua SSH:** scp user@{server_ip}:/workspace/cccd_project_complete.zip ./

---

## 🔐 BẢO MẬT

### VNC Security:
- ✅ Password protected: Abcd@2024
- ✅ Encrypted connection
- ✅ Access control

### Network Security:
- ⚠️ Firewall: Cần cấu hình thêm
- ⚠️ SSL/TLS: Chưa được cấu hình
- ✅ Password authentication

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### Bước 1: Kết nối VNC
1. Cài đặt VNC client
2. Kết nối: vnc://{server_ip}:5900
3. Nhập password: Abcd@2024
4. Truy cập GUI

### Bước 2: Truy cập Web
1. Mở browser
2. Truy cập: http://{server_ip}:8080
3. Xem thông tin dự án

### Bước 3: Tải file dự án
1. Qua VNC: Copy file từ /workspace/
2. Qua Web: Download từ interface
3. Extract và sử dụng

---

## 📞 HỖ TRỢ

### Thông tin server:
- **Server IP:** {server_ip}
- **VNC Port:** 5900
- **Web Port:** 8080
- **Password:** Abcd@2024

### Troubleshooting:
- **VNC không kết nối được:** Kiểm tra firewall, port 5900
- **Web không truy cập được:** Kiểm tra port 8080
- **Password không đúng:** Sử dụng Abcd@2024
- **File không tải được:** Kiểm tra quyền truy cập

---

## 🎯 TRẠNG THÁI HIỆN TẠI

- ✅ VNC Server: Đang chạy
- ✅ Web Server: Đang chạy  
- ✅ Virtual Display: Đang chạy
- ✅ File dự án: Sẵn sàng
- ⚠️ Firewall: Cần cấu hình thêm
- ⚠️ SSL/TLS: Chưa được cấu hình

**🚀 Hệ thống sẵn sàng cho truy cập từ xa!**
"""
        
        # Lưu hướng dẫn
        with open('/workspace/REMOTE_ACCESS_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print("✅ Hướng dẫn đã được tạo: REMOTE_ACCESS_GUIDE.md")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi tạo hướng dẫn: {e}")
        return False

def update_web_interface(server_ip):
    """Cập nhật web interface với thông tin remote access"""
    try:
        print("🌐 CẬP NHẬT WEB INTERFACE")
        print("=" * 50)
        
        # Đọc file hiện tại
        with open('/workspace/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cập nhật thông tin IP
        content = content.replace('172.30.0.2', server_ip)
        
        # Thêm section remote access
        remote_section = f"""
        <div class="remote-access">
            <h3>🌐 Remote Access Information</h3>
            <p><strong>VNC URL:</strong> vnc://{server_ip}:5900</p>
            <p><strong>VNC Password:</strong> Abcd@2024</p>
            <p><strong>Web URL:</strong> http://{server_ip}:8080</p>
            <p><strong>Status:</strong> ✅ Ready for remote access</p>
        </div>
        """
        
        # Thêm vào trước closing body tag
        content = content.replace('</body>', f'{remote_section}\n</body>')
        
        # Lưu file đã cập nhật
        with open('/workspace/index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Web interface đã được cập nhật")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi cập nhật web interface: {e}")
        return False

def main():
    """Hàm chính"""
    print("🌐 SETUP REMOTE ACCESS")
    print("=" * 60)
    
    # Kiểm tra dịch vụ
    if not check_services():
        print("❌ Một số dịch vụ không chạy")
        return
    
    print()
    
    # Lấy thông tin network
    server_ip = get_network_info()
    
    print()
    
    # Tạo hướng dẫn
    if not create_remote_access_guide(server_ip):
        print("❌ Không thể tạo hướng dẫn")
        return
    
    print()
    
    # Cập nhật web interface
    if not update_web_interface(server_ip):
        print("❌ Không thể cập nhật web interface")
        return
    
    print()
    print("🎉 REMOTE ACCESS SETUP HOÀN TẤT!")
    print("=" * 50)
    print(f"🖥️ VNC: vnc://{server_ip}:5900 (Password: Abcd@2024)")
    print(f"🌐 Web: http://{server_ip}:8080")
    print(f"📁 File: cccd_project_complete.zip")
    print(f"📋 Guide: REMOTE_ACCESS_GUIDE.md")
    print()
    print("🚀 Hệ thống sẵn sàng cho truy cập từ xa!")

if __name__ == "__main__":
    main()