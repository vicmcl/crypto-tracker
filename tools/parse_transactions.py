import json
from datetime import datetime
from functools import partial
from pathlib import Path
from tools.send_request import send_public_request, set_payload


def safe_get(data: dict, dot_chained_keys: str):
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


def readable_datetime(timestamp):
    """
    Convert a timestamp to a readable datetime string.

    Args:
        timestamp (int): The timestamp in milliseconds.

    Returns:
        str: The readable datetime string.
    """
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


def parse_json(transactions, config):
    """
    Parse JSON transactions based on the transaction type.

    Args:
        transactions (dict): The transactions data.
        config (dict): The configuration dictionary for the transaction type.

    Returns:
        list: The list of transactions.
    """
    if config["transaction_type"] == "convert":
        transactions = safe_get(transactions, "list") or []
    elif config["transaction_type"] == "fiat":
        transactions = safe_get(transactions, "data") or []
    return transactions


def parse_transactions(transactions, config):
    """
    Parse transactions and convert them into a list of queries.

    Args:
        transactions (dict): The transactions data.
        config (dict): The configuration dictionary for the transaction type.

    Returns:
        list: The list of parsed queries.
    """
    queries = []
    transactions_found = parse_json(transactions=transactions, config=config)
    for t in transactions_found:
        vals = [safe_get(t, key) for key in config["response_keys"]]
        if None in vals:
            continue
        query = {key: val for key, val in zip(config["keys"], vals)}
        query["transaction"] = config["transaction_type"]
        query["dt"] = readable_datetime(query["dt"])
        if config["transaction_type"] in ["convert", "trade"]:
            query = add_usd_value(query)
        queries.append(query)
    return queries


def select_transaction_parser(transaction_type):
    """
    Select the appropriate transaction parser based on the transaction type.

    Args:
        transaction_type (str): The type of transaction.

    Returns:
        function: A partial function for parsing transactions with the specified configuration.
    """
    json_path = Path(__file__).parent / "transaction_configs.json"
    with open(json_path, "r") as f:
        transaction_configs = json.load(f)
    config = transaction_configs.get(transaction_type)
    if config:
        return partial(parse_transactions, config=config)
    return None
