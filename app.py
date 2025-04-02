import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Set dark theme
st.set_page_config(page_title="Cab Profit Prediction", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #1e1e1e; color: #d3d3d3;}
    .sidebar .sidebar-content {background-color: #2e2e2e;}
    .stButton>button {background-color: #4CAF50; color: white;}
    .stSlider>div>div>div {background-color: #555555;}
    h1, h2, h3 {color: #d3d3d3;}
    </style>
""", unsafe_allow_html=True)

# Load data and pickle files
data = pd.read_csv('merged_data.csv')
data.columns = data.columns.str.replace(' ', '_')

# Preprocess data to add required columns
data['Date_of_Travel'] = pd.to_datetime(data['Date_of_Travel'])
data['Travel_Year'] = data['Date_of_Travel'].dt.year
data['Travel_Month'] = data['Date_of_Travel'].dt.month
data['Travel_Day'] = data['Date_of_Travel'].dt.day
data = data.drop(columns=['Date_of_Travel'])
if 'Month' in data.columns:
    data = data.drop(columns=['Month'])

# Load model and metadata
with open('lightgbm_profit_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('metadata.pkl', 'rb') as f:
    metadata = pickle.load(f)
label_encoders = metadata['label_encoders']
avg_trips_pink = metadata['avg_trips_per_month_pink']
avg_trips_yellow = metadata['avg_trips_per_month_yellow']

# Apply label encoding to all categorical columns
categorical_cols = ['Company', 'City', 'Payment_Mode', 'Gender']
for col in categorical_cols:
    if col in data.columns:
        data[col] = label_encoders[col].transform(data[col])

# Decode company names for display
company_names = {0: 'Pink Cab', 1: 'Yellow Cab'}

# Function to generate future data with company ID
def generate_future_data(base_data, year, month, num_trips, company_id):
    if base_data.empty:
        st.error(f"No data available for {company_names[company_id]}.")
        return None, None
    historical_month_data = base_data[base_data['Travel_Month'] == month].copy()
    if historical_month_data.empty:
        historical_month_data = base_data.copy()
        st.warning(f"No data for month {month} in {company_names[company_id]}. Using all available data.")
    adjusted_trips = int(num_trips * (1 + 0.01) ** max(0, year - 2025))
    if adjusted_trips <= 0:
        st.error("Adjusted trips must be greater than 0.")
        return None, None
    future_data = historical_month_data.sample(n=adjusted_trips, replace=True, random_state=year).copy()
    future_data['Travel_Year'] = year
    future_data['Travel_Month'] = month
    future_data['Travel_Day'] = np.random.randint(1, 31, size=adjusted_trips)
    years_diff = year - 2018 + (month - 1) / 12
    future_data['Price_Charged'] *= (1 + 0.025) ** years_diff
    future_data['Cost_of_Trip'] *= (1 + 0.02) ** years_diff
    exclude_cols = ['Profit', 'Price_Charged', 'Cost_of_Trip', 'City_Distance']
    future_X = future_data.drop(columns=exclude_cols, errors='ignore')
    return future_X, future_data

# Sidebar
st.sidebar.title("Input Parameters")
year = st.sidebar.slider("Year", 2025, 2035, 2025)
month = st.sidebar.selectbox("Month", list(range(1, 13)), index=2)  # Default March (3)

# Main area
st.title("Cab Profit Prediction")
if st.sidebar.button("Predict"):
    # Predict for Pink Cab
    pink_X, pink_data = generate_future_data(data[data['Company'] == 0], year, month, avg_trips_pink, 0)
    if pink_X is None or pink_data is None:
        st.error("Prediction failed for Pink Cab.")
    else:
        pink_pred = model.predict(pink_X)
        pink_data['Predicted_Profit'] = pink_pred
        pink_profit = pink_data['Predicted_Profit'].sum()

    # Predict for Yellow Cab
    yellow_X, yellow_data = generate_future_data(data[data['Company'] == 1], year, month, avg_trips_yellow, 1)
    if yellow_X is None or yellow_data is None:
        st.error("Prediction failed for Yellow Cab.")
    else:
        yellow_pred = model.predict(yellow_X)
        yellow_data['Predicted_Profit'] = yellow_pred
        yellow_profit = yellow_data['Predicted_Profit'].sum()

    # Display results if both predictions succeed
    if pink_X is not None and yellow_X is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<h3 style='color: #FF69B4'>{company_names[0]}: ${pink_profit:,.2f}</h3>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<h3 style='color: #FFFF00'>{company_names[1]}: ${yellow_profit:,.2f}</h3>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h3>Total: ${(pink_profit + yellow_profit):,.2f}</h3>", unsafe_allow_html=True)
else:
    st.write("Enter year and month, then click 'Predict' to see results.")