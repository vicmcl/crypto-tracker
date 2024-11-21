import requests
import sys

sys.path.append("..")

from tools.send_request import send_signed_request, set_payload, get_endpoint
from pprint import pprint
from tools.parse_transactions import select_transaction_parser

transaction_type = "convert"
start = "19-12-2023"
end = "18-01-2024"
endpoint = get_endpoint(transaction_type)
params = set_payload(endpoint, start=start, end=end)
transaction_parser = select_transaction_parser(transaction_type)


def main():

    try:
        response = send_signed_request("GET", endpoint, params)
        pprint(transaction_parser(response))
    except requests.exceptions.RequestException as e:
        print(f"Error pinging Binance API: {e}")


if __name__ == "__main__":
    main()
