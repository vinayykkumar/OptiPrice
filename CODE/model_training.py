import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler

def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    """Train and evaluate multiple models"""
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),
        'XGBoost': XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            subsample=0.8,
            colsample_bytree=0.8
        )
    }
    
    results = {}
    best_model = None
    best_r2 = -np.inf
    
    for name, model in models.items():
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        accuracy = (1 - mape) * 100  # Convert MAPE to accuracy percentage
        
        # Store results
        results[name] = {
            'RMSE': rmse,
            'MAE': mae,
            'R2 Score': r2,
            'MAPE': mape,
            'Accuracy': accuracy
        }
        
        # Update best model
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
    
    return results, best_model, models

def save_model(model, scaler, label_encoders, metrics):
    """Save the trained model, preprocessing objects, and metrics"""
    joblib.dump(model, 'price_predictor_model.joblib')
    joblib.dump(scaler, 'scaler.joblib')
    joblib.dump(label_encoders, 'label_encoders.joblib')
    joblib.dump(metrics, 'model_metrics.joblib')

if __name__ == "__main__":
    # Load preprocessed data
    df = pd.read_csv('processed_data.csv')
    
    # Prepare data for modeling
    X = df.drop('Price (USD)', axis=1)
    y = df['Price (USD)']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train and evaluate all models
    results, best_model, models = train_and_evaluate_models(X_train, X_test, y_train, y_test)
    
    # Print results for all models
    print("\nModel Evaluation Results:")
    print("=" * 50)
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        print(f"R² Score: {metrics['R2 Score']:.4f}")
        print(f"Accuracy: {metrics['Accuracy']:.2f}%")
        print(f"RMSE: {metrics['RMSE']:.2f}")
        print(f"MAE: {metrics['MAE']:.2f}")
        print(f"MAPE: {metrics['MAPE']:.4f}")
    print("=" * 50)
    
    # Load the scaler and label encoders
    scaler = joblib.load('scaler.joblib')
    label_encoders = joblib.load('label_encoders.joblib')
    
    # Save the best model, preprocessing objects, and metrics
    save_model(best_model, scaler, label_encoders, results)

    # Specifically save the XGBoost model
    xgboost_model = models['XGBoost']
    joblib.dump(xgboost_model, 'xgboost_model.joblib') 