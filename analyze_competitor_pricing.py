import pandas as pd
import numpy as np

# Read the competitor pricing dataset
df = pd.read_csv('competitor_price_analysis.csv')

print("=== Amazon vs Competitor Price Analysis ===\n")

# Overall Statistics
print("1. Price Comparison Overview:")
price_status_counts = df['price_status'].value_counts()
total_products = len(df)
print(f"Total products analyzed: {total_products}")
for status, count in price_status_counts.items():
    percentage = round((count/total_products * 100), 2)
    print(f"{status}: {count} products ({percentage}%)")

# Price Difference Statistics
print("\n2. Price Difference Statistics:")
print("Average price difference:")
print(f"- Absolute amount: Rs. {round(df['price_diff_vs_competitor'].mean(), 2)}")
print(f"- Percentage: {round(df['price_diff_percentage'].mean(), 2)}%")

# Category Analysis
print("\n3. Price Comparison by Main Category:")
category_analysis = df.groupby('main_category').agg({
    'price_diff_percentage': 'mean',
    'product_id': 'count'
}).sort_values('price_diff_percentage', ascending=False)
print(category_analysis)

# Brand Analysis
print("\n4. Top 10 Brands with Biggest Price Advantage on Amazon (min 5 products):")
brand_analysis = df.groupby('brand').agg({
    'price_diff_percentage': 'mean',
    'product_id': 'count'
}).query('product_id >= 5').sort_values('price_diff_percentage', ascending=False).head(10)
print(brand_analysis)

# Best Deals on Amazon
print("\n5. Top 5 Best Deals on Amazon (Compared to Competitors):")
best_deals = df[df['price_status'] == 'Amazon Cheaper'].nlargest(5, 'price_diff_vs_competitor')
for _, product in best_deals.iterrows():
    print(f"\n{product['name']}")
    print(f"Amazon Price: Rs. {product['discount_price']}")
    print(f"Competitor Price: Rs. {product['competitor_price']}")
    print(f"You Save: Rs. {round(product['price_diff_vs_competitor'], 2)} ({round(product['price_diff_percentage'], 2)}%)")
    print(f"Ratings: {product['ratings']}* ({int(product['no_of_ratings'])} ratings)")

# Better Deals at Competitors
print("\n6. Top 5 Better Deals at Competitors:")
competitor_deals = df[df['price_status'] == 'Competitor Cheaper'].nlargest(5, 'price_diff_vs_competitor')
for _, product in competitor_deals.iterrows():
    print(f"\n{product['name']}")
    print(f"Amazon Price: Rs. {product['discount_price']}")
    print(f"Competitor Price: Rs. {product['competitor_price']}")
    print(f"Potential Savings at Competitor: Rs. {abs(round(product['price_diff_vs_competitor'], 2))} ({abs(round(product['price_diff_percentage'], 2))}%)")
    print(f"Ratings: {product['ratings']}* ({int(product['no_of_ratings'])} ratings)")

# Price Ranges Analysis
print("\n7. Price Comparison by Price Range:")
df['price_range'] = pd.cut(df['discount_price'], 
                          bins=[0, 500, 1000, 5000, 10000, float('inf')],
                          labels=['Under Rs. 500', 'Rs. 500-1000', 'Rs. 1000-5000', 'Rs. 5000-10000', 'Above Rs. 10000'])
price_range_analysis = df.groupby('price_range').agg({
    'price_diff_percentage': ['mean', 'count']
}).round(2)
print(price_range_analysis)
