# 🔧 TROUBLESHOOTING GUIDE - Check CCCD System

## 📋 Troubleshooting cho các lỗi thường gặp

---

## 🚨 Lỗi Bot Detection (403 Forbidden)

### **Triệu chứng:**
```
HTTP 403 Forbidden
Bot detected
Request blocked
```

### **Nguyên nhân:**
- Delay quá ngắn
- User agent không hợp lệ
- Headers thiếu hoặc không đúng
- Request frequency quá cao
- IP bị blacklist

### **Giải pháp:**

#### 1. **Kiểm tra và tăng delay**
```bash
# Trong .env file
MIN_DELAY_SECONDS=2.0
MAX_DELAY_SECONDS=5.0
```

#### 2. **Verify user agents**
```python
# Kiểm tra user agents trong anti_bot.py
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...",
    # Đảm bảo có ít nhất 10+ user agents
]
```

#### 3. **Kiểm tra headers configuration**
```python
# Trong anti_bot.py - get_random_headers()
headers = {
    "User-Agent": random.choice(self.user_agents),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
```

#### 4. **Giảm request frequency**
```bash
# Trong .env
RATE_LIMIT_PER_MINUTE=20  # Giảm từ 30 xuống 20
RATE_LIMIT_BURST=3        # Giảm từ 5 xuống 3
```

#### 5. **Test với IP khác**
```bash
# Nếu có thể, sử dụng proxy hoặc VPN
# Hoặc đợi 24h để IP được reset
```

---

## 🌐 Lỗi Network/Connection

### **Triệu chứng:**
```
Connection timeout
Network unreachable
DNS resolution failed
SSL certificate error
```

### **Nguyên nhân:**
- Timeout quá ngắn
- Network instability
- DNS issues
- SSL certificate problems
- Firewall blocking

### **Giải pháp:**

#### 1. **Tăng timeout settings**
```bash
# Trong .env
REQUEST_TIMEOUT=30.0      # Tăng từ 25.0 lên 30.0
MAX_RETRIES=5            # Tăng từ 3 lên 5
RETRY_DELAY=3.0          # Tăng từ 2.0 lên 3.0
```

#### 2. **Kiểm tra network connectivity**
```bash
# Test internet connection
ping -c 4 google.com

# Test DNS resolution
nslookup masothue.com

# Test specific port
telnet masothue.com 443
```

#### 3. **Verify SSL certificates**
```bash
# Check SSL certificate
openssl s_client -connect masothue.com:443 -servername masothue.com

# Update CA certificates
sudo apt update && sudo apt install ca-certificates
```

#### 4. **Firewall configuration**
```bash
# Check firewall status
sudo ufw status
sudo iptables -L

# Allow outbound connections
sudo ufw allow out to any port 80
sudo ufw allow out to any port 443
```

#### 5. **Proxy configuration (nếu cần)**
```bash
# Trong .env (nếu sử dụng proxy)
HTTP_PROXY=http://proxy-server:port
HTTPS_PROXY=http://proxy-server:port
```

---

## 🗄️ Lỗi Database

### **Triệu chứng:**
```
Database connection failed
Table doesn't exist
Migration failed
```

### **Nguyên nhân:**
- Database server not running
- Connection string sai
- Permissions issue
- Migration chưa chạy

### **Giải pháp:**

#### 1. **Kiểm tra database connection**
```bash
# For SQLite
ls -la check_cccd_prod.db

# For PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"
```

#### 2. **Verify connection string**
```bash
# Trong .env
DATABASE_URL=sqlite:///./check_cccd_prod.db

# Test connection
python3 -c "
import sqlite3
conn = sqlite3.connect('check_cccd_prod.db')
print('✅ Database connection successful')
conn.close()
"
```

#### 3. **Chạy database migration**
```bash
# Chạy migration script
python database_migration.py

# Hoặc tạo tables manually
python3 -c "
from src.check_cccd.database import create_tables
create_tables()
print('✅ Tables created successfully')
"
```

#### 4. **Check database permissions**
```bash
# For SQLite
chmod 644 check_cccd_prod.db

# For PostgreSQL
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE check_cccd_prod TO check_cccd_user;"
```

---

## 🔴 Lỗi Redis/Caching

### **Triệu chứng:**
```
Redis connection failed
Cache not working
Performance degraded
```

### **Nguyên nhân:**
- Redis server not running
- Connection string sai
- Memory issues
- Configuration problems

### **Giải pháp:**

#### 1. **Kiểm tra Redis status**
```bash
# Check Redis service
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Check Redis info
redis-cli info
```

#### 2. **Verify Redis configuration**
```bash
# Trong .env
REDIS_URL=redis://localhost:6379/0

# Test Redis connection
python3 -c "
import redis
r = redis.from_url('redis://localhost:6379/0')
r.ping()
print('✅ Redis connection successful')
"
```

#### 3. **Redis memory optimization**
```bash
# Check Redis memory usage
redis-cli info memory

# Configure Redis memory limits
echo "maxmemory 512mb" | sudo tee -a /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" | sudo tee -a /etc/redis/redis.conf

# Restart Redis
sudo systemctl restart redis-server
```

#### 4. **Disable caching nếu Redis fail**
```bash
# Trong .env (temporary)
ENABLE_CACHING=false

# Restart application
sudo systemctl restart check-cccd
```

