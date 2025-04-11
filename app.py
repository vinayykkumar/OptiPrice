import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import io
import requests
import json

# Load the trained model and preprocessing objects
model = joblib.load('price_predictor_model.joblib')
scaler = joblib.load('scaler.joblib')
label_encoders = joblib.load('label_encoders.joblib')
features = joblib.load('features.joblib')

# Load the trained XGBoost model
xgboost_model = joblib.load('xgboost_model.joblib')

# Load the original data for comparison
df = pd.read_excel('ecommerce_price_predictor_combined_with_sales_discounted.xlsx')

def fetch_product_details(product_name):
    """Fetch product details using SERP API"""
    api_key = "77eb96b858b636fe6fc4232f8ce437275b31cd012f08596467489c76a76f985d"
    search_url = f"https://serpapi.com/search.json?engine=google_shopping&q={product_name}&api_key={api_key}"
    
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            if "shopping_results" in data and data["shopping_results"]:
                result = data["shopping_results"][0]
                # Clean the price string
                if 'price' in result:
                    result['price'] = float(result['price'].replace('$', '').replace(',', ''))
                return result
    except Exception as e:
        st.error(f"Error fetching product details: {str(e)}")
    return None

def preprocess_input(input_data, label_encoders, scaler):
    """Preprocess the input data for prediction"""
    # Create a DataFrame with the input data
    input_df = pd.DataFrame([input_data])
    
    # Encode categorical variables
    for col in ['Category', 'Brand']:
        if col in label_encoders:
            input_df[col] = label_encoders[col].transform(input_df[col])
    
    # Scale numerical features
    numerical_cols = ['Rating', 'Discount (%)', 'Reviews Count']
    input_df[numerical_cols] = scaler.transform(input_df[numerical_cols])
    
    return input_df

def rating_to_stars(rating):
    """Convert numeric rating to star symbols"""
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return '★' * full_stars + '☆' * half_star + ' ' * empty_stars

def convert_usd_to_inr(usd_price, conversion_rate=85.53):
    """Convert USD to INR using a fixed conversion rate"""
    return usd_price * conversion_rate

# Prepare the data for download
def prepare_download_data():
    # Example: Create a DataFrame for total price analysis
    total_price_analysis = df[['Product Name', 'Price (USD)', 'Sales (Units Sold)', 'Category']].copy()
    total_price_analysis['Total Sales (USD)'] = total_price_analysis['Price (USD)'] * total_price_analysis['Sales (Units Sold)']
    return total_price_analysis

# Convert DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Prepare the selected product data for download, including competitor information and suggested best price
def prepare_selected_product_data(selected_product, df, best_price, best_price_source, best_price_inr):
    # Extract relevant data for the selected product, including competitor information
    selected_data = df[df['Product Name'] == selected_product][[
        'Product Name', 'Price (USD)', 'Sales (Units Sold)', 'Category',
        'Competitor Name', 'Competitor Price (USD)', 'Competitor Rating'
    ]].copy()
    selected_data['Total Sales (USD)'] = selected_data['Price (USD)'] * selected_data['Sales (Units Sold)']
    
    # Add suggested best price information
    selected_data['Suggested Best Price (USD)'] = best_price
    selected_data['Suggested Best Price Source'] = best_price_source
    selected_data['Suggested Best Price (INR)'] = best_price_inr
    
    return selected_data

