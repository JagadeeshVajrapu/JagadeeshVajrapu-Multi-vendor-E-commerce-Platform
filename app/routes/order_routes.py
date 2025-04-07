from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
import datetime

bp = Blueprint('orders', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Get cart
    cart = mongo.db.carts.find_one({'user_email': current_user['email']})
    if not cart or not cart['items']:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Calculate total amount
    total_amount = sum(item['price'] * item['quantity'] for item in cart['items'])
    
    # Apply coupon if provided
    if 'coupon_code' in data:
        coupon = mongo.db.coupons.find_one({'code': data['coupon_code']})
        if coupon and coupon['valid_until'] > datetime.datetime.utcnow():
            total_amount *= (1 - coupon['discount_percentage'] / 100)
    
    # Create order
    order = {
        'user_email': current_user['email'],
        'items': cart['items'],
        'total_amount': total_amount,
        'status': 'pending',
        'created_at': datetime.datetime.utcnow(),
        'shipping_address': data['shipping_address']
    }
    
    # Insert order
    mongo.db.orders.insert_one(order)
    
    # Update product stock
    for item in cart['items']:
        mongo.db.products.update_one(
            {'_id': item['product_id']},
            {'$inc': {'stock': -item['quantity']}}
        )
    
    # Clear cart
    mongo.db.carts.delete_one({'user_email': current_user['email']})
    
    return jsonify({'message': 'Order created successfully'}), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    current_user = get_jwt_identity()
    
    if current_user['role'] == 'vendor':
        # Get all orders containing vendor's products
        orders = list(mongo.db.orders.find({
            'items.product_id': {'$in': [
                product['_id'] for product in mongo.db.products.find(
                    {'vendor_email': current_user['email']},
                    {'_id': 1}
                )
            ]}
        }, {'_id': 0}))
    else:
        # Get customer's orders
        orders = list(mongo.db.orders.find(
            {'user_email': current_user['email']},
            {'_id': 0}
        ))
    
    return jsonify(orders), 200

@bp.route('/<order_id>', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'vendor':
        return jsonify({'error': 'Only vendors can update order status'}), 403
    
    data = request.get_json()
    new_status = data['status']
    
    # Update order status
    result = mongo.db.orders.update_one(
        {'_id': order_id},
        {'$set': {'status': new_status}}
    )
    
    if result.modified_count == 0:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({'message': 'Order status updated successfully'}), 200 