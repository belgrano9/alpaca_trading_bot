from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import StopLimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from utils.logger import setup_logger

logger = setup_logger(
    name="alpaca_service",
    log_file=Path("logs/alpaca.log")
)
@dataclass
class AlpacaConfig:
    api_key: str
    secret_key: str
    paper: bool = True
    base_url: Optional[str] = None

class TradingService:
    def __init__(self, config: AlpacaConfig):
        self.client = TradingClient(
            api_key=config.api_key,
            secret_key=config.secret_key,
            paper=config.paper,
            url_override=config.base_url
        )
        
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information and available buying power."""
        account = self.client.get_account()
        return {
                'buying_power': Decimal(account.buying_power),
                'cash': Decimal(account.cash),
                'portfolio_value': Decimal(account.portfolio_value)
            }
        
        
    def place_stop_limit_order(
    self,
    symbol: str,
    qty: int,
    limit_price: Decimal,
    stop_price: Decimal,
    side: str = "buy",
    time_in_force: str = "gtc"
) -> Dict[str, Any]:
        """
        Places a stop order to buy or sell a security when it reaches a specified price.

        This order is triggered when the market price reaches the stop price.
        It then becomes a market order to be executed at the best available price.
        Used to limit losses (stop-loss) or enter positions at breakouts (stop-buy).

        Args:
            symbol: Stock symbol
            qty: Number of shares
            limit_price: Maximum price to pay (for buy) or minimum price to sell
            stop_price: Price that triggers the limit order
            side: 'buy' or 'sell'
            time_in_force: Order duration ('gtc', 'day', etc.)
            
        Returns:
            Dict containing order details
        
        Raises:
            ValueError: If invalid parameters provided
            RuntimeError: If order placement fails
        """
        try:
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            order_tif = TimeInForce.GTC if time_in_force.lower() == "gtc" else TimeInForce.DAY
            
            # Round prices to 2 decimal places
            rounded_limit_price = float(round(limit_price, 2))
            rounded_stop_price = float(round(stop_price, 2))
            
            req = StopLimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=order_tif,
                limit_price=rounded_limit_price,
                stop_price=rounded_stop_price
            )
            
            response = self.client.submit_order(req)
            logger.info(f"Placed {side} stop-limit order for {qty} shares of {symbol}")
            return response
            
        except ValueError as e:
            logger.error(f"Invalid order parameters: {str(e)}")
            raise ValueError(f"Invalid order parameters: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            raise RuntimeError(f"Order placement failed: {str(e)}")