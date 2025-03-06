import pandas as pd
from prophet import Prophet
import numpy as np

# Load dataset
file_path = r"D:\studies related\projects\optiprice- prognasticator\oil and gas.csv"
df = pd.read_csv(file_path)

# Convert Date column to datetime format
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

# Drop any row with missing Date values
df = df.dropna(subset=["Date"])

# Filter dataset up to 17-06-2022 (no future data)
df = df[df["Date"] <= "2022-06-17"]

# List of oil types
oil_types = ["Brent Oil", "Crude Oil WTI", "Natural Gas", "Heating Oil"]

# Columns to predict
price_columns = ["Open", "High", "Low", "Close", "Volume"]

# Create a dataframe to store all predictions
all_predictions = []

for oil in oil_types:
    for col in price_columns:
        # Prepare data for Prophet
        oil_data = df[df["Symbol"] == oil][["Date", col]].rename(columns={"Date": "ds", col: "y"}).dropna()

        # Ensure we have enough data
        if oil_data.shape[0] < 10:
            print(f"⚠️ Not enough data for {oil} - {col}, skipping...")
            continue

        # Compute percentage change
        oil_data["y"] = oil_data["y"].pct_change()  # Daily % change

        # Remove any rows where y is NaN, inf, or -inf
        oil_data = oil_data.replace([np.inf, -np.inf], np.nan).dropna()

        # Check again if enough data is left after cleaning
        if oil_data.shape[0] < 10:
            print(f"⚠️ Data too small after cleaning for {oil} - {col}, skipping...")
            continue

        # Initialize and fit Prophet model
        model = Prophet()
        model.fit(oil_data)

        # Generate future dates from 18-06-2022 to 31-12-2024
        future_dates = pd.date_range(start="2022-06-18", end="2024-12-31", freq="D")
        future_df = pd.DataFrame({"ds": future_dates})

        # Predict percentage changes
        forecast = model.predict(future_df)

        # Get last known price before 18-06-2022
        last_price_row = df[df["Symbol"] == oil].sort_values("Date", ascending=False).iloc[0]
        last_known_price = last_price_row[col]

        # Convert % change back to actual prices
        forecast["yhat"] = last_known_price * (1 + forecast["yhat"]).cumprod()

        # Extract required columns
        forecast = forecast[["ds", "yhat"]].rename(columns={"ds": "Date", "yhat": col})
        forecast["Symbol"] = oil

        # Store predictions
        all_predictions.append(forecast)

# Merge all predictions into a single dataframe
predicted_df = all_predictions[0]
for i in range(1, len(all_predictions)):
    all_predictions[i] = all_predictions[i].rename(columns=lambda x: f"{x}_{i}" if x not in ["Date", "Symbol"] else x)
    predicted_df = predicted_df.merge(all_predictions[i], on=["Date", "Symbol"], how="outer")

# Save predictions to CSV
output_file = r"D:\studies related\projects\optiprice- prognasticator\predicted_oil_prices_with_volume.csv"
predicted_df.to_csv(output_file, index=False)

print(f"✅ Predictions saved to {output_file}")
