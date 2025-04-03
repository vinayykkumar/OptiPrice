from flask import Flask, jsonify, request, render_template
import sqlite3
from flask_cors import CORS
from price_predictor import PricePredictor

app = Flask(__name__)
CORS(app)

# Initialize price predictor
price_predictor = PricePredictor()

def get_db_connection():
    conn = sqlite3.connect('electronics_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get query parameters
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_reviews = request.args.get('min_reviews', type=int)
    search_term = request.args.get('search', type=str)
    
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if min_price:
        query += " AND offer_price >= ?"
        params.append(min_price)
    if max_price:
        query += " AND offer_price <= ?"
        params.append(max_price)
    if min_reviews:
        query += " AND review_count >= ?"
        params.append(min_reviews)
    if search_term:
        query += " AND product_name LIKE ?"
        params.append(f"%{search_term}%")
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/products/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Get average prices
    cursor.execute('''
        SELECT 
            AVG(offer_price) as avg_offer_price,
            AVG(original_price) as avg_original_price,
            AVG(review_count) as avg_reviews
        FROM products
    ''')
    result = cursor.fetchone()
    stats['average_offer_price'] = result['avg_offer_price']
    stats['average_original_price'] = result['avg_original_price']
    stats['average_reviews'] = result['avg_reviews']
    
    # Get top brands
    cursor.execute('''
        SELECT product_name, review_count
        FROM products
        ORDER BY review_count DESC
        LIMIT 10
    ''')
    stats['top_reviewed_products'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(stats)

@app.route('/products/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM products 
        WHERE product_name LIKE ? 
        ORDER BY review_count DESC
        LIMIT 20
    ''', (f'%{query}%',))
    
    products = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(product) for product in products])

@app.route('/price_trends/<int:product_id>')
def get_price_trends(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get price history for the last 30 days
    cursor.execute('''
        SELECT recorded_at, amazon_price, competitor_price
        FROM price_history
        WHERE product_id = ?
        AND recorded_at >= date('now', '-30 days')
        ORDER BY recorded_at
    ''', (product_id,))
    
    trends = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(trend) for trend in trends])

@app.route('/categories')
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT category 
        FROM products 
        WHERE category IS NOT NULL
        ORDER BY category
    ''')
    
    categories = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(cat) for cat in categories])

