import pandas as pd

# Load datasets
our_prices = pd.read_csv("our_correct_price_updated.csv")
buying_prices = pd.read_csv("oil_prices_last_10_days.csv")
competitor_prices = pd.read_csv("competitor_prices_last_10_days.csv")

# 1️⃣ Prepare Customer CSV
customer_df = our_prices[["Date", "Oil Type", "Selling Price"]]
customer_df.to_csv("customer_ui.csv", index=False)
print("✅ Customer CSV saved as 'customer_ui.csv'")

# 2️⃣ Prepare Owner CSV
# Merge our selling prices with buying prices
owner_df = our_prices.merge(buying_prices, on=["Date", "Oil Type"], suffixes=("_our", "_buying"))

# Rename columns
owner_df.rename(columns={"Selling Price_our": "Selling Price", "Selling Price_buying": "Buying Price"}, inplace=True)

# Calculate profit percentage
owner_df["Profit Percent"] = ((owner_df["Selling Price"] / owner_df["Buying Price"]) - 1) * 100

# Merge with competitor prices to get competitor profit percentages
competitor_prices["Competitor Profit Percent"] = ((competitor_prices["Selling Price"] / owner_df["Buying Price"]) - 1) * 100

# Compute max and average competitor profit percentage
comp_profit_stats = competitor_prices.groupby(["Date", "Oil Type"])["Competitor Profit Percent"].agg(["max", "mean"]).reset_index()
comp_profit_stats.rename(columns={"max": "Competitor Max Profit Percent", "mean": "Competitor Avg Profit Percent"}, inplace=True)

# Merge with owner_df
owner_df = owner_df.merge(comp_profit_stats, on=["Date", "Oil Type"])

# Save the final owner CSV
owner_df.to_csv("owner_ui.csv", index=False)
print("✅ Owner CSV saved as 'owner_ui.csv'")
