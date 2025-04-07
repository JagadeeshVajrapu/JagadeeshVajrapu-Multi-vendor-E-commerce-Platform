from functools import wraps
from flask import request, jsonify
import jwt
from app import app, mongo
from bson import ObjectId

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print("Token data:", data)  # Debug print
            
            # Get user from database
            user_data = data.get('sub', {})
            print("User data from token:", user_data)  # Debug print
            
            if not user_data or 'email' not in user_data:
                return jsonify({'error': 'Invalid token data'}), 401
            
            # Find user in database
            user = mongo.db.users.find_one({'email': user_data['email']})
            print("User from database:", user)  # Debug print
            
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # Convert ObjectId to string
            user['_id'] = str(user['_id'])
            
            return f(user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            print("Token validation error:", str(e))  # Debug print
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            print("Unexpected error in token validation:", str(e))  # Debug print
            return jsonify({'error': 'Token validation failed'}), 401
    
    return decorated 