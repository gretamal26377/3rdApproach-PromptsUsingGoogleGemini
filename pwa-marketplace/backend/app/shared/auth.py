import logging
import jwt  # importing jwt (json web token) for token generation and decoding
from flask import jsonify, request, current_app
from functools import wraps  # for creating decorators
from .models import Users
from .management import get_user_logic
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

def token_required(org_id=None, role_codes_required=None):
    """
    Decorator to require a valid token for authentication and optional org_id and role-based access control to Users types (Org Admin, Platform Admin)
    This is gral purpose decorator, so that's the reason for both checks. Authorization header and cookie.
        Authorization is used when tokens are stored in localStorage/sessionStorage at frontend side
        Cookies store tokens at backend side and are considered more secure against XSS attacks because of features
        like HttpOnly and Secure flags
    Usage:
      @token_required()  # Customer logged-in
      @token_required(org_id=1, role_codes_required=['admin'])  # Org Admin logged-in for org_id 1
      @token_required(role_codes_required=['admin', 'supervisor'])  # Platform level: Only admin/supervisor admitted
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
                return jsonify({'message': 'Invalid or expired Token'}), 401

            # Detect frontend type from request path or header
            # Can't use VITE_APP_TYPE env var because it's only visible at frontend side by Vite 
            # Convention: /api/admin/... -> org-admin, /api/platform/... -> platform-admin, /api/customer/... -> customer
            path = request.path
            if 'backend-org-admin' in path and role_codes_required:
                app_type = 'org-admin'
            elif 'backend-platform-admin' in path and role_codes_required:
                app_type = 'platform-admin'
            elif 'backend-customer' in path and not role_codes_required:
                app_type = 'customer'
            else:
                logging.error("There's no matching between App Types and Required Roles: %s", path, role_codes_required)
                return jsonify({'error': 'Unexpected Authentication Error'}), 500

            # For Customer, user_id is actually customer_id
            user_data, status = get_user_logic(app_type, org_id, user_id)
            if status != 200:
                return jsonify(user_data), status

            # Role-based Access Control
            if role_codes_required:
                user_role_code = user_data.get('role_code')
                if user_role_code not in role_codes_required:
                    return jsonify({"error": f"Insufficient Role: Requires {role_codes_required} Role(s)"}), 403

            return f(user_data, *args, **kwargs)
        return decorated_function
    return decorator
