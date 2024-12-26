import hashlib
import hmac
import requests
import time
from dateutil import parser
from tools.get_key import get_key
from typing import Dict, Any
from urllib.parse import urlencode

KEY = get_key("BINANCE_API_KEY")
SECRET = get_key("BINANCE_SECRET_KEY")
BASE_URL = "https://api.binance.com"


def get_endpoint(transaction_type: str) -> str:
    """
    Get the endpoint based on the transaction type.

    Args:
        transaction_type (str): The type of transaction.

    Returns:
        str: The endpoint URL path.
    """
    match transaction_type:
        case "trade":
            return "/api/v3/myTrades"
        case "fiat":
            return "/sapi/v1/fiat/payments"
        case "convert":
            return "/sapi/v1/convert/tradeFlow"
        case "deposit":
            return "/sapi/v1/capital/deposit/hisrec"
        case "withdraw":
            return "/sapi/v1/capital/withdraw/history"
        case _:
            raise TypeError("Invalid transaction type")


def check_endpoint(endpoint: str) -> None:
    """
    Check if the endpoint is valid.

    Args:
        endpoint (str): The endpoint URL path.

    Raises:
        TypeError: If the endpoint is not valid.
    """
    if endpoint not in [
        "/api/v3/myTrades",
        "/sapi/v1/capital/deposit/hisrec",
        "/sapi/v1/capital/withdraw/history",
        "/sapi/v1/convert/tradeFlow",
        "/sapi/v1/fiat/payments",
        "/api/v3/klines",
        "/api/v3/account",
    ]:
        raise TypeError("Invalid endpoint")


def match_endpoint(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Match the endpoint with the parameters required for the endpoint.

    Args:
        endpoint (str): The endpoint URL path.
        params (Dict[str, Any]): The parameters for the endpoint.

    Returns:
        Dict[str, Any]: The updated parameters for the endpoint.
    """
    match endpoint:
        case "/sapi/v1/fiat/payments":
            params["transactionType"] = 0
            params["beginTime"] = params.pop("startTime")
        case "/sapi/v1/capital/deposit/hisrec":
            params["includeSource"] = (True,)
            params["status"] = 1
        case "/sapi/v1/capital/withdraw/history":
            params["status"] = 6
        case "/api/v3/klines":
            params["interval"] = "1m"
            params["limit"] = 1
        case _:
            pass
    return params


def set_payload(endpoint: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Set the parameters for the endpoint.

    Args:
        endpoint (str): The endpoint URL path.
        **kwargs (Any): Additional keyword arguments for the parameters.

    Returns:
        Dict[str, Any]: The parameters for the endpoint.
    """
    check_endpoint(endpoint)
    params: Dict[str, Any] = {}
    if endpoint == "/api/v3/account":
        params["omitZeroBalances"] = "true"
        return params
    if endpoint != "/api/v3/myTrades":
        start, end = kwargs.get("start"), kwargs.get("end")
        if start is not None:
            params["startTime"] = int(parser.parse(start).timestamp() * 1000)
        if end is not None:
            params["endTime"] = int(parser.parse(end).timestamp() * 1000)
    params["symbol"] = kwargs.get("symbol")
    params = match_endpoint(endpoint, params)
    return params


def hashing(query_string: str) -> str:
    """
    Generate a HMAC SHA256 signature.

    Args:
        query_string (str): The query string to be signed.

    Returns:
        str: The generated HMAC SHA256 signature.
    """
    return hmac.new(
        SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def get_timestamp() -> int:
    """
    Get the current timestamp in milliseconds.

    Returns:
        int: The current timestamp in milliseconds.
    """
    return int(time.time() * 1000)


def dispatch_request(http_method: str) -> Any:
    """
    Dispatch the HTTP request based on the method.

    Args:
        http_method (str): The HTTP method (GET, POST, PUT, DELETE).

    Returns:
        Any: The request method to be called.
    """
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": KEY}
    )
    return {
        "GET": session.get,
        "DELETE": session.delete,
        "PUT": session.put,
        "POST": session.post,
    }.get(http_method, "GET")


def send_signed_request(
    http_method: str, url_path: str, payload: Dict[str, Any] = {}
) -> Dict[str, Any]:
    """
    Send a signed request to the Binance API.

    Args:
        http_method (str): The HTTP method (GET, POST, PUT, DELETE).
        url_path (str): The URL path for the request.
        payload (Dict[str, Any], optional): The payload for the request. Defaults to {}.

    Returns:
        Dict[str, Any]: The response from the API.
    """
    query_string = urlencode(payload, True)
    if query_string:
        query_string = f"{query_string}&timestamp={get_timestamp()}"
    else:
        query_string = f"timestamp={get_timestamp()}"

    url = (
        BASE_URL + url_path + "?" + query_string + "&signature=" + hashing(query_string)
    )
    params = {"url": url, "params": {}}
    response = dispatch_request(http_method)(**params)
    return response.json()


def send_public_request(url_path: str, payload: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Send a public request to the Binance API.

    Args:
        url_path (str): The URL path for the request.
        payload (Dict[str, Any], optional): The payload for the request. Defaults to {}.

    Returns:
        Dict[str, Any]: The response from the API.
    """
    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + "?" + query_string
    response = dispatch_request("GET")(url=url)
    return response.json()
