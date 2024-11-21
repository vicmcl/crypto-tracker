import json
from pathlib import Path
from tools.parse_transactions import select_transaction_parser
from tools.send_request import (
    get_endpoint,
    set_payload,
    send_public_request,
    send_signed_request,
)


def main():
    start_date = "01-07-2023"
    end_date = "18-11-2024"

    for transaction_type in ["trade", "convert", "fiat", "deposit"]:
        endpoint = get_endpoint(transaction_type)
        kwargs = (
            {"symbol": "WLDUSDC"}
            if transaction_type == "trade"
            else {"start": start_date, "end": end_date}
        )
        params = set_payload(endpoint, **kwargs)
        transaction_parser = select_transaction_parser(transaction_type)
        response = send_signed_request("GET", endpoint, params)
        parsed_response = transaction_parser(response)
        print(parsed_response)

        json_path = Path(__file__).parent / "json"
        transactions_path = json_path / Path(transaction_type + ".json")
        with open(transactions_path, "w") as f:
            transactions = json.load(f)

        for new_element in parsed_response:
            print(new_element)
            new_element_dict = {new_element["id"]: new_element.pop("id")}
            if not any(key == new_element_dict for key in transactions):
                transactions.append(new_element_dict)
        with open(transactions_path, "w") as f:
            json.dump(transactions, f, indent=4)


if __name__ == "__main__":
    main()
