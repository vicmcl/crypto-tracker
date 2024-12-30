import pandas as pd
import sys

sys.path.append("..")

from tools.parse_transactions import transform_keys, select_config, parse_json
from tools.send_request import send_signed_request, set_payload, get_endpoint


def main():
    # Set the symbol and transaction type
    symbol = "BONKUSDT"
    transaction_type = "trade"

    # Get the endpoint and send the request
    endpoint = get_endpoint(transaction_type)
    params = set_payload(endpoint, symbol=symbol)
    response = send_signed_request("GET", endpoint, params)

    # Parse the response and transform the keys
    key_config = select_config(transaction_type)
    transactions = parse_json(response, transaction_type)
    filtered_transactions = transform_keys(transactions, key_config)
    df = pd.DataFrame(filtered_transactions)
    print(df)


if __name__ == "__main__":
    main()
