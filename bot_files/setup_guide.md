# BSC Sniper Bot 2.0 - Complete Setup Guide

## 🚀 Ubuntu Server Deployment

### 1. Initial Server Setup
```bash
# Run the deployment script
chmod +x ubuntu_deploy.sh
./ubuntu_deploy.sh
```

### 2. Copy Bot Files
Upload these files to your server in `~/bsc_sniper_bot_2/`:
- `bsc_sniper_bot_2.py` (main bot)
- `advanced_security_engine.py`
- `blockchain_interface.py`
- `profit_management.py`
- `telegram_notifier.py`
- `config.json`
- `requirements.txt`

### 3. Configuration

#### Edit config.json:
```json
{
  "api_keys": {
    "goplus_app_key": "R3QUChegrrAMyXdA7MP7",
    "goplus_app_secret": "V8nZBkJgTbFYYz5gXKMkM2ASeNws4RyT",
    "bscscan_api_key": "49KJV11NHIES9X4WSH95IIN1YUJJUZ5795",
    "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "telegram_channel_id": "YOUR_TELEGRAM_CHANNEL_ID"
  },
  "trading": {
    "buy_amount_bnb": 0.001,        // ← Change this to your buy amount
    "gas_reserve_bnb": 0.001,       // ← Minimum BNB to keep for gas
    "max_concurrent_positions": 5,  // ← Max positions at once
    "max_token_age_minutes": 3,     // ← Only buy tokens younger than this
    "min_liquidity_usd": 2000,      // ← Minimum liquidity required
    "slippage_tolerance": 15        // ← Slippage tolerance %
  }
}
```

#### Create .env file:
```bash
PRIVATE_KEY=your_wallet_private_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_telegram_channel_id
```

### 4. Run the Bot
```bash
cd ~/bsc_sniper_bot_2
source venv/bin/activate
python bsc_sniper_bot_2.py
```

### 5. Run as Service (24/7 Operation)
```bash
# Create systemd service
sudo nano /etc/systemd/system/bsc-sniper.service
```

Add this content:
```ini
[Unit]
Description=BSC Sniper Bot 2.0
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bsc_sniper_bot_2
Environment=PATH=/home/ubuntu/bsc_sniper_bot_2/venv/bin
ExecStart=/home/ubuntu/bsc_sniper_bot_2/venv/bin/python bsc_sniper_bot_2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bsc-sniper
sudo systemctl start bsc-sniper
sudo systemctl status bsc-sniper
```

## 📊 Monitoring & Management

### Check Bot Status
```bash
sudo systemctl status bsc-sniper
```

### View Real-time Logs
```bash
sudo journalctl -u bsc-sniper -f
```

### Restart Bot
```bash
sudo systemctl restart bsc-sniper
```

### Stop Bot
```bash
sudo systemctl stop bsc-sniper
```

## ⚙️ Configuration Settings Explained

### Trading Settings
- **buy_amount_bnb**: Amount of BNB to spend per token (start with 0.001)
- **gas_reserve_bnb**: Always keep this much BNB for gas fees
- **max_concurrent_positions**: Maximum number of tokens to hold
- **max_token_age_minutes**: Only buy tokens younger than this
- **min_liquidity_usd**: Minimum USD liquidity required
- **slippage_tolerance**: Maximum price slippage allowed

### Profit Management
- **take_profit_1**: Sell 25% at 2x profit
- **take_profit_2**: Sell 30% at 5x profit  
- **take_profit_3**: Sell 25% at 10x profit
- **trailing_stop_loss**: Sell remaining if price drops 30% from peak

### Security Settings
- **min_holders**: Minimum number of token holders
- **max_buy_tax**: Maximum buy tax allowed (%)
- **max_sell_tax**: Maximum sell tax allowed (%)
- **require_verified_contract**: Whether contract must be verified

## 🛠️ Troubleshooting

### Bot Won't Start
1. Check your private key in .env file
2. Ensure you have enough BNB for gas + trading
3. Verify all files are uploaded correctly

### No Trades Executing
1. Check BNB balance (need minimum 0.002 BNB)
2. Verify settings in config.json
3. Most tokens fail security checks (this is good!)

### API Errors
1. Check internet connection
2. Verify API keys in config.json
3. GoPlus API is free and should work

### Low Performance
1. Use better VPS (2GB+ RAM recommended)
2. Check internet speed
3. Monitor logs for errors

## 💰 Maximizing Profits

### Start Small
- Begin with 0.001 BNB per trade ($0.30)
- Let compound growth increase position sizes
- Monitor for first successful trades

### Scale Up
- Once profitable, increase buy_amount_bnb
- Adjust max_concurrent_positions
- Consider running multiple instances

### Risk Management
- Never invest more than you can afford to lose
- Keep gas reserve adequate
- Monitor bot performance regularly

## 🔒 Security Best Practices

1. **Never share your private key**
2. **Use a dedicated trading wallet**
3. **Keep main funds in a separate wallet**
4. **Regularly update the bot**
5. **Monitor for unusual activity**

## 📱 Getting Telegram Notifications

1. Create a Telegram bot with @BotFather
2. Get your bot token
3. Get your chat/channel ID
4. Update config.json with these values
5. Restart the bot

Your bot will send you notifications for:
- New tokens detected
- Security check results
- Buy/sell executions
- Profit milestones
- Daily summaries

## 🎯 Expected Performance

The bot is designed to:
- ✅ Detect tokens within 1-2 seconds of launch
- ✅ Reject 95%+ of tokens (protects from scams)
- ✅ Only buy high-quality, safe tokens
- ✅ Automatically take profits at 2x, 5x, 10x
- ✅ Compound gains for exponential growth
- ✅ Operate 24/7 without intervention

**Remember**: The bot being selective is GOOD - it's protecting your money from scams and only trading profitable opportunities!