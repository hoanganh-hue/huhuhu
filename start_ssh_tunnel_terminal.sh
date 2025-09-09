#!/bin/bash
# Start SSH Tunnel on Separate Terminal
# Script để chạy SSH tunnel trên terminal riêng và duy trì

echo "🔐 START SSH TUNNEL TERMINAL"
echo "============================="
echo "📅 Started: $(date)"
echo "🎯 Purpose: Run SSH tunnel on separate terminal"
echo ""

# Kiểm tra ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok not found!"
    echo "📋 Please install ngrok first"
    exit 1
fi

# Kiểm tra ngrok config
if [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    echo "❌ Ngrok config not found!"
    echo "📋 Creating config template..."
    
    mkdir -p ~/.config/ngrok
    cp /workspace/ngrok_config_template.yml ~/.config/ngrok/ngrok.yml
    
    echo "✅ Config template created: ~/.config/ngrok/ngrok.yml"
    echo "📋 Please edit the config file and add your authtoken:"
    echo "   nano ~/.config/ngrok/ngrok.yml"
    echo "   Replace 'YOUR_AUTHTOKEN_HERE' with your actual authtoken"
    exit 1
fi

# Kiểm tra authtoken
if grep -q "YOUR_AUTHTOKEN_HERE" ~/.config/ngrok/ngrok.yml; then
    echo "❌ Authtoken not configured!"
    echo "📋 Please add your authtoken to ~/.config/ngrok/ngrok.yml"
    echo "   nano ~/.config/ngrok/ngrok.yml"
    exit 1
fi

echo "✅ Ngrok config found and valid"
echo "🔄 Starting SSH tunnel on separate terminal..."

# Tạo log directory
mkdir -p /tmp/ssh_tunnel_logs

# Function để start tunnel
start_tunnel() {
    echo "🔄 Starting SSH tunnel..."
    
    # Kill existing ngrok processes
    pkill -f "ngrok tcp 22" 2>/dev/null
    sleep 2
    
    # Start ngrok SSH tunnel
    nohup ngrok tcp 22 --log=stdout > /tmp/ssh_tunnel_logs/ngrok_ssh.log 2>&1 &
    NGROK_PID=$!
    
    echo "✅ SSH tunnel started (PID: $NGROK_PID)"
    echo "📋 Log file: /tmp/ssh_tunnel_logs/ngrok_ssh.log"
    
    # Wait for tunnel to start
    sleep 5
    
    # Get tunnel URL
    if [ -f /tmp/ssh_tunnel_logs/ngrok_ssh.log ]; then
        URL=$(grep "started tunnel" /tmp/ssh_tunnel_logs/ngrok_ssh.log | grep -o "tcp://[^:]*:[0-9]*" | head -1)
        if [ ! -z "$URL" ]; then
            HOST=$(echo $URL | sed 's/tcp:\/\///' | cut -d: -f1)
            PORT=$(echo $URL | cut -d: -f3)
            echo ""
            echo "🌐 SSH Tunnel URL: $URL"
            echo "🔐 SSH Command: ssh ubuntu@$HOST -p $PORT"
            echo "📋 Connection Info:"
            echo "   Host: $HOST"
            echo "   Port: $PORT"
            echo "   User: ubuntu"
            echo ""
        else
            echo "⚠️ Tunnel URL not found yet, check log file"
        fi
    fi
}

# Function để monitor tunnel
monitor_tunnel() {
    echo "🔄 Monitoring tunnel..."
    echo "📋 Press Ctrl+C to stop"
    echo ""
    
    while true; do
        if ! kill -0 $NGROK_PID 2>/dev/null; then
            echo "❌ Tunnel process died, restarting..."
            start_tunnel
        fi
        
        # Show status every 60 seconds
        echo "✅ Tunnel is running (PID: $NGROK_PID) - $(date)"
        
        sleep 60
    done
}

# Start tunnel
start_tunnel

# Start monitoring
monitor_tunnel