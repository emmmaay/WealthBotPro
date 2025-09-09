#!/bin/bash
# BSC Sniper Bot 2.0 - Ubuntu Startup Script
# This script sets up and starts your bot for 24/7 operation

set -e

echo "🚀 BSC SNIPER BOT 2.0 - UBUNTU STARTUP"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if .env file has real credentials
if [ -f "bot_files/.env" ]; then
    if grep -q "0x1234567890abcdef" bot_files/.env; then
        print_error "Please update your private key in bot_files/.env first!"
        print_warning "Edit bot_files/.env and replace the placeholder private key"
        exit 1
    fi
    print_status "Credentials file found ✅"
else
    print_error "Missing bot_files/.env file!"
    exit 1
fi

# Check if we're on Ubuntu and have systemctl
if ! command -v systemctl &> /dev/null; then
    print_warning "SystemD not found. Starting bot manually..."
    cd bot_files
    python3 bsc_sniper_bot_2.py
    exit 0
fi

# Install systemd service if not exists
if [ ! -f "/etc/systemd/system/bsc-sniper.service" ]; then
    print_status "Installing systemd service..."
    
    # Get current directory
    CURRENT_DIR=$(pwd)
    
    # Create service file
    sudo tee /etc/systemd/system/bsc-sniper.service > /dev/null << EOL
[Unit]
Description=BSC Sniper Bot 2.0 - Ultimate Money Making Machine
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$CURRENT_DIR/bot_files
Environment=PATH=/usr/bin:/bin
ExecStart=/usr/bin/python3 bsc_sniper_bot_2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bsc-sniper

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOL

    # Reload systemd
    sudo systemctl daemon-reload
    print_status "Service installed ✅"
fi

# Start the service
print_status "Starting BSC Sniper Bot service..."
sudo systemctl start bsc-sniper

# Enable auto-start on boot
print_status "Enabling auto-start on boot..."
sudo systemctl enable bsc-sniper

# Check status
sleep 3
if sudo systemctl is-active --quiet bsc-sniper; then
    print_status "🎉 Bot is running successfully!"
    echo ""
    echo "📋 MANAGEMENT COMMANDS:"
    echo "  Check status:    sudo systemctl status bsc-sniper"
    echo "  View live logs:  sudo journalctl -u bsc-sniper -f"
    echo "  Restart bot:     sudo systemctl restart bsc-sniper"
    echo "  Stop bot:        sudo systemctl stop bsc-sniper"
    echo ""
    echo "🔥 Your bot is now running 24/7 and will make trades automatically!"
    echo "💰 Close this terminal - the bot keeps running in the background!"
else
    print_error "Failed to start bot. Check logs:"
    echo "sudo journalctl -u bsc-sniper -n 20"
    exit 1
fi