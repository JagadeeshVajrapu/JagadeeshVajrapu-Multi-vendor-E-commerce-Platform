from flask import Blueprint, jsonify, request, current_app
from bson import ObjectId
import traceback
from app import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from datetime import datetime

cart = Blueprint('cart', __name__)

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

@cart.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    try:
        current_user = get_jwt_identity()
        user_email = current_user['email'] if isinstance(current_user, dict) else current_user
        print("Getting cart for user:", user_email)
        
        # Get user's cart from MongoDB using email
        cart = mongo.db.carts.find_one({'user_email': user_email})
        print("Found cart:", cart)
        
        if not cart:
            print("Creating new cart for user")
            # Create empty cart with proper structure
            cart = {
                'user_email': user_email,
                'items': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            try:
                result = mongo.db.carts.insert_one(cart)
                print("New cart created with ID:", result.inserted_id)
                cart['_id'] = str(result.inserted_id)
            except Exception as e:
                print(f"Error creating cart: {str(e)}")
                return jsonify({'error': 'Failed to create cart'}), 500
        else:
            cart['_id'] = str(cart['_id'])
        
        # Populate product details for each item
        populated_items = []
        for item in cart.get('items', []):
            try:
                product_id = ObjectId(item['product_id']) if isinstance(item['product_id'], str) else item['product_id']
                product = mongo.db.products.find_one({'_id': product_id})
                if product:
                    product['_id'] = str(product['_id'])
                    # Handle product images
                    if 'images' in product:
                        product['images'] = [get_image_url(img) for img in product['images']]
                    else:
                        product['images'] = ['/static/images/default-product.png']
                    item['product'] = product
                    populated_items.append(item)
                else:
                    print(f"Product not found for ID: {item['product_id']}")
            except Exception as e:
                print(f"Error processing cart item: {str(e)}")
                continue
        
        cart['items'] = populated_items
        return jsonify(cart)
    except Exception as e:
        print(f"Error in get_cart: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to retrieve cart'}), 500

@cart.route('/', methods=['POST'])
@jwt_required()
def add_to_cart():
    try:
        current_user = get_jwt_identity()
        print("Current user identity:", current_user)
        
        user_email = current_user['email'] if isinstance(current_user, dict) else current_user
        print("Adding to cart for user:", user_email)
            
        data = request.get_json()
        print("Request data:", data)
        
        if not data or 'product_id' not in data:
            print("Missing product_id in request data")
            return jsonify({'error': 'Product ID is required'}), 400
        
        try:
            product_id = ObjectId(data['product_id'])
        except Exception as e:
            print(f"Invalid product ID: {str(e)}")
            return jsonify({'error': 'Invalid product ID format'}), 400
        
        quantity = int(data.get('quantity', 1))
        if quantity < 1:
            print("Invalid quantity:", quantity)
            return jsonify({'error': 'Quantity must be at least 1'}), 400
        
        # Check if product exists and has enough stock
        try:
            product = mongo.db.products.find_one({'_id': product_id})
            print("Found product:", product)
            
            if not product:
                print(f"Product not found with ID: {product_id}")
                return jsonify({'error': 'Product not found'}), 404
            
            if product.get('stock', 0) < quantity:
                print(f"Insufficient stock. Available: {product.get('stock', 0)}, Requested: {quantity}")
                return jsonify({'error': 'Not enough stock available'}), 400
        except Exception as e:
            print(f"Error checking product: {str(e)}")
            return jsonify({'error': 'Failed to check product availability'}), 500
        
        # Get or create user's cart
        try:
            cart = mongo.db.carts.find_one({'user_email': user_email})
            print("Found existing cart:", cart)
            
            if not cart:
                print("Creating new cart")
                cart = {
                    'user_email': user_email,
                    'items': [],
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                result = mongo.db.carts.insert_one(cart)
                cart['_id'] = result.inserted_id
                print("New cart created with ID:", cart['_id'])
        except Exception as e:
            print(f"Error getting/creating cart: {str(e)}")
            return jsonify({'error': 'Failed to get/create cart'}), 500
        
        # Check if product already in cart
        item_found = False
        for item in cart['items']:
            if str(item['product_id']) == str(product_id):
                item['quantity'] = quantity
                item_found = True
                break
        
        if not item_found:
            cart['items'].append({
                'product_id': product_id,
                'quantity': quantity
            })
        
        # Update cart in database
        print("Updating cart with items:", cart['items'])
        try:
            result = mongo.db.carts.update_one(
                {'_id': cart['_id']},
                {
                    '$set': {
                        'items': cart['items'],
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            print("Update result:", result.modified_count)
        except Exception as e:
            print(f"Error updating cart: {str(e)}")
            return jsonify({'error': 'Failed to update cart in database'}), 500
        
        # Return updated cart with product details
        return get_cart()
    except Exception as e:
        print(f"Error in add_to_cart: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to add item to cart'}), 500

@cart.route('/', methods=['PUT'])
@jwt_required()
def update_cart():
    try:
        current_user = get_jwt_identity()
        user_email = current_user['email'] if isinstance(current_user, dict) else current_user
        data = request.get_json()
        
        if not data or 'product_id' not in data or 'quantity' not in data:
            return jsonify({'error': 'Product ID and quantity are required'}), 400
        
        try:
            product_id = ObjectId(data['product_id'])
        except:
            return jsonify({'error': 'Invalid product ID format'}), 400
        
        quantity = int(data['quantity'])
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400
        
        # Check if product exists and has enough stock
        product = mongo.db.products.find_one({'_id': product_id})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if product.get('stock', 0) < quantity:
            return jsonify({'error': 'Not enough stock available'}), 400
        
        # Update cart
        result = mongo.db.carts.update_one(
            {
                'user_email': user_email,
                'items.product_id': product_id
            },
            {
                '$set': {
                    'items.$.quantity': quantity
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Item not found in cart'}), 404
        
        # Return updated cart
        return get_cart()
    except Exception as e:
        print(f"Error in update_cart: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to update cart'}), 500

@cart.route('/', methods=['DELETE'])
@jwt_required()
def remove_from_cart():
    try:
        current_user = get_jwt_identity()
        user_email = current_user['email'] if isinstance(current_user, dict) else current_user
        data = request.get_json()
        
        if not data or 'product_id' not in data:
            return jsonify({'error': 'Product ID is required'}), 400
            
        try:
            product_id = ObjectId(data['product_id'])
        except:
            return jsonify({'error': 'Invalid product ID format'}), 400
            
        # Remove item from cart
        result = mongo.db.carts.update_one(
            {'user_email': user_email},
            {'$pull': {'items': {'product_id': product_id}}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Item not found in cart'}), 404
            
        # Return updated cart
        return get_cart()
    except Exception as e:
        print(f"Error in remove_from_cart: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to remove item from cart'}), 500 