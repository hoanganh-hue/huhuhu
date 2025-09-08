# Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH - Setup Complete v2.0.0
# PowerShell Script

# Set encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║                    HỆ THỐNG TỰ ĐỘNG HÓA TRA CỨU THÔNG TIN BHXH              ║" -ForegroundColor Magenta
Write-Host "║                              SETUP COMPLETE v2.0.0                          ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# Kiểm tra Python
Write-Host "🔍 Kiểm tra Python..." -ForegroundColor Blue
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python đã được tìm thấy" -ForegroundColor Green
        Write-Host $pythonVersion -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python không được tìm thấy!" -ForegroundColor Red
    Write-Host "💡 Vui lòng cài đặt Python 3.8+ từ: https://python.org" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Nhấn Enter để thoát"
    exit 1
}

Write-Host ""

# Kiểm tra pip
Write-Host "🔍 Kiểm tra pip..." -ForegroundColor Blue
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip đã được tìm thấy" -ForegroundColor Green
    } else {
        throw "pip not found"
    }
} catch {
    Write-Host "❌ pip không được tìm thấy!" -ForegroundColor Red
    Write-Host "💡 Vui lòng cài đặt pip" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Nhấn Enter để thoát"
    exit 1
}

Write-Host ""

# Cập nhật pip
Write-Host "📦 Cập nhật pip..." -ForegroundColor Blue
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Không thể cập nhật pip, tiếp tục với phiên bản hiện tại" -ForegroundColor Yellow
}

Write-Host ""

# Cài đặt dependencies
Write-Host "📦 Cài đặt dependencies từ requirements.txt..." -ForegroundColor Blue
Write-Host "⏳ Đang cài đặt, vui lòng chờ..." -ForegroundColor Yellow
Write-Host ""

python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Lỗi cài đặt dependencies!" -ForegroundColor Red
    Write-Host "💡 Thử chạy: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Nhấn Enter để thoát"
    exit 1
}

Write-Host "✅ Cài đặt dependencies thành công!" -ForegroundColor Green
Write-Host ""

# Kiểm tra cài đặt
Write-Host "🔍 Kiểm tra cài đặt modules..." -ForegroundColor Blue
python -c "import rich, click, requests, pandas, openpyxl, cachetools, fastapi, uvicorn, beautifulsoup4, lxml; print('✅ Tất cả modules chính đã được cài đặt!')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Một số modules có thể chưa được cài đặt đầy đủ" -ForegroundColor Yellow
    Write-Host "💡 Thử chạy lại: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""

# Tạo file .env nếu chưa có
if (!(Test-Path ".env")) {
    Write-Host "📝 Tạo file .env..." -ForegroundColor Blue
    @"
# Hệ Thống Tự Động Hóa Tra Cứu Thông Tin BHXH
# Configuration File

# API Configuration
CAPTCHA_API_KEY=your_2captcha_api_key_here

# CCCD Generation
CCCD_COUNT=1000
CCCD_PROVINCE_CODE=001
CCCD_GENDER=Nam
CCCD_BIRTH_YEAR_FROM=1990
CCCD_BIRTH_YEAR_TO=2000

# System Configuration
LOG_LEVEL=INFO
DEBUG_MODE=false
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ File .env đã được tạo" -ForegroundColor Green
} else {
    Write-Host "✅ File .env đã tồn tại" -ForegroundColor Green
}

Write-Host ""

# Tạo thư mục cần thiết
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
if (!(Test-Path "output")) { New-Item -ItemType Directory -Path "output" }
if (!(Test-Path "output\cccd")) { New-Item -ItemType Directory -Path "output\cccd" }

Write-Host "✅ Thư mục cần thiết đã được tạo" -ForegroundColor Green
Write-Host ""

# Kiểm tra cuối cùng
Write-Host "🎯 Kiểm tra cuối cùng..." -ForegroundColor Blue
python test_imports.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Có lỗi trong quá trình kiểm tra" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║                              🎉 SETUP HOÀN THÀNH! 🎉                        ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""
Write-Host "🚀 SẴN SÀNG CHẠY HỆ THỐNG:" -ForegroundColor Green
Write-Host ""
Write-Host "   📱 GUI Interface (Khuyến nghị):" -ForegroundColor Cyan
Write-Host "      python gui_main.py" -ForegroundColor White
Write-Host ""
Write-Host "   💻 Command Line:" -ForegroundColor Cyan
Write-Host "      python main.py" -ForegroundColor White
Write-Host ""
Write-Host "   🖥️ Windows Scripts:" -ForegroundColor Cyan
Write-Host "      run_windows.bat" -ForegroundColor White
Write-Host "      run_windows_enhanced.bat" -ForegroundColor White
Write-Host ""
Write-Host "📋 CẤU HÌNH:" -ForegroundColor Yellow
Write-Host "   - Chỉnh sửa file .env để cấu hình API keys và tham số"
Write-Host "   - Đăng ký API key từ 2captcha.com cho module BHXH"
Write-Host ""
Write-Host "📚 TÀI LIỆU:" -ForegroundColor Yellow
Write-Host "   - README.md: Tài liệu chính"
Write-Host "   - INSTALLATION_QUICK.md: Hướng dẫn cài đặt nhanh"
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host ""
Read-Host "Nhấn Enter để thoát"