import json
from datetime import datetime
from pathlib import Path
from tools.send_request import send_public_request, set_payload
from pprint import pprint


def _safe_get(data: dict, dot_chained_keys: str):
    """
    Safely retrieve a value from a nested dictionary using dot-separated keys.

    Args:
        data (dict): The dictionary (or list of dictionaries) from which to retrieve the value.
        dot_chained_keys (str): A string of keys separated by dots, representing the path to the desired value.

    Returns:
        The value found at the specified path, or None if any error occurs during the retrieval process.
    """
    keys = dot_chained_keys.split(".")
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[0][key]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data


def get_usdt_price(symbol, start):
    """
    Get the average USDT price for a given symbol and start time.

    Args:
        symbol (str): The symbol for which to get the price.
        start (int): The start time in milliseconds.

    Returns:
        float: The average price.
    """
    endpoint = "/api/v3/klines"
    params = set_payload(endpoint, symbol=symbol, start=start)
    response = send_public_request(endpoint, params)
    avg_price = round((float(response[0][2]) + float(response[0][3])) / 2, 2)
    return avg_price


def _readable_datetime(timestamp):
    """
    Convert a timestamp to a readable datetime string.

    Args:
        timestamp (int): The timestamp in milliseconds.

    Returns:
        str: The readable datetime string.
    """
    if isinstance(timestamp, str):
        return timestamp
    return str(datetime.fromtimestamp(timestamp / 1000)).split(".")[0]


def add_usd_value(query):
    """
    Add the USD value to a query based on from_coin and to_coin keys.

    Args:
        query (dict): The query dictionary containing transaction details.

    Returns:
        dict: The updated query dictionary with the USD value added.
    """
    if "USD" not in query["from_coin"] and "USD" not in query["to_coin"]:
        query["value_usd"] = round(
            get_usdt_price(symbol=query["to_coin"] + "USDT", start=query["dt"])
            * float(query["to_amount"]),
            2,
        )
    elif query["to_coin"].startswith("USD"):
        query["value_usd"] = round(float(query["to_amount"]), 2)
    else:
        query["value_usd"] = round(float(query["from_amount"]), 2)
    return query


def parse_json(transactions, transaction_type):
    """
    Parse JSON transactions based on the transaction type.

    Args:
        transactions (dict): The transactions data.
        config (dict): The configuration dictionary for the transaction type.

    Returns:
        list: The list of transactions.
    """
    if transaction_type == "convert":
        extracted_transactions = _safe_get(transactions, "list") or []
    elif transaction_type == "fiat":
        extracted_transactions = _safe_get(transactions, "data") or []
    else:
        extracted_transactions = transactions
    return extracted_transactions


def select_config(transaction_type):
    """
    Select the appropriate transaction parser based on the transaction type.

    Args:
        transaction_type (str): The type of transaction.

    Returns:
        function: A partial function for parsing transactions with the specified configuration.
    """
    # Construct path to config file relative to this script
    json_path = Path(__file__).parent / "transaction_configs.json"

    # Check if config file exists
    if not json_path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    try:
        # Open and parse the JSON config file
        with open(json_path, "r") as config_file:
            config = json.load(config_file).get(transaction_type)
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        raise ValueError(f"Error decoding JSON from {json_path}: {e}")

    # Ensure config exists for the requested transaction type
    if config is None:
        raise ValueError(f"No configuration found for {transaction_type}.")

    return config


def transform_keys(transactions, config):
    """
    Transform transaction keys based on the configuration.

    Args:
        transactions (list): The list of transactions.
        config (dict): The configuration dictionary for the transaction type.

    Returns:
        list: The list of transformed transactions.
    """
    converted_transactions_data = []
    # Iterate through each transaction in the transactions list
    for transaction in transactions:
        # Create pairs of keys from config using zip
        key_pairs = zip(config["keys"], config["response_keys"])
        # Transform each response key to a new key to unify the format
        data = {
            key: (
                # If key contains "time", convert timestamp to readable datetime
                transaction[response_key]
                if "time" not in response_key.lower()
                else _readable_datetime(transaction[response_key])
            )
            for key, response_key in key_pairs
        }
        # Special handling for trade type transactions to set buy/sell side
        if "isBuyer" in transaction:
            data["side"] = "BUY" if transaction["isBuyer"] else "SELL"
        # Add the transformed transaction to the result list
        converted_transactions_data.append(data)
    return converted_transactions_data
