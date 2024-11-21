import sys

sys.path.append("..")

from tools.send_request import send_signed_request, set_payload, get_endpoint
from pprint import pprint
from datetime import date
from tools.parse_transactions import select_transaction_parser
from tools.moving_window import moving_window

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

transaction_type = "deposit"
start = "July 1, 2023"
end = date.today().isoformat()
endpoint = get_endpoint(transaction_type)
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
            # pprint(response)
            pprint(parser(response))


if __name__ == "__main__":
    main()
