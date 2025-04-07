from flask import Blueprint, request, jsonify, current_app, render_template, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson import ObjectId
import datetime
import traceback
import os
from werkzeug.utils import secure_filename

bp = Blueprint('products', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_url(image_path):
    if not image_path:
        return '/static/images/default-product.png'
    if image_path.startswith('http'):
        return image_path
    # Ensure the path starts with /static/images/
    if not image_path.startswith('/static/images/'):
        # Clean up the filename to match the actual files
        filename = os.path.basename(image_path)
        # Remove any URL encoding and spaces
        filename = filename.replace('%20', ' ').strip()
        return f"/static/images/{filename}"
    return image_path

@bp.route('/images/<path:filename>')
def serve_image(filename):
    try:
        # Decode URL-encoded filename
        filename = filename.replace('%20', ' ')
        return send_from_directory(os.path.join(current_app.root_path, 'static', 'images'), filename)
    except Exception as e:
        print(f"Error serving image {filename}: {str(e)}")
        return send_from_directory(os.path.join(current_app.root_path, 'static', 'images'), 'default-product.png')

@bp.route('/', methods=['GET'])
def get_products():
    try:
        category = request.args.get('category')
        query = {'category': category} if category else {}
        
        # Get all products from MongoDB
        products = list(mongo.db.products.find(query))
        
        # Convert ObjectId to string and ensure images are properly formatted
        for product in products:
            product['_id'] = str(product['_id'])
            # Handle product images
            if 'images' in product and product['images']:
                product['images'] = [get_image_url(img) for img in product['images']]
            else:
                product['images'] = ['/static/images/default-product.png']
            
            # Ensure all required fields are present
            product.setdefault('name', 'Unnamed Product')
            product.setdefault('description', 'No description available')
            product.setdefault('price', 0.0)
            product.setdefault('stock', 0)
            product.setdefault('category', 'Uncategorized')
            
            print(f"Product {product['name']} using images: {product['images']}")  # Debug print
        
        # Check if this is a direct browser request or an API request
        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify(products)
        
        # For browser requests, render the template
        return render_template('products.html', products=products)
    except Exception as e:
        print(f"Error in get_products: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Error loading products', 'details': str(e)}), 500

@bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        # Validate product_id
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400

        product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        product['_id'] = str(product['_id'])
        # Handle product images
        if 'images' in product:
            product['images'] = [get_image_url(img) for img in product['images']]
        else:
            product['images'] = ['/static/images/default-product.png']
        return jsonify(product)
        
    except Exception as e:
        print(f"Error in get_product: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Error loading product', 'details': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def add_product():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'vendor':
            return jsonify({'error': 'Only vendors can add products'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['name', 'price', 'description', 'category', 'stock']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate price and stock
        try:
            price = float(data['price'])
            stock = int(data['stock'])
            if price <= 0 or stock < 0:
                return jsonify({'error': 'Price and stock must be positive numbers'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid price or stock value'}), 400
        
        # Set default image based on product name if no image provided
        images = data.get('images', [])
        if not images:
            default_image = f"/static/images/{data['name'].replace(' ', '_')}.png"
            images = [default_image]
        elif isinstance(images, str):
            images = [images]
        
        product = {
            'name': data['name'],
            'price': price,
            'description': data['description'],
            'category': data['category'],
            'stock': stock,
            'vendor_email': current_user['email'],
            'created_at': datetime.datetime.utcnow(),
            'images': images
        }
        
        result = mongo.db.products.insert_one(product)
        product['_id'] = str(result.inserted_id)
        
        print(f"Product added with images: {images}")  # Debug print
        return jsonify({'message': 'Product added successfully', 'product': product}), 201
        
    except Exception as e:
        print(f"Error in add_product: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Error adding product', 'details': str(e)}), 500

@bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    try:
        # Validate product_id
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400

        current_user = get_jwt_identity()
        product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if product['vendor_email'] != current_user['email']:
            return jsonify({'error': 'You can only update your own products'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate price and stock if provided
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({'error': 'Price must be a positive number'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid price value'}), 400

        if 'stock' in data:
            try:
                stock = int(data['stock'])
                if stock < 0:
                    return jsonify({'error': 'Stock must be a non-negative number'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid stock value'}), 400
            
        update_data = {
            'name': data.get('name', product['name']),
            'price': float(data.get('price', product['price'])),
            'description': data.get('description', product['description']),
            'category': data.get('category', product['category']),
            'stock': int(data.get('stock', product['stock'])),
            'images': data.get('images', product['images'])
        }
        
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        update_data['_id'] = product_id
        return jsonify({'message': 'Product updated successfully', 'product': update_data}), 200
        
    except Exception as e:
        print(f"Error in update_product: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Error updating product', 'details': str(e)}), 500

@bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        # Validate product_id
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400

        current_user = get_jwt_identity()
        product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if product['vendor_email'] != current_user['email']:
            return jsonify({'error': 'You can only delete your own products'}), 403
        
        mongo.db.products.delete_one({'_id': ObjectId(product_id)})
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error in delete_product: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Error deleting product', 'details': str(e)}), 500

@bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to make it unique
            filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            
            # Ensure the images directory exists
            images_dir = os.path.join(current_app.static_folder, 'images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            
            filepath = os.path.join(images_dir, filename)
            file.save(filepath)
            
            # Return the URL path to the uploaded image
            image_url = f"/static/images/{filename}"
            print(f"Image saved successfully at: {image_url}")  # Debug print
            return jsonify({'image_url': image_url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Error uploading image', 'details': str(e)}), 500

@bp.route('/featured', methods=['GET'])
def get_featured_products():
    try:
        # Get featured products (for now, just return all products)
        products = list(mongo.db.products.find().limit(6))  # Limit to 6 featured products
        
        # Convert ObjectId to string and ensure images are properly formatted
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
            
            print(f"Featured Product {product['name']} using images: {product['images']}")  # Debug print
        
        return jsonify(products)
    except Exception as e:
        print(f"Error in get_featured_products: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Error loading featured products', 'details': str(e)}), 500 