# Regenerate customer dataset with duplicate vehicle numbers for multiple transactions per customer
import pandas as pd
import random
from datetime import datetime, timedelta
num_entries = 15000

# Generate a smaller set of unique vehicle numbers (e.g., 3000) so they repeat across transactions
unique_vehicle_numbers = [f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(10,99)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000,9999)}" for _ in range(3000)]
vehicle_numbers = [random.choice(unique_vehicle_numbers) for _ in range(num_entries)]

# Generate random datetime values within the last 2 years
start_date = datetime(2023, 1, 1)
date_times = [start_date + timedelta(days=random.randint(0, 730), hours=random.randint(0, 23), minutes=random.randint(0, 59)) for _ in range(num_entries)]

# Generate random amounts spent (assuming oil purchases range between 50 and 5000 units)
amounts_spent = [round(random.uniform(50, 5000), 2) for _ in range(num_entries)]

# Generate other random attributes
fuel_types = random.choices(['Brent Oil', 'Crude Oil', 'Natural Gas', 'Heating Oil'], k=num_entries)
quantities_purchased = [round(random.uniform(10, 1000), 2) for _ in range(num_entries)]
discounts_applied = [round(random.uniform(0, 15), 2) for _ in range(num_entries)]  # Discount in percentage
payment_methods = random.choices(['Credit Card', 'Debit Card', 'Cash', 'UPI'], k=num_entries)
locations = random.choices(['New York', 'Los Angeles', 'Houston', 'Chicago', 'Miami', 'Dallas'], k=num_entries)

# Create DataFrame
df_updated = pd.DataFrame({
    "Vehicle_Number": vehicle_numbers,
    "Date_Time": date_times,
    "Amount_Spent": amounts_spent,
    "Fuel_Type": fuel_types,
    "Quantity_Purchased": quantities_purchased,
    "Discount_Applied (%)": discounts_applied,
    "Payment_Method": payment_methods,
    "Location": locations
})

# Save to CSV
file_path = r"D:\studies related\projects\optiprice- prognasticator\customer_orders_15k.csv"
df_updated.to_csv(file_path, index=False)
file_path
