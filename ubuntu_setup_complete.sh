#!/bin/bash
# BSC Sniper Bot 2.0 - Complete Ubuntu Setup Script
# Run this script on Ubuntu 20.04+ for full installation

set -e

echo "=================================="
echo "🚀 BSC SNIPER BOT 2.0 SETUP"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root!"
    exit 1
fi

# Update system
print_status "Updating Ubuntu system..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    supervisor \
    htop \
    screen \
    unzip

# Install Python 3.11 if not available
print_status "Setting up Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi

# Create bot directory
BOT_DIR="$HOME/bsc_sniper_bot_2"
print_status "Creating bot directory at $BOT_DIR..."
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install core dependencies
    pip install \
        web3==6.15.1 \
        eth-account==0.11.0 \
        requests==2.31.0 \
        asyncio-throttle==1.0.2 \
        colorama==0.4.6 \
        python-telegram-bot==20.7 \
        aiohttp==3.9.1 \
        eth-utils==2.3.1 \
        eth-typing==3.5.2 \
        hexbytes==0.3.1 \
        websockets==12.0 \
        python-dotenv==1.0.0 \
        psutil==5.9.6 \
        numpy==1.24.4 \
        pandas==2.0.3
fi

# Create .env template if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env template..."
    cat > .env << EOL
# BSC Sniper Bot 2.0 Environment Variables
PRIVATE_KEY=your_wallet_private_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_telegram_channel_id
EOL
fi

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/bsc-sniper.service > /dev/null << EOL
[Unit]
Description=BSC Sniper Bot 2.0 - Ultimate Money Making Machine
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/venv/bin
ExecStart=$BOT_DIR/venv/bin/python bsc_sniper_bot_2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bsc-sniper

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$BOT_DIR

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd
sudo systemctl daemon-reload

# Create log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/bsc-sniper > /dev/null << EOL
/var/log/syslog {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}
EOL

# Create startup script
print_status "Creating startup script..."
cat > start_bot.sh << 'EOL'
#!/bin/bash
# Quick start script for BSC Sniper Bot 2.0

BOT_DIR="$HOME/bsc_sniper_bot_2"
cd "$BOT_DIR"
source venv/bin/activate

echo "🤖 Starting BSC Sniper Bot 2.0..."
python bsc_sniper_bot_2.py
EOL

chmod +x start_bot.sh

# Create management script
print_status "Creating management script..."
cat > manage_bot.sh << 'EOL'
#!/bin/bash
# BSC Sniper Bot 2.0 Management Script

case "$1" in
    start)
        echo "🚀 Starting BSC Sniper Bot..."
        sudo systemctl start bsc-sniper
        sudo systemctl status bsc-sniper --no-pager
        ;;
    stop)
        echo "🛑 Stopping BSC Sniper Bot..."
        sudo systemctl stop bsc-sniper
        ;;
    restart)
        echo "🔄 Restarting BSC Sniper Bot..."
        sudo systemctl restart bsc-sniper
        sudo systemctl status bsc-sniper --no-pager
        ;;
    status)
        sudo systemctl status bsc-sniper --no-pager
        ;;
    logs)
        echo "📋 Recent logs (press Ctrl+C to exit):"
        sudo journalctl -u bsc-sniper -f
        ;;
    enable)
        echo "✅ Enabling auto-start on boot..."
        sudo systemctl enable bsc-sniper
        ;;
    disable)
        echo "❌ Disabling auto-start on boot..."
        sudo systemctl disable bsc-sniper
        ;;
    *)
        echo "BSC Sniper Bot 2.0 Management"
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the bot"
        echo "  stop     - Stop the bot" 
        echo "  restart  - Restart the bot"
        echo "  status   - Show bot status"
        echo "  logs     - Show real-time logs"
        echo "  enable   - Auto-start on boot"
        echo "  disable  - Disable auto-start"
        exit 1
        ;;
esac
EOL

chmod +x manage_bot.sh

# Create monitoring script
print_status "Creating monitoring script..."
cat > monitor_bot.sh << 'EOL'
#!/bin/bash
# BSC Sniper Bot 2.0 Monitoring Script

while true; do
    clear
    echo "════════════════════════════════════════"
    echo "🤖 BSC SNIPER BOT 2.0 MONITOR"
    echo "════════════════════════════════════════"
    echo "📅 $(date)"
    echo ""
    
    # Bot status
    if systemctl is-active --quiet bsc-sniper; then
        echo "🟢 Bot Status: RUNNING"
    else
        echo "🔴 Bot Status: STOPPED"
    fi
    
    # System resources
    echo ""
    echo "💻 System Resources:"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "RAM: $(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
    echo "Disk: $(df -h / | awk 'NR==2{print $5}')"
    
    # Network status
    echo ""
    echo "🌐 Network:"
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo "Internet: ✅ Connected"
    else
        echo "Internet: ❌ Disconnected"
    fi
    
    # Recent logs (last 5 lines)
    echo ""
    echo "📋 Recent Activity:"
    sudo journalctl -u bsc-sniper --no-pager -n 5 | tail -5
    
    echo ""
    echo "Press Ctrl+C to exit..."
    sleep 10
done
EOL

chmod +x monitor_bot.sh

# Set permissions
print_status "Setting correct permissions..."
chown -R $USER:$USER "$BOT_DIR"
chmod 600 .env 2>/dev/null || true

print_status "✅ Ubuntu setup complete!"
echo ""
echo "════════════════════════════════════════"
echo "🎯 NEXT STEPS:"
echo "════════════════════════════════════════"
echo "1. Edit .env file with your private key and Telegram credentials"
echo "2. Copy your bot files to: $BOT_DIR"
echo "3. Start the bot: ./manage_bot.sh start"
echo "4. Monitor: ./manage_bot.sh logs"
echo "5. Enable auto-start: ./manage_bot.sh enable"
echo ""
echo "🚀 Your bot is ready to make millions!"
echo "════════════════════════════════════════"