import pandas as pd
import requests
import sys

sys.path.append("..")

from tools.get_account_info import get_account_info
from tools.parse_transactions import select_transaction_parser
from tools.send_request import send_signed_request, set_payload, get_endpoint


def main():
    tickers = list(get_account_info().index)
    transaction_type = "trade"
    transaction_parser = select_transaction_parser(transaction_type)
    endpoint = get_endpoint(transaction_type)

    try:
        df = pd.DataFrame()
        for ticker in tickers:
            for stablecoin in ["USDT", "USDC"]:
                symbol = ticker + stablecoin
                params = set_payload(endpoint, symbol=symbol)
                response = send_signed_request("GET", endpoint, params)
                df = pd.concat([df, pd.DataFrame(transaction_parser(response))])
        df.to_csv(f"../trades.csv", index=False)

    except requests.exceptions.RequestException as e:
        print(f"Error pinging Binance API: {e}")


if __name__ == "__main__":
    main()
