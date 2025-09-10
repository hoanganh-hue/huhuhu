#!/usr/bin/env python3
"""
Setup GUI và Web Interface cho máy chủ
"""

import os
import subprocess
import time
import signal
import sys

def start_xvfb():
    """Khởi động Xvfb (Virtual Display)"""
    try:
        print("🖥️ KHỞI ĐỘNG VIRTUAL DISPLAY")
        print("=" * 50)
        
        # Kiểm tra Xvfb đã chạy chưa
        result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Xvfb đã chạy")
            return True
        
        # Khởi động Xvfb
        print("🔄 Đang khởi động Xvfb...")
        cmd = ['Xvfb', ':99', '-screen', '0', '1920x1080x24', '-ac', '+extension', 'GLX', '+render', '-noreset']
        
        # Chạy Xvfb trong background
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Chờ một chút để Xvfb khởi động
        time.sleep(2)
        
        # Kiểm tra Xvfb đã chạy chưa
        result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Xvfb đã khởi động thành công")
            print(f"🖥️ Display: :99")
            print(f"📺 Resolution: 1920x1080x24")
            return True
        else:
            print("❌ Không thể khởi động Xvfb")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khởi động Xvfb: {e}")
        return False

def start_x11vnc():
    """Khởi động x11vnc server"""
    try:
        print("🌐 KHỞI ĐỘNG VNC SERVER")
        print("=" * 50)
        
        # Kiểm tra x11vnc đã chạy chưa
        result = subprocess.run(['pgrep', 'x11vnc'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ x11vnc đã chạy")
            return True
        
        # Khởi động x11vnc
        print("🔄 Đang khởi động x11vnc...")
        cmd = ['x11vnc', '-display', ':99', '-nopw', '-listen', '0.0.0.0', '-rfbport', '5900', '-forever', '-shared']
        
        # Chạy x11vnc trong background
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Chờ một chút để x11vnc khởi động
        time.sleep(3)
        
        # Kiểm tra x11vnc đã chạy chưa
        result = subprocess.run(['pgrep', 'x11vnc'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ x11vnc đã khởi động thành công")
            print(f"🌐 VNC Port: 5900")
            print(f"🔗 VNC URL: vnc://server-ip:5900")
            return True
        else:
            print("❌ Không thể khởi động x11vnc")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khởi động x11vnc: {e}")
        return False

def start_web_interface():
    """Khởi động Web Interface"""
    try:
        print("🌐 KHỞI ĐỘNG WEB INTERFACE")
        print("=" * 50)
        
        # Tạo web interface đơn giản
        web_content = """
<!DOCTYPE html>
<html>
<head>
    <title>CCCD Project - Server Interface</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .file-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #0056b3; }
        .vnc-info { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CCCD Project - Server Interface</h1>
            <p>Máy chủ GUI đã sẵn sàng</p>
        </div>
        
        <div class="status">
            <h3>✅ Trạng thái hệ thống</h3>
            <p>🖥️ Virtual Display: Đang chạy (Xvfb :99)</p>
            <p>🌐 VNC Server: Đang chạy (Port 5900)</p>
            <p>🌐 Web Interface: Đang chạy</p>
            <p>📁 File: cccd_project_complete.zip (2.2 MB)</p>
        </div>
        
        <div class="vnc-info">
            <h3>🖥️ Kết nối VNC</h3>
            <p>Để truy cập giao diện GUI, sử dụng VNC client:</p>
            <p><strong>VNC URL:</strong> vnc://server-ip:5900</p>
            <p><strong>Port:</strong> 5900</p>
            <p><strong>Password:</strong> Không cần (nopw)</p>
        </div>
        
        <div class="file-info">
            <h3>📁 Thông tin file</h3>
            <p><strong>Tên file:</strong> cccd_project_complete.zip</p>
            <p><strong>Kích thước:</strong> 2.2 MB</p>
            <p><strong>Vị trí:</strong> /workspace/cccd_project_complete.zip</p>
            <p><strong>Trạng thái:</strong> Sẵn sàng upload</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="button" onclick="window.open('https://drive.google.com/', '_blank')">🌐 Mở Google Drive</button>
            <button class="button" onclick="location.reload()">🔄 Refresh</button>
        </div>
    </div>
</body>
</html>
"""
        
        # Lưu web interface
        with open('/workspace/index.html', 'w', encoding='utf-8') as f:
            f.write(web_content)
        
        # Khởi động web server đơn giản
        print("🔄 Đang khởi động web server...")
        cmd = ['python3', '-m', 'http.server', '8080', '--directory', '/workspace']
        
        # Chạy web server trong background
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Chờ một chút để web server khởi động
        time.sleep(2)
        
        print("✅ Web Interface đã khởi động thành công")
        print(f"🌐 Web URL: http://server-ip:8080")
        print(f"📄 File: /workspace/index.html")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khởi động web interface: {e}")
        return False

def get_server_info():
    """Lấy thông tin server"""
    try:
        print("📊 THÔNG TIN SERVER")
        print("=" * 50)
        
        # Lấy IP address
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ip = result.stdout.strip().split()[0]
            print(f"🌐 Server IP: {ip}")
            print(f"🖥️ VNC URL: vnc://{ip}:5900")
            print(f"🌐 Web URL: http://{ip}:8080")
        else:
            print("❌ Không thể lấy IP address")
        
        # Lấy thông tin hệ thống
        print(f"🖥️ Display: :99")
        print(f"📺 Resolution: 1920x1080x24")
        print(f"🌐 VNC Port: 5900")
        print(f"🌐 Web Port: 8080")
        
    except Exception as e:
        print(f"❌ Lỗi lấy thông tin server: {e}")

def main():
    """Hàm chính"""
    print("🚀 SETUP GUI VÀ WEB INTERFACE")
    print("=" * 60)
    
    # Khởi động Virtual Display
    if not start_xvfb():
        print("❌ Không thể khởi động Virtual Display")
        return
    
    print()
    
    # Khởi động VNC Server
    if not start_x11vnc():
        print("❌ Không thể khởi động VNC Server")
        return
    
    print()
    
    # Khởi động Web Interface
    if not start_web_interface():
        print("❌ Không thể khởi động Web Interface")
        return
    
    print()
    
    # Hiển thị thông tin server
    get_server_info()
    
    print()
    print("🎉 SETUP HOÀN TẤT!")
    print("=" * 50)
    print("✅ Virtual Display: Đang chạy")
    print("✅ VNC Server: Đang chạy")
    print("✅ Web Interface: Đang chạy")
    print("📁 File: cccd_project_complete.zip sẵn sàng")
    print()
    print("🌐 Truy cập Web Interface để xem thông tin chi tiết")
    print("🖥️ Sử dụng VNC client để truy cập GUI")

if __name__ == "__main__":
    main()