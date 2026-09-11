from flask import Blueprint, jsonify, request, abort, make_response
from .models import User, Store, Product, Order, OrderItem, db
# from .auth import token_required, admin_required

# If you import auth this way, you must use it this way auth.token_required
# from . import auth 
# If you import the functions directly, you can use them without the auth prefix
from .auth import token_required, admin_required, generate_token, decode_token

import logging
from .store_management import create_store_logic, update_store_logic, delete_store_logic
from .product_management import create_product_logic, update_product_logic, delete_product_logic
from .order_management import get_orders_logic, get_order_logic, create_order_logic, delete_order_logic
from .admin_management import get_users_logic, get_user_logic, update_user_logic, delete_user_logic

logging.basicConfig(level=logging.INFO)

# Customer Routes
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user.
    """
    #Issue: Check for Role Authorization
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    required_fields = ['username', 'password', 'email']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'e-mail already exists'}), 400

    try:
        new_user = User(username=data['username'], email=data['email']) # type: ignore
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        token = generate_token(new_user)
        return jsonify({'message': 'User created successfully', 'token': token}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating user: {e}")
        return jsonify({'message': 'Failed to create user'}), 500

@bp.route('/login', methods=['POST'])
def login_user():
    """
    Login a user and return a token.
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    required_fields = ['username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']): #Issue?
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = generate_token(user)
    return jsonify({'message': 'Login successful', 'token': token}), 200

# Create a Route to decode a user from its token
# Changed to POST as token is received in JSON body. If token is sent as function parameter, it can be GET (conventions)
# It can test this route using curl, Postman, or a similar tool. Here's an example using curl:
# Adjust the http://localhost:5000 part to match your backend's container's localhost address and port
# curl -X POST -H "Content-Type: application/json" -d '{"token": "your_token_here"}' http://localhost:5000/api/decode
@bp.route('/decode', methods=['POST'])
def decode_user():
    """
    Decode a user ID from its token
    """
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'message': 'No token provided'}), 400

    token = data['token']
    user_id = decode_token(token)

    if user_id:
        user = User.query.get(user_id)
        if user:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            return jsonify({'message': 'Token decoded successfully', 'user': user_data}), 200
        else:
            return jsonify({'message': 'User not found for this token'}), 404
    else:
        return jsonify({'message': 'Invalid or expired token'}), 401

@bp.route('/stores', methods=['GET'])
def get_stores():
    """
    Get all stores.
    """
    stores = Store.query.all()
    stores_data = [{'id': store.id, 'name': store.name, 'description': store.description, 'owner_id': store.owner_id} for store in stores]
    return jsonify(stores_data), 200

@bp.route('/stores/<int:store_id>', methods=['GET'])
def get_store(store_id):
    """
    Get a specific store.
    """
    store = Store.query.get_or_404(store_id)
    store_data = {
        'id': store.id,
        'name': store.name,
        'description': store.description,
        'owner_id': store.owner_id
    }
    return jsonify(store_data), 200

@bp.route('/stores', methods=['POST'])
@token_required
def create_store(current_user):
    """
    Create a new store
    """
    #Issue: Check for Role Authorization
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    result, status = create_store_logic(current_user, data)
    return jsonify(result), status

@bp.route('/stores/<int:store_id>', methods=['PUT'])
@token_required
def update_store(current_user, store_id):
    """
    Update a store
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    result, status = update_store_logic(current_user, store_id, data)
    return jsonify(result), status

@bp.route('/stores/<int:store_id>', methods=['DELETE'])
@token_required
def delete_store(current_user, store_id):
    """
    Delete a store
    """
    result, status = delete_store_logic(current_user, store_id)
    return jsonify(result), status

@bp.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    """
    Create a product
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    result, status = create_product_logic(current_user, data)
    return jsonify(result), status

@bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    """
    Update a product
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    result, status = update_product_logic(current_user, product_id, data)
    return jsonify(result), status

@bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    """
    Delete a product
    """
    result, status = delete_product_logic(current_user, product_id)
    return jsonify(result), status

@bp.route('/products', methods=['GET'])
def get_products():
    """
    Get all products
    """
    #Issue: Products should be filtered by store_id if provided
    products = Product.query.all()
    products_data = [{'id': product.id, 'name': product.name, 'description': product.description, 'price': product.price, 'store_id': product.store_id} for product in products]
    return jsonify(products_data), 200

@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get a specific product
    """
    product = Product.query.get_or_404(product_id)
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'store_id': product.store_id
    }
    return jsonify(product_data), 200

@bp.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    """
    Get all orders if user is admin, or user's orders if not
    """
    result, status = get_orders_logic(current_user)
    return jsonify(result), status

@bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    """
    Get a specific order. If the user is not an admin, they can only access their own orders
    """
    result, status = get_order_logic(current_user, order_id)
    return jsonify(result), status

@bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    """
    Create a new order for the current user
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    result, status = create_order_logic(current_user, data)
    return jsonify(result), status

@bp.route('/orders/<int:order_id>', methods=['DELETE'])
@token_required
def delete_order(current_user, order_id):
    """
    Delete an order. If the user is not an admin, they can only delete their own orders
    """
    result, status = delete_order_logic(current_user, order_id)
    return jsonify(result), status


# Admin User Management Routes (if not already registered via Blueprint)
# If you want to expose these via the main blueprint, you can do:

@bp.route('/admin/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    """
    Get all users (admin only)
    """
    result, status = get_users_logic()
    return jsonify(result), status

@bp.route('/admin/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(current_user, user_id):
    """
    Get a specific user (admin only)
    """
    result, status = get_user_logic(user_id)
    return jsonify(result), status

@bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    """
    Update a user (admin only)
    """
    data = request.get_json()
    result, status = update_user_logic(user_id, data)
    return jsonify(result), status

@bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """
    Delete a user (admin only)
    """
    result, status = delete_user_logic(user_id)
    return jsonify(result), status