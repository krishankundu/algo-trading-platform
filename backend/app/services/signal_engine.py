import requests
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD


def fetch_binance_candles(symbol: str, interval: str, limit: int = 100):

    url = "https://api.binance.com/api/v3/klines"

    response = requests.get(
        url,
        params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
    )

    if response.status_code != 200:
        return None

    data = response.json()

    closes = [
        float(candle[4])
        for candle in data
    ]

    return closes


def evaluate_strategy_signal(strategy):

    closes = fetch_binance_candles(
        strategy.symbol,
        strategy.timeframe
    )

    if not closes or len(closes) < 50:
        return {
            "strategy_id": strategy.id,
            "strategy_name": strategy.name,
            "symbol": strategy.symbol,
            "timeframe": strategy.timeframe,
            "strategy_type": strategy.strategy_type,
            "signal": "WAIT",
            "reason": "Not enough candle data"
        }

    df = pd.DataFrame({
        "close": closes
    })

    # RSI
    df["rsi"] = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    # EMA 20
    df["ema20"] = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    # MACD
    macd_indicator = MACD(
        close=df["close"],
        window_slow=26,
        window_fast=12,
        window_sign=9
    )

    df["macd"] = macd_indicator.macd()
    df["macd_signal"] = macd_indicator.macd_signal()

    latest_price = df["close"].iloc[-1]
    latest_rsi = df["rsi"].iloc[-1]
    latest_ema20 = df["ema20"].iloc[-1]
    latest_macd = df["macd"].iloc[-1]
    latest_macd_signal = df["macd_signal"].iloc[-1]

    previous_macd = df["macd"].iloc[-2]
    previous_macd_signal = df["macd_signal"].iloc[-2]

    signal = "WAIT"
    reason = "No condition matched"

    # =========================
    # RSI REVERSAL
    # =========================
    if strategy.strategy_type == "RSI_REVERSAL":

        if latest_rsi < 30:
            signal = "BUY"
            reason = "RSI is below 30"

        elif latest_rsi > 70:
            signal = "SELL"
            reason = "RSI is above 70"

    # =========================
    # MACD CROSSOVER
    # =========================
    elif strategy.strategy_type == "MACD_CROSSOVER":

        if (
            previous_macd <= previous_macd_signal
            and latest_macd > latest_macd_signal
        ):
            signal = "BUY"
            reason = "MACD crossed above signal line"

        elif (
            previous_macd >= previous_macd_signal
            and latest_macd < latest_macd_signal
        ):
            signal = "SELL"
            reason = "MACD crossed below signal line"

    # =========================
    # MACD TREND
    # =========================
    elif strategy.strategy_type == "MACD_TREND":

        if latest_macd > latest_macd_signal:
            signal = "BUY"
            reason = "MACD is above signal line"

        elif latest_macd < latest_macd_signal:
            signal = "SELL"
            reason = "MACD is below signal line"

    # =========================
    # EMA TREND
    # =========================
    elif strategy.strategy_type == "EMA_TREND":

        if latest_price > latest_ema20:
            signal = "BUY"
            reason = "Price is above EMA20"

        elif latest_price < latest_ema20:
            signal = "SELL"
            reason = "Price is below EMA20"

    # =========================
    # RSI + EMA COMBO
    # =========================
    elif strategy.strategy_type == "RSI_EMA_COMBO":

        if latest_rsi < 30 and latest_price > latest_ema20:
            signal = "BUY"
            reason = "RSI below 30 and price above EMA20"

        elif latest_rsi > 70 and latest_price < latest_ema20:
            signal = "SELL"
            reason = "RSI above 70 and price below EMA20"

    return {
        "strategy_id": strategy.id,
        "strategy_name": strategy.name,
        "symbol": strategy.symbol,
        "timeframe": strategy.timeframe,
        "strategy_type": strategy.strategy_type,
        "signal": signal,
        "reason": reason,
        "price": round(latest_price, 2),
        "rsi": round(latest_rsi, 2),
        "ema20": round(latest_ema20, 2),
        "macd": round(latest_macd, 4),
        "macd_signal": round(latest_macd_signal, 4)
    }