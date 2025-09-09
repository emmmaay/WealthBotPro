#!/usr/bin/env python3
"""
Robust Blockchain Interface with Multiple RPC Fallbacks
Handles all blockchain interactions with perfect error handling
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound, TimeExhausted
from eth_account import Account
from colorama import Fore, Style
import json
import os # Added import for os.getenv

class BlockchainInterface:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.w3 = None
        self.current_rpc_index = 0
        self.rpc_endpoints = config['blockchain']['rpc_endpoints']
        self.factory_address = config['blockchain']['pancakeswap_factory']
        self.router_address = config['blockchain']['pancakeswap_router']
        self.wbnb_address = config['blockchain']['wbnb_address']
        self.busd_address = config['blockchain']['busd_address']

        # Contract ABIs
        self.factory_abi = self._get_factory_abi()
        self.router_abi = self._get_router_abi()
        self.erc20_abi = self._get_erc20_abi()
        self.pair_abi = self._get_pair_abi()

        # Initialize connection
        self.initialize_web3_connection()

        # Account management
        self.account = None
        self.wallet_address = None

    def initialize_web3_connection(self) -> bool:
        """Initialize Web3 connection with automatic fallback"""
        for attempt in range(3):  # Try 3 times
            for i, rpc_url in enumerate(self.rpc_endpoints):
                try:
                    logging.info(f"Attempting to connect to RPC {i+1}: {rpc_url}")

                    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

                    # Test connection
                    if w3.is_connected():
                        # Verify we can get latest block
                        latest_block = w3.eth.block_number
                        if latest_block > 0:
                            self.w3 = w3
                            self.current_rpc_index = i
                            logging.info(f"{Fore.GREEN}✅ Connected to BSC via RPC {i+1} (Block: {latest_block}){Style.RESET_ALL}")
                            return True

                except Exception as e:
                    logging.warning(f"RPC {i+1} failed: {e}")
                    continue

            if attempt < 2:
                logging.warning(f"All RPCs failed, retrying in {attempt + 1} seconds...")
                time.sleep(attempt + 1)

        logging.error("Failed to connect to any RPC endpoint after 3 attempts")
        return False

    def setup_account(self, private_key: str) -> bool:
        """Setup account from private key"""
        try:
            if not self.w3:
                logging.error("Web3 not initialized")
                return False

            # Clean and validate private key
            clean_key = private_key.strip()
            if clean_key.startswith('0x'):
                clean_key = clean_key[2:]

            if len(clean_key) != 64:
                logging.error(f"Private key must be 64 hexadecimal characters, got {len(clean_key)}")
                return False

            try:
                # Validate hexadecimal format
                int(clean_key, 16)
                # Add 0x prefix back for Account.from_key
                formatted_key = '0x' + clean_key
                # Create account
                self.account = Account.from_key(formatted_key)
                self.wallet_address = self.account.address

                logging.info(f"{Fore.GREEN}🔑 Wallet loaded: {self.wallet_address}{Style.RESET_ALL}")
                return True

            except ValueError:
                logging.error("Private key contains invalid hexadecimal characters")
                return False

        except Exception as e:
            logging.error(f"Failed to setup account: {e}")
            return False

    async def get_wallet_balance(self, token_address: Optional[str] = None) -> float:
        """Get wallet balance for BNB or specific token"""
        try:
            if not self.wallet_address:
                return 0.0

            if token_address is None or token_address.lower() == self.wbnb_address.lower():
                # Get BNB balance
                balance_wei = self.w3.eth.get_balance(self.wallet_address)
                return balance_wei / (10**18)
            else:
                # Get token balance
                token_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=self.erc20_abi
                )

                balance = token_contract.functions.balanceOf(self.wallet_address).call()
                decimals = token_contract.functions.decimals().call()
                return balance / (10**decimals)

        except Exception as e:
            logging.error(f"Error getting wallet balance: {e}")
            return 0.0

    async def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """Get comprehensive token information"""
        try:
            # Ensure address is properly formatted
            if not token_address.startswith('0x'):
                token_address = '0x' + token_address

            # Validate hex format
            try:
                int(token_address[2:], 16)
            except ValueError:
                logging.error(f"Invalid token address format: {token_address}")
                return self._get_default_token_info(token_address)

            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=self.erc20_abi
            )

            # Get basic token info
            try:
                name = token_contract.functions.name().call()
            except:
                name = "Unknown"

            try:
                symbol = token_contract.functions.symbol().call()
            except:
                symbol = "UNKNOWN"

            try:
                decimals = token_contract.functions.decimals().call()
            except:
                decimals = 18

            try:
                total_supply = token_contract.functions.totalSupply().call()
            except:
                total_supply = 0

            return {
                'address': token_address,
                'name': name,
                'symbol': symbol,
                'decimals': decimals,
                'total_supply': total_supply,
                'total_supply_formatted': total_supply / (10**decimals) if total_supply > 0 else 0
            }

        except Exception as e:
            logging.error(f"Error getting token info for {token_address}: {e}")
            return self._get_default_token_info(token_address)

    def _get_default_token_info(self, token_address: str) -> Dict[str, Any]:
        """Return default token info structure"""
        return {
            'address': token_address,
            'name': 'Unknown',
            'symbol': 'UNKNOWN',
            'decimals': 18,
            'total_supply': 0,
            'total_supply_formatted': 0
        }

    async def get_pair_info(self, pair_address: str) -> Dict[str, Any]:
        """Get detailed pair information"""
        try:
            # Ensure address is properly formatted
            if not pair_address.startswith('0x'):
                pair_address = '0x' + pair_address

            # Validate hex format
            try:
                int(pair_address[2:], 16)
            except ValueError:
                logging.error(f"Invalid pair address format: {pair_address}")
                return {}

            pair_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=self.pair_abi
            )

            # Get pair data
            token0 = pair_contract.functions.token0().call()
            token1 = pair_contract.functions.token1().call()
            reserves = pair_contract.functions.getReserves().call()

            # Get token info for both tokens
            token0_info = await self.get_token_info(token0)
            token1_info = await self.get_token_info(token1)

            return {
                'pair_address': pair_address,
                'token0': {
                    'address': token0,
                    'info': token0_info,
                    'reserve': reserves[0],
                    'reserve_formatted': reserves[0] / (10**token0_info['decimals'])
                },
                'token1': {
                    'address': token1,
                    'info': token1_info,
                    'reserve': reserves[1],
                    'reserve_formatted': reserves[1] / (10**token1_info['decimals'])
                },
                'last_update': reserves[2],
                'creation_time': int(time.time())  # This would need to be fetched from creation event
            }

        except Exception as e:
            logging.error(f"Error getting pair info for {pair_address}: {e}")
            return {}

    async def calculate_token_price_bnb(self, token_address: str, pair_address: str) -> float:
        """Calculate token price in BNB"""
        try:
            pair_info = await self.get_pair_info(pair_address)

            if not pair_info:
                return 0.0

            # Determine which token is WBNB
            wbnb_checksum = Web3.to_checksum_address(self.wbnb_address)
            token0_address = Web3.to_checksum_address(pair_info['token0']['address'])
            token1_address = Web3.to_checksum_address(pair_info['token1']['address'])

            if token0_address == wbnb_checksum:
                # Token1 is our target token, Token0 is WBNB
                bnb_reserve = pair_info['token0']['reserve_formatted']
                token_reserve = pair_info['token1']['reserve_formatted']
            elif token1_address == wbnb_checksum:
                # Token0 is our target token, Token1 is WBNB
                bnb_reserve = pair_info['token1']['reserve_formatted']
                token_reserve = pair_info['token0']['reserve_formatted']
            else:
                logging.warning("Neither token in pair is WBNB")
                return 0.0

            if token_reserve == 0:
                return 0.0

            # Price = BNB Reserve / Token Reserve
            price_bnb = bnb_reserve / token_reserve
            return price_bnb

        except Exception as e:
            logging.error(f"Error calculating token price: {e}")
            return 0.0

    async def estimate_gas_price(self) -> int:
        """Estimate optimal gas price with fallback"""
        try:
            # Get current gas price
            current_gas_price = self.w3.eth.gas_price

            # Apply multiplier for faster execution
            multiplier = self.config['security'].get('gas_multiplier', 1.2)
            optimal_gas_price = int(current_gas_price * multiplier)

            # Cap at maximum
            max_gas_price = int(self.config['security'].get('max_gas_price_gwei', 20) * 10**9)
            final_gas_price = min(optimal_gas_price, max_gas_price)

            logging.info(f"Gas price: {final_gas_price / 10**9:.2f} gwei")
            return final_gas_price

        except Exception as e:
            logging.error(f"Error estimating gas price: {e}")
            return int(5 * 10**9)  # 5 gwei fallback

    async def execute_buy_transaction(self, token_address: str, bnb_amount: float, slippage: float = 15) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute buy transaction with perfect error handling"""
        try:
            if not self.account or not self.wallet_address:
                return False, "Account not setup", {}

            token_address = Web3.to_checksum_address(token_address)
            router_address = Web3.to_checksum_address(self.router_address)

            # Get router contract
            router_contract = self.w3.eth.contract(address=router_address, abi=self.router_abi)

            # Calculate amounts
            bnb_amount_wei = int(bnb_amount * 10**18)
            path = [self.wbnb_address, token_address]

            # Get expected output amount
            amounts_out = router_contract.functions.getAmountsOut(bnb_amount_wei, path).call()
            expected_tokens = amounts_out[1]

            # Calculate minimum tokens with slippage
            min_tokens_out = int(expected_tokens * (100 - slippage) / 100)

            # Get current gas price
            gas_price = await self.estimate_gas_price()

            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)

            # Build transaction
            deadline = int(time.time()) + 300  # 5 minutes

            transaction = router_contract.functions.swapExactETHForTokens(
                min_tokens_out,
                path,
                self.wallet_address,
                deadline
            ).build_transaction({
                'from': self.wallet_address,
                'value': bnb_amount_wei,
                'gasPrice': gas_price,
                'gas': 350000,  # Conservative gas limit
                'nonce': nonce
            })

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()

            logging.info(f"{Fore.GREEN}📡 Buy transaction sent: {tx_hash_hex}{Style.RESET_ALL}")

            # Wait for confirmation with timeout
            try:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                if receipt.status == 1:
                    # Success
                    gas_used = receipt.gasUsed
                    gas_cost_bnb = (gas_used * gas_price) / 10**18

                    result_data = {
                        'transaction_hash': tx_hash_hex,
                        'gas_used': gas_used,
                        'gas_cost_bnb': gas_cost_bnb,
                        'bnb_spent': bnb_amount,
                        'expected_tokens': expected_tokens,
                        'min_tokens_out': min_tokens_out,
                        'block_number': receipt.blockNumber
                    }

                    logging.info(f"{Fore.GREEN}✅ Buy transaction confirmed! Gas: {gas_cost_bnb:.6f} BNB{Style.RESET_ALL}")
                    return True, "Transaction successful", result_data
                else:
                    # Failed
                    logging.error(f"{Fore.RED}❌ Buy transaction failed{Style.RESET_ALL}")
                    return False, "Transaction failed", {'transaction_hash': tx_hash_hex}

            except TimeExhausted:
                logging.error(f"{Fore.RED}⏰ Buy transaction timeout: {tx_hash_hex}{Style.RESET_ALL}")
                return False, "Transaction timeout", {'transaction_hash': tx_hash_hex}

        except Exception as e:
            logging.error(f"Buy transaction error: {e}")
            return False, f"Transaction error: {str(e)}", {}

    async def execute_sell_transaction(self, token_address: str, token_amount: float, slippage: float = 15) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute sell transaction with perfect error handling"""
        try:
            if not self.account or not self.wallet_address:
                return False, "Account not setup", {}

            token_address = Web3.to_checksum_address(token_address)
            router_address = Web3.to_checksum_address(self.router_address)

            # Get token info for decimals
            token_info = await self.get_token_info(token_address)
            token_amount_wei = int(token_amount * 10**token_info['decimals'])

            # Get contracts
            router_contract = self.w3.eth.contract(address=router_address, abi=self.router_abi)
            token_contract = self.w3.eth.contract(address=token_address, abi=self.erc20_abi)

            # Check and approve if needed
            allowance = token_contract.functions.allowance(self.wallet_address, router_address).call()
            if allowance < token_amount_wei:
                # Need to approve
                approve_success = await self._approve_token(token_address, router_address, token_amount_wei * 2)
                if not approve_success:
                    return False, "Failed to approve token", {}

            # Calculate amounts
            path = [token_address, self.wbnb_address]
            amounts_out = router_contract.functions.getAmountsOut(token_amount_wei, path).call()
            expected_bnb = amounts_out[1]

            # Calculate minimum BNB with slippage
            min_bnb_out = int(expected_bnb * (100 - slippage) / 100)

            # Get current gas price and nonce
            gas_price = await self.estimate_gas_price()
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)

            # Build transaction
            deadline = int(time.time()) + 300

            transaction = router_contract.functions.swapExactTokensForETH(
                token_amount_wei,
                min_bnb_out,
                path,
                self.wallet_address,
                deadline
            ).build_transaction({
                'from': self.wallet_address,
                'gasPrice': gas_price,
                'gas': 350000,
                'nonce': nonce
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()

            logging.info(f"{Fore.YELLOW}📤 Sell transaction sent: {tx_hash_hex}{Style.RESET_ALL}")

            # Wait for confirmation
            try:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                if receipt.status == 1:
                    gas_used = receipt.gasUsed
                    gas_cost_bnb = (gas_used * gas_price) / 10**18

                    result_data = {
                        'transaction_hash': tx_hash_hex,
                        'gas_used': gas_used,
                        'gas_cost_bnb': gas_cost_bnb,
                        'tokens_sold': token_amount,
                        'expected_bnb': expected_bnb / 10**18,
                        'min_bnb_out': min_bnb_out / 10**18,
                        'block_number': receipt.blockNumber
                    }

                    logging.info(f"{Fore.GREEN}✅ Sell transaction confirmed! Gas: {gas_cost_bnb:.6f} BNB{Style.RESET_ALL}")
                    return True, "Sell successful", result_data
                else:
                    logging.error(f"{Fore.RED}❌ Sell transaction failed{Style.RESET_ALL}")
                    return False, "Sell transaction failed", {'transaction_hash': tx_hash_hex}

            except TimeExhausted:
                logging.error(f"{Fore.RED}⏰ Sell transaction timeout: {tx_hash_hex}{Style.RESET_ALL}")
                return False, "Sell transaction timeout", {'transaction_hash': tx_hash_hex}

        except Exception as e:
            logging.error(f"Sell transaction error: {e}")
            return False, f"Sell error: {str(e)}", {}

    async def _approve_token(self, token_address: str, spender_address: str, amount: int) -> bool:
        """Approve token spending"""
        try:
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=self.erc20_abi
            )

            gas_price = await self.estimate_gas_price()
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)

            transaction = token_contract.functions.approve(
                Web3.to_checksum_address(spender_address),
                amount
            ).build_transaction({
                'from': self.wallet_address,
                'gasPrice': gas_price,
                'gas': 100000,
                'nonce': nonce
            })

            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            return receipt.status == 1

        except Exception as e:
            logging.error(f"Approval error: {e}")
            return False

    def _get_factory_abi(self) -> List[Dict]:
        """Get PancakeSwap Factory ABI"""
        return [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "token0", "type": "address"},
                    {"indexed": True, "name": "token1", "type": "address"},
                    {"indexed": False, "name": "pair", "type": "address"},
                    {"indexed": False, "name": "", "type": "uint256"}
                ],
                "name": "PairCreated",
                "type": "event"
            }
        ]

    def _get_router_abi(self) -> List[Dict]:
        """Get PancakeSwap Router ABI"""
        return [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsOut",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactETHForTokens",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactTokensForETH",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    def _get_erc20_abi(self) -> List[Dict]:
        """Get standard ERC20 ABI"""
        return [
            {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "remaining", "type": "uint256"}], "type": "function"}
        ]

    def _get_pair_abi(self) -> List[Dict]:
        """Get Uniswap V2 Pair ABI"""
        return [
            {"constant": True, "inputs": [], "name": "getReserves", "outputs": [{"name": "_reserve0", "type": "uint112"}, {"name": "_reserve1", "type": "uint112"}, {"name": "_blockTimestampLast", "type": "uint32"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "token0", "outputs": [{"name": "", "type": "address"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "token1", "outputs": [{"name": "", "type": "address"}], "type": "function"}
        ]