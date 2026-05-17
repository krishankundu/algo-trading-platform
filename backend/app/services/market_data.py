import yfinance as yf
import pandas as pd

def fetch_stock_data(
    symbol: str,
    period: str = "2y",
    interval: str = "1d"
):

    data = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True
    )

    # Reset multi-index columns if present
    if isinstance(data.columns, pd.MultiIndex):

        data.columns = [
            col[0]
            for col in data.columns
        ]

    # Remove duplicated columns
    data = data.loc[:, ~data.columns.duplicated()]

    # Select required columns
    data = data[
        ["Open", "High", "Low", "Close", "Volume"]
    ]

    # Force numeric types
    for column in data.columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Drop NaN values
    data.dropna(inplace=True)

    return data