import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

# Set dark theme
st.set_page_config(page_title="Cab Profit Analysis Dashboard", layout="wide")
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

# Preprocess data
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

# Decode company and city names
company_names = {0: 'Pink Cab', 1: 'Yellow Cab'}
city_names = {i: name for i, name in enumerate(label_encoders['City'].classes_)}
RMSE = 68.93  # From earlier output

# Function to generate future data
def generate_future_data(base_data, year, month, num_trips, company_id, avg_distance=None):
    if base_data.empty:
        st.error(f"No data available for {company_names[company_id]}.")
        return None, None
    historical_month_data = base_data[base_data['Travel_Month'] == month].copy()
    if historical_month_data.empty:
        historical_month_data = base_data.copy()
        st.warning(f"No data for month {month} in {company_names[company_id]}. Using all available data.")
    
    # Differentiate trip growth: Pink Cab 1.5%, Yellow Cab 2.5%
    trip_growth_rate = 0.015 if company_id == 0 else 0.025
    adjusted_trips = int(num_trips * (1 + trip_growth_rate) ** max(0, year - 2025))
    
    future_data = historical_month_data.sample(n=adjusted_trips, replace=True, random_state=year).copy()
    future_data['Travel_Year'] = year
    future_data['Travel_Month'] = month
    future_data['Travel_Day'] = np.random.randint(1, 31, size=adjusted_trips)
    
    # Adjust distance
    distance_growth = 1 + 0.005 * max(0, year - 2025)  # 0.5% annual distance increase
    if avg_distance:
        future_data['Distance_Travelled(KM)'] = np.random.normal(avg_distance * distance_growth, 5, adjusted_trips).clip(min=1)
    else:
        future_data['Distance_Travelled(KM)'] *= distance_growth
    
    # Differentiate inflation: Pink Cab 2%, Yellow Cab 3% for price
    years_diff = year - 2018 + (month - 1) / 12
    price_inflation = 0.02 if company_id == 0 else 0.03
    future_data['Price_Charged'] *= (1 + price_inflation) ** years_diff
    future_data['Cost_of_Trip'] *= (1 + 0.02) ** years_diff
    
    exclude_cols = ['Profit', 'Price_Charged', 'Cost_of_Trip', 'City_Distance']
    future_X = future_data.drop(columns=exclude_cols, errors='ignore')
    return future_X, future_data

# Sidebar
st.sidebar.title("Advanced Options")
city_options = ["All Cities"] + list(city_names.values())
selected_city = st.sidebar.selectbox("Filter by City", city_options)
avg_distance = st.sidebar.slider("Average Trip Distance (km)", 5, 50, 20)
show_trend = st.sidebar.checkbox("Show Trend Analysis")
if show_trend:
    start_year_trend = st.sidebar.text_input("Trend Start Year", value="2025")
    end_year_trend = st.sidebar.text_input("Trend End Year", value="2030")

# Filter data by city if selected
if selected_city != "All Cities":
    city_id = list(city_names.keys())[list(city_names.values()).index(selected_city)]
    filtered_data = data[data['City'] == city_id]
else:
    filtered_data = data

# Main page inputs
st.title("Cab Profit Analysis Dashboard")
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    year = st.text_input("Year", value="2025")
with col2:
    month = st.text_input("Month", value="3")
with col3:
    predict_button = st.button("Predict")

