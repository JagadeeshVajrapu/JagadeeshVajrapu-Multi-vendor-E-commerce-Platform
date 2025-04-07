from flask import Flask, render_template, send_from_directory, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os
import traceback

# Load environment variables
load_dotenv()

# Get the absolute path to the app directory
app_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app
app = Flask(__name__,
            static_folder=os.path.join(app_dir, 'static'),
            template_folder=os.path.join(app_dir, 'templates'))

# Configure MongoDB with proper settings
app.config["MONGO_URI"] = os.getenv("MONGODB_URI", "mongodb://localhost:27017/mve_db")
app.config["MONGO_CONNECT"] = False  # Prevent connection on app creation
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Initialize MongoDB
mongo = PyMongo(app)

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")
jwt = JWTManager(app)

# Enable CORS
CORS(app)

# Import routes
from app.routes import auth_routes, product_routes, order_routes, cart_routes

# Register blueprints
app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
app.register_blueprint(product_routes.bp, url_prefix='/api/products')
app.register_blueprint(order_routes.bp, url_prefix='/api/orders')
app.register_blueprint(cart_routes.cart, url_prefix='/api/cart')

# Add current_user to template context
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Test MongoDB connection route
@app.route('/test-db')
def test_db():
    try:
        # Test MongoDB connection
        mongo.db.command('ping')
        
        # Get database info
        db_info = mongo.db.command('dbStats')
        
        return jsonify({
            'status': 'success',
            'message': 'MongoDB connection successful',
            'database': {
                'name': db_info['db'],
                'collections': list(mongo.db.list_collection_names()),
                'size': db_info['dataSize']
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'MongoDB connection failed',
            'error': str(e)
        }), 500

# Import models after app initialization to avoid circular imports
from app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({'_id': user_id})
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        print(f"Error loading user: {str(e)}")
        return None

# Root route
@app.route('/')
def index():
    try:
        # Get products for initial page load
        products = list(mongo.db.products.find())
        for product in products:
            product['_id'] = str(product['_id'])
            # Ensure product has required fields
            if 'name' not in product:
                product['name'] = 'Unnamed Product'
            if 'description' not in product:
                product['description'] = 'No description available'
            if 'price' not in product:
                product['price'] = 0
            # Handle images
            if not product.get('images') or len(product['images']) == 0:
                product['images'] = ['/static/images/default-product.png']
            elif isinstance(product['images'], str):
                product['images'] = [product['images']]
        
        print(f"Rendering index with {len(products)} products")  # Debug print
        return render_template('index.html', products=products)
    except Exception as e:
        print(f"Error in index route: {str(e)}")  # Debug print
        print(traceback.format_exc())  # Print full traceback
        return render_template('index.html', products=[], error=str(e))

# Vendor dashboard route
@app.route('/vendor-dashboard')
def vendor_dashboard():
    try:
        return render_template('vendor_dashboard.html')
    except Exception as e:
        print(f"Error rendering vendor dashboard: {str(e)}")
        return str(e), 500

# Customer dashboard route
@app.route('/customer-dashboard')
def customer_dashboard():
    try:
        return render_template('customer_dashboard.html')
    except Exception as e:
        print(f"Error rendering customer dashboard: {str(e)}")
        return str(e), 500

# Cart route
@app.route('/cart')
def cart():
    try:
        return render_template('cart.html')
    except Exception as e:
        print(f"Error rendering cart: {str(e)}")
        return str(e), 500

# Orders route
@app.route('/orders')
def orders():
    try:
        return render_template('orders.html')
    except Exception as e:
        print(f"Error rendering orders: {str(e)}")
        return str(e), 500

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename) 