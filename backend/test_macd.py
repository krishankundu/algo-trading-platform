from app.services.market_data import (
    fetch_stock_data
)

from app.strategies.macd_strategy import (
    macd_strategy
)

data = fetch_stock_data("AAPL")

result = macd_strategy(data)

print(
    result[
        [
            "Close",
            "MACD",
            "Signal_Line",
            "Signal"
        ]
    ].tail()
)