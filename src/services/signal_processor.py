from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    date: str
    symbol: str
    signal_type: str
    confidence: float
    current_price: Decimal
    entry_price: Decimal
    entry_limit_price: Decimal
    take_profit: Decimal
    stop_loss: Decimal
    position_size: float
    time_barrier_days: int
    expiry_date: str
    volatility: float
    risk_reward_ratio: float
    window_weeks: int  # Added field for time window

def parse_signal_key(key: str) -> Tuple[str, int]:
    """Parse symbol and window from signal key (e.g., 'AAPL_w1' -> ('AAPL', 1))"""
    symbol, window = key.split('_w')
    return symbol, int(window)

def process_trading_signals(
    json_path: Path | str,
    account_value: Decimal,
    target_symbols: Optional[List[str]] = None,
    min_confidence: float = 0.5,
    min_risk_reward: float = 1.5
) -> Dict[str, List[Tuple[TradingSignal, int]]]:
    """
    Process trading signals filtered by symbols and criteria.
    
    Args:
        json_path: Path to JSON signals file
        account_value: Current account value
        target_symbols: Optional list of symbols to filter
        min_confidence: Minimum signal confidence threshold
        min_risk_reward: Minimum risk/reward ratio threshold
    """
    try:
        with open(json_path) as f:
            data = json.load(f)
        
        signals: Dict[str, List[Tuple[TradingSignal, int]]] = {}
        
        for key, signal_data in data.items():
            symbol, window_weeks = parse_signal_key(key)
            
            if (target_symbols and symbol not in target_symbols or
                signal_data['signal']['confidence'] < min_confidence or
                signal_data['metrics']['risk_reward_ratio'] < min_risk_reward):
                continue
                
            signal = TradingSignal(
                date=signal_data['date'],
                symbol=symbol,
                signal_type=signal_data['signal']['type'],
                confidence=float(signal_data['signal']['confidence']),
                current_price=Decimal(str(signal_data['current_price'])),
                entry_price=Decimal(str(signal_data['orders']['entry']['stop_price'])),
                entry_limit_price=Decimal(str(signal_data['orders']['entry']['limit_price'])),
                take_profit=Decimal(str(signal_data['orders']['take_profit']['price'])),
                stop_loss=Decimal(str(signal_data['orders']['stop_loss']['price'])),
                position_size=float(signal_data['position_size']['recommended_size'].split('%')[0]) / 100,
                time_barrier_days=int(signal_data['time_barrier']['days']),
                expiry_date=signal_data['time_barrier']['expiry_date'],
                volatility=float(signal_data['metrics']['daily_volatility']),
                risk_reward_ratio=float(signal_data['metrics']['risk_reward_ratio']),
                window_weeks=window_weeks
            )
            
            position_size = int(account_value * Decimal(str(signal.position_size)) / signal.entry_price)
            
            if symbol not in signals:
                signals[symbol] = []
            signals[symbol].append((signal, position_size))
        
        return signals
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Error processing signals file: {str(e)}")
        raise