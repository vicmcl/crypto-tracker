import pandas as pd
import numpy as np
from datetime import datetime
from tools.send_request import set_payload, send_public_request
from pprint import pprint


def _convert_dt_format(string, from_format, to_format):
    """
    Convert a datetime string from one format to another.

    Args:
        string (str): The datetime string to convert.
        from_format (str): The format of the input datetime string.
        to_format (str): The format of the output datetime string.

    Returns:
        str: The converted datetime string.
    """
    try:
        return datetime.strptime(string, from_format).strftime(to_format)
    except ValueError:
        return string


def _get_usdt_price(symbol, start):
    """
    Get the average USDT price for a given symbol and start time.

    Args:
        symbol (str): The symbol for which to get the price.
        start (int): The start time in milliseconds.

    Returns:
        float: The average price.
    """
    endpoint = "/api/v3/klines"
    old_format = "%Y-%m-%d %H:%M:%S"
    new_format = "%d-%m-%Y %H:%M:%S"
    start_formatted = _convert_dt_format(str(start), old_format, new_format)
    params = set_payload(endpoint, symbol=symbol, start=start_formatted)
    response = send_public_request(endpoint, params)
    avg_price = (float(response[0][2]) + float(response[0][3])) / 2
    return avg_price


def _calculate_avg(csv_file, transactions, amount_side):
    if "fiat" in csv_file:
        return float(
            (transactions[amount_side] * transactions["price"]).sum()
            / transactions[amount_side].sum()
        )
    if "convert" in csv_file:
        return float(transactions["usd_value"].sum() / transactions[amount_side].sum())


def _fiat_price_in_usd(df):
    if "price" not in df.columns:
        raise ValueError("The 'price' column is missing.")
    df["price_in_usd"] = np.where(
        df["to_asset"].str.contains("USD"),
        1 / df["price"],
        [_get_usdt_price("EURUSDT", dt) for dt in df["dt"].values],
    )
    return df


def _usd_convert_value(df):
    mask = df["to_asset"].str.contains("USD") | df["from_asset"].str.contains("USD")
    missing_usd_value = lambda row: row["from_amount"] * _get_usdt_price(
        f"{row['from_asset']}USDT", row["dt"]
    )
    df["usd_value"] = np.where(~mask, df[~mask].apply(missing_usd_value, axis=1), "")
    copy_usd_value = lambda row: (
        row["from_amount"] if "USD" in row["from_asset"] else row["to_amount"]
    )
    df.loc[mask, "usd_value"] = df[mask].apply(copy_usd_value, axis=1)
    df["usd_value"] = df["usd_value"].astype(float)
    return df


def add_usd_prices(csv_file):
    df = pd.read_csv(csv_file)
    if "fiat" in csv_file:
        df = _fiat_price_in_usd(df)
    if "convert" in csv_file:
        df = _usd_convert_value(df)
    return df


def all_coins_avg(csv_file, side):
    df = add_usd_prices(csv_file)
    avg_values = {}
    asset_side = {"buy": "to_asset", "sell": "from_asset"}.get(side)
    amount_side = {"buy": "to_amount", "sell": "from_amount"}.get(side)
    for coin in df[asset_side].unique():
        transactions = df[df[asset_side] == coin]
        avg_values[coin] = {
            f"avg_{side}_value": _calculate_avg(csv_file, transactions, amount_side),
            "total_amount": float(transactions[amount_side].sum()),
        }
    return pd.DataFrame(avg_values).transpose()
