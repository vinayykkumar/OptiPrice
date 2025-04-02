import streamlit as st
import joblib
import numpy as np
from tensorflow.keras.models import load_model

# Load your models and scalers
xgb_model = joblib.load("xgb_model.pkl")
lstm_model = load_model("lstm_model.h5", compile=False)  # Avoid compiling during load
scaler = joblib.load("feature_scaler.pkl")
scaler_preds = joblib.load("prediction_scaler.pkl")

# Streamlit UI
st.title("Oil Price Prediction")

# Input form for user to enter data
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

    # LSTM prediction
    future_predictions = lstm_model.predict(xgb_preds_scaled_reshaped)
    
    # Inverse scale predictions to get the actual price
    future_predictions_inverse = scaler_preds.inverse_transform(future_predictions)
    
    # Display the result
    st.subheader("Predicted Future Oil Prices")
    st.write(f"Predicted Selling Price: {future_predictions_inverse[0][0]:.2f}")
