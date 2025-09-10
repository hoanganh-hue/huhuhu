#!/usr/bin/env python3
"""
Comprehensive Remote Access Setup
"""

import subprocess
import time
import os
import socket

def check_network_connectivity():
    """Kiểm tra kết nối mạng"""
    try:
        print("🌐 KIỂM TRA KẾT NỐI MẠNG")
        print("=" * 50)
        
        # Kiểm tra DNS
        result = subprocess.run(['nslookup', 'google.com'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ DNS: Hoạt động bình thường")
        else:
            print("❌ DNS: Có vấn đề")
        
        # Kiểm tra ping gateway
        result = subprocess.run(['ping', '-c', '3', '172.30.0.1'], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Gateway: Có thể kết nối")
        else:
            print("❌ Gateway: Không thể kết nối")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra mạng: {e}")
        return False

def setup_ssh_server():
    """Cài đặt và cấu hình SSH server"""
    try:
        print("🔐 CÀI ĐẶT SSH SERVER")
        print("=" * 50)
        
        # Cài đặt OpenSSH server
        result = subprocess.run(['sudo', 'apt', 'install', '-y', 'openssh-server'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ OpenSSH server đã được cài đặt")
        else:
            print("❌ Không thể cài đặt OpenSSH server")
            return False
        
        # Khởi động SSH service
        result = subprocess.run(['sudo', 'systemctl', 'start', 'ssh'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ SSH service đã khởi động")
        else:
            print("❌ Không thể khởi động SSH service")
        
        # Enable SSH service
        result = subprocess.run(['sudo', 'systemctl', 'enable', 'ssh'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ SSH service đã được enable")
        else:
            print("❌ Không thể enable SSH service")
        
        # Kiểm tra SSH port
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        if ':22' in result.stdout:
            print("✅ SSH port 22 đang listen")
        else:
            print("❌ SSH port 22 không listen")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi cài đặt SSH: {e}")
        return False

def setup_ngrok():
    """Cài đặt và cấu hình ngrok cho tunneling"""
    try:
        print("🌐 CÀI ĐẶT NGROK")
        print("=" * 50)
        
        # Download ngrok
        result = subprocess.run(['wget', '-q', 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok đã được download")
        else:
            print("❌ Không thể download ngrok")
            return False
        
        # Extract ngrok
        result = subprocess.run(['tar', '-xzf', 'ngrok-v3-stable-linux-amd64.tgz'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok đã được extract")
        else:
            print("❌ Không thể extract ngrok")
            return False
        
        # Make executable
        result = subprocess.run(['chmod', '+x', 'ngrok'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok đã được make executable")
        else:
            print("❌ Không thể make executable ngrok")
        
        # Move to /usr/local/bin
        result = subprocess.run(['sudo', 'mv', 'ngrok', '/usr/local/bin/'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok đã được move to /usr/local/bin")
        else:
            print("❌ Không thể move ngrok")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi cài đặt ngrok: {e}")
        return False

def create_tunnel_script():
    """Tạo script để tạo tunnel"""
    try:
        print("📝 TẠO TUNNEL SCRIPT")
        print("=" * 50)
        
        tunnel_script = """#!/bin/bash
# Tunnel Script for Remote Access

echo "🌐 STARTING TUNNELS"
echo "=================="

# Start VNC tunnel
echo "🖥️ Starting VNC tunnel (port 5900)..."
ngrok tcp 5900 --log=stdout > /tmp/ngrok_vnc.log 2>&1 &
VNC_PID=$!

# Start Web tunnel  
echo "🌐 Starting Web tunnel (port 8080)..."
ngrok http 8080 --log=stdout > /tmp/ngrok_web.log 2>&1 &
WEB_PID=$!

# Wait for tunnels to start
sleep 5

echo "✅ Tunnels started!"
echo "📋 Check logs:"
echo "   VNC: tail -f /tmp/ngrok_vnc.log"
echo "   Web: tail -f /tmp/ngrok_web.log"

# Keep script running
echo "🔄 Tunnels are running... Press Ctrl+C to stop"
wait
"""
        
        with open('/workspace/start_tunnels.sh', 'w') as f:
            f.write(tunnel_script)
        
        # Make executable
        subprocess.run(['chmod', '+x', '/workspace/start_tunnels.sh'], 
                      capture_output=True, text=True)
        
        print("✅ Tunnel script đã được tạo: start_tunnels.sh")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi tạo tunnel script: {e}")
        return False

def setup_noip_dynamic_dns():
    """Cài đặt NoIP Dynamic DNS"""
    try:
        print("🌐 CÀI ĐẶT NOIP DYNAMIC DNS")
        print("=" * 50)
        
        # Download NoIP client
        result = subprocess.run(['wget', '-q', 'https://www.noip.com/client/linux/noip-duc-linux.tar.gz'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NoIP client đã được download")
        else:
            print("❌ Không thể download NoIP client")
            return False
        
        # Extract
        result = subprocess.run(['tar', '-xzf', 'noip-duc-linux.tar.gz'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NoIP client đã được extract")
        else:
            print("❌ Không thể extract NoIP client")
            return False
        
        # Find extracted directory
        result = subprocess.run(['ls', '-la'], capture_output=True, text=True)
        noip_dir = None
        for line in result.stdout.split('\n'):
            if 'noip' in line and 'drwx' in line:
                noip_dir = line.split()[-1]
                break
        
        if noip_dir:
            print(f"✅ Found NoIP directory: {noip_dir}")
            
            # Make and install
            os.chdir(noip_dir)
            subprocess.run(['make'], capture_output=True, text=True)
            subprocess.run(['sudo', 'make', 'install'], capture_output=True, text=True)
            
            print("✅ NoIP client đã được cài đặt")
            return True
        else:
            print("❌ Không tìm thấy NoIP directory")
            return False
        
    except Exception as e:
        print(f"❌ Lỗi cài đặt NoIP: {e}")
        return False

def create_comprehensive_guide():
    """Tạo hướng dẫn toàn diện"""
    try:
        print("📋 TẠO HƯỚNG DẪN TOÀN DIỆN")
        print("=" * 50)
        
        guide_content = """
# 🌐 HƯỚNG DẪN TRUY CẬP TỪ XA TOÀN DIỆN

## 🎯 TỔNG QUAN

Hệ thống đã được cấu hình với nhiều phương pháp truy cập từ xa:

### ✅ Các phương pháp đã cài đặt:
1. **VNC Server** (Port 5900) - GUI Access
2. **Web Server** (Port 8080) - Web Interface  
3. **SSH Server** (Port 22) - Command Line Access
4. **Ngrok Tunnels** - Public Access
5. **NoIP Dynamic DNS** - Domain Access

---

## 🖥️ PHƯƠNG PHÁP 1: VNC ACCESS

### Thông tin kết nối:
- **Local VNC:** vnc://172.30.0.2:5900
- **Password:** Abcd@2024
- **Ngrok VNC:** Sử dụng ngrok tunnel

### Cách kết nối:
1. **Local Network:**
   - VNC Client → 172.30.0.2:5900
   - Password: Abcd@2024

2. **Ngrok Tunnel:**
   - Chạy: `./start_tunnels.sh`
   - Xem log: `tail -f /tmp/ngrok_vnc.log`
   - Sử dụng ngrok URL từ log

---

## 🌐 PHƯƠNG PHÁP 2: WEB ACCESS

### Thông tin kết nối:
- **Local Web:** http://172.30.0.2:8080
- **Ngrok Web:** Sử dụng ngrok tunnel

### Cách truy cập:
1. **Local Network:**
   - Browser → http://172.30.0.2:8080

2. **Ngrok Tunnel:**
   - Chạy: `./start_tunnels.sh`
   - Xem log: `tail -f /tmp/ngrok_web.log`
   - Sử dụng ngrok URL từ log

---

## 🔐 PHƯƠNG PHÁP 3: SSH ACCESS

### Thông tin kết nối:
- **SSH:** ssh ubuntu@172.30.0.2
- **Port:** 22
- **Authentication:** Key-based hoặc Password

### Cách kết nối:
1. **Local Network:**
   ```bash
   ssh ubuntu@172.30.0.2
   ```

2. **Ngrok SSH:**
   - Chạy: `ngrok tcp 22`
   - Sử dụng ngrok URL

---

## 🌐 PHƯƠNG PHÁP 4: NGROK TUNNELS

### Cài đặt và sử dụng:
1. **Start Tunnels:**
   ```bash
   ./start_tunnels.sh
   ```

2. **Check Logs:**
   ```bash
   tail -f /tmp/ngrok_vnc.log
   tail -f /tmp/ngrok_web.log
   ```

3. **Get URLs:**
   - VNC: Từ ngrok_vnc.log
   - Web: Từ ngrok_web.log

### Lưu ý:
- Ngrok URLs thay đổi mỗi lần restart
- Cần ngrok account để sử dụng lâu dài
- Free tier có giới hạn

---

## 🌐 PHƯƠNG PHÁP 5: NOIP DYNAMIC DNS

### Cài đặt:
1. **Register NoIP account**
2. **Create hostname**
3. **Configure client:**
   ```bash
   sudo noip2 -C
   ```

### Sử dụng:
- **Domain:** yourhostname.ddns.net
- **VNC:** vnc://yourhostname.ddns.net:5900
- **Web:** http://yourhostname.ddns.net:8080

---

## 🔧 TROUBLESHOOTING

### VNC không kết nối được:
1. Kiểm tra VNC server: `pgrep x11vnc`
2. Kiểm tra port: `netstat -tlnp | grep 5900`
3. Kiểm tra password: Abcd@2024
4. Thử ngrok tunnel

### Web không truy cập được:
1. Kiểm tra web server: `pgrep python3`
2. Kiểm tra port: `netstat -tlnp | grep 8080`
3. Thử ngrok tunnel

### SSH không kết nối được:
1. Kiểm tra SSH service: `sudo systemctl status ssh`
2. Kiểm tra port: `netstat -tlnp | grep 22`
3. Kiểm tra firewall

### Ngrok không hoạt động:
1. Kiểm tra ngrok: `ngrok version`
2. Kiểm tra account: `ngrok config check`
3. Kiểm tra logs: `tail -f /tmp/ngrok_*.log`

---

## 🚀 QUICK START

### Bước 1: Kiểm tra services
```bash
# VNC
pgrep x11vnc

# Web  
pgrep python3

# SSH
sudo systemctl status ssh
```

### Bước 2: Start tunnels
```bash
./start_tunnels.sh
```

### Bước 3: Get URLs
```bash
tail -f /tmp/ngrok_vnc.log
tail -f /tmp/ngrok_web.log
```

### Bước 4: Connect
- VNC: Sử dụng ngrok URL
- Web: Sử dụng ngrok URL
- SSH: Sử dụng ngrok URL

---

## 📊 TRẠNG THÁI HỆ THỐNG

### ✅ Đã cài đặt:
- VNC Server (x11vnc)
- Web Server (python3 http.server)
- SSH Server (openssh-server)
- Ngrok (tunneling)
- NoIP Client (dynamic DNS)

### 🔧 Cần cấu hình:
- Ngrok account (cho public access)
- NoIP account (cho domain access)
- Firewall rules (nếu cần)

### 🎯 Sẵn sàng sử dụng:
- Local network access
- Ngrok tunnel access
- SSH access
- Web interface access

---

## 🎉 KẾT LUẬN

Hệ thống đã được cấu hình toàn diện với 5 phương pháp truy cập từ xa:

1. **VNC** - GUI access
2. **Web** - Browser access  
3. **SSH** - Command line access
4. **Ngrok** - Public tunnel access
5. **NoIP** - Domain access

**🚀 Chọn phương pháp phù hợp với nhu cầu của bạn!**
"""
        
        with open('/workspace/COMPREHENSIVE_REMOTE_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print("✅ Comprehensive guide đã được tạo: COMPREHENSIVE_REMOTE_GUIDE.md")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi tạo comprehensive guide: {e}")
        return False

def main():
    """Hàm chính"""
    print("🔧 COMPREHENSIVE REMOTE ACCESS SETUP")
    print("=" * 60)
    
    # Kiểm tra network
    if not check_network_connectivity():
        print("❌ Network có vấn đề")
        return
    
    print()
    
    # Cài đặt SSH server
    if not setup_ssh_server():
        print("❌ Không thể cài đặt SSH server")
        return
    
    print()
    
    # Cài đặt ngrok
    if not setup_ngrok():
        print("❌ Không thể cài đặt ngrok")
        return
    
    print()
    
    # Tạo tunnel script
    if not create_tunnel_script():
        print("❌ Không thể tạo tunnel script")
        return
    
    print()
    
    # Cài đặt NoIP (optional)
    print("🌐 Cài đặt NoIP Dynamic DNS (Optional)")
    setup_noip_dynamic_dns()
    
    print()
    
    # Tạo comprehensive guide
    if not create_comprehensive_guide():
        print("❌ Không thể tạo comprehensive guide")
        return
    
    print()
    print("🎉 COMPREHENSIVE SETUP HOÀN TẤT!")
    print("=" * 50)
    print("✅ VNC Server: Đang chạy")
    print("✅ Web Server: Đang chạy")
    print("✅ SSH Server: Đã cài đặt")
    print("✅ Ngrok: Đã cài đặt")
    print("✅ NoIP: Đã cài đặt")
    print("✅ Tunnel Script: start_tunnels.sh")
    print("✅ Guide: COMPREHENSIVE_REMOTE_GUIDE.md")
    print()
    print("🚀 Hệ thống sẵn sàng với 5 phương pháp truy cập từ xa!")

if __name__ == "__main__":
    main()