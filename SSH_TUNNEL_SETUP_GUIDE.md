# 🔐 HƯỚNG DẪN CẤU HÌNH SSH TUNNEL VIA NGROK

## 🎯 **TỔNG QUAN**

Hướng dẫn cấu hình SSH tunnel qua ngrok để chạy trên terminal riêng và duy trì kết nối.

### **📋 Các file đã tạo:**
1. **ngrok_config_template.yml** - Template cấu hình ngrok
2. **ssh_tunnel_daemon.sh** - Script daemon chạy tunnel
3. **ssh-tunnel.service** - Systemd service file
4. **start_ssh_tunnel_terminal.sh** - Script chạy trên terminal riêng

---

## 🔧 **BƯỚC 1: CẤU HÌNH NGROK**

### **1.1 Đăng ký ngrok account**
1. Truy cập: https://dashboard.ngrok.com/signup
2. Đăng ký account miễn phí
3. Xác thực email

### **1.2 Lấy authtoken**
1. Đăng nhập: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy authtoken của bạn

### **1.3 Cấu hình ngrok**
```bash
# Tạo config directory
mkdir -p ~/.config/ngrok

# Copy template
cp /workspace/ngrok_config_template.yml ~/.config/ngrok/ngrok.yml

# Edit config file
nano ~/.config/ngrok/ngrok.yml
```

### **1.4 Thêm authtoken**
Thay thế `YOUR_AUTHTOKEN_HERE` bằng authtoken thực của bạn:
```yaml
version: "2"
authtoken: YOUR_ACTUAL_AUTHTOKEN_HERE
tunnels:
  ssh:
    proto: tcp
    addr: 22
    remote_addr: 0.tcp.ngrok.io:0
```

---

## 🚀 **BƯỚC 2: CHẠY SSH TUNNEL**

### **2.1 Phương pháp 1: Terminal riêng (Khuyến nghị)**
```bash
# Chạy script trên terminal riêng
./start_ssh_tunnel_terminal.sh
```

**Tính năng:**
- ✅ Chạy trên terminal riêng
- ✅ Tự động restart khi tunnel bị đứt
- ✅ Hiển thị tunnel URL
- ✅ Monitor liên tục

### **2.2 Phương pháp 2: Daemon script**
```bash
# Chạy daemon script
./ssh_tunnel_daemon.sh
```

**Tính năng:**
- ✅ Chạy background
- ✅ Tự động restart
- ✅ Log file chi tiết

### **2.3 Phương pháp 3: Systemd service**
```bash
# Copy service file
sudo cp /workspace/ssh-tunnel.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable ssh-tunnel

# Start service
sudo systemctl start ssh-tunnel

# Check status
sudo systemctl status ssh-tunnel
```

---

## 📊 **MONITORING & LOGS**

### **3.1 Kiểm tra tunnel status**
```bash
# Check ngrok process
ps aux | grep ngrok

# Check tunnel logs
tail -f /tmp/ssh_tunnel_logs/ngrok_ssh.log

# Check tunnel URL
grep "started tunnel" /tmp/ssh_tunnel_logs/ngrok_ssh.log
```

### **3.2 Kiểm tra SSH service**
```bash
# Check SSH service
sudo service ssh status

# Check SSH port
netstat -tlnp | grep :22
```

---

## 🔗 **KẾT NỐI SSH**

### **4.1 Lấy tunnel URL**
```bash
# Từ log file
grep "started tunnel" /tmp/ssh_tunnel_logs/ngrok_ssh.log | grep -o "tcp://[^:]*:[0-9]*"

# Hoặc từ script output
./start_ssh_tunnel_terminal.sh
```

### **4.2 Kết nối SSH**
```bash
# Sử dụng tunnel URL
ssh ubuntu@[ngrok-host] -p [ngrok-port]

# Ví dụ:
ssh ubuntu@0.tcp.ngrok.io -p 12345
```

---

## 🛠️ **TROUBLESHOOTING**

### **5.1 Ngrok không hoạt động**
```bash
# Check ngrok version
ngrok version

# Check config
cat ~/.config/ngrok/ngrok.yml

# Test ngrok
ngrok tcp 22
```

### **5.2 SSH không kết nối**
```bash
# Check SSH service
sudo service ssh status

# Check SSH port
netstat -tlnp | grep :22

# Test local SSH
ssh ubuntu@localhost
```

### **5.3 Tunnel bị đứt**
```bash
# Check ngrok process
ps aux | grep ngrok

# Restart tunnel
pkill -f "ngrok tcp 22"
./start_ssh_tunnel_terminal.sh
```

---

## 📋 **COMMANDS HỮU ÍCH**

### **6.1 Start/Stop tunnel**
```bash
# Start tunnel
./start_ssh_tunnel_terminal.sh

# Stop tunnel
pkill -f "ngrok tcp 22"

# Restart tunnel
pkill -f "ngrok tcp 22" && ./start_ssh_tunnel_terminal.sh
```

### **6.2 Check status**
```bash
# Check tunnel status
ps aux | grep ngrok

# Check tunnel URL
grep "started tunnel" /tmp/ssh_tunnel_logs/ngrok_ssh.log

# Check SSH service
sudo service ssh status
```

### **6.3 View logs**
```bash
# View tunnel logs
tail -f /tmp/ssh_tunnel_logs/ngrok_ssh.log

# View system logs
sudo journalctl -u ssh-tunnel -f
```

---

## 🎯 **KẾT QUẢ MONG ĐỢI**

### **✅ Sau khi cấu hình thành công:**
1. **SSH Tunnel** chạy trên terminal riêng
2. **Tunnel URL** hiển thị liên tục
3. **Auto-restart** khi tunnel bị đứt
4. **SSH Access** qua ngrok URL
5. **Monitoring** liên tục

### **🔗 Thông tin kết nối:**
- **Tunnel URL:** tcp://0.tcp.ngrok.io:XXXXX
- **SSH Command:** ssh ubuntu@0.tcp.ngrok.io -p XXXXX
- **User:** ubuntu
- **Authentication:** Password-based

---

## 🎉 **KẾT LUẬN**

**SSH tunnel đã được cấu hình để:**
- ✅ Chạy trên terminal riêng
- ✅ Duy trì kết nối liên tục
- ✅ Tự động restart khi cần
- ✅ Monitor và log chi tiết
- ✅ Truy cập SSH từ xa qua ngrok

**🚀 Sẵn sàng sử dụng SSH tunnel!**