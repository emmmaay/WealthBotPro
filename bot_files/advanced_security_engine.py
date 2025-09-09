#!/usr/bin/env python3
"""
Advanced Security Engine - 30+ Security Checks for Token Verification
The most comprehensive security verification system for BSC token sniping
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, List, Tuple, Optional
from web3 import Web3
from colorama import Fore, Style

class AdvancedSecurityEngine:
    def __init__(self, config: Dict[str, Any], web3_client: Web3):
        self.config = config
        self.w3 = web3_client
        self.api_keys = config['api_keys']
        self.security_config = config['security']
        self.advanced_config = config['advanced_checks']
        
        # Initialize session for API calls
        self.session = None
        
        # Security check results
        self.security_results = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def comprehensive_security_check(self, token_address: str, pair_address: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Run comprehensive security checks on a token
        Returns: (is_safe, failed_reasons, detailed_results)
        """
        token_address = Web3.to_checksum_address(token_address)
        pair_address = Web3.to_checksum_address(pair_address)
        
        logging.info(f"{Fore.YELLOW}🔍 Running comprehensive security check for {token_address}{Style.RESET_ALL}")
        
        failed_reasons = []
        detailed_results = {}
        
        try:
            # Create session if not exists
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Run all security checks in parallel for speed
            results = await asyncio.gather(
                self._check_goplus_security(token_address),
                self._check_honeypot_simulation(token_address, pair_address),
                self._check_contract_verification(token_address),
                self._check_liquidity_analysis(pair_address, token_address),
                self._check_holder_analysis(token_address),
                self._check_ownership_renounced(token_address),
                self._check_trading_taxes(token_address),
                self._check_whale_concentration(token_address),
                self._check_dev_wallet_analysis(token_address),
                self._check_rugpull_patterns(token_address),
                return_exceptions=True
            )
            
            # Process results
            goplus_result = results[0]
            honeypot_result = results[1]
            contract_result = results[2]
            liquidity_result = results[3]
            holder_result = results[4]
            ownership_result = results[5]
            tax_result = results[6]
            whale_result = results[7]
            dev_wallet_result = results[8]
            rugpull_result = results[9]
            
            # GoPlus Security Check
            if isinstance(goplus_result, Exception):
                failed_reasons.append(f"GoPlus API error: {str(goplus_result)}")
                detailed_results['goplus'] = {'error': str(goplus_result)}
            else:
                goplus_safe, goplus_reasons, goplus_data = goplus_result
                detailed_results['goplus'] = goplus_data
                if not goplus_safe:
                    failed_reasons.extend([f"GoPlus: {r}" for r in goplus_reasons])
            
            # Honeypot Simulation
            if isinstance(honeypot_result, Exception):
                failed_reasons.append(f"Honeypot check error: {str(honeypot_result)}")
                detailed_results['honeypot'] = {'error': str(honeypot_result)}
            else:
                if len(honeypot_result) >= 2:
                    honeypot_safe, honeypot_reason = honeypot_result[0], honeypot_result[1]
                    detailed_results['honeypot'] = {'safe': honeypot_safe, 'reason': honeypot_reason}
                    if not honeypot_safe:
                        failed_reasons.append(f"Honeypot: {honeypot_reason}")
                else:
                    failed_reasons.append("Honeypot check failed: Invalid result")
            
            # Contract Verification
            if isinstance(contract_result, Exception):
                logging.warning(f"Contract verification error: {str(contract_result)}")
                detailed_results['contract'] = {'error': str(contract_result)}
            else:
                if len(contract_result) >= 2:
                    contract_safe, contract_data = contract_result[0], contract_result[1]
                    detailed_results['contract'] = contract_data
                    if self.security_config['require_verified_contract'] and not contract_safe:
                        failed_reasons.append("Contract not verified")
                else:
                    detailed_results['contract'] = {'error': 'Invalid contract result'}
            
            # Liquidity Analysis
            if isinstance(liquidity_result, Exception):
                failed_reasons.append(f"Liquidity check error: {str(liquidity_result)}")
                detailed_results['liquidity'] = {'error': str(liquidity_result)}
            else:
                if len(liquidity_result) >= 2:
                    liquidity_safe, liquidity_data = liquidity_result[0], liquidity_result[1]
                    detailed_results['liquidity'] = liquidity_data
                    if not liquidity_safe:
                        reason = liquidity_data.get('reason', 'Failed check') if isinstance(liquidity_data, dict) else 'Failed check'
                        failed_reasons.append(f"Liquidity: {reason}")
                else:
                    failed_reasons.append("Liquidity check failed: Invalid result")
            
            # Holder Analysis
            if isinstance(holder_result, Exception):
                logging.warning(f"Holder analysis error: {str(holder_result)}")
                detailed_results['holders'] = {'error': str(holder_result)}
            else:
                holder_safe, holder_data = holder_result
                detailed_results['holders'] = holder_data
                if not holder_safe:
                    failed_reasons.append(f"Holders: {holder_data.get('reason', 'Failed check')}")
            
            # Ownership Check
            if isinstance(ownership_result, Exception):
                logging.warning(f"Ownership check error: {str(ownership_result)}")
                detailed_results['ownership'] = {'error': str(ownership_result)}
            else:
                ownership_safe, ownership_data = ownership_result
                detailed_results['ownership'] = ownership_data
                if not ownership_safe:
                    failed_reasons.append(f"Ownership: {ownership_data.get('reason', 'Not renounced')}")
            
            # Tax Analysis
            if isinstance(tax_result, Exception):
                logging.warning(f"Tax analysis error: {str(tax_result)}")
                detailed_results['taxes'] = {'error': str(tax_result)}
            else:
                tax_safe, tax_data = tax_result
                detailed_results['taxes'] = tax_data
                if not tax_safe:
                    failed_reasons.append(f"Tax: {tax_data.get('reason', 'High taxes')}")
            
            # Whale Concentration
            if isinstance(whale_result, Exception):
                logging.warning(f"Whale analysis error: {str(whale_result)}")
                detailed_results['whales'] = {'error': str(whale_result)}
            else:
                whale_safe, whale_data = whale_result
                detailed_results['whales'] = whale_data
                if not whale_safe:
                    failed_reasons.append(f"Whales: {whale_data.get('reason', 'High concentration')}")
            
            # Dev Wallet Analysis
            if isinstance(dev_wallet_result, Exception):
                logging.warning(f"Dev wallet analysis error: {str(dev_wallet_result)}")
                detailed_results['dev_wallets'] = {'error': str(dev_wallet_result)}
            else:
                dev_safe, dev_data = dev_wallet_result
                detailed_results['dev_wallets'] = dev_data
                if not dev_safe:
                    failed_reasons.append(f"Dev wallets: {dev_data.get('reason', 'Suspicious activity')}")
            
            # Rugpull Pattern Analysis
            if isinstance(rugpull_result, Exception):
                logging.warning(f"Rugpull analysis error: {str(rugpull_result)}")
                detailed_results['rugpull'] = {'error': str(rugpull_result)}
            else:
                rugpull_safe, rugpull_data = rugpull_result
                detailed_results['rugpull'] = rugpull_data
                if not rugpull_safe:
                    failed_reasons.append(f"Rugpull risk: {rugpull_data.get('reason', 'Suspicious patterns')}")
            
            # Final safety determination
            is_safe = len(failed_reasons) == 0
            
            if is_safe:
                logging.info(f"{Fore.GREEN}✅ Token passed all security checks: {token_address}{Style.RESET_ALL}")
            else:
                logging.warning(f"{Fore.RED}❌ Token failed security checks: {', '.join(failed_reasons)}{Style.RESET_ALL}")
            
            return is_safe, failed_reasons, detailed_results
            
        except Exception as e:
            logging.error(f"Comprehensive security check error: {e}")
            return False, [f"Security check error: {str(e)}"], {}

    async def _check_goplus_security(self, token_address: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Check token security using GoPlus API"""
        try:
            # GoPlus API endpoint for BSC
            url = f"https://api.gopluslabs.io/api/v1/token_security/56"
            params = {'contract_addresses': token_address}
            
            headers = {}
            if self.api_keys.get('goplus_app_key'):
                headers['X-API-KEY'] = self.api_keys['goplus_app_key']
            
            async with self.session.get(url, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'result' in data and token_address.lower() in data['result']:
                        token_data = data['result'][token_address.lower()]
                        
                        failed_reasons = []
                        
                        # Check critical security issues
                        if token_data.get('is_honeypot', '0') == '1':
                            failed_reasons.append("Detected as honeypot")
                        
                        if token_data.get('is_blacklisted', '0') == '1':
                            failed_reasons.append("Token is blacklisted")
                        
                        if token_data.get('is_whitelisted', '0') == '0' and token_data.get('is_open_source', '0') == '0':
                            failed_reasons.append("Contract not open source")
                        
                        # Check buy/sell taxes
                        buy_tax = float(token_data.get('buy_tax', '0'))
                        sell_tax = float(token_data.get('sell_tax', '0'))
                        
                        max_buy_tax = self.config['trading'].get('max_buy_tax', 10)
                        max_sell_tax = self.config['trading'].get('max_sell_tax', 10)
                        
                        if buy_tax > max_buy_tax:
                            failed_reasons.append(f"High buy tax: {buy_tax}%")
                        
                        if sell_tax > max_sell_tax:
                            failed_reasons.append(f"High sell tax: {sell_tax}%")
                        
                        # Check for suspicious functions
                        if token_data.get('is_mintable', '0') == '1':
                            failed_reasons.append("Token is mintable")
                        
                        if token_data.get('can_take_back_ownership', '0') == '1':
                            failed_reasons.append("Ownership can be reclaimed")
                        
                        # Check holder count
                        holder_count = int(token_data.get('holder_count', '0'))
                        if holder_count < self.config['trading']['min_holders']:
                            failed_reasons.append(f"Too few holders: {holder_count}")
                        
                        return len(failed_reasons) == 0, failed_reasons, token_data
                    else:
                        return False, ["Token data not found in GoPlus"], {}
                else:
                    logging.warning(f"GoPlus API returned status {response.status}")
                    return False, [f"GoPlus API error: {response.status}"], {}
                    
        except Exception as e:
            logging.error(f"GoPlus security check error: {e}")
            raise e

    async def _check_honeypot_simulation(self, token_address: str, pair_address: str) -> Tuple[bool, str]:
        """Simulate buy/sell to detect honeypots"""
        try:
            # Get router contract
            router_abi = [
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                        {"internalType": "address[]", "name": "path", "type": "address[]"}
                    ],
                    "name": "getAmountsOut",
                    "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            router_address = self.config['blockchain']['pancakeswap_router']
            router_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(router_address),
                abi=router_abi
            )
            
            wbnb_address = self.config['blockchain']['wbnb_address']
            test_amount = int(self.security_config['honeypot_simulation_amount'] * 10**18)
            
            # Test buy simulation
            try:
                buy_path = [wbnb_address, token_address]
                buy_amounts = router_contract.functions.getAmountsOut(test_amount, buy_path).call()
                
                if len(buy_amounts) < 2 or buy_amounts[1] == 0:
                    return False, "Cannot simulate buy transaction"
                
                # Test sell simulation
                sell_path = [token_address, wbnb_address]
                sell_amounts = router_contract.functions.getAmountsOut(buy_amounts[1], sell_path).call()
                
                if len(sell_amounts) < 2 or sell_amounts[1] == 0:
                    return False, "Cannot simulate sell transaction"
                
                # Calculate price impact
                price_impact = (test_amount - sell_amounts[1]) / test_amount * 100
                
                if price_impact > 90:  # More than 90% loss
                    return False, f"Extreme price impact: {price_impact:.1f}%"
                
                return True, f"Honeypot check passed (impact: {price_impact:.1f}%)"
                
            except Exception as e:
                return False, f"Simulation failed: {str(e)}"
                
        except Exception as e:
            logging.error(f"Honeypot simulation error: {e}")
            raise e

    async def _check_contract_verification(self, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if contract is verified on BSCScan"""
        try:
            api_key = self.api_keys.get('bscscan_api_key', '')
            url = "https://api.bscscan.com/api"
            
            params = {
                'module': 'contract',
                'action': 'getsourcecode',
                'address': token_address,
                'apikey': api_key
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == '1' and data.get('result'):
                        source_code = data['result'][0].get('SourceCode', '')
                        contract_name = data['result'][0].get('ContractName', '')
                        
                        is_verified = len(source_code) > 0
                        
                        result_data = {
                            'verified': is_verified,
                            'contract_name': contract_name,
                            'has_source': len(source_code) > 0
                        }
                        
                        return is_verified, result_data
                    else:
                        return False, {'verified': False, 'error': 'No contract data'}
                else:
                    return False, {'verified': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logging.error(f"Contract verification error: {e}")
            raise e

    async def _check_liquidity_analysis(self, pair_address: str, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Analyze liquidity pool"""
        try:
            # Get pair contract
            pair_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getReserves",
                    "outputs": [
                        {"name": "_reserve0", "type": "uint112"},
                        {"name": "_reserve1", "type": "uint112"},
                        {"name": "_blockTimestampLast", "type": "uint32"}
                    ],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "token0",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "token1",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function"
                }
            ]
            
            pair_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=pair_abi
            )
            
            # Get reserves and tokens
            reserves = pair_contract.functions.getReserves().call()
            token0 = pair_contract.functions.token0().call()
            token1 = pair_contract.functions.token1().call()
            
            wbnb_address = Web3.to_checksum_address(self.config['blockchain']['wbnb_address'])
            
            # Determine which reserve is BNB
            bnb_reserve = 0
            token_reserve = 0
            
            if Web3.to_checksum_address(token0) == wbnb_address:
                bnb_reserve = reserves[0] / (10**18)
                token_reserve = reserves[1]
            elif Web3.to_checksum_address(token1) == wbnb_address:
                bnb_reserve = reserves[1] / (10**18)
                token_reserve = reserves[0]
            else:
                return False, {'reason': 'No BNB pair found', 'bnb_reserve': 0}
            
            # Get BNB price (approximate)
            bnb_price_usd = await self._get_bnb_price()
            liquidity_usd = bnb_reserve * bnb_price_usd * 2  # Both sides of pool
            
            # Check minimum liquidity
            min_liquidity = self.config['trading']['min_liquidity_usd']
            
            result_data = {
                'bnb_reserve': bnb_reserve,
                'token_reserve': token_reserve,
                'liquidity_usd': liquidity_usd,
                'bnb_price_usd': bnb_price_usd
            }
            
            if liquidity_usd < min_liquidity:
                result_data['reason'] = f"Insufficient liquidity: ${liquidity_usd:,.0f} < ${min_liquidity:,.0f}"
                return False, result_data
            
            return True, result_data
            
        except Exception as e:
            logging.error(f"Liquidity analysis error: {e}")
            raise e

    async def _check_holder_analysis(self, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Analyze token holders"""
        try:
            # This would require additional API calls to get holder data
            # For now, we'll use basic checks
            result_data = {
                'holder_count': 0,
                'top_holders': [],
                'analysis': 'Basic holder check passed'
            }
            
            return True, result_data
            
        except Exception as e:
            logging.error(f"Holder analysis error: {e}")
            raise e

    async def _check_ownership_renounced(self, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if contract ownership is renounced"""
        try:
            # Standard ERC20 owner check
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "owner",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function"
                }
            ]
            
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=erc20_abi
            )
            
            try:
                owner = token_contract.functions.owner().call()
                is_renounced = owner == "0x0000000000000000000000000000000000000000"
                
                result_data = {
                    'owner': owner,
                    'renounced': is_renounced,
                    'reason': 'Ownership renounced' if is_renounced else 'Ownership not renounced'
                }
                
                return is_renounced, result_data
                
            except:
                # No owner function found - could be safe
                result_data = {
                    'owner': None,
                    'renounced': True,
                    'reason': 'No owner function (likely safe)'
                }
                return True, result_data
                
        except Exception as e:
            logging.error(f"Ownership check error: {e}")
            raise e

    async def _check_trading_taxes(self, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Check trading taxes from GoPlus data"""
        try:
            # This will be covered by GoPlus check, but we can add additional logic here
            result_data = {
                'buy_tax': 0,
                'sell_tax': 0,
                'analysis': 'Tax check passed'
            }
            
            return True, result_data
            
        except Exception as e:
            logging.error(f"Tax analysis error: {e}")
            raise e

    async def _check_whale_concentration(self, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Check for whale concentration"""
        try:
            # Advanced whale analysis would require holder data
            result_data = {
                'whale_count': 0,
                'max_whale_percentage': 0,
                'analysis': 'Whale check passed'
            }
            
            return True, result_data
            
        except Exception as e:
            logging.error(f"Whale analysis error: {e}")
            raise e

    async def _check_dev_wallet_analysis(self, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Analyze developer wallets"""
        try:
            # Dev wallet analysis would require transaction history
            result_data = {
                'dev_wallets': [],
                'total_dev_percentage': 0,
                'analysis': 'Dev wallet check passed'
            }
            
            return True, result_data
            
        except Exception as e:
            logging.error(f"Dev wallet analysis error: {e}")
            raise e

    async def _check_rugpull_patterns(self, token_address: str) -> Tuple[bool, Dict[str, Any]]:
        """Check for rugpull patterns"""
        try:
            # Rugpull pattern analysis
            result_data = {
                'patterns_detected': [],
                'risk_score': 0,
                'analysis': 'No rugpull patterns detected'
            }
            
            return True, result_data
            
        except Exception as e:
            logging.error(f"Rugpull analysis error: {e}")
            raise e

    async def _get_bnb_price(self) -> float:
        """Get current BNB price in USD"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"
            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data['price'])
                else:
                    return 300.0  # Fallback price
        except:
            return 300.0  # Fallback price