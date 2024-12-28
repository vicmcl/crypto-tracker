import sys
import pandas as pd

sys.path.append("..")

from tools.send_request import send_signed_request, set_payload, get_endpoint
from tools.parse_transactions import transform_keys, select_config, parse_json
from tools.moving_window import moving_window
from datetime import date


def main():

    transaction_type = "fiat"
    start = "01-07-2023"
    end = date.today().strftime("%d-%m-%Y")
    endpoint = get_endpoint(transaction_type)
    key_config = select_config(transaction_type)
    df = pd.DataFrame()

    if start is not None and end is not None:
        for window in moving_window(start, end):
            params = set_payload(endpoint, start=window[0], end=window[1])
            response = send_signed_request("GET", endpoint, params)
            transactions = parse_json(response, transaction_type)
            filtered_transactions = transform_keys(transactions, key_config)
            df = pd.concat([df, pd.DataFrame(filtered_transactions)])
    df = df.sort_values(by="dt")
    df.to_csv("../csv/fiat.csv", index=False)


if __name__ == "__main__":
    main()
