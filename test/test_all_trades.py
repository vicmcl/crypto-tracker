import pandas as pd
import requests
import sys

sys.path.append("..")

from tools.get_account_info import get_account_info
from tools.parse_transactions import transform_keys, parse_json, select_config
from tools.send_request import send_signed_request, set_payload, get_endpoint


def main():
    transaction_type = "trade"
    endpoint = get_endpoint(transaction_type)
    key_config = select_config(transaction_type)
    df = pd.DataFrame()

    try:
        tickers = [t for t in list(get_account_info().index) if "USD" not in t]
        for ticker in tickers:
            for stablecoin in ["USDT", "USDC"]:
                symbol = ticker + stablecoin
                params = set_payload(endpoint, symbol=symbol)
                response = send_signed_request("GET", endpoint, params)
                if "code" in response:
                    print(f"Error: {response['msg']}")
                    continue
                transactions = parse_json(response, transaction_type)
                filtered_transactions = transform_keys(transactions, key_config)
                df = pd.concat([df, pd.DataFrame(filtered_transactions)])
        df.to_csv(f"../csv/trades.csv", index=False)

    except requests.exceptions.RequestException as e:
        print(f"Error pinging Binance API: {e}")


if __name__ == "__main__":
    main()
