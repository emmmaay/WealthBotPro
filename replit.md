# BSC Sniper Bot 2.0

## Overview

BSC Sniper Bot 2.0 is an advanced cryptocurrency trading bot designed for automated token sniping on the Binance Smart Chain (BSC). The system autonomously detects new token launches, performs comprehensive security analysis, executes trades, and manages positions with sophisticated profit-taking strategies. It features a modular architecture with multiple failsafe mechanisms, real-time notifications, and advanced security checks to maximize profitability while minimizing risks.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture Pattern
The system follows a modular, event-driven architecture with clear separation of concerns across specialized components:

**Main Bot Controller (`bsc_sniper_bot_2.py`)**
- Acts as the central orchestrator and entry point
- Manages overall bot lifecycle and coordination between modules
- Handles configuration loading and system initialization
- Implements graceful shutdown and error recovery mechanisms

**Blockchain Interface Layer (`blockchain_interface.py`)**
- Provides robust Web3 connectivity with automatic RPC failover
- Manages contract interactions (PancakeSwap router, factory, ERC20 tokens)
- Handles transaction execution with gas optimization
- Implements connection pooling and retry logic for reliability

**Security Engine (`advanced_security_engine.py`)**
- Performs 30+ comprehensive security checks on tokens
- Integrates with multiple security APIs (GoPlus, BSCScan)
- Validates contract code, liquidity locks, and ownership patterns
- Implements honeypot detection and rug pull prevention

**Profit Management System (`profit_management.py`)**
- Manages active trading positions with detailed tracking
- Implements multi-tier profit-taking strategies (2x, 5x, 10x multipliers)
- Features trailing stop-loss mechanisms
- Supports position compounding and automatic reinvestment

**Notification System (`telegram_notifier.py`)**
- Provides real-time updates via Telegram integration
- Sends formatted trade alerts and portfolio summaries
- Implements message queuing to prevent rate limiting
- Supports rich formatting for trade analysis

### Data Flow Architecture
The system operates on an asynchronous, pipeline-based data flow:

1. **Token Detection** → Monitors new liquidity pairs on PancakeSwap
2. **Security Analysis** → Comprehensive multi-API security validation
3. **Trade Execution** → Automated buying with gas optimization
4. **Position Management** → Continuous monitoring and profit-taking
5. **Notification** → Real-time updates on all activities

### Configuration Management
Centralized configuration system using JSON with environment variable support:
- Trading parameters (amounts, slippage, taxes)
- Security thresholds and risk parameters
- API keys and external service credentials
- Profit management rules and multipliers

### Error Handling Strategy
Multi-layered error handling approach:
- RPC endpoint failover for blockchain connectivity
- API retry mechanisms with exponential backoff
- Transaction failure recovery and gas adjustment
- Graceful degradation when external services fail

## External Dependencies

### Blockchain Infrastructure
- **Web3.py**: Primary blockchain interaction library
- **BSC RPC Endpoints**: Multiple RPC providers for redundancy
- **PancakeSwap Contracts**: DEX integration for trading operations
- **ERC20 Token Standards**: Smart contract interaction protocols

### Security APIs
- **GoPlus Labs API**: Token security analysis and risk assessment
- **BSCScan API**: Contract verification and transaction history
- **Custom Security Checks**: Internal honeypot and rug pull detection

### Communication Services
- **Telegram Bot API**: Real-time notifications and alerts
- **Python Telegram Bot Library**: Async messaging framework

### Core Python Libraries
- **aiohttp**: Asynchronous HTTP client for API calls
- **asyncio**: Concurrent programming and event loops
- **eth-account**: Ethereum account management and signing
- **colorama**: Terminal output formatting and colors

### Development Tools
- **python-dotenv**: Environment variable management
- **logging**: Comprehensive system logging and debugging

### Trading Infrastructure
- **PancakeSwap Router**: DEX trading execution
- **PancakeSwap Factory**: Pair detection and monitoring
- **WBNB/BUSD Contracts**: Base trading pair references