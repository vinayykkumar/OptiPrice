import pandas as pd
import random
from datetime import datetime, timedelta

# Number of entries
num_entries = 15000

# Generate a set of unique vehicle numbers (customers)
unique_vehicle_numbers = [f"AB{random.randint(10,99)}CD{random.randint(1000,9999)}" for _ in range(3000)]
vehicle_numbers = [random.choice(unique_vehicle_numbers) for _ in range(num_entries)]

# Generate random dates within the last 2 years
start_date = datetime(2023, 1, 1)
date_times = [start_date + timedelta(days=random.randint(0, 730), hours=random.randint(0, 23), minutes=random.randint(0, 59)) for _ in range(num_entries)]

# Fuel types
fuel_types = ["Brent Oil", "Crude Oil", "Natural Gas", "Heating Oil"]

# Generate competitor pricing & inventory-based dynamic pricing values
competitor_prices = {fuel: random.uniform(80, 150) for fuel in fuel_types}  # Competitor prices vary per fuel
price_elasticity = random.uniform(-0.5, -0.1)  # Negative value (Higher price -> Lower demand)

data = []
for i in range(num_entries):
    fuel = random.choice(fuel_types)
    
    # Competitor pricing & deviation
    competitor_price = competitor_prices[fuel] + random.uniform(-5, 5)  # Competitor variation
    price_difference = round((random.uniform(-10, 10) / 100) * competitor_price, 2)  # % deviation

    # Stock availability impact
    stock_availability = random.uniform(1000, 50000)  # Stock in liters
    discount_applied = round(random.uniform(0, 15), 2)  # Discount in percentage

    # Volume sold based on price difference & elasticity
    base_volume = random.uniform(100, 5000)  # Base sales volume
    volume_sold = round(base_volume * (1 + price_elasticity * price_difference), 2)

    # Calculate refueling cost dynamically
    refueling_cost = round(competitor_price * 0.9 + random.uniform(1, 5), 2)  # 90% of competitor price

    # Time-based features
    day_of_week = date_times[i].weekday()  # 0 = Monday, 6 = Sunday
    month = date_times[i].month  # 1 = Jan, 12 = Dec

    # Purchase frequency (simulated for repeating customers)
    purchase_frequency = random.choice(["Daily", "Weekly", "Monthly"])

    data.append([vehicle_numbers[i], date_times[i], fuel, competitor_price, price_difference, 
                 volume_sold, stock_availability, discount_applied, refueling_cost, 
                 day_of_week, month, purchase_frequency])

# Create DataFrame
columns = ["Vehicle_Number", "Date_Time", "Fuel_Type", "Competitor_Avg_Price", "Price_Difference (%)", 
           "Volume_Sold", "Stock_Availability", "Discount_Applied (%)", "Refueling_Cost", 
           "Day_of_Week", "Month", "Purchase_Frequency"]
df_features = pd.DataFrame(data, columns=columns)

# Save dataset
file_path = "engineered_customer_dataset.csv"
df_features.to_csv(file_path, index=False)
file_path
