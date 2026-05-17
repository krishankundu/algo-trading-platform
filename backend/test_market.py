from app.services.market_data import fetch_stock_data

data = fetch_stock_data("AAPL")

print(data.head())