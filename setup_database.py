import sqlite3
import pandas as pd
from datetime import datetime

def setup_database():
    # Create connection to database
    conn = sqlite3.connect('electronics_pricing.db')
    cursor = conn.cursor()

    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        brand TEXT,
        main_category TEXT,
        sub_category TEXT,
        product_category TEXT,
        ratings FLOAT,
        no_of_ratings INTEGER,
        stock_availability TEXT
    )
    ''')

    # Create price_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        amazon_price FLOAT,
        actual_price FLOAT,
        competitor_price FLOAT,
        discount_percentage FLOAT,
        price_diff_vs_competitor FLOAT,
        price_diff_percentage FLOAT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')

    # Create price_alerts table with enhanced alert types
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        alert_type TEXT,
        threshold_value FLOAT,
        comparison_type TEXT,
        notification_frequency TEXT,
        last_triggered TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')

    # Create alert history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            threshold_value REAL NOT NULL,
            comparison_type TEXT NOT NULL,
            triggered_value REAL NOT NULL,
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (alert_id) REFERENCES price_alerts (id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    # Load data from CSV
    df = pd.read_csv('../cleaned_electronics_dataset.csv')
    
    # Insert products data
    for _, row in df.iterrows():
        cursor.execute('''
        INSERT OR REPLACE INTO products (
            product_id, name, brand, main_category, sub_category, 
            product_category, ratings, no_of_ratings, stock_availability
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['product_id'], row['name'], row['brand'], 
            row['main_category'], row['sub_category'], row['product_category'],
            row['ratings'], row['no_of_ratings'], row['stock_availability']
        ))

        # Insert initial price history
        cursor.execute('''
        INSERT INTO price_history (
            product_id, amazon_price, actual_price, competitor_price,
            discount_percentage, price_diff_vs_competitor, price_diff_percentage
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['product_id'], row['discount_price'], row['actual_price'],
            row['competitor_price'], row['discount_percentage'],
            row['price_diff_vs_competitor'], row['price_diff_percentage']
        ))

    # Create comprehensive set of initial price alerts
    sample_alerts = [
        # Price drop alerts
        (1, 'price_drop', df.loc[0, 'discount_price'] * 0.9, 'percentage', 'immediate'),  # 10% price drop
        (2, 'price_drop', df.loc[1, 'discount_price'] * 0.85, 'percentage', 'daily'),    # 15% price drop
        
        # Competitor price alerts
        (3, 'competitor_cheaper', df.loc[2, 'discount_price'] * 0.95, 'absolute', 'immediate'),  # Competitor price 5% lower
        (4, 'competitor_higher', df.loc[3, 'discount_price'] * 1.1, 'absolute', 'daily'),       # Competitor price 10% higher
        
        # Price volatility alerts
        (5, 'price_volatility', 10.0, 'percentage', 'daily'),  # Alert on 10% price change in either direction
        
        # Stock alerts
        (6, 'stock_status', 0, 'status_change', 'immediate'),  # Alert on stock status changes
        
        # Discount alerts
        (7, 'discount_increase', 25.0, 'percentage', 'immediate'),  # Alert on discounts >= 25%
        
        # Price trend alerts
        (8, 'price_trend', 5.0, 'trend_change', 'weekly'),  # Alert on trend changes >= 5%
        
        # Market position alerts
        (9, 'market_position', -5.0, 'percentage', 'daily'),  # Alert when price is 5% below market average
        
        # Custom threshold alerts
        (10, 'custom_threshold', 999.99, 'absolute', 'immediate')  # Alert when price drops below specific value
    ]

    for product_id, alert_type, threshold, comparison_type, frequency in sample_alerts:
        cursor.execute('''
        INSERT INTO price_alerts (
            product_id, alert_type, threshold_value, 
            comparison_type, notification_frequency
        ) VALUES (?, ?, ?, ?, ?)
        ''', (product_id, alert_type, threshold, comparison_type, frequency))

    # Add some sample alert history data
    cursor.execute('''
        INSERT INTO alert_history (
            alert_id, product_id, alert_type, threshold_value, 
            comparison_type, triggered_value, triggered_at, details
        ) VALUES 
        (1, 1, 'price_drop', 499.99, 'absolute', 489.99, '2025-03-30 10:00:00', 'Price dropped below threshold'),
        (1, 1, 'price_drop', 499.99, 'absolute', 479.99, '2025-03-31 15:30:00', 'Price dropped further'),
        (2, 2, 'competitor_cheaper', 899.99, 'absolute', 849.99, '2025-03-31 09:15:00', 'Competitor price lower by 50'),
        (3, 3, 'discount_increase', 10.0, 'percentage', 15.0, '2025-04-01 11:20:00', 'Discount increased to 15%')
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    print("Database setup completed successfully!")