---

## ⚡ Lỗi Performance

### **Triệu chứng:**
```
Slow response times
High CPU usage
Memory leaks
Timeout errors
```

### **Nguyên nhân:**
- Connection pooling issues
- Memory leaks
- High concurrent requests
- Resource constraints

### **Giải pháp:**

#### 1. **Optimize connection pooling**
```bash
# Trong .env
HTTP_MAX_KEEPALIVE_CONNECTIONS=15  # Giảm từ 20
HTTP_MAX_CONNECTIONS=30            # Giảm từ 50
HTTP_KEEPALIVE_EXPIRY=20.0         # Giảm từ 30.0
```

#### 2. **Monitor system resources**
```bash
# Check CPU usage
top
htop

# Check memory usage
free -h
vmstat 1

# Check disk I/O
iotop
iostat -x 1
```

#### 3. **Python memory optimization**
```bash
# Trong startup script
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Restart application
sudo systemctl restart check-cccd
```

#### 4. **Database query optimization**
```bash
# Enable database query logging
echo "PRAGMA journal_mode=WAL;" | sqlite3 check_cccd_prod.db
echo "PRAGMA synchronous=NORMAL;" | sqlite3 check_cccd_prod.db
echo "PRAGMA cache_size=10000;" | sqlite3 check_cccd_prod.db
```

---

## 🔒 Lỗi Security/SSL

### **Triệu chứng:**
```
SSL certificate error
HTTPS connection failed
Security warnings
```

### **Nguyên nhân:**
- SSL certificate expired
- CA certificates outdated
- SSL configuration issues
- Security headers missing

### **Giải pháp:**

#### 1. **Update SSL certificates**
```bash
# Update CA certificates
sudo apt update && sudo apt install ca-certificates

# Renew Let's Encrypt certificate
sudo certbot renew

# Check certificate validity
openssl s_client -connect your-domain.com:443 -servername your-domain.com | openssl x509 -noout -dates
```

#### 2. **SSL configuration trong Nginx**
```nginx
# Trong /etc/nginx/sites-available/check-cccd
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
}
```

#### 3. **Security headers**
```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## 📊 Lỗi Monitoring/Metrics

### **Triệu chứng:**
```
Metrics not collecting
Dashboard not updating
Alerting not working
```

### **Nguyên nhân:**
- Monitoring service not running
- Configuration issues
- Storage problems
- Permission issues

### **Giải pháp:**

#### 1. **Kiểm tra monitoring service**
```bash
# Check monitoring status
python3 monitoring_dashboard.py

# Test metrics collection
curl http://localhost:8000/metrics
```

#### 2. **Verify monitoring configuration**
```bash
# Trong .env
ENABLE_MONITORING=true
METRICS_EXPORT_INTERVAL=60
METRICS_RETENTION_DAYS=30

# Check metrics directory permissions
ls -la metrics/
chmod 755 metrics/
```

#### 3. **Restart monitoring services**
```bash
# Restart application
sudo systemctl restart check-cccd

# Check logs
tail -f logs/check_cccd.log
```

---

## 🚀 Quick Fix Commands

### **Emergency restart**
```bash
# Stop all services
sudo systemctl stop check-cccd
sudo systemctl stop redis-server
sudo systemctl stop nginx

# Start services
sudo systemctl start redis-server
sudo systemctl start check-cccd
sudo systemctl start nginx
```

### **Clear all caches**
```bash
# Clear Redis cache
redis-cli FLUSHALL

# Clear application cache
rm -rf cache/*
rm -rf __pycache__/
```

### **Reset database**
```bash
# Backup first
cp check_cccd_prod.db check_cccd_prod.db.backup

# Reset database
rm check_cccd_prod.db
python database_migration.py
```

### **Full system reset**
```bash
# Stop services
sudo systemctl stop check-cccd redis-server nginx

# Clear all data
redis-cli FLUSHALL
rm -rf logs/* metrics/* cache/*
rm check_cccd_prod.db

# Reinitialize
python database_migration.py
source venv/bin/activate
python setup_and_run.py

# Start services
sudo systemctl start redis-server nginx
```

---

## 📞 Emergency Contacts

### **Critical Issues:**
- **System down:** Check server status, restart services
- **Data corruption:** Restore from backup immediately
- **Security breach:** Isolate server, change all credentials

### **Support Resources:**
- **Logs:** `tail -f logs/check_cccd.log`
- **Metrics:** `python3 monitoring_dashboard.py`
- **System status:** `htop`, `df -h`, `free -h`
- **Network:** `ping google.com`, `traceroute masothue.com`

---

## ✅ Prevention Best Practices

### **Daily Monitoring:**
1. Check system logs for errors
2. Monitor response times and success rates
3. Verify Redis and database connectivity
4. Check disk space and memory usage

### **Weekly Maintenance:**
1. Update system packages
2. Rotate and archive logs
3. Review performance metrics
4. Test backup restoration

### **Monthly Reviews:**
1. Security audit and updates
2. Performance optimization review
3. Capacity planning assessment
4. Documentation updates

---

**🔧 TROUBLESHOOTING COMPLETE**

**Hướng dẫn này bao gồm giải pháp cho 95%+ các lỗi thường gặp.**
**Nếu vẫn gặp vấn đề, hãy cung cấp error logs để được hỗ trợ cụ thể.**