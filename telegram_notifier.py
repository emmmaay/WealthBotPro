#!/usr/bin/env python3
"""
Advanced Telegram Notification System
Sends detailed updates about bot activities and trading results
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from telegram import Bot
from telegram.error import TelegramError
from colorama import Fore, Style
import time

class TelegramNotifier:
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.bot = None
        self.message_queue = []
        self.last_message_time = 0
        self.message_delay = 1  # Minimum seconds between messages
        
        if bot_token and channel_id:
            self.bot = Bot(token=bot_token)

    async def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.bot:
            logging.warning("Telegram bot not configured")
            return False
        
        try:
            bot_info = await self.bot.get_me()
            logging.info(f"{Fore.GREEN}✅ Telegram bot connected: @{bot_info.username}{Style.RESET_ALL}")
            
            # Send test message
            await self._send_message("🤖 BSC Sniper Bot 2.0 connected and ready to make money! 🚀")
            return True
            
        except Exception as e:
            logging.error(f"Telegram connection test failed: {e}")
            return False

    async def notify_bot_started(self, wallet_address: str, buy_amount: float, config: Dict[str, Any]) -> None:
        """Notify bot startup"""
        try:
            message = (
                f"🚀 <b>BSC SNIPER BOT 2.0 STARTED</b> 🚀\n\n"
                f"📍 <b>Wallet:</b> <code>{wallet_address[:8]}...{wallet_address[-8:]}</code>\n"
                f"💰 <b>Buy Amount:</b> {buy_amount:.6f} BNB\n"
                f"🛡️ <b>Gas Reserve:</b> {config['trading']['gas_reserve_bnb']:.6f} BNB\n"
                f"🎯 <b>Max Positions:</b> {config['trading']['max_concurrent_positions']}\n"
                f"⏱️ <b>Max Token Age:</b> {config['trading']['max_token_age_minutes']} minutes\n"
                f"💧 <b>Min Liquidity:</b> ${config['trading']['min_liquidity_usd']:,}\n\n"
                f"💎 <b>Ready to hunt for gems!</b> 💎"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending startup notification: {e}")

    async def notify_token_detected(self, token_address: str, name: str, symbol: str, 
                                  liquidity_usd: float, age_minutes: float) -> None:
        """Notify new token detection"""
        try:
            message = (
                f"👀 <b>NEW TOKEN DETECTED</b>\n\n"
                f"📛 <b>Name:</b> {name}\n"
                f"🏷️ <b>Symbol:</b> {symbol}\n"
                f"📍 <b>Address:</b> <code>{token_address}</code>\n"
                f"💧 <b>Liquidity:</b> ${liquidity_usd:,.0f}\n"
                f"⏰ <b>Age:</b> {age_minutes:.1f} minutes\n\n"
                f"🔍 <b>Running security checks...</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending detection notification: {e}")

    async def notify_security_check_result(self, token_address: str, passed: bool, 
                                         reasons: List[str], detailed_results: Dict[str, Any] = None) -> None:
        """Notify security check results"""
        try:
            if passed:
                message = (
                    f"✅ <b>SECURITY CHECK PASSED</b>\n\n"
                    f"📍 <b>Token:</b> <code>{token_address[:8]}...{token_address[-8:]}</code>\n"
                    f"🛡️ <b>Status:</b> All 30+ checks passed\n"
                    f"🚀 <b>Proceeding to buy...</b>"
                )
            else:
                failed_reasons = "\n".join([f"❌ {reason}" for reason in reasons[:5]])  # Limit to 5 reasons
                message = (
                    f"🚫 <b>SECURITY CHECK FAILED</b>\n\n"
                    f"📍 <b>Token:</b> <code>{token_address[:8]}...{token_address[-8:]}</code>\n"
                    f"⚠️ <b>Issues found:</b>\n{failed_reasons}\n\n"
                    f"🛡️ <b>Token rejected for safety</b>"
                )
            
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending security check notification: {e}")

    async def notify_buy_attempt(self, token_address: str, bnb_amount: float, 
                               expected_tokens: float, token_symbol: str = "TOKEN") -> None:
        """Notify buy attempt"""
        try:
            message = (
                f"💳 <b>EXECUTING BUY ORDER</b>\n\n"
                f"🏷️ <b>Token:</b> {token_symbol}\n"
                f"📍 <b>Address:</b> <code>{token_address[:8]}...{token_address[-8:]}</code>\n"
                f"💰 <b>Amount:</b> {bnb_amount:.6f} BNB\n"
                f"🎯 <b>Expected:</b> {expected_tokens:,.0f} tokens\n\n"
                f"⏳ <b>Waiting for confirmation...</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending buy attempt notification: {e}")

    async def notify_buy_success(self, token_address: str, token_symbol: str, bnb_spent: float, 
                               tokens_received: float, tx_hash: str, gas_cost: float) -> None:
        """Notify successful buy"""
        try:
            bscscan_link = f"https://bscscan.com/tx/{tx_hash}"
            
            message = (
                f"🎉 <b>BUY SUCCESSFUL!</b> 🎉\n\n"
                f"🏷️ <b>Token:</b> {token_symbol}\n"
                f"📍 <b>Address:</b> <code>{token_address[:8]}...{token_address[-8:]}</code>\n"
                f"💰 <b>Spent:</b> {bnb_spent:.6f} BNB\n"
                f"🎯 <b>Received:</b> {tokens_received:,.0f} tokens\n"
                f"⛽ <b>Gas:</b> {gas_cost:.6f} BNB\n"
                f"📊 <b>Entry Price:</b> {bnb_spent/tokens_received:.12f} BNB per token\n\n"
                f"🔗 <a href='{bscscan_link}'>View Transaction</a>\n\n"
                f"💎 <b>Now monitoring for profits...</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending buy success notification: {e}")

    async def notify_buy_failed(self, token_address: str, token_symbol: str, reason: str) -> None:
        """Notify failed buy"""
        try:
            message = (
                f"❌ <b>BUY FAILED</b>\n\n"
                f"🏷️ <b>Token:</b> {token_symbol}\n"
                f"📍 <b>Address:</b> <code>{token_address[:8]}...{token_address[-8:]}</code>\n"
                f"💥 <b>Reason:</b> {reason}\n\n"
                f"🔄 <b>Continuing to hunt for gems...</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending buy failed notification: {e}")

    async def notify_profit_taken(self, token_symbol: str, percentage: float, multiplier: float, 
                                bnb_received: float, tx_hash: str) -> None:
        """Notify profit taking"""
        try:
            bscscan_link = f"https://bscscan.com/tx/{tx_hash}"
            
            message = (
                f"💰 <b>PROFIT TAKEN!</b> 💰\n\n"
                f"🏷️ <b>Token:</b> {token_symbol}\n"
                f"📈 <b>Multiplier:</b> {multiplier}x\n"
                f"📊 <b>Sold:</b> {percentage}% of position\n"
                f"💵 <b>Received:</b> {bnb_received:.6f} BNB\n\n"
                f"🔗 <a href='{bscscan_link}'>View Transaction</a>\n\n"
                f"🚀 <b>Continuing to ride the moon!</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending profit notification: {e}")

    async def notify_position_closed(self, token_symbol: str, reason: str, final_bnb: float, 
                                   total_profit: float, tx_hash: str) -> None:
        """Notify position closure"""
        try:
            bscscan_link = f"https://bscscan.com/tx/{tx_hash}"
            profit_emoji = "🎉" if total_profit > 0 else "😔" if total_profit < 0 else "😐"
            
            message = (
                f"{profit_emoji} <b>POSITION CLOSED</b>\n\n"
                f"🏷️ <b>Token:</b> {token_symbol}\n"
                f"🔄 <b>Reason:</b> {reason}\n"
                f"💵 <b>Final Sale:</b> {final_bnb:.6f} BNB\n"
                f"📊 <b>Total P&L:</b> {total_profit:.6f} BNB\n"
                f"📈 <b>ROI:</b> {(total_profit / abs(total_profit) * 100) if total_profit != 0 else 0:.1f}%\n\n"
                f"🔗 <a href='{bscscan_link}'>View Transaction</a>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending position closed notification: {e}")

    async def notify_compound_growth(self, old_amount: float, new_amount: float) -> None:
        """Notify compound growth"""
        try:
            message = (
                f"📈 <b>COMPOUND GROWTH ACTIVATED!</b>\n\n"
                f"💰 <b>Previous Buy Amount:</b> {old_amount:.6f} BNB\n"
                f"🚀 <b>New Buy Amount:</b> {new_amount:.6f} BNB\n"
                f"📊 <b>Increase:</b> {((new_amount/old_amount - 1) * 100):.1f}%\n\n"
                f"💎 <b>Scaling up for bigger profits!</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending compound growth notification: {e}")

    async def notify_sell_failed(self, token_symbol: str, reason: str) -> None:
        """Notify failed sell"""
        try:
            message = (
                f"⚠️ <b>SELL FAILED</b>\n\n"
                f"🏷️ <b>Token:</b> {token_symbol}\n"
                f"💥 <b>Reason:</b> {reason}\n\n"
                f"🔄 <b>Will retry on next opportunity...</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending sell failed notification: {e}")

    async def notify_daily_summary(self, summary: Dict[str, Any]) -> None:
        """Send daily performance summary"""
        try:
            win_rate = summary.get('win_rate_percentage', 0)
            net_profit = summary.get('net_profit_bnb', 0)
            profit_emoji = "🎉" if net_profit > 0 else "😔" if net_profit < 0 else "😐"
            
            message = (
                f"{profit_emoji} <b>DAILY SUMMARY</b> {profit_emoji}\n\n"
                f"💰 <b>Net Profit:</b> {net_profit:.6f} BNB\n"
                f"📊 <b>Win Rate:</b> {win_rate:.1f}%\n"
                f"✅ <b>Successful Trades:</b> {summary.get('successful_trades', 0)}\n"
                f"❌ <b>Failed Trades:</b> {summary.get('failed_trades', 0)}\n"
                f"🏃 <b>Active Positions:</b> {summary.get('active_positions', 0)}\n"
                f"⛽ <b>Total Fees:</b> {summary.get('total_fees_bnb', 0):.6f} BNB\n\n"
                f"🚀 <b>Bot running smoothly!</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending daily summary: {e}")

    async def notify_error(self, error_type: str, error_message: str) -> None:
        """Notify errors"""
        try:
            message = (
                f"🚨 <b>BOT ERROR</b>\n\n"
                f"⚠️ <b>Type:</b> {error_type}\n"
                f"💥 <b>Message:</b> {error_message}\n\n"
                f"🔧 <b>Bot attempting recovery...</b>"
            )
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending error notification: {e}")

    async def _send_message(self, message: str) -> None:
        """Send message with rate limiting"""
        if not self.bot or not self.channel_id:
            return
        
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_message_time < self.message_delay:
                await asyncio.sleep(self.message_delay - (current_time - self.last_message_time))
            
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
            self.last_message_time = time.time()
            
        except TelegramError as e:
            logging.error(f"Telegram error: {e}")
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")