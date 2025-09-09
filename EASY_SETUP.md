# 🚀 EASY SETUP GUIDE - BSC Sniper Bot 2.0

## 📁 Where to Put Your Credentials

### Step 1: Find the .env file
Your credentials go in: **`bot_files/.env`**

### Step 2: Edit the .env file
Open `bot_files/.env` and replace the placeholders:

```env
# Replace this with your wallet private key:
PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# Replace with your Telegram bot details (optional):
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHANNEL_ID=-1001234567890
```

## 🔑 How to Get Your Private Key

1. **MetaMask**: Settings → Security & Privacy → Reveal Private Key
2. **Trust Wallet**: Settings → Wallets → [Your Wallet] → Private Key
3. **Copy the entire key** including the `0x` at the beginning

## 📱 How to Get Telegram Credentials (Optional)

1. **Message @BotFather** on Telegram
2. **Send `/newbot`** and follow instructions
3. **Copy the bot token** (looks like: `123456789:ABCdefGHI...`)
4. **Start a chat** with your bot, send any message
5. **Visit**: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
6. **Find your chat ID** in the response

## 🚀 How to Start the Bot (Ubuntu)

### Method 1: Quick Start (Testing)
```bash
cd bot_files
python3 bsc_sniper_bot_2.py
```

### Method 2: 24/7 Operation (Production)
```bash
# Make executable
chmod +x ubuntu_setup_complete.sh

# Install everything
./ubuntu_setup_complete.sh

# Start as service (runs forever, even if you close terminal)
sudo systemctl start bsc-sniper
sudo systemctl enable bsc-sniper

# Check if running
sudo systemctl status bsc-sniper
```

## 🔄 How to Manage the Bot

### Start the bot:
```bash
sudo systemctl start bsc-sniper
```

### Stop the bot:
```bash
sudo systemctl stop bsc-sniper
```

### Restart the bot:
```bash
sudo systemctl restart bsc-sniper
```

### Check if it's running:
```bash
sudo systemctl status bsc-sniper
```

### View live logs:
```bash
sudo journalctl -u bsc-sniper -f
```

## 💻 Keeps Running Even When You Close Termius

Once you run `sudo systemctl start bsc-sniper`, the bot runs as a **system service**. This means:

✅ **Runs 24/7** - Even if you close Termius/SSH  
✅ **Auto-restarts** - If it crashes, it automatically restarts  
✅ **Survives reboots** - Starts automatically when server boots  
✅ **Background operation** - Doesn't need your terminal open  

## 🔧 Quick Troubleshooting

### Bot won't start?
```bash
# Check what's wrong
sudo journalctl -u bsc-sniper -n 20

# Common issues:
# 1. Wrong private key format
# 2. Not enough BNB (need at least 0.002 BNB)
# 3. Internet connection problems
```

### Check your wallet balance:
```bash
cd bot_files
python3 -c "
from blockchain_interface import BlockchainInterface
import asyncio
import json

async def check_balance():
    with open('config.json') as f:
        config = json.load(f)
    
    blockchain = BlockchainInterface(config)
    await blockchain.initialize()
    balance = await blockchain.get_wallet_balance()
    print(f'Wallet Balance: {balance} BNB')

asyncio.run(check_balance())
"
```

## 🎯 That's It!

1. **Put your private key** in `bot_files/.env`
2. **Add some BNB** to your wallet (0.002 minimum)  
3. **Run**: `sudo systemctl start bsc-sniper`
4. **Check logs**: `sudo journalctl -u bsc-sniper -f`

The bot will run forever and make trades automatically! 🔥💰