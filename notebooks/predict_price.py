import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler

# Fix "mse" error in Keras model loading
tf.keras.losses.mse = tf.keras.losses.MeanSquaredError()

# Load models and scalers
lstm_model = tf.keras.models.load_model("lstm_oil_price_model.h5", compile=False)
xgb_model = joblib.load("xgb_oil_price_model.pkl")
scaler = joblib.load("feature_scaler.pkl")
scaler_preds = joblib.load("prediction_scaler.pkl")
ohe = joblib.load("ohe_encoder.pkl")

# 🔹 Oil Types (Matching final df column names)
oil_types = ["Brent Oil", "Crude Oil WTI", "Heating Oil", "Natural Gas"]

# 🔹 Oil Type Mapping
oil_type_dict = {
    "Brent Oil": "OilType_Brent_Oil",
    "Crude Oil WTI": "OilType_Crude_Oil_WTI",
    "Heating Oil": "OilType_Heating_Oil",
    "Natural Gas": "OilType_Natural_Gas"
}

# 🔹 Streamlit UI
st.title("Oil Price Prediction 💰")

# 📅 Date Input
date_input = st.date_input("Select Start Date:")
date_unix = pd.to_datetime(date_input).timestamp()  # Convert to UNIX timestamp

# ⛽ Oil Type Selection
selected_oil_type = st.selectbox("Select Oil Type:", oil_types)

# 💲 Closing Price Input
closing_price = st.number_input("Enter Closing Price ($)", min_value=0.0, format="%.2f")

# 📆 Sidebar: Number of Days for Prediction
num_days = st.sidebar.slider("Select number of days to predict:", min_value=1, max_value=30, value=1)

# 🔹 Predict Button
if st.button("Predict Selling Price"):
    predictions = []
    future_closing_price = closing_price  # Initialize with user input

    for i in range(num_days):
        # Adjust date for each day
        future_date_unix = date_unix + (i * 86400)  # Add i days (86400 seconds in a day)

        # 🔹 One-Hot Encode Oil Type
        oil_type_encoded = ohe.transform([[selected_oil_type]])[0]

        encoded_features = [0, 0, 0, 0]  # Initialize all as 0
        encoded_features[oil_types.index(selected_oil_type)] = 1  # Set selected oil type to 1

        # 🔹 Prepare Input Data
        input_data = np.array([future_date_unix, future_closing_price] + encoded_features).reshape(1, -1)

        # 🔹 Scale Input Data
        input_data_scaled = scaler.transform(input_data)

        # 🔹 Predict using XGBoost
        xgb_pred = xgb_model.predict(input_data_scaled).reshape(-1, 1)

        # 🔹 Scale XGBoost Prediction for LSTM
        xgb_pred_scaled = scaler_preds.transform(xgb_pred).reshape(1, 1, 1)

        # 🔹 Predict using LSTM
        lstm_pred = lstm_model.predict(xgb_pred_scaled)

        # Store results
        predictions.append((pd.to_datetime(future_date_unix, unit="s").strftime("%Y-%m-%d"), lstm_pred[0][0]))

        # Use the predicted price as the closing price for the next day
        future_closing_price = lstm_pred[0][0]

    # 🔹 Display Results
    st.subheader("📊 Predicted Selling Prices:")
    pred_df = pd.DataFrame(predictions, columns=["Date", "Predicted Price"])
    st.table(pred_df)

    # 🔹 Plot Line Graph
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(pred_df["Date"], pred_df["Predicted Price"], marker="o", linestyle="-", color="b", label="Predicted Price")
    ax.set_xlabel("Date")
    ax.set_ylabel("Predicted Price ($)")
    ax.set_title(f"Predicted Oil Prices for {selected_oil_type}")
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility

    # Display the graph in Streamlit
    st.pyplot(fig)
