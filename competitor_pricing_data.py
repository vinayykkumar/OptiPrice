import pandas as pd
import numpy as np
from datetime import datetime

# Load dataset
df = pd.read_csv("E:\OIL_InfySpringboard\Code\oil and gas.csv")  # Update with actual file path

# Define companies and their base profit margins per commodity
companies = {
    "ExxonMobil": {"Brent Oil": 0.12, "Crude Oil WTI": 0.10, "Natural Gas": 0.15, "Heating Oil": 0.08},
    "Chevron": {"Brent Oil": 0.14, "Crude Oil WTI": 0.09, "Natural Gas": 0.16, "Heating Oil": 0.07},
    "ConocoPhillips": {"Brent Oil": 0.13, "Crude Oil WTI": 0.11, "Natural Gas": 0.14, "Heating Oil": 0.09},
    "Marathon Petroleum": {"Brent Oil": 0.11, "Crude Oil WTI": 0.12, "Natural Gas": 0.13, "Heating Oil": 0.10},
}

# Initial cost, inflation, and tax parameters
base_tax = 0.5  
tax_increase = 0.02  # r
base_cost = 0.5  # Initial logistics cost
inflation_rate = 1.05  # 5% increase per year

# Function to compute selling price
def compute_selling_price(market_price, year_diff, volume, base_margin):
    """Compute selling price considering inflation, tax, and dynamic margins."""
    tax = base_tax + (tax_increase * year_diff)
    cost = base_cost * (inflation_rate ** year_diff)
    dynamic_margin = base_margin + (0.001 * np.log1p(volume))  # Adjust based on volume
    selling_price = market_price * (1 + dynamic_margin) + cost + tax
    return selling_price

# Prepare new dataset
data = []

for index, row in df.iterrows():
    symbol = row["Symbol"]
    date = row["Date"]
    closing_price = row["Close"]
    total_volume = row["Volume"]
    
    # Compute year difference from 2000 for inflation & tax
    year_diff = datetime.strptime(date, "%Y-%m-%d").year - 2000  

    selling_prices = []
    
    for company in companies.keys():
        # Get company-specific profit margin for the commodity (default 10% if unknown)
        profit_margin = companies[company].get(symbol, 0.10)

        # Compute selling price
        selling_price = compute_selling_price(closing_price, year_diff, total_volume, profit_margin)
        selling_prices.append(selling_price)

    # Compute volume distribution based on inverse selling price
    inverse_prices = [1 / sp for sp in selling_prices]
    total_inverse = sum(inverse_prices)
    volumes = [(total_volume * (inv / total_inverse)) for inv in inverse_prices]

    # Store new rows
    for i, company in enumerate(companies.keys()):
        data.append([symbol, company, date, closing_price, selling_prices[i], int(volumes[i])])  # Convert volume to int

# Convert to DataFrame
df_new = pd.DataFrame(data, columns=["Symbol", "Company", "Date", "Closing Price", "Selling Price", "Volume Sold"])

# Save dataset
df_new.to_csv("selling_prices_adjusted.csv", index=False)

print("✅ Selling prices dataset successfully generated and saved as 'selling_prices_adjusted.csv'")
