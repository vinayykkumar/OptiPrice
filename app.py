import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set page config FIRST
st.set_page_config(page_title="Oil Price Prediction", page_icon="⛽", layout="wide")

# Load data (updated caching)
@st.cache_data
def load_customer_data():
    return pd.read_csv('customer_data.csv')

@st.cache_data
def load_owner_data():
    return pd.read_csv('owner_data.csv')

# Main function
def main():
    st.title("Oil Price Prediction")

    # Sidebar for navigation
    option = st.sidebar.radio("Select View", ["Customer View", "Owner Dashboard"])

    if option == "Customer View":
        st.header("Customer View")
        customer_data = load_customer_data()

        oil_types = customer_data['Oil Type'].unique()
        cols = st.columns(len(oil_types))  

        for i, oil in enumerate(oil_types):
            with cols[i]:
                st.subheader(oil)
                oil_data = customer_data[customer_data['Oil Type'] == oil]
                for _, row in oil_data.iterrows():
                    st.write(f"Price: {row['Selling Price']} on {row['Date']}")

    elif option == "Owner Dashboard":
        st.header("Owner Dashboard")
        owner_data = load_owner_data()

        # Convert relevant columns to numeric (ensure proper data type for calculations)
        owner_data['competitor_profit_percent'] = pd.to_numeric(owner_data['competitor_profit_percent'], errors='coerce')
        owner_data['our_profit_percent'] = pd.to_numeric(owner_data['our_profit_percent'], errors='coerce')
        owner_data['Volume Sold'] = pd.to_numeric(owner_data['Volume Sold'], errors='coerce')
        owner_data['max_volume'] = pd.to_numeric(owner_data['max_volume'], errors='coerce')

        # 📊 Profit Margin Comparison - Show profit margin for us vs competitors
        st.subheader("📊 Profit Margin Comparison")
        
        profit_margin = owner_data.groupby('Oil Type').agg(
            avg_profit_us=('our_profit_percent', 'mean'),
            avg_profit_competitor=('competitor_profit_percent', 'mean')
        ).reset_index()

        # Plotting the bar graph for Profit Margin
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(profit_margin['Oil Type'], profit_margin['avg_profit_us'], width=0.4, label='Our Profit Margin', align='center')
        ax.bar(profit_margin['Oil Type'], profit_margin['avg_profit_competitor'], width=0.4, label='Competitor Profit Margin', align='edge')

        ax.set_xlabel('Oil Type')
        ax.set_ylabel('Average Profit Margin (%)')
        ax.set_title('Profit Margin Comparison: Our Company vs Competitors')
        ax.legend()

        st.pyplot(fig)

        # Bar Graph for Total Volume Sold
        st.subheader("📊 Total Volume Sold - Competitor vs Us")
        
        # Grouping by Oil Type to get the total volume sold by us and competitor
        total_volume = owner_data.groupby('Oil Type').agg(
            total_volume_us=('Volume Sold', 'sum'),
            total_volume_competitor=('max_volume', 'sum')
        ).reset_index()

        # Plotting the bar graph
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(total_volume['Oil Type'], total_volume['total_volume_us'], width=0.4, label='Our Volume Sold', align='center')
        ax.bar(total_volume['Oil Type'], total_volume['total_volume_competitor'], width=0.4, label='Competitor Volume Sold', align='edge')

        ax.set_xlabel('Oil Type')
        ax.set_ylabel('Total Volume Sold')
        ax.set_title('Total Volume Sold by Us vs Competitor')
        ax.legend()

        st.pyplot(fig)

        # Volume Trends and Selling Price Trends for each oil type
        oil_types = owner_data['Oil Type'].unique()
        for oil in oil_types:
            st.subheader(oil)
            oil_data = owner_data[owner_data['Oil Type'] == oil].copy()

            # Convert Date column to datetime
            oil_data['Date'] = pd.to_datetime(oil_data['Date'], format='%d-%m-%Y')

            # 📈 Total Profit Comparison – Show the total profit made by us vs. competitors over the last 10 days.
            total_profit_our = oil_data['our_profit_percent'].sum()
            total_profit_competitor = oil_data['competitor_profit_percent'].sum()

            st.write(f"**Total Profit Comparison over Last 10 Days for {oil}:**")
            st.write(f"Total Profit (Our Company): {total_profit_our:.2f}%")
            st.write(f"Total Profit (Competitors): {total_profit_competitor:.2f}%")

            # 📊 Volume Trends – Compare the volume sold by us vs. competitors over time.
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(oil_data['Date'], oil_data['Volume Sold'], label='Our Volume Sold', color='blue', marker='o')
            ax.plot(oil_data['Date'], oil_data['max_volume'], label='Competitor Volume Sold', color='red', marker='s')

            ax.set_xlabel('Date')
            ax.set_ylabel('Volume Sold')
            ax.set_title(f'Volume Trends for {oil}')
            ax.legend()

            # Format x-axis
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45)

            st.pyplot(fig)

            # 💹 Selling Price Trends – Show a line chart for how our selling price changes over the last 10 days compared to competitors.
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(oil_data['Date'], oil_data['Selling Price'], label='Our Selling Price', color='blue', marker='o')
            ax.plot(oil_data['Date'], oil_data['Selling Price'], label='Competitor Selling Price', color='red', marker='s')

            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            ax.set_title(f'Selling Price Trends for {oil}')
            ax.legend()

            # Format x-axis
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45)

            st.pyplot(fig)

if __name__ == "__main__":
    main()
