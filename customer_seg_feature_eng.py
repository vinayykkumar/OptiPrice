import os
import pandas as pd

# Define file paths
input_path = r"E:\OIL_InfySpringboard\Code\customer_orders_15k.csv"
output_path = r"E:\OIL_InfySpringboard\Code\customer_dataset_feature_engineered.csv"

# Load Customer Dataset
df_customer = pd.read_csv(input_path)

# Feature 1: Purchase Frequency (Total Transactions per Customer)
df_customer["Purchase_Frequency"] = df_customer.groupby("Vehicle_Number")["Date_Time"].transform("count")

# Feature 2: Average Spend Per Transaction
df_customer["Average_Spend_Per_Transaction"] = df_customer.groupby("Vehicle_Number")["Amount_Spent"].transform("mean")

# Feature 3: Total Discount Received by Each Customer
df_customer["Total_Discount_Received"] = df_customer.groupby("Vehicle_Number")["Discount_Applied (%)"].transform("sum")

# Feature 4: One-Hot Encoding for Payment Method
df_customer = pd.get_dummies(df_customer, columns=["Payment_Method"], drop_first=True)

# Ensure the directory exists before saving
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save the engineered dataset
df_customer.to_csv(output_path, index=False)

print(f"✅ File successfully saved at: {output_path}")