# Process prediction
if predict_button:
    try:
        year = int(year)
        month = int(month)
        if not (2025 <= year <= 2035) or not (1 <= month <= 12):
            st.error("Year must be 2025-2035, Month must be 1-12.")
        else:
            # Predict for Pink Cab
            pink_X, pink_data = generate_future_data(filtered_data[filtered_data['Company'] == 0], year, month, avg_trips_pink, 0, avg_distance)
            if pink_X is not None:
                pink_pred = model.predict(pink_X)
                pink_data['Predicted_Profit'] = pink_pred
                pink_profit = pink_data['Predicted_Profit'].sum()

            # Predict for Yellow Cab
            yellow_X, yellow_data = generate_future_data(filtered_data[filtered_data['Company'] == 1], year, month, avg_trips_yellow, 1, avg_distance)
            if yellow_X is not None:
                yellow_pred = model.predict(yellow_X)
                yellow_data['Predicted_Profit'] = yellow_pred
                yellow_profit = yellow_data['Predicted_Profit'].sum()

            # Tabs
            tab1, tab2, tab3 = st.tabs(["Predictions", "City Analysis", "Model Insights"])

            # Predictions Tab
            with tab1:
                if pink_X is not None and yellow_X is not None:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"<h3 style='color: #FF69B4'>{company_names[0]}: ${pink_profit:,.2f} (±${RMSE:,.2f})</h3>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<h3 style='color: #FFFF00'>{company_names[1]}: ${yellow_profit:,.2f} (±${RMSE:,.2f})</h3>", unsafe_allow_html=True)
                    with col3:
                        total_profit = pink_profit + yellow_profit
                        total_rmse = RMSE * np.sqrt(2)
                        st.markdown(f"<h3>Total: ${total_profit:,.2f} (±${total_rmse:,.2f})</h3>", unsafe_allow_html=True)

                    # Trend Analysis (if enabled)
                    if show_trend:
                        try:
                            start_year_trend = int(start_year_trend)
                            end_year_trend = int(end_year_trend)
                            if not (2025 <= start_year_trend <= 2035) or not (2025 <= end_year_trend <= 2035) or start_year_trend > end_year_trend:
                                st.error("Trend years must be 2025-2035, and Start Year must be less than or equal to End Year.")
                            else:
                                trend_data = []
                                for y in range(start_year_trend, end_year_trend + 1):
                                    p_X, p_data = generate_future_data(filtered_data[filtered_data['Company'] == 0], y, month, avg_trips_pink, 0, avg_distance)
                                    y_X, y_data = generate_future_data(filtered_data[filtered_data['Company'] == 1], y, month, avg_trips_yellow, 1, avg_distance)
                                    if p_X is not None and y_X is not None:
                                        p_pred = model.predict(p_X)
                                        y_pred = model.predict(y_X)
                                        p_data['Predicted_Profit'] = p_pred
                                        y_data['Predicted_Profit'] = y_pred
                                        p_profit = p_data['Predicted_Profit'].sum()
                                        y_profit = y_data['Predicted_Profit'].sum()
                                        trend_data.append({
                                            'Year': y,
                                            'Pink Cab': p_profit,
                                            'Yellow Cab': y_profit,
                                            'Total': p_profit + y_profit
                                        })
                                if trend_data:
                                    trend_df = pd.DataFrame(trend_data)
                                    fig, ax = plt.subplots(figsize=(10, 6))
                                    ax.plot(trend_df['Year'], trend_df['Pink Cab'], label='Pink Cab', color='#FF69B4')
                                    ax.plot(trend_df['Year'], trend_df['Yellow Cab'], label='Yellow Cab', color='#FFFF00')
                                    ax.plot(trend_df['Year'], trend_df['Total'], label='Total', color='#00CED1')
                                    ax.set_title(f"Profit Trend ({start_year_trend}-{end_year_trend})", color='white')
                                    ax.set_xlabel("Year", color='white')
                                    ax.set_ylabel("Profit ($)", color='white')
                                    ax.legend()
                                    ax.set_facecolor('#333333')
                                    fig.set_facecolor('#1e1e1e')
                                    ax.tick_params(colors='white')
                                    st.pyplot(fig)
                        except ValueError:
                            st.error("Please enter valid numeric values for Trend Start Year and End Year.")

            # City Analysis Tab
            with tab2:
                if pink_X is not None and yellow_X is not None:
                    future_data = pd.concat([pink_data, yellow_data])
                    city_profit = future_data.groupby(['City', 'Company'])['Predicted_Profit'].sum().unstack().fillna(0)
                    city_profit.index = label_encoders['City'].inverse_transform(city_profit.index)
                    fig, ax = plt.subplots(figsize=(12, 6))
                    city_profit.plot(kind='bar', ax=ax, color=['#FF69B4', '#FFFF00'], width=0.8)
                    ax.set_title(f"Profit by City ({year})", color='white')
                    ax.set_xlabel("City", color='white')
                    ax.set_ylabel("Profit ($)", color='white')
                    ax.legend(["Pink Cab", "Yellow Cab"])
                    ax.set_facecolor('#333333')
                    fig.set_facecolor('#1e1e1e')
                    ax.tick_params(colors='white')
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)

                    city_stats = future_data.groupby('City').agg({
                        'Predicted_Profit': ['sum', 'mean', 'count']
                    }).reset_index()
                    city_stats.columns = ['City', 'Total Profit', 'Avg Profit/Trip', 'Trip Count']
                    city_stats['City'] = label_encoders['City'].inverse_transform(city_stats['City'])
                    st.table(city_stats.style.format({'Total Profit': "${:,.2f}", 'Avg Profit/Trip': "${:.2f}"}))

            # Model Insights Tab
            with tab3:
                fig, ax = plt.subplots(figsize=(10, 6))
                importance_df = pd.DataFrame({'Feature': model.feature_name_, 'Importance': model.feature_importances_})
                sns.barplot(x='Importance', y='Feature', data=importance_df.sort_values('Importance', ascending=False), ax=ax, color='#4682B4')
                ax.set_title("Feature Importance", color='white')
                ax.set_xlabel("Importance Score", color='white')
                ax.set_ylabel("Feature", color='white')
                ax.set_facecolor('#333333')
                fig.set_facecolor('#1e1e1e')
                ax.tick_params(colors='white')
                st.pyplot(fig)
    except ValueError:
        st.error("Please enter valid numeric values for Year and Month.")
else:
    st.write("Enter year and month, then click 'Predict' to see results.")