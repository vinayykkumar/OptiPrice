# OptiPrice Prognosticator

A Streamlit-based web application for predicting optimal product prices using machine learning.

## 🚀 Features

- **Price Prediction**: Uses XGBoost model to predict optimal product prices
- **Interactive UI**: User-friendly interface with real-time predictions
- **Market Analysis**: Visualizes market trends and competitor prices
- **Demand Analysis**: Analyzes product demand across different categories
- **Stock Impact**: Shows how stock availability affects pricing decisions

## 📊 Key Visualizations

1. **Price Comparison**: Bar chart comparing predicted vs. competitor prices
2. **Demand Distribution**: Pie chart showing demand across categories
3. **Sales vs. Discounts**: Scatter plot analyzing discount impact on sales
4. **Category Revenue**: Bar chart showing revenue by category
5. **Price Distribution**: Histogram of price distribution
6. **Stock Impact**: Boxplot showing price adjustments based on stock availability

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

1. Start the Streamlit app:
```bash
streamlit run appmain.py
```

2. Open your web browser and navigate to:
```
http://localhost:8501
```

## 📝 Usage

1. **Select Product Category**: Choose from available product categories
2. **Select Product**: Pick a specific product from the selected category
3. **Select Demand Level**: Choose between Low, Medium, or High demand
4. **Enter Features**:
   - 💰 Price (USD)
   - 📦 Sales Volume (Units Sold)
   - ⚡ Discount (%)
   - 🏷️ Competitor Price (USD)
   - 📦 Stock Availability
6. **Get Prediction**: Click "Predict Price" to see the optimal price

## 📈 Data Sources

- Product data from `ecommerce_price_predictor_combined_with_sales_discounted.xlsx`
- Trained XGBoost model from `xgboost_model.pkl`

## 🧩 Dependencies

- streamlit==1.32.0
- pandas==2.2.1
- numpy==1.26.4
- matplotlib==3.8.2
- seaborn==0.13.2
- scikit-learn==1.4.2
- xgboost==3.0.0
- openpyxl==3.1.2
- plotly==5.19.0



## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For any questions or suggestions, please open an issue in the repository. # OptiPrice
