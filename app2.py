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

# Decode company names for display
company_names = {0: 'Pink Cab', 1: 'Yellow Cab'}

# Function to generate future data
def generate_future_data(base_data, year, month, num_trips, company_id, trip_adj=0, price_inflation=0.025, cost_inflation=0.02):
    if base_data.empty:
        st.error(f"No data available for {company_names[company_id]}.")
        return None, None
    historical_month_data = base_data[base_data['Travel_Month'] == month].copy()
    if historical_month_data.empty:
        historical_month_data = base_data.copy()
        st.warning(f"No data for month {month} in {company_names[company_id]}. Using all available data.")
    adjusted_trips = int(num_trips * (1 + 0.01) ** max(0, year - 2025) * (1 + trip_adj / 100))
    if adjusted_trips <= 0:
        st.error("Adjusted trips must be greater than 0.")
        return None, None
    future_data = historical_month_data.sample(n=adjusted_trips, replace=True, random_state=year).copy()
    future_data['Travel_Year'] = year
    future_data['Travel_Month'] = month
    future_data['Travel_Day'] = np.random.randint(1, 31, size=adjusted_trips)
    years_diff = year - 2018 + (month - 1) / 12
    future_data['Price_Charged'] *= (1 + price_inflation) ** years_diff
    future_data['Cost_of_Trip'] *= (1 + cost_inflation) ** years_diff
    exclude_cols = ['Profit', 'Price_Charged', 'Cost_of_Trip', 'City_Distance']
    future_X = future_data.drop(columns=exclude_cols, errors='ignore')
    return future_X, future_data

# Sidebar for advanced features
st.sidebar.title("Advanced Options")
pink_trip_adj = st.sidebar.slider("Pink Cab Trip Change (%)", -20, 20, 0)
yellow_trip_adj = st.sidebar.slider("Yellow Cab Trip Change (%)", -20, 20, 0)
price_inflation = st.sidebar.slider("Price Inflation Rate (%)", 0.0, 5.0, 2.5) / 100
cost_inflation = st.sidebar.slider("Cost Inflation Rate (%)", 0.0, 5.0, 2.0) / 100
show_trend = st.sidebar.checkbox("Show 2025-2030 Trend")

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
            pink_X, pink_data = generate_future_data(data[data['Company'] == 0], year, month, avg_trips_pink, 0, pink_trip_adj, price_inflation, cost_inflation)
            if pink_X is not None:
                pink_pred = model.predict(pink_X)
                pink_data['Predicted_Profit'] = pink_pred
                pink_profit = pink_data['Predicted_Profit'].sum()

            # Predict for Yellow Cab
            yellow_X, yellow_data = generate_future_data(data[data['Company'] == 1], year, month, avg_trips_yellow, 1, yellow_trip_adj, price_inflation, cost_inflation)
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
                        st.markdown(f"<h3 style='color: #FF69B4'>{company_names[0]}: ${pink_profit:,.2f}</h3>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<h3 style='color: #FFFF00'>{company_names[1]}: ${yellow_profit:,.2f}</h3>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"<h3>Total: ${(pink_profit + yellow_profit):,.2f}</h3>", unsafe_allow_html=True)
                    if show_trend:
                        trend_data = []
                        for y in range(2025, 2031):
                            p_X, p_data = generate_future_data(data[data['Company'] == 0], y, month, avg_trips_pink, 0, pink_trip_adj, price_inflation, cost_inflation)
                            y_X, y_data = generate_future_data(data[data['Company'] == 1], y, month, avg_trips_yellow, 1, yellow_trip_adj, price_inflation, cost_inflation)
                            if p_X is not None and y_X is not None:
                                p_pred = model.predict(p_X)
                                y_pred = model.predict(y_X)
                                trend_data.append({
                                    'Year': y,
                                    'Pink Cab': p_pred.sum(),
                                    'Yellow Cab': y_pred.sum(),
                                    'Total': p_pred.sum() + y_pred.sum()
                                })
                        if trend_data:
                            trend_df = pd.DataFrame(trend_data)
                            fig, ax = plt.subplots(figsize=(10, 6))
                            ax.plot(trend_df['Year'], trend_df['Pink Cab'], label='Pink Cab', color='#FF69B4')
                            ax.plot(trend_df['Year'], trend_df['Yellow Cab'], label='Yellow Cab', color='#FFFF00')
                            ax.plot(trend_df['Year'], trend_df['Total'], label='Total', color='#00CED1')
                            ax.set_title("Profit Trend 2025-2030", color='white')
                            ax.set_xlabel("Year", color='white')
                            ax.set_ylabel("Profit ($)", color='white')
                            ax.legend()
                            ax.set_facecolor('#333333')
                            fig.set_facecolor('#1e1e1e')
                            ax.tick_params(colors='white')
                            st.pyplot(fig)

            # City Analysis Tab
            with tab2:
                if pink_X is not None and yellow_X is not None:
                    future_data = pd.concat([pink_data, yellow_data])
                    city_profit = future_data.groupby(['City', 'Company'])['Predicted_Profit'].sum().unstack().fillna(0)
                    city_profit.index = label_encoders['City'].inverse_transform(city_profit.index)
                    fig, ax = plt.subplots(figsize=(12, 6))
                    city_profit.plot(kind='bar', ax=ax, color=['#FF69B4', '#FFFF00'], width=0.8)
                    ax.set_title("Profit by City", color='white')
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