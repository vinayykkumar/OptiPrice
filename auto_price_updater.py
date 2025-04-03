import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import time
import random
from price_monitor import PriceMonitor

class AutoPriceUpdater:
    def __init__(self, db_path='electronics_pricing.db'):
        self.db_path = db_path
        self.monitor = PriceMonitor(db_path)
        
    def connect_db(self):
        return sqlite3.connect(self.db_path)

    def get_current_prices(self):
        conn = self.connect_db()
        query = '''
        SELECT p.product_id, p.name, ph.amazon_price, ph.actual_price, 
               ph.competitor_price, ph.stock_status
        FROM products p
        JOIN price_history ph ON p.product_id = ph.product_id
        WHERE ph.recorded_at = (
            SELECT MAX(recorded_at)
            FROM price_history
            WHERE product_id = p.product_id
        )
        '''
        prices_df = pd.read_sql_query(query, conn)
        conn.close()
        return prices_df

    def simulate_price_change(self, current_price, max_change_percent=5):
        """Simulate realistic price changes"""
        if pd.isna(current_price) or current_price == 0:
            return current_price
            
        # 70% chance of no price change
        if random.random() < 0.7:
            return current_price
            
        max_change = current_price * (max_change_percent / 100)
        change = random.uniform(-max_change, max_change)
        new_price = round(current_price + change, 2)
        return max(new_price, 0.01)  # Ensure price doesn't go below 0.01

    def simulate_stock_status(self, current_status):
        """Simulate stock status changes"""
        if random.random() < 0.95:  # 95% chance to keep current status
            return current_status
        return random.choice(['In Stock', 'Out of Stock'])

    def simulate_competitor_response(self, amazon_price, current_competitor_price):
        """Simulate competitor price responses"""
        if pd.isna(current_competitor_price) or current_competitor_price == 0:
            return current_competitor_price

        # Competitor has 20% chance to respond to Amazon's price
        if random.random() < 0.2:
            # Competitor tries to undercut or match Amazon's price
            price_diff = amazon_price - current_competitor_price
            if price_diff < 0:  # Amazon is cheaper
                # 70% chance competitor will try to match or beat Amazon's price
                if random.random() < 0.7:
                    new_price = amazon_price * random.uniform(0.95, 1.02)
                    return round(new_price, 2)
            else:  # Amazon is more expensive
                # 30% chance competitor will increase their price
                if random.random() < 0.3:
                    new_price = amazon_price * random.uniform(0.9, 0.98)
                    return round(new_price, 2)
        
        # If no response, apply small random fluctuation
        return self.simulate_price_change(current_competitor_price, max_change_percent=2)

    def update_prices(self):
        """Update prices for all products"""
        current_prices = self.get_current_prices()
        updates = 0
        
        for _, row in current_prices.iterrows():
            # Simulate new prices
            new_amazon_price = self.simulate_price_change(row['amazon_price'])
            new_actual_price = max(new_amazon_price, 
                                 self.simulate_price_change(row['actual_price']))
            new_competitor_price = self.simulate_competitor_response(
                new_amazon_price, row['competitor_price'])
            new_stock_status = self.simulate_stock_status(row['stock_status'])
            
            # Only record if there's a change
            if (new_amazon_price != row['amazon_price'] or 
                new_actual_price != row['actual_price'] or
                new_competitor_price != row['competitor_price'] or
                new_stock_status != row['stock_status']):
                
                self.monitor.record_price_change(
                    product_id=row['product_id'],
                    amazon_price=new_amazon_price,
                    actual_price=new_actual_price,
                    competitor_price=new_competitor_price,
                    stock_status=new_stock_status
                )
                updates += 1
        
        return updates

def run_continuous_updates(interval_seconds=300):  # 5 minutes default
    updater = AutoPriceUpdater()
    print(f"Starting automated price updates every {interval_seconds} seconds...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            start_time = time.time()
            
            # Update prices
            updates = updater.update_prices()
            
            # Check for alerts
            alerts = updater.monitor.check_price_alerts()
            
            # Print status
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"Updated {updates} products")
            if alerts:
                print("\nPrice Alerts:")
                for alert in alerts:
                    print(f"- {alert}")
            
            # Wait for next update
            elapsed = time.time() - start_time
            sleep_time = max(0, interval_seconds - elapsed)
            if sleep_time > 0:
                print(f"\nNext update in {sleep_time:.0f} seconds...")
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\nStopping price updates...")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated price updater')
    parser.add_argument('--interval', type=int, default=300,
                      help='Update interval in seconds (default: 300)')
    args = parser.parse_args()
    
    run_continuous_updates(args.interval)
