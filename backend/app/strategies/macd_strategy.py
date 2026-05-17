import pandas as pd

def macd_strategy(data):

    # Calculate EMAs
    short_ema = data["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    long_ema = data["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    # MACD
    data["MACD"] = short_ema - long_ema

    # Signal line
    data["Signal_Line"] = (
        data["MACD"]
        .ewm(span=9, adjust=False)
        .mean()
    )

    signals = []

    for i in range(len(data)):

        if i == 0:

            signals.append("NEUTRAL")
            continue

        prev_macd = data["MACD"].iloc[i - 1]
        prev_signal = data["Signal_Line"].iloc[i - 1]

        curr_macd = data["MACD"].iloc[i]
        curr_signal = data["Signal_Line"].iloc[i]

        # BUY crossover
        if (
            prev_macd <= prev_signal
            and curr_macd > curr_signal
        ):

            signals.append("BUY")

        # SELL crossover
        elif (
            prev_macd >= prev_signal
            and curr_macd < curr_signal
        ):

            signals.append("SELL")

        else:

            signals.append("HOLD")

    data["Signal"] = signals

    return data