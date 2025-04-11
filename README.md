# E-commerce Price Predictor

## Overview

The E-commerce Price Predictor is a Streamlit application designed to predict optimal product prices using machine learning models, specifically the XGBoost model. The app allows users to input product details and receive price predictions based on various features such as category, rating, discount, and reviews count. Additionally, the app provides insights into competitor pricing and market demand.

## Features

- **Price Prediction**: Predict optimal prices using the XGBoost model.
- **Product Details**: Input and view detailed product information.
- **Competitor Analysis**: Compare prices with competitors.
- **Demand Insights**: Visualize demand distribution and sales by category.
- **Downloadable Reports**: Export price analysis and competitor data.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies**:
   Ensure you have Python installed. Then, install the required packages using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download Pre-trained Models**:
   Ensure the following model files are in the project directory:
   - `xgboost_model.joblib`
   - `scaler.joblib`
   - `label_encoders.joblib`
   - `features.joblib`

4. **Prepare Data**:
   Ensure the data file `ecommerce_price_predictor_combined_with_sales_discounted.xlsx` is in the project directory.

## Usage

1. **Run the Application**:
   Start the Streamlit app by running:
   ```bash
   streamlit run app.py
   ```

2. **Interact with the App**:
   - Select a product category and product.
   - Input product details such as rating, discount, and reviews count.
   - Click "Predict Optimal Price" to get the price prediction.
   - View competitor information and demand insights.
   - Download the price analysis report.

## Project Structure

- `app.py`: Main application file for the Streamlit app.
- `model_training.py`: Script for training machine learning models.
- `requirements.txt`: List of Python dependencies.
- `ecommerce_price_predictor_combined_with_sales_discounted.xlsx`: Dataset used for predictions and analysis.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For questions or support, please contact [Your Name] at [Your Email]. 