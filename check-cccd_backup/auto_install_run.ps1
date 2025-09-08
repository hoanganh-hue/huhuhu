# Auto Install & Run Script cho Check CCCD (PowerShell)
# Script tự động cài đặt dependencies, setup database và chạy hệ thống

param(
    [string]$Action = "install"
)

# Colors
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Project info
$ProjectName = "Check CCCD API"
$ProjectDir = $PSScriptRoot
$LogFile = Join-Path $ProjectDir "install.log"

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor $Red }
        "WARNING" { Write-Host $logMessage -ForegroundColor $Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor $Green }
        "INFO" { Write-Host $logMessage -ForegroundColor $Blue }
        default { Write-Host $logMessage -ForegroundColor $White }
    }
    
    Add-Content -Path $LogFile -Value $logMessage -Encoding UTF8
}

function Write-Error-Log {
    param([string]$Message)
    Write-Log $Message "ERROR"
}

function Write-Warning-Log {
    param([string]$Message)
    Write-Log $Message "WARNING"
}

function Write-Success-Log {
    param([string]$Message)
    Write-Log $Message "SUCCESS"
}

# Print banner
function Show-Banner {
    Write-Host "============================================================" -ForegroundColor $Blue
    Write-Host "🔍 $ProjectName - Auto Install & Run" -ForegroundColor $Blue
    Write-Host "============================================================" -ForegroundColor $Blue
}

# Check system requirements
function Test-Requirements {
    Write-Log "🔍 Kiểm tra system requirements..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success-Log "✅ Python found: $pythonVersion"
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Error-Log "❌ Python không được tìm thấy. Vui lòng cài đặt Python 3.8+"
        exit 1
    }
    
    # Check pip
    try {
        pip --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success-Log "✅ pip found"
        } else {
            throw "pip not found"
        }
    } catch {
        Write-Error-Log "❌ pip không được tìm thấy. Vui lòng cài đặt pip"
        exit 1
    }
    
    # Check requirements.txt
    if (-not (Test-Path "requirements.txt")) {
        Write-Error-Log "❌ Không tìm thấy requirements.txt. Vui lòng chạy script từ thư mục project"
        exit 1
    }
    
    Write-Success-Log "✅ System requirements OK"
}

# Create virtual environment
function New-VirtualEnvironment {
    Write-Log "🐍 Tạo virtual environment..."
    
    if (-not (Test-Path "venv")) {
        python -m venv venv
        Write-Success-Log "✅ Virtual environment đã được tạo"
    } else {
        Write-Log "✅ Virtual environment đã tồn tại"
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $ProjectDir "venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        Write-Success-Log "✅ Virtual environment đã được kích hoạt"
    } else {
        Write-Error-Log "❌ Không thể kích hoạt virtual environment"
        exit 1
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Log "📦 Cài đặt dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success-Log "✅ Dependencies đã được cài đặt"
    } else {
        Write-Error-Log "❌ Lỗi khi cài đặt dependencies"
        exit 1
    }
}

# Setup environment
function Set-Environment {
    Write-Log "🔧 Thiết lập environment..."
    
    # Create .env file if not exists
    if (-not (Test-Path ".env")) {
        $envContent = @"
# Database Configuration
DATABASE_URL=sqlite:///./check_cccd.db

# Redis Configuration (optional for development)
REDIS_URL=redis://localhost:6379/0

# API Security
API_KEY=dev-api-key-123
SECRET_KEY=dev-secret-key-123

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Scraping Configuration
REQUEST_TIMEOUT=15.0
MAX_RETRIES=3
RETRY_DELAY=1.0

# Cache Configuration
CACHE_TTL_SECONDS=3600

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=text

# Monitoring Configuration
ENABLE_METRICS=true

# Development/Production Mode
ENVIRONMENT=development
"@
        
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success-Log "✅ File .env đã được tạo"
    } else {
        Write-Log "✅ File .env đã tồn tại"
    }
}

# Setup database
function Set-Database {
    Write-Log "🗄️ Thiết lập database..."
    
    # Run database migration
    python database_migration.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success-Log "✅ Database đã được thiết lập"
    } else {
        Write-Error-Log "❌ Lỗi khi thiết lập database"
        exit 1
    }
}

# Test installation
function Test-Installation {
    Write-Log "🧪 Kiểm tra installation..."
    
    # Test imports
    $testScript = @"
import sys
sys.path.insert(0, 'src')
try:
    from check_cccd.app import app
    from check_cccd.scraper import scrape_cccd_sync
    from check_cccd.database import create_tables
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"@
    
    $testScript | python
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success-Log "✅ Installation test passed"
    } else {
        Write-Error-Log "❌ Installation test failed"
        exit 1
    }
}

# Start services
function Start-Services {
    Write-Log "🚀 Khởi động services..."
    
    Write-Host ""
    Write-Host "📖 API Documentation sẽ có tại: http://localhost:8000/docs" -ForegroundColor $Blue
    Write-Host "🔍 Health Check sẽ có tại: http://localhost:8000/health" -ForegroundColor $Blue
    Write-Host "📊 Metrics sẽ có tại: http://localhost:8000/metrics" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "🎯 Để test API, chạy: python test_api.py" -ForegroundColor $Blue
    Write-Host "🛑 Để dừng server, nhấn Ctrl+C" -ForegroundColor $Blue
    Write-Host ""
    
    # Start the application
    python setup_and_run.py
}

# Main installation function
function Start-MainInstallation {
    Show-Banner
    
    # Run installation steps
    Test-Requirements
    New-VirtualEnvironment
    Install-Dependencies
    Set-Environment
    Set-Database
    Test-Installation
    
    Write-Success-Log "🎉 Installation hoàn tất thành công!"
    Write-Log "🚀 Đang khởi động hệ thống..."
    
    Start-Services
}

# Handle different actions
switch ($Action.ToLower()) {
    "install" {
        Show-Banner
        Test-Requirements
        New-VirtualEnvironment
        Install-Dependencies
        Set-Environment
        Set-Database
        Test-Installation
        Write-Success-Log "🎉 Installation hoàn tất! Chạy '.\auto_install_run.ps1 -Action run' để khởi động"
    }
    "run" {
        Write-Log "🚀 Khởi động hệ thống..."
        $activateScript = Join-Path $ProjectDir "venv\Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            & $activateScript
        }
        Start-Services
    }
    "test" {
        Write-Log "🧪 Chạy tests..."
        $activateScript = Join-Path $ProjectDir "venv\Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            & $activateScript
        }
        python test_api.py
    }
    "migrate" {
        Write-Log "🔄 Chạy database migration..."
        $activateScript = Join-Path $ProjectDir "venv\Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            & $activateScript
        }
        python database_migration.py
    }
    "clean" {
        Write-Log "🧹 Cleaning up..."
        if (Test-Path "venv") {
            Remove-Item -Recurse -Force "venv"
        }
        if (Test-Path "*.db") {
            Remove-Item -Force "*.db"
        }
        if (Test-Path "*.log") {
            Remove-Item -Force "*.log"
        }
        Write-Success-Log "✅ Cleanup hoàn tất"
    }
    default {
        Start-MainInstallation
    }
}