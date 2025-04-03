import sqlite3
from datetime import datetime
import pandas as pd
import time

class PriceMonitor:
    def __init__(self, db_path='electronics_pricing.db'):
        self.db_path = db_path

    def connect_db(self):
        return sqlite3.connect(self.db_path)

    def record_price_change(self, product_id, amazon_price, actual_price, competitor_price, stock_status):
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Calculate metrics
        discount_percentage = ((actual_price - amazon_price) / actual_price * 100) if actual_price > 0 else 0
        price_diff = competitor_price - amazon_price if competitor_price else 0
        
        # Insert into price_history
        cursor.execute('''
        INSERT INTO price_history 
        (product_id, amazon_price, actual_price, competitor_price, 
         discount_percentage, price_diff_vs_competitor, stock_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, amazon_price, actual_price, competitor_price, 
              discount_percentage, price_diff, stock_status))
        
        conn.commit()
        conn.close()

    def check_price_alerts(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Get active alerts
        cursor.execute('''
        SELECT a.id, a.product_id, p.name, a.alert_type, a.threshold_value, 
               ph.amazon_price, ph.competitor_price
        FROM price_alerts a
        JOIN products p ON a.product_id = p.product_id
        JOIN price_history ph ON p.product_id = ph.product_id
        WHERE a.is_active = 1
        AND ph.recorded_at = (
            SELECT MAX(recorded_at) 
            FROM price_history 
            WHERE product_id = a.product_id
        )
        ''')
        
        alerts = cursor.fetchall()
        triggered_alerts = []
        
        for alert in alerts:
            alert_id, product_id, name, alert_type, threshold, amazon_price, competitor_price = alert
            
            if alert_type == 'price_drop' and amazon_price <= threshold:
                triggered_alerts.append(f"Price Drop Alert: {name} is now Rs. {amazon_price} (Below Rs. {threshold})")
            elif alert_type == 'competitor_cheaper' and competitor_price < amazon_price:
                triggered_alerts.append(f"Competitor Alert: {name} is cheaper at competitor (Rs. {competitor_price} vs Rs. {amazon_price})")
        
        conn.close()
        return triggered_alerts

    def get_price_trends(self, product_id, days=30):
        conn = self.connect_db()
        
        query = f'''
        SELECT recorded_at, amazon_price, competitor_price
        FROM price_history
        WHERE product_id = {product_id}
        AND recorded_at >= date('now', '-{days} days')
        ORDER BY recorded_at
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def add_price_alert(self, product_id, alert_type, threshold_value):
        conn = self.connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO price_alerts (product_id, alert_type, threshold_value)
        VALUES (?, ?, ?)
        ''', (product_id, alert_type, threshold_value))
        
        conn.commit()
        conn.close()

def main():
    monitor = PriceMonitor()
    
    print("Price Monitor initialized. Available functions:")
    print("1. record_price_change() - Record new price data")
    print("2. check_price_alerts() - Check for triggered price alerts")
    print("3. get_price_trends() - Get historical price trends")
    print("4. add_price_alert() - Set up price monitoring alerts")
    
    print("\nExample usage:")
    print("monitor = PriceMonitor()")
    print("monitor.add_price_alert(product_id=1, alert_type='price_drop', threshold_value=1000)")
    print("monitor.check_price_alerts()")

if __name__ == "__main__":
    main()
