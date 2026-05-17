import requests

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/market",
    tags=["Market"]
)


BINANCE_BASE_URLS = [
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
    "https://api4.binance.com",
]


def fetch_from_binance(endpoint: str, params: dict):
    last_error = None

    for base_url in BINANCE_BASE_URLS:
        try:
            response = requests.get(
                f"{base_url}{endpoint}",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

            last_error = response.text

        except Exception as error:
            last_error = str(error)

    raise HTTPException(
        status_code=400,
        detail=f"Binance request failed. Last response: {last_error}"
    )


@router.get("/price/{symbol}")
def get_price(symbol: str):
    symbol = symbol.upper()

    data = fetch_from_binance(
        "/api/v3/ticker/price",
        {
            "symbol": symbol
        }
    )

    return {
        "symbol": data["symbol"],
        "price": float(data["price"])
    }


@router.get("/candles/{symbol}")
def get_candles(
    symbol: str,
    interval: str = "1h",
    limit: int = 50
):
    symbol = symbol.upper()

    data = fetch_from_binance(
        "/api/v3/klines",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
    )

    candles = []

    for candle in data:
        candles.append({
            "open_time": candle[0],
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        })

    return candles