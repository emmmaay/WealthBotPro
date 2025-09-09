
#!/bin/bash
# BSC Sniper Bot 2.0 - Ubuntu Deployment Script (Python 3.12)
# Run this script on your Ubuntu server to deploy the bot

echo "🚀 BSC Sniper Bot 2.0 - Ubuntu Deployment (Python 3.12)"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.12 and dependencies
echo "🐍 Installing Python 3.12 and dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev git curl

# Create bot directory
echo "📁 Creating bot directory..."
mkdir -p ~/bsc_sniper_bot_2
cd ~/bsc_sniper_bot_2

# Create virtual environment with Python 3.12
echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "⚡ Installing Python packages..."
pip install web3==6.15.1
pip install eth-account==0.11.0
pip install requests==2.31.0
pip install asyncio-throttle==1.0.2
pip install colorama==0.4.6
pip install python-telegram-bot==20.7
pip install aiohttp==3.9.1
pip install eth-utils==2.3.1
pip install eth-typing==3.5.2
pip install hexbytes==0.3.1
pip install websockets==12.0
pip install python-dotenv==1.0.0

echo "✅ Dependencies installed successfully!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Copy all bot files to ~/bsc_sniper_bot_2/"
echo "2. Create .env file with your private key"
echo "3. Update config.json with your settings"
echo "4. Run: source venv/bin/activate && python bsc_sniper_bot_2.py"
echo ""
echo "🔥 Your bot will be ready to make money!"
