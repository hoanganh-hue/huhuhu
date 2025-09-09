#!/bin/bash
# SSH Tunnel Daemon Script
# Chạy SSH tunnel trên terminal riêng và duy trì kết nối

echo "🔐 SSH TUNNEL DAEMON"
echo "===================="
echo "📅 Started: $(date)"
echo "🎯 Purpose: Maintain SSH tunnel via ngrok"
echo ""

# Kiểm tra ngrok config
if [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    echo "❌ Ngrok config not found!"
    echo "📋 Please configure ngrok:"
    echo "1. Copy ngrok_config_template.yml to ~/.config/ngrok/ngrok.yml"
    echo "2. Add your authtoken to the config file"
    echo "3. Run this script again"
    exit 1
fi

# Kiểm tra authtoken
if grep -q "YOUR_AUTHTOKEN_HERE" ~/.config/ngrok/ngrok.yml; then
    echo "❌ Authtoken not configured!"
    echo "📋 Please add your authtoken to ~/.config/ngrok/ngrok.yml"
    exit 1
fi

echo "✅ Ngrok config found"
echo "🔄 Starting SSH tunnel..."

# Tạo log directory
mkdir -p /tmp/ssh_tunnel_logs

# Function để restart tunnel
restart_tunnel() {
    echo "🔄 Restarting SSH tunnel..."
    pkill -f "ngrok tcp 22" 2>/dev/null
    sleep 2
    
    # Start ngrok SSH tunnel
    nohup ngrok tcp 22 --log=stdout > /tmp/ssh_tunnel_logs/ngrok_ssh.log 2>&1 &
    NGROK_PID=$!
    
    echo "✅ SSH tunnel restarted (PID: $NGROK_PID)"
    echo "📋 Log: /tmp/ssh_tunnel_logs/ngrok_ssh.log"
}

# Function để get tunnel URL
get_tunnel_url() {
    sleep 5
    if [ -f /tmp/ssh_tunnel_logs/ngrok_ssh.log ]; then
        URL=$(grep "started tunnel" /tmp/ssh_tunnel_logs/ngrok_ssh.log | grep -o "tcp://[^:]*:[0-9]*" | head -1)
        if [ ! -z "$URL" ]; then
            echo "🌐 SSH Tunnel URL: $URL"
            echo "🔐 SSH Command: ssh ubuntu@$(echo $URL | sed 's/tcp:\/\///' | cut -d: -f1) -p $(echo $URL | cut -d: -f3)"
        else
            echo "⚠️ Tunnel URL not found yet, retrying..."
        fi
    fi
}

# Function để monitor tunnel
monitor_tunnel() {
    while true; do
        if ! kill -0 $NGROK_PID 2>/dev/null; then
            echo "❌ Tunnel process died, restarting..."
            restart_tunnel
        fi
        
        # Get tunnel URL every 30 seconds
        get_tunnel_url
        
        sleep 30
    done
}

# Start initial tunnel
restart_tunnel

# Get initial tunnel URL
get_tunnel_url

echo ""
echo "🔄 SSH Tunnel Daemon is running..."
echo "📋 Monitor logs: tail -f /tmp/ssh_tunnel_logs/ngrok_ssh.log"
echo "🛑 Stop daemon: pkill -f ssh_tunnel_daemon"
echo ""

# Start monitoring
monitor_tunnel