# 🚀 HƯỚNG DẪN CÀI ĐẶT NHANH

## ❌ Lỗi Thường Gặp: `No module named 'rich'`

Nếu bạn gặp lỗi này khi chạy `python gui_main.py`, hãy làm theo các bước sau:

---

## 🔧 GIẢI PHÁP NHANH

### **Phương Pháp 1: Cài Đặt Tự Động (Khuyến nghị)**

#### **Windows:**
```cmd
install_dependencies.bat
```

#### **Linux/Mac:**
```bash
./install_dependencies.sh
```

#### **Tất cả Platform:**
```bash
python install_dependencies.py
```

### **Phương Pháp 2: Cài Đặt Thủ Công**

```bash
# Cài đặt dependencies từ requirements.txt
pip install -r requirements.txt

# Hoặc cài đặt từng package cụ thể
pip install rich==13.7.0 click==8.1.7 requests==2.31.0 pandas==2.1.4
```

---

## 📋 DEPENDENCIES CẦN THIẾT

### **Core Dependencies:**
- `rich==13.7.0` - Enhanced console output
- `click==8.1.7` - CLI interface
- `requests==2.31.0` - HTTP requests
- `pandas==2.1.4` - Data processing
- `openpyxl==3.1.2` - Excel processing

### **GUI Dependencies:**
- `tkinter` - Built-in GUI (Python standard library)
- `Pillow==10.1.0` - Image processing

### **API Dependencies:**
- `fastapi==0.116.1` - Web API framework
- `uvicorn==0.35.0` - ASGI server
- `httpx==0.28.1` - HTTP client
- `beautifulsoup4==4.13.5` - HTML parsing
- `lxml==6.0.1` - XML/HTML processing

### **BHXH Tool Dependencies:**
- `pydantic==2.5.0` - Data validation
- `cachetools==5.3.2` - Caching
- `structlog==23.2.0` - Structured logging

---

## ✅ KIỂM TRA CÀI ĐẶT

Sau khi cài đặt, kiểm tra bằng cách chạy:

```bash
python -c "import rich, click, requests, pandas, openpyxl; print('✅ Tất cả modules đã được cài đặt!')"
```

---

## 🚀 CHẠY HỆ THỐNG

Sau khi cài đặt thành công:

### **GUI Interface (Khuyến nghị):**
```bash
python gui_main.py
```

### **Command Line:**
```bash
python main.py
```

### **Scripts:**
```bash
# Linux/Mac
./run_linux_mac.sh

# Windows
run_windows.bat
```

---

## 🔍 TROUBLESHOOTING

### **Lỗi 1: `No module named 'rich'`**
```bash
pip install rich==13.7.0
```

### **Lỗi 2: `No module named 'click'`**
```bash
pip install click==8.1.7
```

### **Lỗi 3: `No module named 'requests'`**
```bash
pip install requests==2.31.0
```

### **Lỗi 4: Permission denied (Linux/Mac)**
```bash
sudo pip install -r requirements.txt
# Hoặc sử dụng user install
pip install --user -r requirements.txt
```

### **Lỗi 5: Virtual Environment**
```bash
# Tạo virtual environment
python -m venv .venv

# Kích hoạt virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

---

## 📞 HỖ TRỢ

Nếu vẫn gặp lỗi, hãy:

1. **Kiểm tra Python version:** `python --version` (cần Python 3.8+)
2. **Kiểm tra pip:** `pip --version`
3. **Cập nhật pip:** `pip install --upgrade pip`
4. **Chạy script cài đặt:** `python install_dependencies.py`

---

**📅 Cập nhật:** 07/01/2025  
**👨‍💻 Tác giả:** MiniMax Agent  
**📋 Phiên bản:** 2.0.0 - PRODUCTION READY