from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import List

import requests
from django.http import JsonResponse


def home(request):
    data = {"message": "hello from json response", "num": 12.2}
    return JsonResponse(data)


@dataclass
class ExchangeRate:
    from_: str
    to: str
    value: float

    @classmethod
    def from_response(cls, response: requests.Response) -> ExchangeRate:
        pure_response: dict = response.json()["Realtime Currency Exchange Rate"]
        from_ = pure_response["1. From_Currency Code"]
        to = pure_response["3. To_Currency Code"]
        value = pure_response["5. Exchange Rate"]

        return cls(from_=from_, to=to, value=value)

    def __eq__(self, other: ExchangeRate) -> bool:
        return self.value == other.value


ExchangeRates = List[ExchangeRate]


class ExchangeRatesHistory:
    PATH_TO_FILE = os.path.join("history.json")
    history_data: 'ExchangeRates' = []

    @classmethod
    def read_history_file(cls) -> None:
        with open(cls.PATH_TO_FILE, "r") as file:
            if cls.history_data:
                data = json.load(file)
                cls.history_data = data["results"]

    @classmethod
    def add(cls, instance: 'ExchangeRate') -> None:
        cls.read_history_file()

        instance = asdict(instance)
        if not cls.history_data:
            cls.history_data.append(instance)
        elif cls.history_data[-1] != instance:
            cls.history_data.append(instance)

    @classmethod
    def as_dict(cls) -> dict:
        return {"results": [data for data in cls.history_data]}

    @classmethod
    def save_to_file(cls, history_dict: dict) -> None:
        with open(cls.PATH_TO_FILE, "w") as file:
            json.dump(history_dict, file)

    @classmethod
    def save_history(cls) -> dict:

        if not cls.history_data:
            cls.read_history_file()
            history_dict = cls.as_dict()
        elif cls.history_data:
            history_dict = cls.as_dict()

        cls.save_to_file(history_dict)
        return history_dict


def btc_usd(request):
    # NOTE: Connect to the external exchange rates API
    API_KEY = "82I46WMYT3C7EX3J"
    url = (
        "https://www.alphavantage.co/"
        f"query?function=CURRENCY_EXCHANGE_RATE&from_currency=BTC&to_currency=USD&apikey={API_KEY}"
    )

    response = requests.get(url)
    exchange_rate = ExchangeRate.from_response(response)
    ExchangeRatesHistory.add(exchange_rate)

    return JsonResponse(asdict(exchange_rate))


def history(request):
    return JsonResponse(ExchangeRatesHistory.save_history())