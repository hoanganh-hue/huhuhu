@echo off
REM Auto Install & Run Script cho Check CCCD (Windows)
REM Script tự động cài đặt dependencies, setup database và chạy hệ thống

setlocal enabledelayedexpansion

REM Project info
set PROJECT_NAME=Check CCCD API
set PROJECT_DIR=%~dp0
set LOG_FILE=%PROJECT_DIR%install.log

REM Colors (Windows doesn't support colors in batch, so we'll use text)
set INFO_PREFIX=[INFO]
set ERROR_PREFIX=[ERROR]
set WARNING_PREFIX=[WARNING]
set SUCCESS_PREFIX=[SUCCESS]

REM Logging function
:log
echo %INFO_PREFIX% [%date% %time%] %~1
echo %INFO_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:error
echo %ERROR_PREFIX% [%date% %time%] %~1
echo %ERROR_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:warning
echo %WARNING_PREFIX% [%date% %time%] %~1
echo %WARNING_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:success
echo %SUCCESS_PREFIX% [%date% %time%] %~1
echo %SUCCESS_PREFIX% [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

REM Print banner
:print_banner
echo ============================================================
echo 🔍 %PROJECT_NAME% - Auto Install ^& Run
echo ============================================================
goto :eof

REM Check system requirements
:check_requirements
call :log "🔍 Kiểm tra system requirements..."

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :error "❌ Python không được tìm thấy. Vui lòng cài đặt Python 3.8+"
    exit /b 1
)

REM Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    call :error "❌ pip không được tìm thấy. Vui lòng cài đặt pip"
    exit /b 1
)

REM Check requirements.txt
if not exist "requirements.txt" (
    call :error "❌ Không tìm thấy requirements.txt. Vui lòng chạy script từ thư mục project"
    exit /b 1
)

call :success "✅ System requirements OK"
goto :eof

REM Create virtual environment
:create_venv
call :log "🐍 Tạo virtual environment..."

if not exist "venv" (
    python -m venv venv
    call :success "✅ Virtual environment đã được tạo"
) else (
    call :log "✅ Virtual environment đã tồn tại"
)

REM Activate virtual environment
call venv\Scripts\activate.bat
call :success "✅ Virtual environment đã được kích hoạt"
goto :eof

REM Install dependencies
:install_dependencies
call :log "📦 Cài đặt dependencies..."

REM Upgrade pip
pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

call :success "✅ Dependencies đã được cài đặt"
goto :eof

REM Setup environment
:setup_environment
call :log "🔧 Thiết lập environment..."

REM Create .env file if not exists
if not exist ".env" (
    (
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///./check_cccd.db
        echo.
        echo # Redis Configuration ^(optional for development^)
        echo REDIS_URL=redis://localhost:6379/0
        echo.
        echo # API Security
        echo API_KEY=dev-api-key-123
        echo SECRET_KEY=dev-secret-key-123
        echo.
        echo # Rate Limiting
        echo RATE_LIMIT_PER_MINUTE=60
        echo RATE_LIMIT_BURST=10
        echo.
        echo # Scraping Configuration
        echo REQUEST_TIMEOUT=15.0
        echo MAX_RETRIES=3
        echo RETRY_DELAY=1.0
        echo.
        echo # Cache Configuration
        echo CACHE_TTL_SECONDS=3600
        echo.
        echo # Logging Configuration
        echo LOG_LEVEL=INFO
        echo LOG_FORMAT=text
        echo.
        echo # Monitoring Configuration
        echo ENABLE_METRICS=true
        echo.
        echo # Development/Production Mode
        echo ENVIRONMENT=development
    ) > .env
    call :success "✅ File .env đã được tạo"
) else (
    call :log "✅ File .env đã tồn tại"
)
goto :eof

REM Setup database
:setup_database
call :log "🗄️ Thiết lập database..."

REM Run database migration
python database_migration.py

if %errorlevel% equ 0 (
    call :success "✅ Database đã được thiết lập"
) else (
    call :error "❌ Lỗi khi thiết lập database"
    exit /b 1
)
goto :eof

REM Test installation
:test_installation
call :log "🧪 Kiểm tra installation..."

REM Test imports
python -c "import sys; sys.path.insert(0, 'src'); from check_cccd.app import app; from check_cccd.scraper import scrape_cccd_sync; from check_cccd.database import create_tables; print('✅ All imports successful')"

if %errorlevel% equ 0 (
    call :success "✅ Installation test passed"
) else (
    call :error "❌ Installation test failed"
    exit /b 1
)
goto :eof

REM Start services
:start_services
call :log "🚀 Khởi động services..."

echo.
echo 📖 API Documentation sẽ có tại: http://localhost:8000/docs
echo 🔍 Health Check sẽ có tại: http://localhost:8000/health
echo 📊 Metrics sẽ có tại: http://localhost:8000/metrics
echo.
echo 🎯 Để test API, chạy: python test_api.py
echo 🛑 Để dừng server, nhấn Ctrl+C
echo.

REM Start the application
python setup_and_run.py
goto :eof

REM Main installation function
:main
call :print_banner

REM Run installation steps
call :check_requirements
if %errorlevel% neq 0 exit /b 1

call :create_venv
if %errorlevel% neq 0 exit /b 1

call :install_dependencies
if %errorlevel% neq 0 exit /b 1

call :setup_environment
if %errorlevel% neq 0 exit /b 1

call :setup_database
if %errorlevel% neq 0 exit /b 1

call :test_installation
if %errorlevel% neq 0 exit /b 1

call :success "🎉 Installation hoàn tất thành công!"
call :log "🚀 Đang khởi động hệ thống..."

call :start_services
goto :eof

REM Handle command line arguments
if "%1"=="install" (
    call :print_banner
    call :check_requirements
    call :create_venv
    call :install_dependencies
    call :setup_environment
    call :setup_database
    call :test_installation
    call :success "🎉 Installation hoàn tất! Chạy 'auto_install_run.bat run' để khởi động"
    goto :eof
)

if "%1"=="run" (
    call :log "🚀 Khởi động hệ thống..."
    call venv\Scripts\activate.bat
    call :start_services
    goto :eof
)

if "%1"=="test" (
    call :log "🧪 Chạy tests..."
    call venv\Scripts\activate.bat
    python test_api.py
    goto :eof
)

if "%1"=="migrate" (
    call :log "🔄 Chạy database migration..."
    call venv\Scripts\activate.bat
    python database_migration.py
    goto :eof
)

if "%1"=="clean" (
    call :log "🧹 Cleaning up..."
    if exist venv rmdir /s /q venv
    if exist *.db del *.db
    if exist *.log del *.log
    call :success "✅ Cleanup hoàn tất"
    goto :eof
)

REM Default: run main installation
call :main