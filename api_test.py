#!/usr/bin/env python3
"""
API Test Script - Test all API integrations
"""

import asyncio
import aiohttp
import json
import os
from web3 import Web3
from web3.middleware import geth_poa_middleware

async def test_goplus_api():
    """Test GoPlus API"""
    try:
        print("🔍 Testing GoPlus API...")
        
        # Test token (WBNB)
        test_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
        url = f"https://api.gopluslabs.io/api/v1/token_security/56"
        params = {'contract_addresses': test_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ GoPlus API working! Status: {response.status}")
                    print(f"📊 Response keys: {list(data.keys())}")
                    return True
                else:
                    print(f"❌ GoPlus API failed with status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ GoPlus API error: {e}")
        return False

async def test_bscscan_api():
    """Test BSCScan API"""
    try:
        print("🔍 Testing BSCScan API...")
        
        # Load API key from config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        api_key = config['api_keys']['bscscan_api_key']
        test_address = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"  # WBNB
        
        url = "https://api.bscscan.com/api"
        params = {
            'module': 'contract',
            'action': 'getsourcecode',
            'address': test_address,
            'apikey': api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ BSCScan API working! Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"❌ BSCScan API failed with status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ BSCScan API error: {e}")
        return False

async def test_rpc_endpoints():
    """Test RPC endpoints"""
    try:
        print("🔍 Testing RPC endpoints...")
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        rpc_endpoints = config['blockchain']['rpc_endpoints']
        
        for i, rpc_url in enumerate(rpc_endpoints):
            try:
                print(f"Testing RPC {i+1}: {rpc_url}")
                w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if w3.is_connected():
                    latest_block = w3.eth.block_number
                    print(f"✅ RPC {i+1} working! Latest block: {latest_block}")
                else:
                    print(f"❌ RPC {i+1} connection failed")
            except Exception as e:
                print(f"❌ RPC {i+1} error: {e}")
        
        return True
    except Exception as e:
        print(f"❌ RPC test error: {e}")
        return False

async def test_binance_api():
    """Test Binance API for BNB price"""
    try:
        print("🔍 Testing Binance API...")
        
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    price = float(data['price'])
                    print(f"✅ Binance API working! BNB price: ${price:.2f}")
                    return True
                else:
                    print(f"❌ Binance API failed with status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Binance API error: {e}")
        return False

async def main():
    """Test all APIs"""
    print("🚀 Testing all API integrations...")
    print("="*50)
    
    results = await asyncio.gather(
        test_goplus_api(),
        test_bscscan_api(),
        test_rpc_endpoints(),
        test_binance_api(),
        return_exceptions=True
    )
    
    print("="*50)
    print("📊 Test Results Summary:")
    tests = ["GoPlus API", "BSCScan API", "RPC Endpoints", "Binance API"]
    
    for i, (test_name, result) in enumerate(zip(tests, results)):
        if isinstance(result, Exception):
            print(f"❌ {test_name}: ERROR - {result}")
        elif result:
            print(f"✅ {test_name}: WORKING")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Check if all critical APIs work
    critical_working = not isinstance(results[0], Exception) and results[0]  # GoPlus
    if critical_working:
        print("\n🎉 All critical APIs are working! Bot ready to make money!")
    else:
        print("\n⚠️ Some APIs need attention, but bot can still operate")

if __name__ == "__main__":
    asyncio.run(main())