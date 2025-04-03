import yfinance as yf
import pandas as pd

# Define tickers for different oils
oil_tickers = {
    "Brent Oil": "BZ=F",
    "Crude Oil WTI": "CL=F",
    "Natural Gas": "NG=F",
    "Heating Oil": "HO=F"
}

# Fetch data for the last 10 days
oil_data = []
for oil, ticker in oil_tickers.items():
    data = yf.download(ticker, period="10d", interval="1d")
    
    # Reset index to ensure Date is a column
    data = data[["Close", "Volume"]].reset_index()

    for _, row in data.iterrows():
        oil_data.append([oil, row["Date"].date(), row["Close"], row["Volume"]])

# Convert to DataFrame
df = pd.DataFrame(oil_data, columns=["Oil Type", "Date", "Closing Price", "Volume Sold"])

# Save to CSV
df.to_csv("oil_prices_last_10_days.csv", index=False)

print("✅ Data saved to oil_prices_last_10_days.csv")
