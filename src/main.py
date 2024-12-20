import typer
from pathlib import Path
from decimal import Decimal
import os
from typing import List, Optional

from services.alpaca_service import TradingService, AlpacaConfig
from services.signal_processor import process_trading_signals
from utils.logger import setup_logger
from utils.file_utils import get_latest_signals_file

app = typer.Typer()

logger = setup_logger(name="main",
                      log_file=Path("src/logs/main.log"))

def confirm_trade(signal, shares, account_value: Decimal) -> bool:
    """Get user confirmation for trade execution."""
    trade_value = signal.entry_price * Decimal(str(shares))
    print("\nTrade Details:")
    print(f"Symbol: {signal.symbol}")
    print(f"Type: {signal.signal_type}")
    print(f"Shares: {1}")
    print(f"Entry Price: ${round(signal.entry_price, 2)}")
    print(f"Stop Loss: ${round(signal.stop_loss, 2)}")
    print(f"Take Profit: ${round(signal.take_profit, 2)}")
    print(f"Trade Value: ${round(trade_value, 2)}")
    print(f"Account Value: ${round(account_value, 2)}")
    print(f"Position Size: {(trade_value/account_value * 100):.2f}%")
    
    return input("\nExecute trade? (Y/N): ").lower() == 'y'

@app.command()
def run(
    symbols: Optional[List[str]] = typer.Option(None, help="Stock symbols (e.g. AAPL MSFT)"),
    min_confidence: float = typer.Option(0.5, help="Minimum signal confidence"),
    min_risk_reward: float = typer.Option(1.5, help="Minimum risk/reward ratio"),
):
    """Execute trading strategy for specified symbols."""
    try:
        config = AlpacaConfig(
            api_key=os.getenv("API_KEY"),
            secret_key=os.getenv("SECRET_KEY"),
            paper=True
        )
        trading_service = TradingService(config)
        
        account_info = trading_service.get_account_info()
        account_value = account_info['portfolio_value']
        logger.info(f"Account value: ${account_value}")
        signals_dir = Path("C:/Users/tomso/workspace/mlfinlab/mlfinlab/ch3/outputs/daily_orders")
        signals_path = get_latest_signals_file(signals_dir)
        if signals_path is None:
            logger.error("No signals file found")
            return
        signals_dict = process_trading_signals(
            signals_path,
            account_value=Decimal(account_value),
            target_symbols=symbols,
            min_confidence=min_confidence,
            min_risk_reward=min_risk_reward
        )
        
        if not signals_dict:
            logger.info("No valid signals found matching criteria")
            return
            
        orders_placed = 0
        orders_failed = 0
        
        for symbol, signals in signals_dict.items():
            for signal, shares in signals:
                logger.info(
                    f"Signal - Symbol: {symbol} | Window: {signal.window_weeks}w | "
                    f"Type: {signal.signal_type} | Confidence: {signal.confidence:.2f} | "
                    f"R/R: {signal.risk_reward_ratio:.2f} | Shares: {shares}"
                )
                
                if not confirm_trade(signal, shares, account_value):
                    logger.info(f"Trade skipped for {symbol}")
                    continue
                
                try:
                    side = signal.signal_type.lower()
                    if side not in ["buy", "sell"]:
                        logger.error(f"Invalid signal type for {symbol}: {side}")
                        orders_failed += 1
                        continue
                    
                    order = trading_service.place_stop_limit_order(
                        symbol=signal.symbol,
                        qty=1, #TODO: detect it automatically = shares variable
                        limit_price=signal.entry_limit_price,
                        stop_price=signal.entry_price,
                        side=side,
                        time_in_force="gtc"
                    )
                    
                    logger.info(f"Order placed successfully - ID: {order.id} for {symbol}")
                    orders_placed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to place order for {symbol}: {str(e)}")
                    orders_failed += 1
                    continue
        
        logger.info(f"Execution complete - Orders placed: {orders_placed}, Failed: {orders_failed}")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    app()