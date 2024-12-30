import sys
import pandas as pd

sys.path.append("..")

from tools.send_request import send_signed_request, set_payload, get_endpoint
from tools.parse_transactions import transform_keys, select_config, parse_json
from tools.moving_window import moving_window
from datetime import date


def fetch_transactions(endpoint, start_date, end_date, side, transaction_type):
    params = set_payload(endpoint, start=start_date, end=end_date, side=side)
    response = send_signed_request("GET", endpoint, params)
    return parse_json(response, transaction_type=transaction_type)


def process_transactions(transactions, key_config, side):
    if not transactions:
        return pd.DataFrame()
    df = pd.DataFrame(transform_keys(transactions, key_config))
    df["side"] = "BUY" if not side else "SELL"
    return df


def fetch_all_transactions(start, end, transaction_type):
    endpoint = get_endpoint(transaction_type)
    key_config = select_config(transaction_type)
    df = pd.DataFrame()

    for side in range(2):
        for window_start, window_end in moving_window(start, end):
            transactions = fetch_transactions(
                endpoint,
                window_start,
                window_end,
                side,
                transaction_type,
            )
            partial_df = process_transactions(transactions, key_config, side)
            df = pd.concat([df, partial_df])

    return df.sort_values(by="dt") if not df.empty else df


def main():
    transaction_type = "fiat"
    start = "01-07-2023"
    end = date.today().strftime("%d-%m-%Y")
    df = fetch_all_transactions(start, end, transaction_type)
    df.to_csv("../csv/fiat.csv", index=False)


if __name__ == "__main__":
    main()
