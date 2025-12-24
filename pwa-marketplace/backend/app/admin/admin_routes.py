from flask import Blueprint, jsonify, request
from ..shared.auth import token_required, admin_required
from .admin_management import (
    get_users_logic, get_user_logic, update_user_logic, inactivate_user_logic,
    create_store_logic, update_store_logic, inactivate_store_logic,
    create_product_logic, update_product_logic, inactivate_product_logic,
    mark_order_shipped_logic, refund_order_logic
)


admin_bp = Blueprint('admin_bp', __name__, url_prefix='api/admin')

@admin_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    result, status = get_users_logic()
    return jsonify(result), status

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(current_user, user_id):
    result, status = get_user_logic(user_id)
    return jsonify(result), status

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    data = request.get_json()
    result, status = update_user_logic(user_id, data)
    return jsonify(result), status

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def inactivate_user(current_user, user_id):
    result, status = inactivate_user_logic(user_id)
    return jsonify(result), status

@admin_bp.route('/stores', methods=['POST'])
@token_required
def create_store(current_user):
    data = request.get_json()
    result, status = create_store_logic(current_user, data)
    return jsonify(result), status

@admin_bp.route('/stores/<int:store_id>', methods=['PUT'])
@token_required
def update_store(current_user, store_id):
    data = request.get_json()
    result, status = update_store_logic(current_user, store_id, data)
    return jsonify(result), status

@admin_bp.route('/stores/<int:store_id>', methods=['DELETE'])
@token_required
def delete_store(current_user, store_id):
    result, status = inactivate_store_logic(current_user, store_id)
    return jsonify(result), status

@admin_bp.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json()
    result, status = create_product_logic(current_user, data)
    return jsonify(result), status

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    data = request.get_json()
    result, status = update_product_logic(current_user, product_id, data)
    return jsonify(result), status

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    result, status = inactivate_product_logic(current_user, product_id)
    return jsonify(result), status

@admin_bp.route('/orders/<int:order_id>/ship', methods=['PATCH'])
@token_required
@admin_required
def mark_order_shipped(current_user, order_id):
    """Signals the OrderWorkflow to handle shipping"""
    result, status = mark_order_shipped_logic(order_id)
    return jsonify(result), status

@admin_bp.route('/orders/<int:order_id>/refund', methods=['PATCH'])
@token_required
@admin_required
def refund_order(current_user, order_id):
    """Signals the OrderWorkflow to initiate a refund"""
    result, status = refund_order_logic(order_id)
    return jsonify(result), status