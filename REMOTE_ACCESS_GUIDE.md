
# 🌐 HƯỚNG DẪN TRUY CẬP TỪ XA

## 🖥️ VNC ACCESS (GUI Interface)

### Thông tin kết nối:
- **VNC URL:** vnc://172.30.0.2:5900
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
   - Nhập địa chỉ: 172.30.0.2:5900
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
- **Web URL:** http://172.30.0.2:8080
- **Port:** 8080
- **Protocol:** HTTP

### Cách truy cập:
1. **Mở browser** (Chrome, Firefox, Safari, Edge)
2. **Nhập URL:** http://172.30.0.2:8080
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
3. **Qua SSH:** scp user@172.30.0.2:/workspace/cccd_project_complete.zip ./

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
2. Kết nối: vnc://172.30.0.2:5900
3. Nhập password: Abcd@2024
4. Truy cập GUI

### Bước 2: Truy cập Web
1. Mở browser
2. Truy cập: http://172.30.0.2:8080
3. Xem thông tin dự án

### Bước 3: Tải file dự án
1. Qua VNC: Copy file từ /workspace/
2. Qua Web: Download từ interface
3. Extract và sử dụng

---

## 📞 HỖ TRỢ

### Thông tin server:
- **Server IP:** 172.30.0.2
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
