def run_backtest(data):

    initial_balance = 100000.0

    balance = initial_balance

    shares = 0.0

    trades = []

    for i in range(len(data)):

        signal = str(
            data["Signal"].iloc[i]
        )

        price = float(
            data["Close"].iloc[i]
        )

        # BUY
        if signal == "BUY" and shares == 0:

            shares = balance / price

            balance = 0

            trades.append(
                f"BUY at {round(price, 2)}"
            )

        # SELL
        elif signal == "SELL" and shares > 0:

            balance = shares * price

            shares = 0

            trades.append(
                f"SELL at {round(price, 2)}"
            )

    # Final Value
    if shares > 0:

        final_value = (
            shares
            * float(data["Close"].iloc[-1])
        )

    else:

        final_value = balance

    profit = final_value - initial_balance

    return {

        "initial_balance": round(
            initial_balance,
            2
        ),

        "final_value": round(
            final_value,
            2
        ),

        "profit": round(
            profit,
            2
        ),

        "total_trades": len(trades),

        "trades": trades[-10:]
    }