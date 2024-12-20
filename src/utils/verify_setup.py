import os
import sys
from decimal import Decimal
from typing import Any

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderStatus, AccountStatus

class AccountVerification:
    def __init__(self, api_key: str, secret_key: str):
        self.client = TradingClient(api_key=api_key, secret_key=secret_key, paper=True)
        self.account = self.client.get_account()

    def verify_trading_status(self) -> dict[str, Any]:
        return {
            "account_active": self.account.status == AccountStatus.ACTIVE,
            "trading_enabled": not self.account.trading_blocked,
            "account_healthy": not self.account.account_blocked,
            "day_trades": self.account.daytrade_count,
            "pdt_status": self.account.pattern_day_trader
        }

    def verify_buying_power(self) -> dict[str, Any]:
        return {
            "total_portfolio": Decimal(self.account.portfolio_value),
            "buying_power": Decimal(self.account.buying_power),
            "cash": Decimal(self.account.cash),
            "margin_multiplier": self.account.multiplier
        }

def main():
    api_key = os.getenv("API_KEY")
    secret_key = os.getenv("SECRET_KEY")

    if not all([api_key, secret_key]):
        print("ERROR: API credentials not found in environment variables")
        sys.exit(1)

    try:
        verifier = AccountVerification(api_key, secret_key)
        
        trading_status = verifier.verify_trading_status()
        buying_power = verifier.verify_buying_power()

        print("\nTrading Status:")
        print(f"Account Active: {'✓' if trading_status['account_active'] else '✗'}")
        print(f"Trading Enabled: {'✓' if trading_status['trading_enabled'] else '✗'}")
        print(f"Account Healthy: {'✓' if trading_status['account_healthy'] else '✗'}")
        print(f"Day Trades Today: {trading_status['day_trades']}")
        print(f"Pattern Day Trader: {'Yes' if trading_status['pdt_status'] else 'No'}")

        print("\nAccount Balance:")
        print(f"Portfolio Value: ${buying_power['total_portfolio']:,.2f}")
        print(f"Buying Power: ${buying_power['buying_power']:,.2f}")
        print(f"Cash: ${buying_power['cash']:,.2f}")
        print(f"Margin Multiplier: {buying_power['margin_multiplier']}x")

        if all([
            trading_status['account_active'],
            trading_status['trading_enabled'],
            trading_status['account_healthy']
        ]):
            print("\n✓ Account ready for trading")
            return 0
        else:
            print("\n✗ Account not ready for trading")
            return 1

    except Exception as e:
        print(f"Error during verification: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())