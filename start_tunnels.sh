#!/bin/bash
# Tunnel Script for Remote Access

echo "🌐 STARTING TUNNELS"
echo "=================="

# Start VNC tunnel
echo "🖥️ Starting VNC tunnel (port 5900)..."
ngrok tcp 5900 --log=stdout > /tmp/ngrok_vnc.log 2>&1 &
VNC_PID=$!

# Start Web tunnel  
echo "🌐 Starting Web tunnel (port 8080)..."
ngrok http 8080 --log=stdout > /tmp/ngrok_web.log 2>&1 &
WEB_PID=$!

# Start SSH tunnel
echo "🔐 Starting SSH tunnel (port 22)..."
ngrok tcp 22 --log=stdout > /tmp/ngrok_ssh.log 2>&1 &
SSH_PID=$!

# Wait for tunnels to start
sleep 5

echo "✅ Tunnels started!"
echo "📋 Check logs:"
echo "   VNC: tail -f /tmp/ngrok_vnc.log"
echo "   Web: tail -f /tmp/ngrok_web.log"
echo "   SSH: tail -f /tmp/ngrok_ssh.log"

# Keep script running
echo "🔄 Tunnels are running... Press Ctrl+C to stop"
wait
