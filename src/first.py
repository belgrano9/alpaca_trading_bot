import os
from alpaca.trading.client import TradingClient

API_KEY = "PKAESVJGRRXC7AI67K9Q"
SECRET_KEY = "xQocqVCMycdjWa8giVhCUP7YTxyHRLczVx5hmeqP"

#### We use paper environment for this example ####
paper = True # Please do not modify this. This example is for paper trading only.
####

# Below are the variables for development this documents
# Please do not change these variables
trade_api_url = None#"https://paper-api.alpaca.markets/v2"
trade_api_wss = None
data_api_url = None
stream_data_wss = None


trade_client = TradingClient(api_key=API_KEY, secret_key=SECRET_KEY, paper=paper, url_override=trade_api_url)
acct = trade_client.get_account()

print(acct)