import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import plotly.express as px
import joblib

def load_data(file_path):
    """Load and return the dataset"""
    df = pd.read_excel(file_path)
    return df

def basic_info(df):
    """Display basic information about the dataset"""
    print("\nDataset Shape:", df.shape)
    print("\nData Types:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nBasic Statistics:")
    print(df.describe())

def perform_eda(df):
    """Perform exploratory data analysis"""
    # Price distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Price (USD)'], kde=True)
    plt.title('Price Distribution')
    plt.savefig('price_distribution.png')
    plt.close()

    # Top categories
    plt.figure(figsize=(12, 6))
    df['Category'].value_counts().head(10).plot(kind='bar')
    plt.title('Top 10 Categories')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('top_categories.png')
    plt.close()

    # Brand vs Price
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Brand', y='Price (USD)', data=df)
    plt.title('Brand vs Price')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('brand_vs_price.png')
    plt.close()

    # Rating vs Price
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Rating', y='Price (USD)', data=df)
    plt.title('Rating vs Price')
    plt.savefig('rating_vs_price.png')
    plt.close()

def preprocess_data(df):
    """Preprocess the data for modeling"""
    # Select relevant features
    features = ['Category', 'Brand', 'Rating', 'Discount (%)', 'Reviews Count', 'Price (USD)']
    df = df[features].copy()
    
    # Handle missing values
    df = df.dropna(subset=['Price (USD)'])  # Drop rows with missing prices
    
    # Fill missing values in categorical columns with mode
    categorical_cols = ['Category', 'Brand']
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
    
    # Fill missing values in numerical columns with median
    numerical_cols = ['Rating', 'Discount (%)', 'Reviews Count']
    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())
    
    # Encode categorical variables
    label_encoders = {}
    for col in categorical_cols:
        label_encoders[col] = LabelEncoder()
        df[col] = label_encoders[col].fit_transform(df[col])
    
    # Scale numerical features
    scaler = StandardScaler()
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    
    return df, label_encoders, scaler, features

def prepare_data_for_modeling(df, target_col='Price (USD)'):
    """Prepare data for modeling"""
    X = df.drop(target_col, axis=1)
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    # Load data
    df = load_data('ecommerce_price_predictor_combined_with_sales_discounted.xlsx')
    
    # Display basic information
    basic_info(df)
    
    # Perform EDA
    perform_eda(df)
    
    # Preprocess data
    df_processed, label_encoders, scaler, features = preprocess_data(df)
    
    # Prepare data for modeling
    X_train, X_test, y_train, y_test = prepare_data_for_modeling(df_processed)
    
    # Save preprocessed data and encoders
    df_processed.to_csv('processed_data.csv', index=False)
    joblib.dump(label_encoders, 'label_encoders.joblib')
    joblib.dump(scaler, 'scaler.joblib')
    joblib.dump(features, 'features.joblib') 