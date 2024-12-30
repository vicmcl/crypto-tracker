import json
from datetime import datetime
from pathlib import Path


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
        extract_transactions = _safe_get(transactions, "list") or []
    elif transaction_type == "fiat":
        all_transactions = _safe_get(transactions, "data") or []
        extract_transactions = [t for t in all_transactions if t["status"] != "Failed"]
    else:
        extract_transactions = transactions
    return extract_transactions


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
