# File: src/monitoring.py

"""
Standalone script for monitoring trading orders and positions.
Run this script to start monitoring independently of the main trading system.
"""

import os
import asyncio
from pathlib import Path

from services.alpaca_service import TradingService, AlpacaConfig
from services.order_monitor import OrderMonitor

from utils.logger import setup_logger

logger = setup_logger(
    name="monitoring",
    log_file=Path("src/logs/monitoring.log")
)

async def run_monitor():
    """Initialize and run the order monitor."""
    try:        
        config = AlpacaConfig(
            api_key=os.getenv("API_KEY"),
            secret_key=os.getenv("SECRET_KEY"),
            paper=True
        )
        trading_service = TradingService(config)
        
        logger.info("Starting order monitoring...")
        monitor = OrderMonitor(trading_service.client)

        while True:
            status = await monitor.get_active_positions_and_orders()
            logger.info("Current Portfolio Status:")
            logger.info(f"Positions: {status['positions']}")
            logger.info(f"Open Orders: {status['orders']}")
            await asyncio.sleep(monitor.check_interval)
            
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitor error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_monitor())