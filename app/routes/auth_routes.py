from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
import datetime

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Find user
        user = mongo.db.users.find_one({'email': data['email']})
        if not user or not check_password_hash(user['password'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token with user info
        access_token = create_access_token(
            identity={
                'email': user['email'],
                'role': user['role']
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'email': user['email'],
            'role': user['role']
        }), 200
        
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        if data['role'] not in ['vendor', 'customer']:
            return jsonify({'error': 'Invalid role. Must be either vendor or customer'}), 400
        
        # Check if user already exists
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already exists'}), 400
        
        # Hash password
        hashed_password = generate_password_hash(data['password'])
        
        # Create user document
        user = {
            'email': data['email'],
            'password': hashed_password,
            'role': data['role'],
            'created_at': datetime.datetime.utcnow()
        }
        
        # Insert user into database
        mongo.db.users.insert_one(user)
        
        return jsonify({'message': 'User registered successfully'}), 201
        
    except Exception as e:
        print(f"Error in register: {str(e)}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500 