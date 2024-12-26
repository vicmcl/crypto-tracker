from tools.send_request import send_signed_request, set_payload
from pprint import pprint
import pandas as pd


def get_account_info(date):
    """
    Get account information from the Binance API.

    Args:
        date (str): The date to get the account information.
    """
    endpoint = "/api/v3/account"
    params = set_payload(endpoint)
    response = send_signed_request("GET", endpoint, params)
    df = pd.DataFrame(response["balances"]).set_index("asset")
    return df
