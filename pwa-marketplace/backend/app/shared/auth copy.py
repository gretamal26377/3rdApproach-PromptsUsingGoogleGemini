import jwt  # importing jwt (json web token) for token generation and decoding
from flask import jsonify, request, current_app
from functools import wraps  # for creating decorators
from .models import Users
import datetime  # for handling date and time

def generate_token(id):
    """
    Generate a JWT token for an id
    """
    payload = {
        'user_id': id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Token expires in 7 days
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """
    Decode a JWT token
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        # If decoding is successful, return the user_id from the payload, which was defined in generate_token function
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(roles=None):
    """
    Decorator to require a valid token for authentication and optional role-based access control.
    This is gral purpose decorator, so that's the reason for both checks. Authorization header and cookie.
        Authorization is used when tokens are stored in localStorage/sessionStorage at frontend side
        Cookies store tokens at backend side and are considered more secure against XSS attacks because of features
        like HttpOnly and Secure flags
    Usage:
      @token_required()  # Any logged-in user
      @token_required(roles=['admin', 'supervisor'])  # Only admin/supervisor
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            cookie_token = request.cookies.get('auth_token')

            token = None
            if auth_header:
                if not auth_header.startswith('Bearer '):
                    return jsonify({'message': 'Invalid token format'}), 401
                token = auth_header.split(' ')[1]
            elif cookie_token:
                token = cookie_token
            if not token:
                return jsonify({'message': 'Token is missing'}), 401
            
            user_id = decode_token(token)
            if not user_id:
                return jsonify({'message': 'Invalid or expired token'}), 401

            current_user = Users.query.get(user_id)
            if not current_user:
                return jsonify({'message': 'User not found'}), 401

            # Role-based Access Control
            if roles:
                user_role = getattr(current_user, 'role_code', None) or (getattr(current_user, 'role', None) and getattr(current_user.role, 'role_code', None))
                if user_role not in roles:
                    return jsonify({"error": f"Insufficient Role: Requires {roles} Role(s)"}), 403

            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator
