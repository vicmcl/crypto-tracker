import requests
import sys

sys.path.append("..")

from tools.parse_transactions import select_transaction_parser
from tools.send_request import send_signed_request, set_payload, get_endpoint
from tools.get_account_info import get_account_info
import pandas as pd

### ENDPOINTS ###

# /api/v3/myTrades
#   - Get trades for a specific account and symbol
#   - Paramaters: symbol, startTime, endTime

# /sapi/v1/fiat/payments
#   - Get fiat payments
#   - Paramaters: transactionType, beginTime, endTime

# /sapi/v1/convert/tradeFlow
#   - Get conversion trades
#   - Paramaters: startTime, endTime

# /sapi/v1/capital/deposit/hisrec
#   - Get deposit history
#   - Paramaters: startTime, endTime, includeSource = True, status = 1

# /sapi/v1/capital/withdraw/history
#   - Get withdraw history
#   - Paramaters: startTime, endTime, status = 1

tickers = list(get_account_info().index)
transaction_type = "trade"
transaction_parser = select_transaction_parser(transaction_type)
endpoint = get_endpoint(transaction_type)


def main():

    try:
        df = pd.DataFrame()
        for ticker in tickers:
            for stabelcoin in ["USDT", "USDC"]:
                params = set_payload(endpoint, symbol=ticker + stabelcoin)
                response = send_signed_request("GET", endpoint, params)
                df = pd.concat([df, pd.DataFrame(transaction_parser(response))])
        df.to_csv(f"../trades.csv", index=False)
    except requests.exceptions.RequestException as e:
        print(f"Error pinging Binance API: {e}")


if __name__ == "__main__":
    main()
