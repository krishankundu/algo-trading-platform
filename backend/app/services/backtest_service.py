import requests

from ta.momentum import RSIIndicator

from ta.trend import EMAIndicator

import pandas as pd


def run_backtest(

    symbol: str,

    interval: str,

    initial_balance: float

):

    url = "https://api.binance.com/api/v3/klines"

    response = requests.get(

        url,

        params={

            "symbol": symbol,

            "interval": interval,

            "limit": 200
        }
    )

    data = response.json()

    closes = [float(candle[4]) for candle in data]

    df = pd.DataFrame({
        "close": closes
    })

    # INDICATORS
    df["rsi"] = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    df["ema"] = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    balance = initial_balance

    btc = 0

    trades = []

    for i in range(20, len(df)):

        price = df["close"][i]

        rsi = df["rsi"][i]

        ema = df["ema"][i]

        # BUY SIGNAL
        if rsi < 30 and price > ema and balance > 0:

            btc = balance / price

            balance = 0

            trades.append({

                "side": "BUY",

                "price": round(price, 2)
            })

        # SELL SIGNAL
        elif rsi > 70 and btc > 0:

            balance = btc * price

            btc = 0

            trades.append({

                "side": "SELL",

                "price": round(price, 2)
            })

    final_balance = balance

    if btc > 0:

        final_balance = btc * df["close"].iloc[-1]

    profit = final_balance - initial_balance

    roi = (profit / initial_balance) * 100

    return {

        "symbol": symbol,

        "interval": interval,

        "initial_balance": round(initial_balance, 2),

        "final_balance": round(final_balance, 2),

        "profit": round(profit, 2),

        "roi": round(roi, 2),

        "total_trades": len(trades),

        "trades": trades
    }