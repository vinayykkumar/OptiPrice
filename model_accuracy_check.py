import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# ============================
# 🔹 1️⃣ Load & Merge Datasets
# ============================

# Load Historical Dataset
historical_path = r"D:\studies related\projects\optiprice- prognasticator\oil and gas.csv"
df_historical = pd.read_csv(historical_path)

# Load Competitor Dataset
competitor_path = r"D:\studies related\projects\optiprice- prognasticator\competitor-dataset.csv"
df_competitor = pd.read_csv(competitor_path)

# Load Scraped Real-Time Prices
scraped_prices_path = r"D:\studies related\projects\optiprice- prognasticator\scraped_oil_prices.csv"
df_scraped = pd.read_csv(scraped_prices_path)

# Merge datasets on Date & Symbol
df = pd.merge(df_historical, df_competitor, on=["Date", "Symbol"], how="left")
df = pd.merge(df, df_scraped, on=["Date", "Symbol"], how="left")

# ============================
# 🔹 2️⃣ Feature Selection
# ============================

# Ensure critical columns exist
for col in ["Closing Price", "Selling Price", "Volume Sold"]:
    if col not in df.columns:
        df[col] = np.nan  # Assign NaN if missing

# Fill missing values
df.fillna(method="ffill", inplace=True)  # Forward-fill missing data
df.fillna(0, inplace=True)  # Replace remaining NaNs with 0

# Define Features (X) and Target (y)
features = ["Closing Price", "Selling Price", "Volume Sold"]
target = "Selling Price"

X = df[features]
y = df[target]

# Split into Train-Test (80-20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize Features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================
# 🔹 3️⃣ Train & Evaluate ML Models (Now 5 Models)
# ============================

models = {
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42),
    "Support Vector Regression (SVR)": SVR(kernel='rbf', C=100, gamma=0.1),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
}

results = []

for model_name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    
    # Evaluate Model
    mae = mean_absolute_error(y_test, y_pred)
    
    results.append({"Model": model_name, "MAE": mae})
    print(f"✅ {model_name} - MAE: {mae:.2f}")

# Convert results to DataFrame & Save
df_results = pd.DataFrame(results)
df_results.to_csv(r"D:\studies related\projects\optiprice- prognasticator\model_performance.csv", index=False)

print("🚀 Model training & evaluation completed. Results saved!")
