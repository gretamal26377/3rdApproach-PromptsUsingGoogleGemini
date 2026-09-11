from flask import Blueprint, jsonify, request
from ..shared.auth import token_required
# Issue: Missing logics (update_order_logic)
from .customer_management import (
    register_user_logic, login_user_logic, decode_user_logic,
    create_store_logic, update_store_logic, delete_store_logic,
    create_product_logic, update_product_logic, delete_product_logic,
    get_stores_logic, get_store_logic, get_products_logic, get_product_logic,
    create_order_logic, get_orders_logic, get_order_logic, delete_order_logic
)

customer_bp = Blueprint('customer_bp', __name__, url_prefix='/api')

@customer_bp.route('/register', methods=['POST'])
def register_user():
    #Issue: Check for Role Authorization
    data = request.get_json()
    result, status = register_user_logic(data)
    return jsonify(result), status

@customer_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    result, status = login_user_logic(data)
    return jsonify(result), status

"""
Create a Route to decode a user from its token
Changed to POST as token is received in JSON body. If token is sent as function parameter, it can be GET (conventions)
It can test this route using curl, Postman, or a similar tool. Here's an example using curl:
Adjust the http://localhost:5000 part to match your backend's container's localhost address and port
curl -X POST -H "Content-Type: application/json" -d '{"token": "your_token_here"}' http://localhost:5000/api/decode
"""
@customer_bp.route('/decode', methods=['POST'])
def decode_user():
    data = request.get_json()
    result, status = decode_user_logic(data)
    return jsonify(result), status

@customer_bp.route('/stores', methods=['POST'])
@token_required
def create_store(current_user):
    data = request.get_json()
    result, status = create_store_logic(current_user, data)
    return jsonify(result), status

@customer_bp.route('/stores/<int:store_id>', methods=['PUT'])
@token_required
def update_store(current_user, store_id):
    data = request.get_json()
    result, status = update_store_logic(current_user, store_id, data)
    return jsonify(result), status

@customer_bp.route('/stores/<int:store_id>', methods=['DELETE'])
@token_required
def delete_store(current_user, store_id):
    result, status = delete_store_logic(current_user, store_id)
    return jsonify(result), status

@customer_bp.route('/stores', methods=['GET'])
def get_stores():
    result, status = get_stores_logic()
    return jsonify(result), status

@customer_bp.route('/stores/<int:store_id>', methods=['GET'])
def get_store(store_id):
    result, status = get_store_logic(store_id)
    return jsonify(result), status

@customer_bp.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json()
    result, status = create_product_logic(current_user, data)
    return jsonify(result), status

@customer_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    data = request.get_json()
    result, status = update_product_logic(current_user, product_id, data)
    return jsonify(result), status

@customer_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    result, status = delete_product_logic(current_user, product_id)
    return jsonify(result), status

@customer_bp.route('/products', methods=['GET'])
def get_products():
    result, status = get_products_logic()
    return jsonify(result), status

@customer_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    result, status = get_product_logic(product_id)
    return jsonify(result), status

@customer_bp.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    result, status = get_orders_logic(current_user)
    return jsonify(result), status

@customer_bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    result, status = get_order_logic(current_user, order_id)
    return jsonify(result), status

@customer_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()
    result, status = create_order_logic(current_user, data)
    return jsonify(result), status

@customer_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@token_required
def delete_order(current_user, order_id):
    result, status = delete_order_logic(current_user, order_id)
    return jsonify(result), status
