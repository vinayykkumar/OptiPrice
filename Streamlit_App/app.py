import streamlit as st
import numpy as np
import re
import pickle
from xgboost import XGBRegressor
import pandas as pd

# Load the trained XGBoost model
with open("xgb_model.pkl", "rb") as model_file:
    xgb_model = pickle.load(model_file)

# Sample dataset (Replace with actual dataset)
data = {
    "departure": ["USA", "Canada", "India", "Japan", "Germany", "Brazil", "France", "UK", "South Africa", "Australia"],
    "destination": ["Tokyo", "New York", "Paris", "Bangkok", "Sydney", "Toronto", "Singapore", "Dubai", "Cape Town", "Rome"],
    "flight_price": np.random.randint(500, 2000, 10),
    "hotel_price": np.random.randint(100, 800, 10)
}
df = pd.DataFrame(data)

month_price_adjustments = {
    1: 220, 2: 220,  
    4: 442, 5: 442,  
    6: 132, 8: 132,  
    9: 238, 10: 238,  
    11: 485, 12: 485  
}

# Function to predict travel cost
def predict_travel_cost(departure, destination, departure_date, return_date, interests):
    try:
        departure_day, departure_month, _ = departure_date.split(" ")
        return_day, return_month, _ = return_date.split(" ")

        departure_day = int(re.sub(r"(st|nd|rd|th)", "", departure_day))
        return_day = int(re.sub(r"(st|nd|rd|th)", "", return_day))

        months_dict = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
        }

        departure_month = months_dict[departure_month]
        return_month = months_dict[return_month]

        num_interests = len(interests)
        activities_charges = 200 if num_interests == 1 else 400 if num_interests == 2 else 600

        matching_row = df[(df["departure"] == departure) & (df["destination"] == destination)]

        flight_price = matching_row.iloc[0]["flight_price"] if not matching_row.empty else 1000
        hotel_price = matching_row.iloc[0]["hotel_price"] if not matching_row.empty else 500

        flight_price += month_price_adjustments.get(departure_month, 0)
        hotel_price += month_price_adjustments.get(departure_month, 0)

        season = (departure_month // 3)
        budget_category = 2  

        input_data = np.array([[departure_day, departure_month, return_day, return_month, flight_price, hotel_price, activities_charges, season, budget_category]])

        predicted_flight_price = xgb_model.predict(input_data)[0] + month_price_adjustments.get(departure_month, 0)
        predicted_hotel_price = (xgb_model.predict(input_data)[0] / 2) + (month_price_adjustments.get(departure_month, 0) / 2)

        total_estimated_cost = predicted_flight_price + predicted_hotel_price + activities_charges
        return total_estimated_cost
    except Exception:
        st.error("⚠️ Error in processing input. Please check your date format.")
        return None

# Streamlit UI
st.set_page_config(page_title="Travel Cost Estimator", page_icon="✈️", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #121212; color: #ffffff; }
        .title { text-align: center; font-size: 32px; font-weight: bold; color: #1db954; }
        .stButton>button { background-color: #1db954; color: white; border-radius: 8px; padding: 10px; width: 100%; font-size: 16px; }
        .stTextInput>div>div>input, .stMultiSelect>div>div { border-radius: 8px; background-color: #333; color: white; border: 1px solid #1db954; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>🌍 Travel Cost Estimator ✈️</h1>", unsafe_allow_html=True)

with st.container():
    departure = st.selectbox("🏠 Departure City", df["departure"].unique())
    destination = st.selectbox("📍 Destination City", df["destination"].unique())
    departure_date = st.text_input("📅 Departure Date (e.g., 12th May 2025)")
    return_date = st.text_input("📅 Return Date (e.g., 31st May 2025)")
    interests = st.multiselect("🎭 Select Interests", ["Food", "Sightseeing", "Adventure", "Spiritual", "Culture"])

if st.button("🚀 Estimate Cost"):
    if departure and destination and departure_date and return_date:
        total_cost = predict_travel_cost(departure, destination, departure_date, return_date, interests)
        if total_cost:
            st.success(f"💰 Estimated Total Charges: **${total_cost:.2f}**")
    else:
        st.error("⚠️ Please fill in all required fields.")