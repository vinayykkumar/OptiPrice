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
    
    # Convert index (dates) to a column
    data.reset_index(inplace=True)

    # Extract only relevant columns
    for _, row in data.iterrows():
        closing_price = float(row["Close"]) if not pd.isna(row["Close"]) else None
        volume_sold = float(row["Volume"]) if not pd.isna(row["Volume"]) else None
        oil_data.append([oil, row["Date"].strftime('%Y-%m-%d'), closing_price, volume_sold])

# Convert to DataFrame
df = pd.DataFrame(oil_data, columns=["Oil Type", "Date", "Closing Price", "Volume Sold"])

# Save to CSV
df.to_csv("oil_prices_last_10_days_cleaned.csv", index=False)

print("✅ Data saved to oil_prices_last_10_days_cleaned.csv")
