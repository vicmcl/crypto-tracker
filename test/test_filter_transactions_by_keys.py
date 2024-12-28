import sys
import unittest

sys.path.append("..")

from tools.parse_transactions import transform_keys


class TestTransformKeys(unittest.TestCase):

    def setUp(self):
        self.trades = {
            "transactions": [
                {
                    "commission": "0.75800000",
                    "commissionAsset": "PHA",
                    "id": 27542515,
                    "isBestMatch": True,
                    "isBuyer": True,
                    "isMaker": False,
                    "orderId": 242129954,
                    "orderListId": -1,
                    "price": "0.16900000",
                    "qty": "758.00000000",
                    "quoteQty": "128.10200000",
                    "symbol": "PHAUSDT",
                    "time": 1733901279809,
                },
                {
                    "commission": "0.56608000",
                    "commissionAsset": "USDT",
                    "id": 29370585,
                    "isBestMatch": True,
                    "isBuyer": False,
                    "isMaker": False,
                    "orderId": 251681116,
                    "orderListId": -1,
                    "price": "0.30500000",
                    "qty": "1856.00000000",
                    "quoteQty": "566.08000000",
                    "symbol": "PHAUSDT",
                    "time": 1735190184846,
                },
            ],
            "config": {
                "transaction_type": "trade",
                "response_keys": [
                    "orderId",
                    "symbol",
                    "qty",
                    "quoteQty",
                    "commission",
                    "commissionAsset",
                ],
                "keys": [
                    "id",
                    "pair",
                    "amount",
                    "value",
                    "fee",
                    "fee_asset",
                ],
            },
        }

    def test_transform_keys(self):
        result = transform_keys(
            transactions=self.trades["transactions"],
            config=self.trades["config"],
            transaction_type="trade",
        )
        expected = [
            {
                "id": 242129954,
                "dt": "2024-12-11 08:14:39",
                "pair": "PHAUSDT",
                "amount": "758.00000000",
                "value": "128.10200000",
                "fee": "0.75800000",
                "fee_asset": "PHA",
                "side": "BUY",
            },
            {
                "id": 251681116,
                "dt": "2024-12-26 06:16:24",
                "pair": "PHAUSDT",
                "amount": "1856.00000000",
                "value": "566.08000000",
                "fee": "0.56608000",
                "fee_asset": "USDT",
                "side": "SELL",
            },
        ]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
