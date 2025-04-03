# Nykaa Products API

This is a Flask-based API for the Nykaa Products dataset that provides various endpoints to query and analyze beauty product data.

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Create the database:
```bash
python create_database.py
```

3. Run the API server:
```bash
python app.py
```

## API Endpoints

### 1. Get All Products
- Endpoint: `/products`
- Method: GET
- Query Parameters:
  - min_price: Minimum offer price
  - max_price: Maximum offer price
  - min_reviews: Minimum number of reviews
  - search: Search term for product name

Example: `http://localhost:5000/products?min_price=500&max_price=1000&min_reviews=1000`

### 2. Get Statistics
- Endpoint: `/products/stats`
- Method: GET
- Returns average prices, review counts, and top reviewed products

Example: `http://localhost:5000/products/stats`

### 3. Search Products
- Endpoint: `/products/search`
- Method: GET
- Query Parameters:
  - q: Search query string

Example: `http://localhost:5000/products/search?q=moisturizer`

## Features

1. Full-text search on product names
2. Price range filtering
3. Review count filtering
4. Product statistics and analytics
5. Top products by review count
6. Average price calculations
