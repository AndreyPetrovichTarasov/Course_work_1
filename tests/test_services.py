import yfinance as yf

symbol = "AAPL"
stock = yf.Ticker(symbol)
data = stock.history(period="1d")
json_data = data.to_json(orient="index")

print(json_data)