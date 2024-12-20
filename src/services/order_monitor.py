# File: src/services/order_monitor.py

"""
Order monitoring service for tracking and managing trading orders.
Provides real-time monitoring of order status, position tracking, and risk management.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List
import logging
import asyncio
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus, OrderStatus

from utils.logger import setup_logger

logger = setup_logger(name="order_monitor")

@dataclass
class OrderMonitor:
    """
    Service for monitoring order status and managing active trades.
    
    Attributes:
        client (TradingClient): Alpaca trading client instance
        check_interval (int): Seconds between order status checks
        active_orders (Dict[str, dict]): Dictionary of currently active orders
        _running (bool): Internal flag for monitoring loop control
    """
    
    client: TradingClient
    check_interval: int = 60  # Seconds between order checks
    
    def __init__(self, client: TradingClient, check_interval: int = 60):
        """
        Initialize the OrderMonitor service.
        
        Args:
            client: Initialized Alpaca trading client
            check_interval: Time between order checks in seconds
        """
        self.client = client
        self.check_interval = check_interval
        self.active_orders: Dict[str, dict] = {}
        self._running = False
    
    async def start_monitoring(self):
        """
        Start the asynchronous order monitoring loop.
        Continuously checks order status at specified intervals.
        """
        self._running = True
        logger.info("Order monitoring started")
        while self._running:
            try:
                await self._check_orders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in order monitoring loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop the order monitoring loop."""
        self._running = False
        logger.info("Order monitoring stopped")
    
    async def _check_orders(self):
        """
        Check status of all active orders and process updates.
        Retrieves current orders and compares with previously active orders.
        """
        try:
            today = datetime.now()
            orders_request = GetOrdersRequest(
                status=QueryOrderStatus.OPEN,
                after=today.strftime('%Y-%m-%d')
            )
            orders = self.client.get_orders(orders_request)
            
            # Update active orders
            current_orders = {order.id: order for order in orders}
            
            # Check for filled or cancelled orders
            for order_id, prev_order in self.active_orders.items():
                if order_id not in current_orders:
                    try:
                        order = self.client.get_order_by_id(order_id)
                        await self._handle_order_update(order)
                    except Exception as e:
                        logger.error(f"Error getting order {order_id}: {str(e)}")
            
            self.active_orders = current_orders
            logger.debug(f"Active orders updated. Count: {len(self.active_orders)}")
            
        except Exception as e:
            logger.error(f"Error checking orders: {str(e)}")
    
    async def _handle_order_update(self, order):
        """
        Handle updates for filled or cancelled orders.
        
        Args:
            order: Alpaca order object with updated status
        """
        try:
            if order.status == OrderStatus.FILLED:
                await self._handle_filled_order(order)
            elif order.status in [OrderStatus.CANCELED, OrderStatus.EXPIRED]:
                await self._handle_cancelled_order(order)
        except Exception as e:
            logger.error(f"Error handling order update for {order.id}: {str(e)}")
    
    async def _handle_filled_order(self, order):
        """
        Process filled orders and place associated risk management orders.
        
        Args:
            order: Filled order object from Alpaca
        """
        try:
            fill_price = Decimal(str(order.filled_avg_price))
            filled_qty = Decimal(str(order.filled_qty))
            total_value = fill_price * filled_qty
            
            logger.info(
                f"Order filled - Symbol: {order.symbol} | Side: {order.side} | "
                f"Qty: {filled_qty} | Price: ${fill_price} | "
                f"Total: ${total_value:.2f}"
            )
            
            await self._place_risk_management_orders(order)
            
        except Exception as e:
            logger.error(f"Error handling filled order {order.id}: {str(e)}")
    
    async def _handle_cancelled_order(self, order):
        """
        Process cancelled or expired orders.
        
        Args:
            order: Cancelled order object from Alpaca
        """
        logger.info(
            f"Order cancelled/expired - ID: {order.id} | "
            f"Symbol: {order.symbol} | Type: {order.type}"
        )
        
    async def _place_risk_management_orders(self, filled_order):
        """
        Place stop loss and take profit orders for filled positions.
        
        Args:
            filled_order: Order object for filled position
        """
        # TODO: Implement based on your risk management strategy
        pass

    async def get_active_positions_and_orders(self) -> Dict[str, List[dict]]:
        """Get current active positions and orders with detailed status."""
        try:
            # Get positions
            positions = self.client.get_all_positions()
            position_data = [
                {
                    'symbol': pos.symbol,
                    'qty': pos.qty,
                    'entry_price': pos.avg_entry_price,
                    'current_price': pos.current_price,
                    'unrealized_pl': pos.unrealized_pl,
                    'unrealized_plpc': pos.unrealized_plpc,
                    'market_value': pos.market_value,
                    'cost_basis': pos.cost_basis
                }
                for pos in positions
            ]
            
            # Get orders
            orders_request = GetOrdersRequest(
                status=QueryOrderStatus.OPEN,
                after=datetime.now().strftime('%Y-%m-%d')
            )
            orders = self.client.get_orders(orders_request)
            order_data = [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'type': order.type,
                    'qty': order.qty,
                    'filled_qty': order.filled_qty,
                    'limit_price': order.limit_price,
                    'stop_price': order.stop_price,
                    'status': order.status,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at
                }
                for order in orders
            ]
            
            logger.info(f"Active positions: {len(position_data)} | Open orders: {len(order_data)}")
            return {
                'positions': position_data,
                'orders': order_data
            }
                
        except Exception as e:
            logger.error(f"Error getting positions and orders: {str(e)}")
            return {'positions': [], 'orders': []}
    
    async def get_active_positions(self) -> List[dict]:
        """
        Retrieve current active positions with their status.
        
        Returns:
            List of dictionaries containing position information
        """
        try:
            positions = self.client.get_all_positions()
            position_data = [
                {
                    'symbol': pos.symbol,
                    'qty': pos.qty,
                    'entry_price': pos.avg_entry_price,
                    'current_price': pos.current_price,
                    'unrealized_pl': pos.unrealized_pl,
                    'unrealized_plpc': pos.unrealized_plpc,
                    'market_value': pos.market_value,
                    'cost_basis': pos.cost_basis
                }
                for pos in positions
            ]
            logger.info(f"Active positions count: {len(position_data)}")
            return position_data
            
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []