#!/usr/bin/env python3
"""
BSC Sniper Bot 2.0 - Installation Verification Script
Run this to verify all components are properly installed
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[0;32m",    # Green
        "WARN": "\033[1;33m",    # Yellow  
        "ERROR": "\033[0;31m",   # Red
        "RESET": "\033[0m"       # Reset
    }
    print(f"{colors.get(status, '')}[{status}] {message}{colors['RESET']}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_status(f"Python version: {version.major}.{version.minor}.{version.micro} ✅")
        return True
    else:
        print_status(f"Python version: {version.major}.{version.minor}.{version.micro} - Need 3.11+ ❌", "ERROR")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    required_packages = [
        'web3', 'eth_account', 'requests', 'asyncio_throttle',
        'colorama', 'telegram', 'aiohttp', 'eth_utils', 
        'eth_typing', 'hexbytes', 'websockets', 'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if not missing_packages:
        print_status(f"All {len(required_packages)} required packages installed ✅")
        return True
    else:
        print_status(f"Missing packages: {', '.join(missing_packages)} ❌", "ERROR")
        return False

def check_bot_files():
    """Check if all bot files exist"""
    required_files = [
        'bsc_sniper_bot_2.py',
        'blockchain_interface.py', 
        'advanced_security_engine.py',
        'profit_management.py',
        'telegram_notifier.py',
        'validate_key.py',
        'config.json',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = Path('bot_files') / file if Path('bot_files').exists() else Path(file)
        if not file_path.exists():
            missing_files.append(file)
    
    if not missing_files:
        print_status(f"All {len(required_files)} bot files present ✅")
        return True
    else:
        print_status(f"Missing files: {', '.join(missing_files)} ❌", "ERROR")
        return False

def check_environment_file():
    """Check if .env file exists and has required variables"""
    env_files = ['.env', 'bot_files/.env']
    env_found = False
    
    for env_file in env_files:
        if Path(env_file).exists():
            env_found = True
            print_status(f"Environment file found: {env_file} ✅")
            
            # Check if it has the required variables
            with open(env_file, 'r') as f:
                content = f.read()
                if 'PRIVATE_KEY=' in content:
                    print_status("PRIVATE_KEY variable found ✅")
                else:
                    print_status("PRIVATE_KEY variable missing ❌", "WARN")
            break
    
    if not env_found:
        print_status("No .env file found ❌", "WARN")
        print_status("Create .env file with: PRIVATE_KEY=your_private_key_here", "INFO")
    
    return env_found

def check_system_dependencies():
    """Check system-level dependencies"""
    commands = ['git', 'curl', 'python3.11']
    missing_commands = []
    
    for cmd in commands:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_commands.append(cmd)
    
    if not missing_commands:
        print_status("All system dependencies available ✅")
        return True
    else:
        print_status(f"Missing system commands: {', '.join(missing_commands)} ❌", "ERROR")
        return False

def check_network_connectivity():
    """Test network connectivity"""
    try:
        import requests
        response = requests.get('https://api.gopluslabs.io', timeout=5)
        print_status("GoPlus API connectivity ✅")
        return True
    except Exception as e:
        print_status(f"Network connectivity issue: {e} ❌", "WARN")
        return False

def main():
    print("=" * 50)
    print("🔍 BSC SNIPER BOT 2.0 - INSTALLATION VERIFICATION")
    print("=" * 50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Bot Files", check_bot_files),
        ("Environment File", check_environment_file),
        ("System Dependencies", check_system_dependencies),
        ("Network Connectivity", check_network_connectivity)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"Checking {name}...")
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 VERIFICATION SUMMARY: {passed}/{total} checks passed")
    print("=" * 50)
    
    if passed == total:
        print_status("🚀 ALL CHECKS PASSED! Your bot is ready to run!", "INFO")
        print_status("Next steps:", "INFO")
        print("   1. Configure your .env file with real credentials")
        print("   2. Run: python bsc_sniper_bot_2.py")
        print("   3. Monitor the logs for successful startup")
        return True
    else:
        print_status(f"❌ {total - passed} issues found. Please fix them before running the bot.", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)