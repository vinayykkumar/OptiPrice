import streamlit as st
import numpy as np
import re
import pickle
from xgboost import XGBRegressor
import pandas as pd

# Load the trained XGBoost model
with open("xgb_model.pkl", "rb") as model_file:
    xgb_model = pickle.load(model_file)

data = {
    "departure": ["USA", "Canada", "India", "Japan", "Germany", "Brazil", "France", "UK", "South Africa", "Australia"],
    "destination": ["Tokyo", "New York", "Paris", "Bangkok", "Sydney", "Toronto", "Singapore", "Dubai", "Cape Town", "Rome"],
    "flight_price": np.random.randint(500, 2000, 10),
    "hotel_price": np.random.randint(100, 800, 10)
}
df = pd.DataFrame(data)

month_price_adjustments = {
    1: 220, 2: 120,  
    4: 442, 5: 642,  
    6: 232, 8: 132,  
    9: 238, 10: 338,  
    11: 485, 12: 685  
}

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
        if num_interests == 1:
            activities_charges = 200
        elif num_interests == 2:
            activities_charges = 400
        elif num_interests == 3:
            activities_charges = 600
        else:
            activities_charges = 800

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
        return predicted_flight_price, predicted_hotel_price, activities_charges, total_estimated_cost
    except Exception:
        st.error("⚠️ Error in processing input. Please check your date format.")
        return None, None, None, None

# Streamlit UI
st.set_page_config(page_title="Travel Cost Estimator", page_icon="✈️", layout="centered")

st.markdown("""
    <style>
        body {
            background-image: url('https://www.w3schools.com/w3images/mountains.jpg');
            background-size: cover;
            background-attachment: fixed;
            color: #fff;
            font-family: 'Arial', sans-serif;
        }
        .stApp { background-color: rgba(0, 0, 0, 0.7); color: #ffffff; }
        
        .title { 
            text-align: center; 
            font-size: 42px; 
            font-weight: bold; 
            color: #FF6F61; 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .stButton>button {
            background: linear-gradient(45deg, #FF6F61, #FF3B2D);
            color: white; 
            border-radius: 12px; 
            padding: 15px; 
            width: 100%; 
            font-size: 20px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background: linear-gradient(45deg, #FF3B2D, #FF6F61);
            transform: scale(1.05);
        }
        
        .stTextInput>div>div>input, .stMultiSelect>div>div {
            border-radius: 15px; 
            background-color: rgba(255, 255, 255, 0.3); 
            color: white; 
            font-size: 18px;
            padding: 12px;
            border: 1px solid #FF6F61;
        }
        
        .stTextInput>div>div>input:focus, .stMultiSelect>div>div:focus {
            border-color: #FF3B2D;
        }

        .stContainer {
            margin-top: 40px;
        }

        .stText {
            font-size: 18px; 
            font-weight: bold;
            color: #FF6F61;
        }

        .stMarkdown {
            color: #FF6F61;
            font-size: 22px;
            font-weight: bold;
        }

        .stCard {
            background-color: rgba(0, 0, 0, 0.7); 
            border-radius: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
            padding: 20px;
            margin-bottom: 30px;
        }
        
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>🌍 Travel Cost Estimator ✈️</h1>", unsafe_allow_html=True)

with st.container():
    departure = st.selectbox("🏠 Departure", df["departure"].unique(), key="departure")
    destination = st.selectbox("📍 Destination", df["destination"].unique(), key="destination")
    departure_date = st.text_input("📅 Departure Date (e.g., 12th May 2025)", key="departure_date")
    return_date = st.text_input("📅 Return Date (e.g., 31st May 2025)", key="return_date")
    interests = st.multiselect("🎭 Select Interests", ["Food", "Sightseeing", "Adventure", "Spiritual", "Culture"], key="interests")

if st.button("🚀 Estimate Cost", use_container_width=True):
    if departure and destination and departure_date and return_date:
        with st.spinner("Processing..."):
            flight_price, hotel_price, activities_charges, total_cost = predict_travel_cost(departure, destination, departure_date, return_date, interests)
        if total_cost:
            st.success(f"💰 Estimated Total Charges: **${total_cost:.2f}**")
            st.markdown(f"### Breakdown of Charges:")
            st.markdown(f"🚗 **Flight Charges**: ${flight_price:.2f}")
            st.markdown(f"🏨 **Hotel Charges**: ${hotel_price:.2f}")
            st.markdown(f"🎭 **Activities Charges**: ${activities_charges:.2f}")
    else:
        st.error("⚠️ Please fill in all required fields.")
