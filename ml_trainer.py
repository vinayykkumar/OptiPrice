import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import sqlite3
from datetime import datetime, timedelta

class PriceMLTrainer:
    def __init__(self, db_path='electronics_pricing.db'):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        
    def load_data(self):
        conn = sqlite3.connect(self.db_path)
        
        # Load price history with product details
        query = '''
            SELECT 
                ph.*,
                p.brand,
                p.main_category,
                p.sub_category,
                p.product_category,
                p.ratings,
                p.no_of_ratings
            FROM price_history ph
            JOIN products p ON ph.product_id = p.product_id
        '''
        self.data = pd.read_sql_query(query, conn)
        conn.close()
        
        # Convert timestamp to datetime
        self.data['recorded_at'] = pd.to_datetime(self.data['recorded_at'])
        
        # Extract time features
        self.data['hour'] = self.data['recorded_at'].dt.hour
        self.data['day_of_week'] = self.data['recorded_at'].dt.dayofweek
        self.data['month'] = self.data['recorded_at'].dt.month
        
        # Calculate price volatility
        self.data['price_volatility'] = self.data.groupby('product_id')['amazon_price'].transform(lambda x: x.std())
        
    def preprocess_data(self):
        # Handle missing values
        numeric_columns = ['amazon_price', 'actual_price', 'competitor_price', 'ratings', 'no_of_ratings']
        for col in numeric_columns:
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            self.data[col].fillna(self.data[col].mean(), inplace=True)
            
        # Create label encoders for categorical variables
        categorical_columns = ['brand', 'main_category', 'sub_category', 'product_category']
        
        for col in categorical_columns:
            le = LabelEncoder()
            self.data[f'{col}_encoded'] = le.fit_transform(self.data[col].fillna('Unknown'))
            self.label_encoders[col] = le
            
        # Calculate price volatility with error handling
        self.data['price_volatility'] = self.data.groupby('product_id')['amazon_price'].transform(
            lambda x: x.std() if len(x) > 1 else 0
        )
        
        # Create feature sets for different models
        self.create_feature_sets()
        
    def create_feature_sets(self):
        # Features for price prediction
        self.price_features = [
            'hour', 'day_of_week', 'month',
            'brand_encoded', 'main_category_encoded',
            'sub_category_encoded', 'product_category_encoded',
            'ratings', 'no_of_ratings', 'competitor_price',
            'price_volatility'
        ]
        
        # Features for discount prediction
        self.discount_features = [
            'hour', 'day_of_week', 'month',
            'brand_encoded', 'main_category_encoded',
            'sub_category_encoded', 'product_category_encoded',
            'ratings', 'no_of_ratings', 'amazon_price',
            'competitor_price', 'price_volatility'
        ]
        
        # Features for volatility prediction
        self.volatility_features = [
            'brand_encoded', 'main_category_encoded',
            'sub_category_encoded', 'product_category_encoded',
            'ratings', 'no_of_ratings', 'amazon_price',
            'competitor_price'
        ]
        
    def train_price_predictor(self):
        X = self.data[self.price_features]
        y = self.data['amazon_price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        models = {
            'rf': RandomForestRegressor(n_estimators=100, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'lr': LinearRegression()
        }
        
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.fit(X_train_scaled, y_train).predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            print(f'{name.upper()} Price Predictor - R2: {r2:.4f}, RMSE: {rmse:.2f}')
            
            self.models[f'price_{name}'] = model
            
        self.scalers['price'] = scaler
        
    def train_discount_predictor(self):
        self.data['discount_percentage'] = ((self.data['actual_price'] - self.data['amazon_price']) / 
                                          self.data['actual_price'] * 100)
        
        X = self.data[self.discount_features]
        y = self.data['discount_percentage']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        print(f'Discount Predictor - R2: {r2:.4f}, RMSE: {rmse:.2f}')
        
        self.models['discount'] = model
        self.scalers['discount'] = scaler
        
    def train_volatility_predictor(self):
        X = self.data[self.volatility_features]
        y = self.data['price_volatility']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        print(f'Volatility Predictor - R2: {r2:.4f}, RMSE: {rmse:.2f}')
        
        self.models['volatility'] = model
        self.scalers['volatility'] = scaler
        
    def save_models(self, output_dir='models'):
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f'{output_dir}/{name}_model.joblib')
            
        # Save scalers
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'{output_dir}/{name}_scaler.joblib')
            
        # Save label encoders
        for name, encoder in self.label_encoders.items():
            joblib.dump(encoder, f'{output_dir}/{name}_encoder.joblib')
            
    def train_all(self):
        print("Loading data...")
        self.load_data()
        
        print("\nPreprocessing data...")
        self.preprocess_data()
        
        print("\nTraining price predictors...")
        self.train_price_predictor()
        
        print("\nTraining discount predictor...")
        self.train_discount_predictor()
        
        print("\nTraining volatility predictor...")
        self.train_volatility_predictor()
        
        print("\nSaving models...")
        self.save_models()
        
        print("\nTraining completed successfully!")

if __name__ == '__main__':
    trainer = PriceMLTrainer()
    trainer.train_all()
