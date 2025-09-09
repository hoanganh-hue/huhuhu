# 🌐 HƯỚNG DẪN TRUY CẬP HOÀN CHỈNH

## 🎯 **TỔNG QUAN**

Hệ thống đã được cấu hình hoàn chỉnh với 4 phương pháp truy cập từ xa:

### ✅ **Các phương pháp đã cài đặt:**
1. **VNC Server** (Port 5900) - GUI Access
2. **Web Server** (Port 8080) - Web Interface  
3. **SSH Server** (Port 22) - Command Line Access
4. **Ngrok Tunnels** - Public Access

---

## 🖥️ **PHƯƠNG PHÁP 1: VNC ACCESS**

### **Thông tin kết nối:**
- **Local VNC:** vnc://172.30.0.2:5900
- **Password:** Abcd@2024
- **Ngrok VNC:** Sử dụng ngrok tunnel

### **Cách kết nối:**
1. **Local Network:**
   - VNC Client → 172.30.0.2:5900
   - Password: Abcd@2024

2. **Ngrok Tunnel:**
   - Chạy: `./start_tunnels.sh`
   - Xem log: `tail -f /tmp/ngrok_vnc.log`
   - Sử dụng ngrok URL từ log

### **Tính năng:**
- ✅ Truy cập giao diện GUI đầy đủ
- ✅ Điều khiển từ xa
- ✅ Chia sẻ màn hình
- ✅ Bảo mật password

---

## 🌐 **PHƯƠNG PHÁP 2: WEB ACCESS**

### **Thông tin kết nối:**
- **Local Web:** http://172.30.0.2:8080
- **Ngrok Web:** Sử dụng ngrok tunnel

### **Cách truy cập:**
1. **Local Network:**
   - Browser → http://172.30.0.2:8080

2. **Ngrok Tunnel:**
   - Chạy: `./start_tunnels.sh`
   - Xem log: `tail -f /tmp/ngrok_web.log`
   - Sử dụng ngrok URL từ log

### **Tính năng:**
- ✅ Xem trạng thái hệ thống
- ✅ Thông tin file dự án
- ✅ Hướng dẫn sử dụng
- ✅ Links truy cập

---

## 🔐 **PHƯƠNG PHÁP 3: SSH ACCESS**

### **Thông tin kết nối:**
- **SSH:** ssh ubuntu@172.30.0.2
- **Port:** 22
- **Authentication:** Key-based hoặc Password

### **Cách kết nối:**
1. **Local Network:**
   ```bash
   ssh ubuntu@172.30.0.2
   ```

2. **Ngrok SSH:**
   - Chạy: `./start_tunnels.sh`
   - Xem log: `tail -f /tmp/ngrok_ssh.log`
   - Sử dụng ngrok URL

### **Tính năng:**
- ✅ Command line access
- ✅ File transfer (scp, rsync)
- ✅ Port forwarding
- ✅ Secure connection

---

## 🌐 **PHƯƠNG PHÁP 4: NGROK TUNNELS**

### **Cài đặt và sử dụng:**
1. **Start Tunnels:**
   ```bash
   ./start_tunnels.sh
   ```

2. **Check Logs:**
   ```bash
   tail -f /tmp/ngrok_vnc.log
   tail -f /tmp/ngrok_web.log
   tail -f /tmp/ngrok_ssh.log
   ```

3. **Get URLs:**
   - VNC: Từ ngrok_vnc.log
   - Web: Từ ngrok_web.log
   - SSH: Từ ngrok_ssh.log

### **Lưu ý:**
- Ngrok URLs thay đổi mỗi lần restart
- Cần ngrok account để sử dụng lâu dài
- Free tier có giới hạn

---

## 🔧 **TROUBLESHOOTING**

### **VNC không kết nối được:**
1. Kiểm tra VNC server: `pgrep x11vnc`
2. Kiểm tra port: `netstat -tlnp | grep 5900`
3. Kiểm tra password: Abcd@2024
4. Thử ngrok tunnel

### **Web không truy cập được:**
1. Kiểm tra web server: `pgrep python3`
2. Kiểm tra port: `netstat -tlnp | grep 8080`
3. Thử ngrok tunnel

### **SSH không kết nối được:**
1. Kiểm tra SSH service: `sudo service ssh status`
2. Kiểm tra port: `netstat -tlnp | grep 22`
3. Thử ngrok tunnel

### **Ngrok không hoạt động:**
1. Kiểm tra ngrok: `ngrok version`
2. Kiểm tra account: `ngrok config check`
3. Kiểm tra logs: `tail -f /tmp/ngrok_*.log`

---

## 🚀 **QUICK START**

### **Bước 1: Kiểm tra services**
```bash
# VNC
pgrep x11vnc

# Web  
pgrep python3

# SSH
sudo service ssh status
```

### **Bước 2: Start tunnels**
```bash
./start_tunnels.sh
```

### **Bước 3: Get URLs**
```bash
tail -f /tmp/ngrok_vnc.log
tail -f /tmp/ngrok_web.log
tail -f /tmp/ngrok_ssh.log
```

### **Bước 4: Connect**
- VNC: Sử dụng ngrok URL
- Web: Sử dụng ngrok URL
- SSH: Sử dụng ngrok URL

---

## 📊 **TRẠNG THÁI HỆ THỐNG**

### **✅ Đã cài đặt:**
- VNC Server (x11vnc)
- Web Server (python3 http.server)
- SSH Server (openssh-server)
- Ngrok (tunneling)
- Tunnel Script (start_tunnels.sh)

### **🔧 Cần cấu hình:**
- Ngrok account (cho public access)
- SSH keys (cho key-based auth)
- Firewall rules (nếu cần)

### **🎯 Sẵn sàng sử dụng:**
- Local network access
- Ngrok tunnel access
- SSH access
- Web interface access

---

## 🎉 **KẾT LUẬN**

Hệ thống đã được cấu hình hoàn chỉnh với 4 phương pháp truy cập từ xa:

1. **VNC** - GUI access
2. **Web** - Browser access  
3. **SSH** - Command line access
4. **Ngrok** - Public tunnel access

**🚀 Chọn phương pháp phù hợp với nhu cầu của bạn!**

---

## 📞 **HỖ TRỢ**

### **Thông tin server:**
- **Server IP:** 172.30.0.2
- **VNC Port:** 5900
- **Web Port:** 8080
- **SSH Port:** 22
- **VNC Password:** Abcd@2024

### **Troubleshooting:**
- **VNC không kết nối:** Kiểm tra password Abcd@2024
- **Web không truy cập:** Kiểm tra port 8080
- **SSH không kết nối:** Kiểm tra port 22
- **File không tải được:** Kiểm tra quyền truy cập

**🎉 Hệ thống sẵn sàng cho truy cập từ xa!**