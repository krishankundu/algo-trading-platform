from fastapi import APIRouter, HTTPException

import yfinance as yf


router = APIRouter(
    prefix="/market",
    tags=["Market"]
)


YAHOO_SYMBOL_MAP = {
    "BTCUSDT": "BTC-USD",
    "ETHUSDT": "ETH-USD",
    "BNBUSDT": "BNB-USD",
    "SOLUSDT": "SOL-USD",
    "XRPUSDT": "XRP-USD",
    "ADAUSDT": "ADA-USD",
}


@router.get("/price/{symbol}")
def get_price(symbol: str):

    symbol = symbol.upper()

    yahoo_symbol = YAHOO_SYMBOL_MAP.get(symbol)

    if not yahoo_symbol:

        raise HTTPException(
            status_code=400,
            detail="Unsupported symbol"
        )

    try:

        ticker = yf.Ticker(yahoo_symbol)

        price = ticker.fast_info.get("last_price")

        if price is None:

            history = ticker.history(period="1d", interval="1m")

            if history.empty:

                raise HTTPException(
                    status_code=400,
                    detail="Price fetch failed"
                )

            price = history["Close"].iloc[-1]

        return {
            "symbol": symbol,
            "price": float(price),
            "source": "Yahoo Finance"
        }

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Price fetch failed: {str(error)}"
        )


@router.get("/candles/{symbol}")
def get_candles(

    symbol: str,

    interval: str = "1h",

    limit: int = 50

):

    symbol = symbol.upper()

    yahoo_symbol = YAHOO_SYMBOL_MAP.get(symbol)

    if not yahoo_symbol:

        raise HTTPException(
            status_code=400,
            detail="Unsupported symbol"
        )

    interval_map = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "1d": "1d",
    }

    yahoo_interval = interval_map.get(interval, "1h")

    try:

        ticker = yf.Ticker(yahoo_symbol)

        data = ticker.history(
            period="7d",
            interval=yahoo_interval
        )

        if data.empty:

            raise HTTPException(
                status_code=400,
                detail="Failed to fetch candles"
            )

        data = data.tail(limit)

        candles = []

        for index, row in data.iterrows():

            candles.append({
                "open_time": str(index),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"])
            })

        return candles

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Candle fetch failed: {str(error)}"
        )