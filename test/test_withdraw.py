import sys

sys.path.append("..")

from tools.send_request import send_signed_request, set_payload, get_endpoint
from pprint import pprint
from tools.parse_transactions import select_transaction_parser
from tools.moving_window import moving_window

transaction_type = "withdraw"
endpoint = get_endpoint(transaction_type)
start = "01-07-2023"
end = "27-05-2024"
params = set_payload(endpoint, start=start, end=end)

parser = select_transaction_parser(transaction_type)


def main():

    if start is not None and end is not None:
        for window in moving_window(start, end):
            dates = [date for date in window]
            print()
            print("=" * 20, dates[0], "to", dates[1], "=" * 20, end="\n\n")
            params = set_payload(
                endpoint,
                start=window[0],
                end=window[1],
            )
            response = send_signed_request("GET", endpoint, params)
            pprint(parser(response))


if __name__ == "__main__":
    main()