def main():
    # Set page config
    st.set_page_config(
        page_title="E-commerce Price Predictor",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.streamlit.io',
            'Report a bug': 'https://www.streamlit.io',
            'About': '# E-commerce Price Predictor App'
        }
    )
    
    # Custom CSS for styling
    st.markdown("""
        <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7fa;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 12px 28px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            transition: background 0.3s ease, transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #45a049, #4CAF50);
            transform: translateY(-3px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        .title-container {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            padding: 1.1rem;
            border-radius: 15px;
            margin-bottom: 2.5rem;
            text-align: center;
            color: white;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        .price-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .star-rating {
            font-size: 1.5rem;
            color: #FFD700;
            text-shadow: 1px 1px 2px #000;
        }
        @media (max-width: 768px) {
            .price-card, .title-container {
                padding: 10px;
                margin: 5px 0;
            }
            .stButton>button {
                font-size: 16px;
                padding: 10px 20px;
            }
            .star-rating {
                font-size: 1.2rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title container
    st.markdown("""
        <div class="title-container">
            <h1>🛍️ E-commerce Price Predictor</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Main content area with columns for product details and prediction input
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header('Product Details')
        
        # Get unique values for categorical features
        categories = sorted(df['Category'].unique().tolist())
        
        # Create input fields
        category = st.selectbox('Category', categories)
        
        # Show products in the selected category
        st.subheader('Products in Selected Category')
        category_products = sorted(df[df['Category'] == category]['Product Name'].unique().tolist())
        selected_product = st.selectbox('Select a Product', category_products)
        
        # Get product details
        product_data = df[df['Product Name'] == selected_product].iloc[0]
        product_brand = product_data['Brand']
        actual_price = float(product_data['Price (USD)'])
        
        # Fetch additional product details from SERP API
        serp_data = fetch_product_details(selected_product)
        
        # Get competitor information
        competitor_name = product_data['Competitor Name']
        competitor_price = float(product_data['Competitor Price (USD)'])
        competitor_rating = float(product_data['Competitor Rating'])

    with col2:
        st.subheader('Enter Product Details for Prediction')
        rating = st.slider('Rating', min_value=0.0, max_value=5.0, step=0.1, value=float(product_data['Rating']))
        discount = st.slider('Discount (%)', min_value=0.0, max_value=100.0, step=1.0, value=float(product_data['Discount (%)']))
        reviews_count = st.number_input('Reviews Count', min_value=0, step=1, value=int(product_data['Reviews Count']))
        
        # Create input data dictionary
        input_data = {
            'Category': category,
            'Brand': product_brand,
            'Rating': float(rating),
            'Discount (%)': float(discount),
            'Reviews Count': int(reviews_count)
        }
        
        # Prediction button
        predict_button = st.button('Predict Optimal Price', type='primary')

    # Rest of the content below in columns
    col3, col4 = st.columns([1, 1])

    with col3:
        st.subheader('Product Information')
        st.markdown("""
            <div class='price-card' style='padding: 5px; margin: 5px 0;'>
                <h3>Your Product</h3>
                <p><strong>Name:</strong> {}</p>
                <p><strong>Brand:</strong> {}</p>
                <p><strong>Current Price:</strong> ${:.2f}</p>
                <p><strong>Rating:</strong> <span class='star-rating'>{}</span></p>
                <p><strong>Discount:</strong> {}%</p>
                <p><strong>Reviews Count:</strong> {}</p>
            </div>
        """.format(selected_product, product_brand, actual_price, rating_to_stars(rating), discount, reviews_count), unsafe_allow_html=True)

        # Quadrant 3: Performance Metrics & Demand Level
        col5, col6 = st.columns([1, 1])
        with col5:
            st.subheader("📊 Performance Metrics")
            sales = product_data["Sales (Units Sold)"]
            satisfaction = product_data["Customer Satisfaction (%)"]
            profit_margin = product_data["Profit Margin (%)"]

            st.write(f"**Sales:** {sales} units")
            st.write(f"**Customer Satisfaction:** {satisfaction}%")
            st.write(f"**Profit Margin:** {profit_margin}%")

        with col6:
            st.subheader("📈 Demand Level & Price Changes")
            if sales > 1000 and satisfaction > 85:
                demand_level = "High Demand"
                price_change_reason = "Prices tend to increase due to high demand and limited stock."
                price_trend = "📈 Price may increase"
            elif 500 <= sales <= 1000 and 70 <= satisfaction <= 85:
                demand_level = "📉 Moderate Demand"
                price_change_reason = "Prices are stable but may fluctuate based on competitor actions."
                price_trend = "↔️ Price may stay the same"
            else:
                demand_level = "📉 Low Demand"
                price_change_reason = "Prices may drop due to low sales and customer interest."
                price_trend = "📉 Price may decrease"

            st.write(f"**Demand Level:** {demand_level}")
            st.write(f"**Price Trend:** {price_trend}")
            st.write(f"💡 **Why are prices changing?** {price_change_reason}")

    with col4:
        st.subheader('Competitor Information')
        details_col, image_col = st.columns([3, 2])
        
        with details_col:
            st.markdown("""
                <div class='price-card' style='padding: 10px; margin: 5px 0;'>
                    <h3>Competitor Product</h3>
                    <p><strong>Name:</strong> {}</p>
                    <p><strong>Rating:</strong> <span class='star-rating'>{}</span></p>
                    <p><strong>Price:</strong> ${:.2f}</p>
                </div>
            """.format(competitor_name, rating_to_stars(competitor_rating), competitor_price), unsafe_allow_html=True)
        
        with image_col:
            if serp_data and 'thumbnail' in serp_data:
                st.image(serp_data['thumbnail'], width=350)

        # Move Best Price section here
        if predict_button:
            # Preprocess input data
            processed_input = preprocess_input(input_data, label_encoders, scaler)
            
            # Make prediction using XGBoost model
            predicted_price = xgboost_model.predict(processed_input)[0]
            
            # Compare Current Price and Competitor Price to determine best price
            if actual_price < competitor_price:
                best_price = actual_price
                best_price_source = "Current Price"
            else:
                best_price = competitor_price
                best_price_source = "Competitor Price"

            # Convert the determined best price to INR
            best_price_inr = convert_usd_to_inr(best_price)

            # Display the best price suggestion in a full-width card model
            st.markdown(f"""
                <div style='background-color: #d4edda; padding: 2px 10px 0px 2px; width: 60%; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-top: 20px;'>
                    <h3 style='color: #155724; font-weight: bold; text-align: center;'>Best Price</h3>
                    <p style='color: #155724; font-size: 1.5rem; text-align: center;'><strong>$:</strong> ${best_price:.2f} ({best_price_source})</p>
                    <p style='color: #155724; font-size: 1.5rem; text-align: center;'><strong>INR:</strong> ₹{best_price_inr:.2f}</p>
                </div>
            """, unsafe_allow_html=True)

            # Prepare the selected product data for download
            selected_product_data = prepare_selected_product_data(selected_product, df, best_price, best_price_source, best_price_inr)
            csv_selected_data = convert_df_to_csv(selected_product_data)

            # Custom CSS for enhancing the download button and positioning it
            st.markdown("""
                <div class='download-container'>
            """, unsafe_allow_html=True)
            st.download_button(
                label="Download Price Analysis",
                data=csv_selected_data,
                file_name=f'{selected_product}_data_with_competitor.csv',
                mime='text/csv'
            )
            st.markdown("</div>", unsafe_allow_html=True)

    # Create a container for the charts
    st.markdown("""
        <div class='chart-container' style='background-color: #ffffff; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);'>
    """, unsafe_allow_html=True)

    # Create columns for the charts
    col1, col2 = st.columns(2)

    with col1:
        # Chart 1: Demand Distribution (Pie Chart)
        st.subheader("Demand Distribution")
        demand_distribution = df["Category"].value_counts()  # Ensure 'Category' is the correct column name
        fig, ax = plt.subplots(figsize=(6, 6))  # Adjust the size
        ax.pie(demand_distribution, labels=demand_distribution.index, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
        st.pyplot(fig)

    with col2:
        # Bar Chart: Sales by Category
        st.subheader("Sales by Category")
        # Group by category and sum sales, then sort by sales in descending order
        sales_by_category = df.groupby('Category')['Sales (Units Sold)'].sum().reset_index()
        sales_by_category = sales_by_category.sort_values(by='Sales (Units Sold)', ascending=False)
        
        fig = px.bar(sales_by_category, x='Category', y='Sales (Units Sold)', title='Sales by Category')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            height=400,
            xaxis_title='Category',
            yaxis_title='Units Sold',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # Create another set of columns for additional charts
    col3, col4 = st.columns(2)

    with col3:
        # Scatter Plot of Price vs Rating
        st.subheader("Scatter Plot of Price vs Rating")
        fig = px.scatter(df, x='Price (USD)', y='Rating', title='Scatter Plot of Price vs Rating')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            height=400,
            xaxis_title='Price (USD)',
            yaxis_title='Rating',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        
        st.subheader("Sales by Product")
        # Group by product and sum sales, then sort by sales in descending order
        sales_by_product = df.groupby('Product Name')['Sales (Units Sold)'].sum().reset_index()
        sales_by_product = sales_by_product.sort_values(by='Sales (Units Sold)', ascending=False)
        
        fig = px.bar(sales_by_product, x='Product Name', y='Sales (Units Sold)', title='Sales by Product')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            height=400,
            xaxis_title='Product Name',
            yaxis_title='Units Sold',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # Close the container
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()