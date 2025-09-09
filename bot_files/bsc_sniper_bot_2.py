#!/usr/bin/env python3
"""
BSC Sniper Bot 2.0 - Advanced Cryptocurrency Trading Bot
The ultimate autonomous money-making machine for BSC token sniping
"""

import asyncio
import logging
import json
import time
import signal
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
from web3 import Web3
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Import our advanced modules
from advanced_security_engine import AdvancedSecurityEngine
from blockchain_interface import BlockchainInterface
from profit_management import ProfitManager
from telegram_notifier import TelegramNotifier

# Initialize colorama
init()

class BSCSniperBot2:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the advanced BSC Sniper Bot 2.0"""
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Initialize components
        self.blockchain = BlockchainInterface(self.config)
        self.notifier = TelegramNotifier(
            self.config['api_keys'].get('telegram_bot_token', ''),
            self.config['api_keys'].get('telegram_channel_id', '')
        )
        
        # Bot state
        self.running = False
        self.start_time = 0
        self.processed_pairs = set()
        self.session_stats = {
            'tokens_detected': 0,
            'tokens_analyzed': 0,
            'tokens_purchased': 0,
            'total_profit_bnb': 0.0
        }
        
        # Initialize security engine and profit manager
        self.security_engine = None
        self.profit_manager = None
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            sys.exit(1)

    def setup_logging(self):
        """Setup comprehensive logging"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Setup multiple log handlers
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f'logs/sniper_bot_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logging.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def start(self):
        """Start the advanced BSC sniper bot"""
        try:
            # Display startup banner
            self.display_startup_banner()
            
            # Initialize all components
            if not await self.initialize_components():
                logging.error("Failed to initialize components")
                return
            
            # Test all connections
            if not await self.test_all_connections():
                logging.error("Connection tests failed")
                return
            
            # Start the bot
            self.running = True
            self.start_time = time.time()
            
            logging.info(f"{Fore.GREEN}🚀 BSC Sniper Bot 2.0 started successfully!{Style.RESET_ALL}")
            
            # Send startup notification
            await self.notifier.notify_bot_started(
                self.blockchain.wallet_address,
                self.config['trading']['buy_amount_bnb'],
                self.config
            )
            
            # Start all main tasks
            await asyncio.gather(
                self.monitor_new_pairs(),
                self.manage_positions(),
                self.send_periodic_updates(),
                return_exceptions=True
            )
            
        except Exception as e:
            logging.error(f"Fatal error in bot startup: {e}")
            await self.notifier.notify_error("Startup Error", str(e))
        finally:
            await self.cleanup()

    def display_startup_banner(self):
        """Display the startup banner"""
        banner = f"""
{Fore.CYAN}{'='*80}{Style.RESET_ALL}
{Fore.YELLOW}    🤖 BSC SNIPER BOT 2.0 - ULTIMATE MONEY MAKING MACHINE 🤖{Style.RESET_ALL}
{Fore.CYAN}{'='*80}{Style.RESET_ALL}
{Fore.GREEN}📍 Version: 2.0.0 - Advanced Security & Profit Management{Style.RESET_ALL}
{Fore.GREEN}🛡️ Security: 30+ Advanced Checks with Multiple API Fallbacks{Style.RESET_ALL}
{Fore.GREEN}💰 Target: Turn $1 into millions through compound growth{Style.RESET_ALL}
{Fore.GREEN}⚡ Speed: Lightning-fast detection within 1-2 seconds{Style.RESET_ALL}
{Fore.GREEN}🤖 Operation: Fully autonomous - no human intervention needed{Style.RESET_ALL}
{Fore.CYAN}{'='*80}{Style.RESET_ALL}
"""
        print(banner)

    async def initialize_components(self) -> bool:
        """Initialize all bot components"""
        try:
            logging.info("Initializing bot components...")
            
            # Setup wallet from environment variable
            private_key = os.getenv('PRIVATE_KEY')
            if not private_key:
                logging.error("PRIVATE_KEY not found in environment variables")
                logging.info("Please set PRIVATE_KEY in your environment variables or .env file")
                return False
            
            # Clean the private key
            private_key = private_key.strip()
            if not private_key:
                logging.error("PRIVATE_KEY is empty")
                return False
            
            # Initialize blockchain connection
            if not self.blockchain.setup_account(private_key):
                logging.error("Failed to setup wallet account")
                return False
            
            # Initialize security engine
            self.security_engine = AdvancedSecurityEngine(self.config, self.blockchain.w3)
            
            # Initialize profit manager
            self.profit_manager = ProfitManager(self.config, self.blockchain, self.notifier)
            
            logging.info(f"{Fore.GREEN}✅ All components initialized successfully{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            logging.error(f"Error initializing components: {e}")
            return False

    async def test_all_connections(self) -> bool:
        """Test all connections and APIs"""
        try:
            logging.info("Testing all connections...")
            
            # Test blockchain connection
            if not self.blockchain.w3 or not self.blockchain.w3.is_connected():
                logging.error("Blockchain connection failed")
                return False
            
            # Test wallet balance
            balance = await self.blockchain.get_wallet_balance()
            logging.info(f"Wallet BNB balance: {balance:.6f} BNB")
            
            required_balance = (self.config['trading']['buy_amount_bnb'] + 
                              self.config['trading']['gas_reserve_bnb'])
            
            if balance < required_balance:
                logging.warning(f"Low BNB balance! Need at least {required_balance:.6f} BNB")
                await self.notifier.notify_error("Low Balance", f"Need {required_balance:.6f} BNB, have {balance:.6f} BNB")
            
            # Test Telegram connection
            if not await self.notifier.test_connection():
                logging.warning("Telegram connection failed - notifications disabled")
            
            # Test security engine
            async with self.security_engine:
                logging.info("Security engine ready")
            
            logging.info(f"{Fore.GREEN}✅ All connection tests passed{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            logging.error(f"Connection test error: {e}")
            return False

    async def monitor_new_pairs(self):
        """Monitor for new pair creation events"""
        logging.info(f"{Fore.YELLOW}🔍 Starting pair monitoring...{Style.RESET_ALL}")
        
        try:
            # Get factory contract
            factory_address = Web3.to_checksum_address(self.blockchain.factory_address)
            factory_contract = self.blockchain.w3.eth.contract(
                address=factory_address,
                abi=self.blockchain.factory_abi
            )
            
            # Create event filter for new pairs
            event_filter = factory_contract.events.PairCreated.create_filter(fromBlock='latest')
            
            while self.running:
                try:
                    # Check for new events
                    new_events = event_filter.get_new_entries()
                    
                    for event in new_events:
                        await self.handle_new_pair_event(event)
                    
                    # Small delay to prevent excessive API calls
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logging.error(f"Error monitoring pairs: {e}")
                    await asyncio.sleep(5)  # Longer delay on error
                    
        except Exception as e:
            logging.error(f"Fatal error in pair monitoring: {e}")
            await self.notifier.notify_error("Pair Monitoring Error", str(e))

    async def handle_new_pair_event(self, event):
        """Handle new pair creation event"""
        try:
            pair_address = event['args']['pair']
            token0 = event['args']['token0']
            token1 = event['args']['token1']
            
            # Skip if already processed
            if pair_address in self.processed_pairs:
                return
            
            self.processed_pairs.add(pair_address)
            self.session_stats['tokens_detected'] += 1
            
            # Determine which token is new (not WBNB/BUSD/USDT)
            wbnb_address = Web3.to_checksum_address(self.blockchain.wbnb_address)
            busd_address = Web3.to_checksum_address(self.blockchain.busd_address)
            usdt_address = Web3.to_checksum_address(self.config['blockchain']['usdt_address'])
            
            new_token = None
            if (token0 != wbnb_address and token0 != busd_address and token0 != usdt_address):
                new_token = token0
            elif (token1 != wbnb_address and token1 != busd_address and token1 != usdt_address):
                new_token = token1
            
            if not new_token:
                return  # Not a valid token pair
            
            logging.info(f"{Fore.YELLOW}🔍 New token pair detected: {new_token}{Style.RESET_ALL}")
            
            # Get token information
            token_info = await self.blockchain.get_token_info(new_token)
            
            # Quick age check
            current_time = int(time.time())
            max_age_seconds = self.config['trading']['max_token_age_minutes'] * 60
            
            # Estimate pair age (this is approximate)
            estimated_age_minutes = 0  # New pair, so very young
            
            # Notify detection
            await self.notifier.notify_token_detected(
                new_token,
                token_info['name'],
                token_info['symbol'],
                0,  # Will calculate liquidity in security check
                estimated_age_minutes
            )
            
            # Run comprehensive security analysis
            await self.analyze_and_trade_token(new_token, pair_address, token_info)
            
        except Exception as e:
            logging.error(f"Error handling new pair event: {e}")

    async def analyze_and_trade_token(self, token_address: str, pair_address: str, token_info: Dict[str, Any]):
        """Analyze token and execute trade if it passes all checks"""
        try:
            self.session_stats['tokens_analyzed'] += 1
            
            logging.info(f"{Fore.CYAN}🔍 Analyzing {token_info['symbol']} ({token_address[:8]}...){Style.RESET_ALL}")
            
            # Run comprehensive security check
            async with self.security_engine:
                is_safe, failed_reasons, detailed_results = await self.security_engine.comprehensive_security_check(
                    token_address, pair_address
                )
            
            # Notify security check result
            await self.notifier.notify_security_check_result(
                token_address, is_safe, failed_reasons, detailed_results
            )
            
            if is_safe:
                # Token passed all security checks - execute buy
                await self.execute_buy_order(token_address, pair_address, token_info)
            else:
                logging.warning(f"{Fore.RED}❌ {token_info['symbol']} failed security checks: {', '.join(failed_reasons[:3])}{Style.RESET_ALL}")
            
        except Exception as e:
            logging.error(f"Error analyzing token {token_address}: {e}")

    async def execute_buy_order(self, token_address: str, pair_address: str, token_info: Dict[str, Any]):
        """Execute buy order for approved token"""
        try:
            buy_amount_bnb = self.config['trading']['buy_amount_bnb']
            
            logging.info(f"{Fore.GREEN}💳 Executing buy order for {token_info['symbol']} ({buy_amount_bnb:.6f} BNB){Style.RESET_ALL}")
            
            # Check current positions
            if len(self.profit_manager.positions) >= self.config['trading']['max_concurrent_positions']:
                logging.warning(f"Max concurrent positions reached ({len(self.profit_manager.positions)})")
                return
            
            # Check wallet balance
            balance = await self.blockchain.get_wallet_balance()
            required_balance = buy_amount_bnb + self.config['trading']['gas_reserve_bnb']
            
            if balance < required_balance:
                logging.warning(f"Insufficient balance: {balance:.6f} < {required_balance:.6f} BNB")
                await self.notifier.notify_error("Insufficient Balance", f"Need {required_balance:.6f} BNB")
                return
            
            # Notify buy attempt
            await self.notifier.notify_buy_attempt(
                token_address, buy_amount_bnb, 0, token_info['symbol']
            )
            
            # Execute buy transaction
            success, message, result_data = await self.blockchain.execute_buy_transaction(
                token_address, buy_amount_bnb, self.config['trading']['slippage_tolerance']
            )
            
            if success:
                # Buy successful
                gas_cost = result_data.get('gas_cost_bnb', 0)
                tokens_received = result_data.get('expected_tokens', 0) / (10**token_info['decimals'])
                tx_hash = result_data.get('transaction_hash', '')
                
                # Calculate entry price
                entry_price_bnb = buy_amount_bnb / tokens_received if tokens_received > 0 else 0
                
                # Add position to profit manager
                self.profit_manager.add_position(
                    token_address=token_address,
                    token_symbol=token_info['symbol'],
                    entry_price_bnb=entry_price_bnb,
                    tokens_owned=tokens_received,
                    investment_bnb=buy_amount_bnb,
                    pair_address=pair_address,
                    transaction_hash=tx_hash
                )
                
                # Update session stats
                self.session_stats['tokens_purchased'] += 1
                
                # Notify success
                await self.notifier.notify_buy_success(
                    token_address, token_info['symbol'], buy_amount_bnb,
                    tokens_received, tx_hash, gas_cost
                )
                
                logging.info(f"{Fore.GREEN}🎉 Successfully bought {token_info['symbol']}! Tokens: {tokens_received:,.0f}{Style.RESET_ALL}")
                
            else:
                # Buy failed
                logging.error(f"{Fore.RED}❌ Buy failed for {token_info['symbol']}: {message}{Style.RESET_ALL}")
                await self.notifier.notify_buy_failed(token_address, token_info['symbol'], message)
            
        except Exception as e:
            logging.error(f"Error executing buy order: {e}")
            await self.notifier.notify_error("Buy Order Error", str(e))

    async def manage_positions(self):
        """Manage existing positions and profit taking"""
        logging.info(f"{Fore.BLUE}💼 Starting position management...{Style.RESET_ALL}")
        
        while self.running:
            try:
                # Update all position prices
                await self.profit_manager.update_position_prices()
                
                # Check profit opportunities
                await self.profit_manager.check_profit_opportunities()
                
                # Update session stats
                portfolio_summary = self.profit_manager.get_portfolio_summary()
                self.session_stats['total_profit_bnb'] = portfolio_summary.get('net_profit_bnb', 0)
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logging.error(f"Error in position management: {e}")
                await asyncio.sleep(30)  # Longer delay on error

    async def send_periodic_updates(self):
        """Send periodic status updates"""
        last_update = 0
        update_interval = 3600  # 1 hour
        
        while self.running:
            try:
                current_time = time.time()
                
                if current_time - last_update >= update_interval:
                    # Send status update
                    await self.send_status_update()
                    last_update = current_time
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error sending periodic updates: {e}")
                await asyncio.sleep(300)  # 5 minute delay on error

    async def send_status_update(self):
        """Send status update"""
        try:
            runtime_hours = (time.time() - self.start_time) / 3600
            portfolio_summary = self.profit_manager.get_portfolio_summary()
            
            # Create status message
            status = {
                'runtime_hours': runtime_hours,
                'tokens_detected': self.session_stats['tokens_detected'],
                'tokens_analyzed': self.session_stats['tokens_analyzed'],
                'tokens_purchased': self.session_stats['tokens_purchased'],
                'active_positions': len(self.profit_manager.positions),
                'total_profit_bnb': portfolio_summary.get('net_profit_bnb', 0),
                'successful_trades': portfolio_summary.get('successful_trades', 0),
                'failed_trades': portfolio_summary.get('failed_trades', 0),
                'win_rate_percentage': portfolio_summary.get('win_rate_percentage', 0)
            }
            
            # Send daily summary
            await self.notifier.notify_daily_summary(status)
            
        except Exception as e:
            logging.error(f"Error sending status update: {e}")

    async def cleanup(self):
        """Cleanup resources"""
        try:
            logging.info("Cleaning up resources...")
            
            if self.security_engine and hasattr(self.security_engine, 'session') and self.security_engine.session:
                await self.security_engine.session.close()
            
            # Save final positions
            if self.profit_manager:
                self.profit_manager.save_positions()
            
            logging.info("Cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

async def main():
    """Main entry point"""
    try:
        # Create and start the bot
        bot = BSCSniperBot2()
        await bot.start()
        
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        logging.info("BSC Sniper Bot 2.0 shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())