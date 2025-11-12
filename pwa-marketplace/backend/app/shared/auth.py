import jwt  # importing jwt (json web token) for token generation and decoding
from flask import jsonify, request, current_app
from functools import wraps  # for creating decorators
from .models import User
import datetime  # for handling date and time

def generate_token(user):
    """
    Generate a JWT token for a user
    """
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expires in 24 hours
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """
    Decode a JWT token
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    Decorator to require a valid token for authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        if not token.startswith('Bearer '):
            return jsonify({'message': 'Invalid token format'}), 401

        token = token.split(' ')[1]
        user_id = decode_token(token)
        if not user_id:
            return jsonify({'message': 'Invalid or expired token'}), 401

        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'message': 'User not found'}), 401

        return f(current_user, *args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require the user to be an admin.  Must be used after token_required
    """
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function