@app.route('/active_alerts')
def get_active_alerts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            a.id,
            a.product_id,
            p.name as product_name,
            a.alert_type,
            a.threshold_value,
            a.comparison_type,
            a.notification_frequency,
            a.last_triggered,
            ph.amazon_price as current_price,
            ph.competitor_price,
            ph.discount_percentage,
            CASE 
                WHEN a.alert_type = 'price_drop' AND ph.amazon_price <= a.threshold_value THEN 1
                WHEN a.alert_type = 'competitor_cheaper' AND ph.competitor_price < ph.amazon_price THEN 1
                WHEN a.alert_type = 'competitor_higher' AND ph.competitor_price > ph.amazon_price THEN 1
                WHEN a.alert_type = 'price_volatility' AND ABS(ph.price_diff_percentage) >= a.threshold_value THEN 1
                WHEN a.alert_type = 'discount_increase' AND ph.discount_percentage >= a.threshold_value THEN 1
                ELSE 0
            END as is_triggered
        FROM price_alerts a
        JOIN products p ON a.product_id = p.product_id
        JOIN price_history ph ON p.product_id = ph.product_id
        WHERE a.is_active = 1
        AND ph.recorded_at = (
            SELECT MAX(recorded_at) 
            FROM price_history 
            WHERE product_id = p.product_id
        )
        ORDER BY is_triggered DESC, a.created_at DESC
    ''')
    
    alerts = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(alert) for alert in alerts])

@app.route('/alert_types')
def get_alert_types():
    alert_types = [
        {
            'type': 'price_drop',
            'description': 'Alert when price drops below threshold',
            'comparison_types': ['percentage', 'absolute'],
            'frequencies': ['immediate', 'daily', 'weekly']
        },
        {
            'type': 'competitor_cheaper',
            'description': 'Alert when competitor price is lower',
            'comparison_types': ['percentage', 'absolute'],
            'frequencies': ['immediate', 'daily', 'weekly']
        },
        {
            'type': 'competitor_higher',
            'description': 'Alert when competitor price is higher',
            'comparison_types': ['percentage', 'absolute'],
            'frequencies': ['immediate', 'daily', 'weekly']
        },
        {
            'type': 'price_volatility',
            'description': 'Alert on significant price changes',
            'comparison_types': ['percentage'],
            'frequencies': ['daily', 'weekly']
        },
        {
            'type': 'stock_status',
            'description': 'Alert on stock status changes',
            'comparison_types': ['status_change'],
            'frequencies': ['immediate']
        },
        {
            'type': 'discount_increase',
            'description': 'Alert on discount threshold',
            'comparison_types': ['percentage'],
            'frequencies': ['immediate', 'daily']
        },
        {
            'type': 'price_trend',
            'description': 'Alert on price trend changes',
            'comparison_types': ['trend_change'],
            'frequencies': ['daily', 'weekly']
        },
        {
            'type': 'market_position',
            'description': 'Alert on market position changes',
            'comparison_types': ['percentage'],
            'frequencies': ['daily', 'weekly']
        },
        {
            'type': 'custom_threshold',
            'description': 'Alert on custom price threshold',
            'comparison_types': ['absolute'],
            'frequencies': ['immediate', 'daily', 'weekly']
        }
    ]
    return jsonify(alert_types)

@app.route('/alerts/create', methods=['POST'])
def create_alert():
    data = request.json
    required_fields = ['product_id', 'alert_type', 'threshold_value', 'comparison_type', 'notification_frequency']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO price_alerts (
            product_id, alert_type, threshold_value, 
            comparison_type, notification_frequency
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        data['product_id'], data['alert_type'], data['threshold_value'],
        data['comparison_type'], data['notification_frequency']
    ))
    
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': alert_id, 'message': 'Alert created successfully'}), 201

@app.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE price_alerts SET is_active = 0 WHERE id = ?', (alert_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Alert deleted successfully'}), 200

@app.route('/alert_history')
def get_alert_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            h.id,
            h.alert_id,
            h.product_id,
            p.name as product_name,
            h.alert_type,
            h.threshold_value,
            h.comparison_type,
            h.triggered_value,
            h.triggered_at,
            h.details
        FROM alert_history h
        JOIN products p ON h.product_id = p.product_id
        ORDER BY h.triggered_at DESC
        LIMIT 50
    ''')
    
    history = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(record) for record in history])

