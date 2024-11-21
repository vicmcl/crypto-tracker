import requests
import sys

sys.path.append("..")

from tools.parse_transactions import select_transaction_parser
from tools.send_request import send_signed_request, set_payload, get_endpoint
from pprint import pprint

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

transaction_type = "trade"
endpoint = get_endpoint(transaction_type)
params = set_payload(endpoint, symbol="WLDUSDC")
transaction_parser = select_transaction_parser(transaction_type)


def main():

    try:
        response = send_signed_request("GET", endpoint, params)
        pprint(transaction_parser(response))
    except requests.exceptions.RequestException as e:
        print(f"Error pinging Binance API: {e}")


if __name__ == "__main__":
    main()
