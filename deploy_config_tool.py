#!/usr/bin/env python3
"""
BSC Sniper Bot 2.0 - Production Deployment Configuration
Optimizes the bot for production Ubuntu deployment
"""

import json
import os
import shutil
from pathlib import Path

def create_production_config():
    """Create optimized production configuration"""
    config = {
        "api_keys": {
            "goplus_app_key": "R3QUChegrrAMyXdA7MP7",
            "goplus_app_secret": "V8nZBkJgTbFYYz5gXKMkM2ASeNws4RyT",
            "goplus_fallback_key": "backup_key_here",
            "bscscan_api_key": "49KJV11NHIES9X4WSH95IIN1YUJJUZ5795",
            "bscscan_fallback_api_key": "backup_bscscan_key",
            "multichain_api_key": "your_multichain_api_key_here",
            "honeypot_api_key": "backup_honeypot_key",
            "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
            "telegram_channel_id": "YOUR_TELEGRAM_CHANNEL_ID"
        },
        "trading": {
            "buy_amount_bnb": 0.001,
            "gas_reserve_bnb": 0.001,
            "max_concurrent_positions": 5,
            "max_token_age_minutes": 3,
            "min_liquidity_usd": 500,
            "slippage_tolerance": 15,
            "max_buy_tax": 10,
            "max_sell_tax": 10,
            "min_holders": 3,
            "auto_compound": True,
            "compound_threshold_bnb": 0.01,
            "gas_optimization": {
                "max_gas_price_gwei": 20,
                "gas_price_multiplier": 1.2,
                "priority_fee_gwei": 2,
                "fast_execution_mode": True
            },
            "advanced_profit": {
                "compound_percentage": 80,
                "reinvest_threshold_multiplier": 3.0,
                "max_position_size_bnb": 0.1,
                "scaling_factor": 1.5
            }
        },
        "profit_management": {
            "take_profit_1": {
                "multiplier": 2,
                "percentage": 25
            },
            "take_profit_2": {
                "multiplier": 5,
                "percentage": 30
            },
            "take_profit_3": {
                "multiplier": 10,
                "percentage": 25
            },
            "trailing_stop_loss_percentage": 30,
            "max_holding_time_hours": 24
        },
        "security": {
            "min_liquidity_lock_days": 30,
            "max_ownership_percentage": 10,
            "require_verified_contract": False,
            "blacklisted_functions": [
                "mint",
                "blacklist", 
                "addToBlackList",
                "setFee",
                "enableTrading",
                "pause"
            ],
            "min_contract_age_minutes": 0,
            "honeypot_simulation_amount": 0.0001,
            "enhanced_checks": {
                "check_proxy_patterns": True,
                "check_fee_manipulation": True,
                "check_liquidity_burns": True,
                "max_transaction_cooldown": 300
            }
        },
        "blockchain": {
            "rpc_endpoints": [
                "https://bsc-dataseed1.binance.org/",
                "https://bsc-dataseed2.binance.org/",
                "https://bsc-dataseed3.binance.org/",
                "https://bsc-dataseed4.binance.org/",
                "https://rpc.ankr.com/bsc",
                "https://bsc.nodereal.io"
            ],
            "pancakeswap_factory": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
            "pancakeswap_router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "wbnb_address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
            "busd_address": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
            "usdt_address": "0x55d398326f99059fF775485246999027B3197955"
        },
        "advanced_checks": {
            "check_rugpull_patterns": True,
            "check_dev_wallets": True,
            "check_whale_concentration": True,
            "check_liquidity_locks": True,
            "check_social_signals": False,
            "max_dev_wallet_percentage": 5,
            "max_whale_wallet_percentage": 3,
            "additional_security": {
                "check_contract_similarity": True,
                "check_team_tokens": True,
                "check_presale_dumps": True,
                "check_bot_activity": True,
                "min_natural_holders": 3,
                "max_holder_concentration": 50,
                "focus_on_concentration": True,
                "allow_new_tokens": True
            }
        }
    }
    
    # Write production config
    with open('config_production.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Production configuration created: config_production.json")

def create_systemd_service():
    """Create systemd service file"""
    service_content = """[Unit]
Description=BSC Sniper Bot 2.0 - Ultimate Money Making Machine
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/bsc_sniper_bot_2
Environment=PATH=/home/ubuntu/bsc_sniper_bot_2/venv/bin
Environment=PYTHONPATH=/home/ubuntu/bsc_sniper_bot_2
ExecStart=/home/ubuntu/bsc_sniper_bot_2/venv/bin/python bsc_sniper_bot_2.py
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
ReadWritePaths=/home/ubuntu/bsc_sniper_bot_2

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
"""
    
    with open('bsc-sniper.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created: bsc-sniper.service")

def create_production_requirements():
    """Create optimized requirements.txt for production"""
    requirements = """# BSC Sniper Bot 2.0 - Production Dependencies
# Core blockchain libraries - Locked versions for stability
web3==6.15.1
eth-account==0.11.0
eth-utils==2.3.1
eth-typing==3.5.2
hexbytes==0.3.1

# HTTP and async libraries - Performance optimized
requests==2.31.0
aiohttp==3.9.1
websockets==12.0
asyncio-throttle==1.0.2

# Notification and UI
python-telegram-bot==20.7
colorama==0.4.6

# Configuration and environment
python-dotenv==1.0.0

# System monitoring and performance
psutil==5.9.6
numpy==1.24.4
pandas==2.0.3

# Additional stability packages for production
certifi==2023.7.22
urllib3==2.0.4
charset-normalizer==3.2.0
idna==3.4
"""
    
    with open('requirements_production.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Production requirements created: requirements_production.txt")

def create_env_template():
    """Create comprehensive .env template"""
    env_template = """# BSC Sniper Bot 2.0 - Environment Variables
# ================================================

# WALLET CONFIGURATION (REQUIRED)
# Your wallet's private key - KEEP THIS SECRET!
PRIVATE_KEY=your_wallet_private_key_here

# TELEGRAM NOTIFICATIONS (OPTIONAL)
# Get these from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_telegram_channel_id

# API KEYS (OPTIONAL - for enhanced features)
# GoPlus backup key for redundancy
GOPLUS_FALLBACK_KEY=backup_goplus_key

# BSCScan backup key
BSCSCAN_FALLBACK_KEY=backup_bscscan_key

# Multichain API for additional security checks
MULTICHAIN_API_KEY=your_multichain_key

# PRODUCTION SETTINGS
# Set to 'production' for live trading
BOT_ENVIRONMENT=development

# LOGGING LEVEL (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ================================================
# SECURITY REMINDER:
# - Never share this file or commit it to Git
# - Use a dedicated trading wallet only
# - Keep most funds in a separate secure wallet
# ================================================
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("✅ Environment template created: .env.template")

def main():
    print("🚀 BSC Sniper Bot 2.0 - Production Deployment Setup")
    print("=" * 60)
    
    # Create all production files
    create_production_config()
    create_systemd_service() 
    create_production_requirements()
    create_env_template()
    
    print("\n✅ ALL PRODUCTION FILES CREATED!")
    print("\n📋 Files created:")
    print("   • config_production.json - Optimized production configuration")
    print("   • bsc-sniper.service - Systemd service for 24/7 operation")
    print("   • requirements_production.txt - Locked dependencies")
    print("   • .env.template - Environment variables template")
    
    print("\n🎯 DEPLOYMENT INSTRUCTIONS:")
    print("1. Copy all files to your Ubuntu server")
    print("2. Run: chmod +x ubuntu_setup_complete.sh")
    print("3. Run: ./ubuntu_setup_complete.sh")
    print("4. Configure your .env file with real credentials")
    print("5. Start: sudo systemctl start bsc-sniper")
    print("6. Enable auto-start: sudo systemctl enable bsc-sniper")
    
    print("\n🔥 Ready to make millions on Ubuntu! 💰")

if __name__ == "__main__":
    main()