@app.route('/alert_history/<int:alert_id>')
def get_alert_history_by_id(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            h.id,
            h.alert_id,
            h.product_id,
            p.name as product_name,
            h.alert_type,
            h.threshold_value,
            h.comparison_type,
            h.triggered_value,
            h.triggered_at,
            h.details
        FROM alert_history h
        JOIN products p ON h.product_id = p.product_id
        WHERE h.alert_id = ?
        ORDER BY h.triggered_at DESC
    ''', (alert_id,))
    
    history = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(record) for record in history])

def record_alert_trigger(alert_id, product_id, alert_type, threshold_value, comparison_type, triggered_value, details):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alert_history (
            alert_id, product_id, alert_type, threshold_value,
            comparison_type, triggered_value, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (alert_id, product_id, alert_type, threshold_value, comparison_type, triggered_value, details))
    
    conn.commit()
    conn.close()

@app.route('/competitor_analysis')
def get_competitor_analysis():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get price difference analysis
    cursor.execute('''
        SELECT 
            p.product_name,
            ph.amazon_price,
            ph.competitor_price,
            ((ph.competitor_price - ph.amazon_price) / ph.amazon_price * 100) as price_difference_percent
        FROM products p
        JOIN price_history ph ON p.product_id = ph.product_id
        WHERE ph.recorded_at = (
            SELECT MAX(recorded_at) 
            FROM price_history 
            WHERE product_id = p.product_id
        )
        AND ph.competitor_price IS NOT NULL
        ORDER BY price_difference_percent DESC
        LIMIT 10
    ''')
    
    analysis = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(item) for item in analysis])

@app.route('/price_predictions/<int:product_id>')
def get_price_predictions(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get product details
    cursor.execute('''
        SELECT * FROM products WHERE product_id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    
    # Get current and competitor prices
    cursor.execute('''
        SELECT amazon_price, competitor_price
        FROM price_history
        WHERE product_id = ?
        ORDER BY recorded_at DESC
        LIMIT 1
    ''', (product_id,))
    latest_prices = cursor.fetchone()
    conn.close()
    
    if not product or not latest_prices:
        return jsonify({'error': 'Product not found'}), 404
        
    # Get price insights
    insights = price_predictor.get_price_insights(
        dict(product),
        latest_prices['amazon_price'],
        latest_prices['competitor_price']
    )
    
    return jsonify(insights)

@app.route('/bulk_predictions')
def get_bulk_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all active products with their latest prices
    cursor.execute('''
        WITH LatestPrices AS (
            SELECT 
                product_id,
                amazon_price,
                competitor_price,
                ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY recorded_at DESC) as rn
            FROM price_history
        )
        SELECT 
            p.*,
            lp.amazon_price,
            lp.competitor_price
        FROM products p
        JOIN LatestPrices lp ON p.product_id = lp.product_id
        WHERE lp.rn = 1
        LIMIT 50
    ''')
    
    products = cursor.fetchall()
    conn.close()
    
    predictions = []
    for product in products:
        insights = price_predictor.get_price_insights(
            dict(product),
            product['amazon_price'],
            product['competitor_price']
        )
        predictions.append({
            'product_id': product['product_id'],
            'name': product['name'],
            'current_price': product['amazon_price'],
            'predictions': insights
        })
    
    return jsonify(predictions)

@app.route('/optimize_alert/<int:alert_id>')
def optimize_alert(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get alert details
    cursor.execute('''
        SELECT a.*, p.* 
        FROM price_alerts a
        JOIN products p ON a.product_id = p.product_id
        WHERE a.id = ?
    ''', (alert_id,))
    alert = cursor.fetchone()
    
    # Get current prices
    cursor.execute('''
        SELECT amazon_price, competitor_price
        FROM price_history
        WHERE product_id = ?
        ORDER BY recorded_at DESC
        LIMIT 1
    ''', (alert['product_id'],))
    latest_prices = cursor.fetchone()
    
    if not alert or not latest_prices:
        return jsonify({'error': 'Alert not found'}), 404
    
    # Get price insights
    insights = price_predictor.get_price_insights(
        dict(alert),
        latest_prices['amazon_price'],
        latest_prices['competitor_price']
    )
    
    # Calculate optimized threshold
    optimized_threshold = None
    if alert['alert_type'] == 'price_drop':
        # Set threshold slightly above predicted lowest price
        optimized_threshold = insights['predicted_price'] * 1.05
    elif alert['alert_type'] == 'discount_increase':
        # Set threshold slightly below predicted maximum discount
        optimized_threshold = insights['predicted_discount'] * 0.95
    elif alert['alert_type'] in ['competitor_cheaper', 'competitor_higher']:
        # Set threshold based on predicted competitive position
        price_gap = insights['price_gap']
        optimized_threshold = price_gap * 0.9 if alert['alert_type'] == 'competitor_cheaper' else price_gap * 1.1
    
    # Update alert if threshold is calculated
    if optimized_threshold is not None:
        cursor.execute('''
            UPDATE price_alerts
            SET threshold_value = ?
            WHERE id = ?
        ''', (optimized_threshold, alert_id))
        conn.commit()
    
    conn.close()
    
    return jsonify({
        'alert_id': alert_id,
        'previous_threshold': alert['threshold_value'],
        'optimized_threshold': optimized_threshold,
        'insights': insights
    })

if __name__ == '__main__':
    app.run(debug=True)
