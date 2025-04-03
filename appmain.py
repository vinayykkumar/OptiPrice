import streamlit as st
import pandas as pd
import pickle  
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import random
import base64

# Load dataset
@st.cache_data
def load_data():
    file_path = r"C:\Users\THRINADH\OneDrive\Desktop\infosys\streamlit\ecommerce_price_predictor_combined_with_sales_discounted.xlsx"
    return pd.read_excel(file_path)
data = load_data()
data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

# Load trained model
@st.cache_resource
def load_model():
    with open(r"C:\Users\THRINADH\OneDrive\Desktop\infosys\streamlit\xgboost_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model
model = load_model()
st.sidebar.header("🔎 Product Filters")

# Custom CSS
st.markdown(
    """
    <style>
        @keyframes gradientAnimation {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        .title-container {
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            color: white;
            font-size: 50px;
            font-weight: bold;
            text-shadow: 3px 2px 5px rgba(0, 0, 0, 0.3);
            background: linear-gradient(-45deg, #1E3A8A, #2563EB, #3B82F6, #1E40AF);
            background-size: 400% 400%;
            animation: gradientAnimation 6s ease infinite;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        }
    </style>

    <div class="title-container">
        🔮 OptiPrice Prognosticator
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar: Category & Product Selection
categories = data['category'].unique()
selected_category = st.sidebar.selectbox("🗂️ Select Category", categories)
filtered_products = data[data['category'] == selected_category]['product_name'].unique()
selected_product = st.sidebar.selectbox("🛒 Select Product", filtered_products)

# Sidebar: Stock Level
stock_levels = ["High", "Moderate", "Low"]
selected_stock_level = st.sidebar.selectbox("📦 Demand Level", stock_levels)

# Main UI: Product Details Input
st.markdown("<h3 style='color:#0000000; font-weight: bold;'> Enter Product Features</h3>", unsafe_allow_html=True)

feature1 = st.number_input("💰 **Price (USD)**", min_value=0.0, value=20.0)
feature2 = st.number_input("📦 **Sales Volume (Units Sold)**", min_value=0.0, value=10.0)
feature3 = st.number_input("⚡ **Discount (%)**", min_value=0.0, value=5.0)
feature4 = st.number_input("🏷️ **Competitor Price (USD)**", min_value=0.0, value=20.0)
feature5 = st.number_input("📦 **Stock Availability**", min_value=0, value=100)
st.markdown("""
    <style>
        @keyframes gradientAnimation {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        div.stButton > button:first-child {
            background: linear-gradient(-45deg, #1E3A8A, #2563EB, #3B82F6, #1E40AF);
            background-size: 400% 400%;
            animation: gradientAnimation 6s ease infinite;
            color: white;
            font-size: 26px;
            font-weight: bold;
            font-family: 'Arial Black', sans-serif; /* Change Font */
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
            padding: 15px 30px;
            border-radius: 15px;
            border: none;
            box-shadow: 0px 5px 12px rgba(0, 0, 0, 0.35);
            transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        }

        div.stButton > button:first-child:hover {
            transform: scale(1.1);
            box-shadow: 0px 8px 18px rgba(0, 0, 0, 0.45);
        }
    </style>
""", unsafe_allow_html=True)


# 🔍 Prediction Button
if st.button("🔍 Predict Price"):

    input_features = [[feature1, feature2, feature3, feature4, feature5]]  
    predicted_price = model.predict(input_features)[0]
    
    # Apply stock level-based price adjustments
    if selected_stock_level == "High":
        discount = random.uniform(0.05, 0.15)  # 5% - 15% discount
        adjusted_price = predicted_price * (1 - discount)
    elif selected_stock_level == "Moderate":
        discount = random.uniform(0, 0.05)  # 0% - 5% discount
        adjusted_price = predicted_price * (1 - discount)
    elif selected_stock_level == "Low":
        markup = random.uniform(0.10, 0.30)  # 10% - 30% markup
        adjusted_price = predicted_price * (1 + markup)
    
    # 💡 Styled Prediction Output
    st.markdown(
        f"""
        <div style="padding: 15px; border-radius: 10px; background: #F0F8FF; text-align: center;">
            <h2 style="color: #0047AB; font-size: 28px;">🤖 Predicted Price: <span style="color: #D6336C;">${adjusted_price:.2f}</span></h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# Chart 1: Demand Distribution (Pie Chart)
st.subheader("Demand Distribution")
demand_distribution = data["category"].value_counts()
fig, ax = plt.subplots()
ax.pie(demand_distribution, labels=demand_distribution.index, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
st.pyplot(fig)

# Chart 2: Sales vs. Discounts (Scatter Plot)
st.subheader("Sales vs. Discounts")
fig, ax = plt.subplots()
sns.scatterplot(data=data, x="discount_(%)", y="sales_(units_sold)", hue="category", palette="coolwarm", ax=ax)
st.pyplot(fig)

# Chart 3: Category-wise Revenue (Bar Chart)
st.subheader("Category-wise Revenue")
category_revenue = data.groupby("category")["discounted_price_(usd)"].sum().reset_index()
fig, ax = plt.subplots()
sns.barplot(data=category_revenue, x="category", y="discounted_price_(usd)", palette="viridis", ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)

# Chart 4: Price Distribution (Histogram)
st.subheader("Price Distribution")
fig, ax = plt.subplots()
sns.histplot(data=data, x="price_(usd)", bins=20, kde=True, color='blue', ax=ax)
st.pyplot(fig)  

# Chart 5: Discount Impact on Sales (Line Chart)
st.subheader("Discount Impact on Sales")
discount_sales = data.groupby("discount_(%)")["sales_(units_sold)"].mean().reset_index()
fig, ax = plt.subplots()
sns.lineplot(data=discount_sales, x="discount_(%)", y="sales_(units_sold)", marker="o", color='red', ax=ax)
st.pyplot(fig)

# Chart 6: Box Plot of Price Adjustments
st.subheader("Price Adjustments Based on Stock Availability")
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=data, x="stock_availability", y="price_(usd)", palette="pastel", ax=ax)
st.pyplot(fig)
