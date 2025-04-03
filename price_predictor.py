import joblib
import pandas as pd
import numpy as np
from datetime import datetime

class PricePredictor:
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.load_models()
        
    def load_models(self):
        """Load all trained models, scalers, and encoders"""
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        
        # Load price prediction models
        for model_type in ['rf', 'gb', 'lr']:
            self.models[f'price_{model_type}'] = joblib.load(f'{self.models_dir}/price_{model_type}_model.joblib')
            
        # Load other models
        self.models['discount'] = joblib.load(f'{self.models_dir}/discount_model.joblib')
        self.models['volatility'] = joblib.load(f'{self.models_dir}/volatility_model.joblib')
        
        # Load scalers
        for scaler_type in ['price', 'discount', 'volatility']:
            self.scalers[scaler_type] = joblib.load(f'{self.models_dir}/{scaler_type}_scaler.joblib')
            
        # Load label encoders
        for category in ['brand', 'main_category', 'sub_category', 'product_category']:
            self.label_encoders[category] = joblib.load(f'{self.models_dir}/{category}_encoder.joblib')
            
    def prepare_features(self, product_data, current_price, competitor_price):
        """Prepare feature vector for prediction"""
        now = datetime.now()
        
        # Encode categorical features
        encoded_features = {}
        for category in ['brand', 'main_category', 'sub_category', 'product_category']:
            try:
                encoded_features[f'{category}_encoded'] = self.label_encoders[category].transform([product_data[category]])[0]
            except (KeyError, ValueError):
                # Handle unknown categories
                encoded_features[f'{category}_encoded'] = -1
                
        # Create feature dictionary
        features = {
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'month': now.month,
            'ratings': product_data['ratings'],
            'no_of_ratings': product_data['no_of_ratings'],
            'amazon_price': current_price,
            'competitor_price': competitor_price,
            'price_volatility': 0  # Will be updated with predicted volatility
        }
        
        # Combine all features
        features.update(encoded_features)
        return features
        
    def predict_price(self, product_data, current_price, competitor_price):
        """Predict future price using ensemble of models"""
        features = self.prepare_features(product_data, current_price, competitor_price)
        
        # First predict volatility
        volatility_features = pd.DataFrame([{
            k: v for k, v in features.items() 
            if k in ['brand_encoded', 'main_category_encoded', 'sub_category_encoded', 
                    'product_category_encoded', 'ratings', 'no_of_ratings', 
                    'amazon_price', 'competitor_price']
        }])
        
        volatility_scaled = self.scalers['volatility'].transform(volatility_features)
        predicted_volatility = self.models['volatility'].predict(volatility_scaled)[0]
        
        # Update features with predicted volatility
        features['price_volatility'] = predicted_volatility
        
        # Prepare features for price prediction
        price_features = pd.DataFrame([{
            k: v for k, v in features.items()
            if k in ['hour', 'day_of_week', 'month', 'brand_encoded', 
                    'main_category_encoded', 'sub_category_encoded', 
                    'product_category_encoded', 'ratings', 'no_of_ratings',
                    'competitor_price', 'price_volatility']
        }])
        
        # Scale features
        price_scaled = self.scalers['price'].transform(price_features)
        
        # Get predictions from all models
        predictions = {}
        weights = {'rf': 0.4, 'gb': 0.4, 'lr': 0.2}  # Model weights
        
        for model_type, weight in weights.items():
            pred = self.models[f'price_{model_type}'].predict(price_scaled)[0]
            predictions[model_type] = pred
            
        # Weighted ensemble prediction
        predicted_price = sum(pred * weights[model_type] 
                            for model_type, pred in predictions.items())
        
        return {
            'predicted_price': predicted_price,
            'model_predictions': predictions,
            'predicted_volatility': predicted_volatility
        }
        
    def predict_discount(self, product_data, current_price, competitor_price):
        """Predict potential discount percentage"""
        features = self.prepare_features(product_data, current_price, competitor_price)
        
        # Prepare features for discount prediction
        discount_features = pd.DataFrame([{
            k: v for k, v in features.items()
            if k in ['hour', 'day_of_week', 'month', 'brand_encoded',
                    'main_category_encoded', 'sub_category_encoded',
                    'product_category_encoded', 'ratings', 'no_of_ratings',
                    'amazon_price', 'competitor_price', 'price_volatility']
        }])
        
        # Scale features
        discount_scaled = self.scalers['discount'].transform(discount_features)
        
        # Predict discount
        predicted_discount = self.models['discount'].predict(discount_scaled)[0]
        
        return max(0, min(100, predicted_discount))  # Clip to valid percentage range
        
    def get_price_insights(self, product_data, current_price, competitor_price):
        """Get comprehensive price insights"""
        price_pred = self.predict_price(product_data, current_price, competitor_price)
        discount_pred = self.predict_discount(product_data, current_price, competitor_price)
        
        # Calculate price change
        price_change = price_pred['predicted_price'] - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Determine price trend
        if abs(price_change_pct) < 1:
            trend = "stable"
        else:
            trend = "increasing" if price_change > 0 else "decreasing"
            
        # Generate insights
        insights = {
            'current_price': current_price,
            'predicted_price': price_pred['predicted_price'],
            'price_change': price_change,
            'price_change_percentage': price_change_pct,
            'price_trend': trend,
            'predicted_discount': discount_pred,
            'price_volatility': price_pred['predicted_volatility'],
            'model_confidence': {
                model: abs(pred - price_pred['predicted_price'])
                for model, pred in price_pred['model_predictions'].items()
            },
            'competitive_position': 'above' if current_price > competitor_price else 'below',
            'price_gap': abs(current_price - competitor_price)
        }
        
        return insights
