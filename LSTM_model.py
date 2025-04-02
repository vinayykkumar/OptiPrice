import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import matplotlib.dates as mdates
import tensorflow as tf

# Load the model
try:
    lstm_model = load_model("lstm_oil_price_model.h5", compile=False)
    print("LSTM Model loaded successfully")
except Exception as e:
    print("Error loading LSTM model:", e)

# Load additional models and scalers
xgb_model = joblib.load("xgb_oil_price_model.pkl")
scaler = joblib.load("feature_scaler.pkl")
scaler_preds = joblib.load("prediction_scaler.pkl")

# Function to generate time range for future predictions
def generate_dates(start_date, num_days):
    dates = pd.date_range(start=start_date, periods=num_days).strftime('%Y-%m-%d').tolist()
    return dates

# Streamlit UI
st.title("Oil Price Prediction Dashboard")

# Sidebar for filters and inputs
st.sidebar.header("Filters")

# Oil Type Filter
oil_types = ['Crude Oil', 'Brent Oil', 'WTI Oil', 'Other Oil']
selected_oil_type = st.sidebar.selectbox("Select Oil Type", oil_types)

# Volume Filter
volume_min = st.sidebar.number_input("Min Volume Sold", min_value=0, step=1)
volume_max = st.sidebar.number_input("Max Volume Sold", min_value=0, step=1)

# Date Range Filter
start_date = st.sidebar.date_input("Start Date", pd.to_datetime('today'))
num_days_range = st.sidebar.slider("Select Prediction Range (Days)", min_value=1, max_value=30, value=(5, 15))

# Input form for entering data (e.g., closing price, selling price, volume sold)
st.header("Enter Data to Predict Future Oil Prices")

with st.form(key='oil_input_form'):
    closing_price = st.number_input("Closing Price", min_value=0.0, step=0.01)
    selling_price = st.number_input("Selling Price", min_value=0.0, step=0.01)
    volume_sold = st.number_input("Volume Sold", min_value=0, step=1)
    
    # Submit button
    submit_button = st.form_submit_button("Predict Future Prices")

# When the user submits the form
if submit_button:
    # Prepare the input data for prediction
    input_data = np.array([[closing_price, selling_price, volume_sold]])
    
    # Scale the input data
    scaled_input_data = scaler.transform(input_data)
    
    # XGBoost prediction
    xgb_preds = xgb_model.predict(scaled_input_data).reshape(-1, 1)
    xgb_preds_scaled = scaler_preds.transform(xgb_preds)

    # Reshape data for LSTM (LSTM expects 3D input)
    xgb_preds_scaled_reshaped = np.reshape(xgb_preds_scaled, (xgb_preds_scaled.shape[0], 1, 1))

    # Predict prices for selected range of days
    future_predictions = []
    for day in range(num_days_range[0], num_days_range[1] + 1):
        lstm_pred = lstm_model.predict(xgb_preds_scaled_reshaped)
        future_predictions.append(lstm_pred[0][0])
    
    # Inverse scale predictions to get the actual price
    future_predictions_inverse = scaler_preds.inverse_transform(np.array(future_predictions).reshape(-1, 1))
    
    # Generate future dates
    future_dates = generate_dates(start_date, len(future_predictions_inverse))
    
    # Display the result
    st.subheader(f"Predicted Future Oil Prices for {selected_oil_type}")
    
    # Display future predictions as a table
    prediction_df = pd.DataFrame({
        "Date": future_dates,
        "Predicted Selling Price": future_predictions_inverse.flatten()
    })
    st.write(prediction_df)

    # Plotting the future predictions
    st.subheader("Prediction Trend Over Time")
    plt.figure(figsize=(10, 6))
    plt.plot(future_dates, future_predictions_inverse.flatten(), marker='o', color='blue', label='Predicted Price')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.title(f"Future Price Predictions for {selected_oil_type}")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    # Additional insights
    st.subheader("Price Sensitivity and Insights")
    st.write("This section will display price sensitivity analysis and how volume sold can impact prices.")