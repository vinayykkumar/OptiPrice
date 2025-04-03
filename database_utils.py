import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class DatabaseUtils:
    def __init__(self, db_path='electronics_pricing.db'):
        self.db_path = db_path

    def connect_db(self):
        return sqlite3.connect(self.db_path)

    def get_product_info(self, search_term=None, brand=None, limit=10):
        """Search for products by name or brand"""
        conn = self.connect_db()
        
        query = """
        SELECT p.*, 
               ph.amazon_price as current_price,
               ph.competitor_price as competitor_price,
               ph.stock_status
        FROM products p
        LEFT JOIN price_history ph ON p.product_id = ph.product_id
        WHERE ph.recorded_at = (
            SELECT MAX(recorded_at)
            FROM price_history
            WHERE product_id = p.product_id
        )
        """
        
        conditions = []
        params = []
        if search_term:
            conditions.append("p.name LIKE ?")
            params.append(f"%{search_term}%")
        if brand:
            conditions.append("p.brand LIKE ?")
            params.append(f"%{brand}%")
            
        if conditions:
            query += " AND " + " AND ".join(conditions)
            
        query += f" LIMIT {limit}"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

    def get_price_history(self, product_id, days=30):
        """Get price history for a specific product"""
        conn = self.connect_db()
        
        query = """
        SELECT p.name, p.brand,
               ph.recorded_at, ph.amazon_price, ph.competitor_price,
               ph.discount_percentage, ph.stock_status
        FROM products p
        JOIN price_history ph ON p.product_id = ph.product_id
        WHERE p.product_id = ?
        AND ph.recorded_at >= date('now', ?)
        ORDER BY ph.recorded_at
        """
        
        df = pd.read_sql_query(query, conn, params=[product_id, f'-{days} days'])
        conn.close()
        return df

    def get_best_deals(self, min_discount=30, min_ratings=100):
        """Find current best deals"""
        conn = self.connect_db()
        
        query = """
        SELECT p.name, p.brand, p.ratings, p.no_of_ratings,
               ph.amazon_price, ph.actual_price, ph.competitor_price,
               ph.discount_percentage
        FROM products p
        JOIN price_history ph ON p.product_id = ph.product_id
        WHERE ph.recorded_at = (
            SELECT MAX(recorded_at)
            FROM price_history
            WHERE product_id = p.product_id
        )
        AND ph.discount_percentage >= ?
        AND p.no_of_ratings >= ?
        ORDER BY ph.discount_percentage DESC
        LIMIT 10
        """
        
        df = pd.read_sql_query(query, conn, params=[min_discount, min_ratings])
        conn.close()
        return df

    def compare_with_competitors(self, min_price_diff=10):
        """Find products with significant price differences vs competitors"""
        conn = self.connect_db()
        
        query = """
        SELECT p.name, p.brand, p.ratings,
               ph.amazon_price, ph.competitor_price,
               ((ph.competitor_price - ph.amazon_price) / ph.competitor_price * 100) as price_diff_percent
        FROM products p
        JOIN price_history ph ON p.product_id = ph.product_id
        WHERE ph.recorded_at = (
            SELECT MAX(recorded_at)
            FROM price_history
            WHERE product_id = p.product_id
        )
        AND ABS(((ph.competitor_price - ph.amazon_price) / ph.competitor_price * 100)) >= ?
        ORDER BY ABS(((ph.competitor_price - ph.amazon_price) / ph.competitor_price * 100)) DESC
        LIMIT 10
        """
        
        df = pd.read_sql_query(query, conn, params=[min_price_diff])
        conn.close()
        return df

    def plot_price_trends(self, product_id):
        """Plot price trends for a product"""
        df = self.get_price_history(product_id)
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['recorded_at'], df['amazon_price'], label='Amazon Price')
        plt.plot(df['recorded_at'], df['competitor_price'], label='Competitor Price')
        plt.title(f"Price Trends for {df['name'].iloc[0]}")
        plt.xlabel('Date')
        plt.ylabel('Price (Rs.)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(f'price_trends_{product_id}.png')
        plt.close()

def main():
    db = DatabaseUtils()
    
    print("\n=== Database Usage Examples ===")
    
    # Example 1: Search for products
    print("\n1. Search for Samsung products:")
    samsung_products = db.get_product_info(brand='Samsung')
    print(samsung_products[['name', 'current_price', 'ratings']].head())
    
    # Example 2: Get price history
    print("\n2. Get price history for first Samsung product:")
    if not samsung_products.empty:
        product_id = samsung_products.iloc[0]['product_id']
        history = db.get_price_history(product_id, days=7)
        print(history[['recorded_at', 'amazon_price', 'competitor_price']].head())
    
    # Example 3: Find best deals
    print("\n3. Current best deals (min 30% discount, 100 ratings):")
    deals = db.get_best_deals()
    print(deals[['name', 'amazon_price', 'discount_percentage']].head())
    
    # Example 4: Compare with competitors
    print("\n4. Significant price differences vs competitors (>10%):")
    comparisons = db.compare_with_competitors()
    print(comparisons[['name', 'amazon_price', 'competitor_price', 'price_diff_percent']].head())

if __name__ == "__main__":
    main()
