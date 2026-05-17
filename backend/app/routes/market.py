from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(
    prefix="/market",
    tags=["Market"]
)

# GET LIVE PRICE
@router.get("/price/{symbol}")
def get_price(symbol: str):

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    response = requests.get(url)

    if response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail="Invalid symbol"
        )

    return response.json()


# GET CANDLESTICK DATA
@router.get("/candles/{symbol}")
def get_candles(

    symbol: str,

    interval: str = "1h",

    limit: int = 50
):

    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}"
        f"&interval={interval}"
        f"&limit={limit}"
    )

    response = requests.get(url)

    if response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail="Failed to fetch candles"
        )

    data = response.json()

    candles = []

    for candle in data:

        candles.append({
            "open_time": candle[0],
            "open": candle[1],
            "high": candle[2],
            "low": candle[3],
            "close": candle[4],
            "volume": candle[5]
        })

    return candles