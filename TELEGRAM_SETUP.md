# 🤖 Telegram Bot Setup Guide for BSC Sniper Bot 2.0

## Step 1: Create Your Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather and send `/newbot`
3. **Choose a name** for your bot (e.g., "My BSC Sniper Bot")
4. **Choose a username** (must end with 'bot', e.g., "my_bsc_sniper_bot")
5. **Copy the bot token** that BotFather gives you

## Step 2: Get Your Chat ID

### Method 1: Personal Messages
1. **Start a chat** with your new bot
2. **Send any message** to the bot
3. **Visit this URL** (replace YOUR_BOT_TOKEN with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. **Find your chat ID** in the response (look for "chat":{"id":YOUR_CHAT_ID})

### Method 2: Group/Channel
1. **Add your bot** to the group/channel
2. **Give the bot admin permissions**
3. **Send a message** mentioning the bot (@your_bot_username)
4. **Use the same URL** as above to get the chat ID

## Step 3: Configure Your Bot

Edit your `bot_files/config.json`:

```json
{
  "api_keys": {
    "telegram_bot_token": "YOUR_BOT_TOKEN_HERE",
    "telegram_channel_id": "YOUR_CHAT_ID_HERE"
  }
}
```

## Step 4: Test Your Setup

Run this command to test:
```bash
cd bot_files
python -c "
import asyncio
from telegram_notifier import TelegramNotifier
notifier = TelegramNotifier('YOUR_BOT_TOKEN', 'YOUR_CHAT_ID')
asyncio.run(notifier.notify_bot_started('Test Wallet Address'))
"
```

## 🔥 What You'll Receive

Your bot will send you notifications for:
- ✅ **New tokens detected** - Real-time alerts when tokens are found
- 🛡️ **Security check results** - Which checks passed/failed
- 💰 **Buy executions** - Successful token purchases with details
- 📈 **Profit milestones** - 2x, 5x, 10x profit alerts
- 💸 **Sell executions** - When tokens are sold and profits realized
- 📊 **Daily summaries** - Portfolio performance reports
- ⚠️ **Error alerts** - If anything goes wrong

## Example Notification Messages

```
🚀 NEW TOKEN DETECTED
Token: MOONSHOT (0x123...abc)
Liquidity: $15,000
Holders: 25
Status: ✅ PASSED ALL CHECKS

💰 BUY EXECUTED
Token: MOONSHOT
Amount: 0.001 BNB ($0.30)
Price: $0.0001
Tokens: 3,000 MOONSHOT

📈 PROFIT MILESTONE
Token: MOONSHOT
Current Value: 0.002 BNB (2.0x)
Profit: +0.001 BNB (+$0.30)
Action: Taking 25% profit
```

## Troubleshooting

**Bot not responding?**
- Check your bot token is correct
- Make sure you've started a chat with the bot
- Verify the chat ID is correct (positive for personal, negative for groups)

**Messages not sending?**
- Ensure the bot has permission to send messages
- Check your internet connection
- Verify the Telegram API is accessible

**Getting 403 errors?**
- You must send a message to the bot first
- For groups, add the bot as admin
- Make sure the chat ID format is correct

Ready to receive those profit notifications! 🎯💰