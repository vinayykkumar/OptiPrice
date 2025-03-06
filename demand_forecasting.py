import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("oil and gas.csv")  # Replace with your actual filename

# Print columns to verify
print("Original Columns:", df.columns)

# Rename required columns
df = df.rename(columns={"Date": "ds", "Volume": "y"})

# Convert 'ds' to datetime
df['ds'] = pd.to_datetime(df['ds'])

# Convert 'y' to numeric (handle any errors)
df['y'] = pd.to_numeric(df['y'], errors='coerce')

# Drop NaN values (if any)
df = df.dropna()

# Print first few rows to verify
print(df.head())

# Initialize Prophet model
model = Prophet()
model.fit(df)

# Create a future dataframe (forecasting for 30 days)
future = model.make_future_dataframe(periods=30)

# Make predictions
forecast = model.predict(future)

# Plot the forecast
model.plot(forecast)
plt.show()
