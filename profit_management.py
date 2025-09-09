#!/usr/bin/env python3
"""
Intelligent Profit Management System with Compound Growth
Manages positions and executes smart selling strategies
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from colorama import Fore, Style
import json

@dataclass
class Position:
    """Represents a trading position"""
    token_address: str
    token_symbol: str
    entry_price_bnb: float
    tokens_owned: float
    initial_investment_bnb: float
    entry_time: int
    pair_address: str
    transaction_hash: str
    
    # Profit tracking
    current_price_bnb: float = 0.0
    current_value_bnb: float = 0.0
    profit_loss_bnb: float = 0.0
    profit_loss_percentage: float = 0.0
    peak_price_bnb: float = 0.0
    peak_value_bnb: float = 0.0
    
    # Selling history
    sold_amounts: List[Dict[str, Any]] = None
    remaining_tokens: float = 0.0
    
    def __post_init__(self):
        if self.sold_amounts is None:
            self.sold_amounts = []
        if self.remaining_tokens == 0.0:
            self.remaining_tokens = self.tokens_owned
        if self.peak_price_bnb == 0.0:
            self.peak_price_bnb = self.entry_price_bnb

class ProfitManager:
    def __init__(self, config: Dict[str, Any], blockchain_interface, notifier):
        self.config = config
        self.blockchain = blockchain_interface
        self.notifier = notifier
        self.positions: Dict[str, Position] = {}
        self.profit_config = config['profit_management']
        self.trading_config = config['trading']
        
        # Profit tracking
        self.total_invested_bnb = 0.0
        self.total_profit_bnb = 0.0
        self.total_fees_bnb = 0.0
        self.successful_trades = 0
        self.failed_trades = 0
        
        # Load existing positions if any
        self.load_positions()

    def add_position(self, token_address: str, token_symbol: str, entry_price_bnb: float, 
                    tokens_owned: float, investment_bnb: float, pair_address: str, 
                    transaction_hash: str) -> None:
        """Add a new position to the portfolio"""
        try:
            position = Position(
                token_address=token_address,
                token_symbol=token_symbol,
                entry_price_bnb=entry_price_bnb,
                tokens_owned=tokens_owned,
                initial_investment_bnb=investment_bnb,
                entry_time=int(time.time()),
                pair_address=pair_address,
                transaction_hash=transaction_hash
            )
            
            self.positions[token_address] = position
            self.total_invested_bnb += investment_bnb
            
            logging.info(f"{Fore.GREEN}📈 Added position: {token_symbol} ({investment_bnb:.6f} BNB){Style.RESET_ALL}")
            self.save_positions()
            
        except Exception as e:
            logging.error(f"Error adding position: {e}")

    async def update_position_prices(self) -> None:
        """Update current prices for all positions"""
        try:
            for token_address, position in self.positions.items():
                try:
                    # Get current price
                    current_price = await self.blockchain.calculate_token_price_bnb(
                        token_address, position.pair_address
                    )
                    
                    if current_price > 0:
                        position.current_price_bnb = current_price
                        position.current_value_bnb = position.remaining_tokens * current_price
                        position.profit_loss_bnb = position.current_value_bnb - position.initial_investment_bnb
                        position.profit_loss_percentage = (position.profit_loss_bnb / position.initial_investment_bnb) * 100
                        
                        # Update peak price for trailing stop
                        if current_price > position.peak_price_bnb:
                            position.peak_price_bnb = current_price
                            position.peak_value_bnb = position.remaining_tokens * current_price
                        
                except Exception as e:
                    logging.warning(f"Error updating price for {position.token_symbol}: {e}")
                    
        except Exception as e:
            logging.error(f"Error updating position prices: {e}")

    async def check_profit_opportunities(self) -> None:
        """Check all positions for profit-taking opportunities"""
        try:
            positions_to_process = list(self.positions.items())
            
            for token_address, position in positions_to_process:
                if position.remaining_tokens <= 0:
                    continue
                
                try:
                    # Check take profit levels
                    await self._check_take_profit_levels(position)
                    
                    # Check trailing stop loss
                    await self._check_trailing_stop_loss(position)
                    
                    # Check maximum holding time
                    await self._check_max_holding_time(position)
                    
                except Exception as e:
                    logging.error(f"Error checking profit opportunities for {position.token_symbol}: {e}")
                    
        except Exception as e:
            logging.error(f"Error checking profit opportunities: {e}")

    async def _check_take_profit_levels(self, position: Position) -> None:
        """Check and execute take profit levels"""
        try:
            current_multiplier = position.current_price_bnb / position.entry_price_bnb
            
            # Take Profit 1
            tp1_multiplier = self.profit_config['take_profit_1']['multiplier']
            tp1_percentage = self.profit_config['take_profit_1']['percentage']
            
            if (current_multiplier >= tp1_multiplier and 
                not self._has_sold_at_level(position, 'tp1')):
                
                await self._execute_partial_sell(position, tp1_percentage, 'tp1', tp1_multiplier)
            
            # Take Profit 2
            tp2_multiplier = self.profit_config['take_profit_2']['multiplier']
            tp2_percentage = self.profit_config['take_profit_2']['percentage']
            
            if (current_multiplier >= tp2_multiplier and 
                not self._has_sold_at_level(position, 'tp2')):
                
                await self._execute_partial_sell(position, tp2_percentage, 'tp2', tp2_multiplier)
            
            # Take Profit 3
            tp3_multiplier = self.profit_config['take_profit_3']['multiplier']
            tp3_percentage = self.profit_config['take_profit_3']['percentage']
            
            if (current_multiplier >= tp3_multiplier and 
                not self._has_sold_at_level(position, 'tp3')):
                
                await self._execute_partial_sell(position, tp3_percentage, 'tp3', tp3_multiplier)
                
        except Exception as e:
            logging.error(f"Error checking take profit levels: {e}")

    async def _check_trailing_stop_loss(self, position: Position) -> None:
        """Check trailing stop loss"""
        try:
            if position.peak_price_bnb <= position.entry_price_bnb:
                return  # No profit to protect
            
            # Calculate stop loss price
            stop_loss_percentage = self.profit_config['trailing_stop_loss_percentage']
            stop_loss_price = position.peak_price_bnb * (1 - stop_loss_percentage / 100)
            
            if position.current_price_bnb <= stop_loss_price:
                # Trigger trailing stop loss - sell all remaining tokens
                logging.warning(f"{Fore.YELLOW}🛑 Trailing stop loss triggered for {position.token_symbol}{Style.RESET_ALL}")
                await self._execute_full_sell(position, 'trailing_stop_loss')
                
        except Exception as e:
            logging.error(f"Error checking trailing stop loss: {e}")

    async def _check_max_holding_time(self, position: Position) -> None:
        """Check maximum holding time"""
        try:
            max_holding_hours = self.profit_config['max_holding_time_hours']
            current_time = int(time.time())
            holding_time_hours = (current_time - position.entry_time) / 3600
            
            if holding_time_hours >= max_holding_hours:
                logging.warning(f"{Fore.YELLOW}⏰ Max holding time reached for {position.token_symbol}{Style.RESET_ALL}")
                await self._execute_full_sell(position, 'max_holding_time')
                
        except Exception as e:
            logging.error(f"Error checking max holding time: {e}")

    async def _execute_partial_sell(self, position: Position, percentage: float, 
                                  level: str, multiplier: float) -> None:
        """Execute partial sell order"""
        try:
            sell_amount = position.remaining_tokens * (percentage / 100)
            
            if sell_amount <= 0:
                return
            
            logging.info(f"{Fore.YELLOW}💰 Executing {percentage}% sell for {position.token_symbol} at {multiplier}x{Style.RESET_ALL}")
            
            # Execute sell transaction
            success, message, result_data = await self.blockchain.execute_sell_transaction(
                position.token_address, sell_amount, self.trading_config['slippage_tolerance']
            )
            
            if success:
                # Update position
                bnb_received = result_data.get('expected_bnb', 0)
                gas_cost = result_data.get('gas_cost_bnb', 0)
                net_bnb = bnb_received - gas_cost
                
                # Record the sale
                sale_record = {
                    'level': level,
                    'multiplier': multiplier,
                    'percentage': percentage,
                    'tokens_sold': sell_amount,
                    'bnb_received': bnb_received,
                    'gas_cost': gas_cost,
                    'net_bnb': net_bnb,
                    'timestamp': int(time.time()),
                    'transaction_hash': result_data.get('transaction_hash', '')
                }
                
                position.sold_amounts.append(sale_record)
                position.remaining_tokens -= sell_amount
                
                # Update totals
                self.total_profit_bnb += net_bnb
                self.total_fees_bnb += gas_cost
                
                # Check if this qualifies for compound trading
                if self.trading_config.get('auto_compound', False):
                    await self._check_compound_opportunity(net_bnb)
                
                # Notify
                await self.notifier.notify_profit_taken(
                    position.token_symbol, percentage, multiplier, net_bnb, position.transaction_hash
                )
                
                logging.info(f"{Fore.GREEN}✅ Sold {percentage}% of {position.token_symbol} for {net_bnb:.6f} BNB{Style.RESET_ALL}")
                
                # Remove position if fully sold
                if position.remaining_tokens <= 0.001:  # Dust threshold
                    await self._close_position(position.token_address)
                
                self.save_positions()
                
            else:
                logging.error(f"{Fore.RED}❌ Failed to sell {position.token_symbol}: {message}{Style.RESET_ALL}")
                await self.notifier.notify_sell_failed(position.token_symbol, message)
                
        except Exception as e:
            logging.error(f"Error executing partial sell: {e}")

    async def _execute_full_sell(self, position: Position, reason: str) -> None:
        """Execute full sell order"""
        try:
            if position.remaining_tokens <= 0:
                return
            
            logging.info(f"{Fore.YELLOW}🔄 Executing full sell for {position.token_symbol} ({reason}){Style.RESET_ALL}")
            
            # Execute sell transaction
            success, message, result_data = await self.blockchain.execute_sell_transaction(
                position.token_address, position.remaining_tokens, self.trading_config['slippage_tolerance']
            )
            
            if success:
                # Update position
                bnb_received = result_data.get('expected_bnb', 0)
                gas_cost = result_data.get('gas_cost_bnb', 0)
                net_bnb = bnb_received - gas_cost
                
                # Record the sale
                sale_record = {
                    'level': 'full_sell',
                    'reason': reason,
                    'percentage': 100,
                    'tokens_sold': position.remaining_tokens,
                    'bnb_received': bnb_received,
                    'gas_cost': gas_cost,
                    'net_bnb': net_bnb,
                    'timestamp': int(time.time()),
                    'transaction_hash': result_data.get('transaction_hash', '')
                }
                
                position.sold_amounts.append(sale_record)
                position.remaining_tokens = 0
                
                # Update totals
                self.total_profit_bnb += net_bnb
                self.total_fees_bnb += gas_cost
                
                # Determine if this was a successful trade
                total_profit = sum(sale['net_bnb'] for sale in position.sold_amounts) - position.initial_investment_bnb
                
                if total_profit > 0:
                    self.successful_trades += 1
                else:
                    self.failed_trades += 1
                
                # Check for compound opportunity
                if self.trading_config.get('auto_compound', False):
                    await self._check_compound_opportunity(net_bnb)
                
                # Notify
                await self.notifier.notify_position_closed(
                    position.token_symbol, reason, net_bnb, total_profit, position.transaction_hash
                )
                
                logging.info(f"{Fore.GREEN}✅ Fully sold {position.token_symbol} for {net_bnb:.6f} BNB (Total P&L: {total_profit:.6f} BNB){Style.RESET_ALL}")
                
                # Close position
                await self._close_position(position.token_address)
                
            else:
                logging.error(f"{Fore.RED}❌ Failed to sell {position.token_symbol}: {message}{Style.RESET_ALL}")
                await self.notifier.notify_sell_failed(position.token_symbol, message)
                
        except Exception as e:
            logging.error(f"Error executing full sell: {e}")

    async def _check_compound_opportunity(self, bnb_amount: float) -> None:
        """Check if we should increase position sizes based on profits"""
        try:
            compound_threshold = self.trading_config.get('compound_threshold_bnb', 0.01)
            
            if bnb_amount >= compound_threshold:
                # Increase the buy amount for future trades
                current_buy_amount = self.trading_config['buy_amount_bnb']
                new_buy_amount = min(current_buy_amount * 1.5, bnb_amount * 0.8)  # Increase by 50% or use 80% of profit
                
                logging.info(f"{Fore.CYAN}📈 Compound growth: Increasing buy amount from {current_buy_amount:.6f} to {new_buy_amount:.6f} BNB{Style.RESET_ALL}")
                
                # Update config (this would be temporary for the session)
                self.trading_config['buy_amount_bnb'] = new_buy_amount
                
                await self.notifier.notify_compound_growth(current_buy_amount, new_buy_amount)
                
        except Exception as e:
            logging.error(f"Error checking compound opportunity: {e}")

    async def _close_position(self, token_address: str) -> None:
        """Close a position completely"""
        try:
            if token_address in self.positions:
                position = self.positions[token_address]
                logging.info(f"{Fore.BLUE}📊 Closing position: {position.token_symbol}{Style.RESET_ALL}")
                del self.positions[token_address]
                self.save_positions()
                
        except Exception as e:
            logging.error(f"Error closing position: {e}")

    def _has_sold_at_level(self, position: Position, level: str) -> bool:
        """Check if we've already sold at this profit level"""
        return any(sale['level'] == level for sale in position.sold_amounts)

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary"""
        try:
            total_current_value = sum(pos.current_value_bnb for pos in self.positions.values())
            total_unrealized_profit = sum(pos.profit_loss_bnb for pos in self.positions.values())
            
            win_rate = (self.successful_trades / (self.successful_trades + self.failed_trades) * 100 
                       if (self.successful_trades + self.failed_trades) > 0 else 0)
            
            summary = {
                'total_invested_bnb': self.total_invested_bnb,
                'total_current_value_bnb': total_current_value,
                'total_realized_profit_bnb': self.total_profit_bnb,
                'total_unrealized_profit_bnb': total_unrealized_profit,
                'total_fees_bnb': self.total_fees_bnb,
                'net_profit_bnb': self.total_profit_bnb - self.total_fees_bnb,
                'active_positions': len(self.positions),
                'successful_trades': self.successful_trades,
                'failed_trades': self.failed_trades,
                'win_rate_percentage': win_rate,
                'positions': {addr: asdict(pos) for addr, pos in self.positions.items()}
            }
            
            return summary
            
        except Exception as e:
            logging.error(f"Error getting portfolio summary: {e}")
            return {}

    def save_positions(self) -> None:
        """Save positions to file"""
        try:
            positions_data = {
                'positions': {addr: asdict(pos) for addr, pos in self.positions.items()},
                'totals': {
                    'total_invested_bnb': self.total_invested_bnb,
                    'total_profit_bnb': self.total_profit_bnb,
                    'total_fees_bnb': self.total_fees_bnb,
                    'successful_trades': self.successful_trades,
                    'failed_trades': self.failed_trades
                }
            }
            
            with open('positions.json', 'w') as f:
                json.dump(positions_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving positions: {e}")

    def load_positions(self) -> None:
        """Load positions from file"""
        try:
            try:
                with open('positions.json', 'r') as f:
                    data = json.load(f)
                
                # Load positions
                for addr, pos_data in data.get('positions', {}).items():
                    position = Position(**pos_data)
                    self.positions[addr] = position
                
                # Load totals
                totals = data.get('totals', {})
                self.total_invested_bnb = totals.get('total_invested_bnb', 0.0)
                self.total_profit_bnb = totals.get('total_profit_bnb', 0.0)
                self.total_fees_bnb = totals.get('total_fees_bnb', 0.0)
                self.successful_trades = totals.get('successful_trades', 0)
                self.failed_trades = totals.get('failed_trades', 0)
                
                logging.info(f"Loaded {len(self.positions)} existing positions")
                
            except FileNotFoundError:
                logging.info("No existing positions file found")
            except json.JSONDecodeError:
                logging.warning("Corrupted positions file, starting fresh")
                
        except Exception as e:
            logging.error(f"Error loading positions: {e}")