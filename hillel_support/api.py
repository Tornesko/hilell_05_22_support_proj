from __future__ import annotations

from dataclasses import asdict, dataclass

import requests
from django.http import JsonResponse

# import json
# from django.http import HttpResponse
# from http import HTTPStatus
# def home(request):
#     headers = {"Content-Type": "application/json"}
#     # message = "{'message': 'hello'}"
#     data = {"message": "hello"}
#     message = json.dumps(data)
#     return HttpResponse(message, headers=headers, status=HTTPStatus.OK)


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


ExchangeRates = list[ExchangeRate]


class ExchangeRatesHistory:
    _history: ExchangeRates = []

    @classmethod
    def add(cls, instance: ExchangeRate) -> None:
        """We woud like to add ExchangeRates instances if it is not last duplicated"""

        if not cls._history:
            cls._history.append(instance)
        elif cls._history[-1] != instance:
            cls._history.append(instance)

    @classmethod
    def as_dict(cls) -> dict:
        """Main representation interface"""

        return {"results": [asdict(er) for er in cls._history]}


def btc_usd(request):
    # NOTE: Connect to the external exchange rates API
    API_KEY = "82I46WMYT3C7EX3J"
    url = (
        "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&"
        f"from_currency=BTC&to_currency=USD&apikey={API_KEY}"
    )
    response = requests.get(url)

    exchange_rate = ExchangeRate.from_response(response)
    ExchangeRatesHistory.add(exchange_rate)

    return JsonResponse(asdict(exchange_rate))


def history(request):
    return JsonResponse(ExchangeRatesHistory.as_dict())