from flask import Blueprint, jsonify, request
from ..shared.auth import token_required
from ..shared.management import (
    get_users_logic, get_user_logic, create_user_logic, update_user_logic, inactivate_user_logic,
    create_store_logic, update_store_logic, inactivate_store_logic,
    create_store_product_service_logic, update_store_product_service_logic, inactivate_store_product_service_logic,
    mark_order_shipped_logic, refund_order_logic, accept_order_logic
)


org_admin_bp = Blueprint('org_admin_bp', __name__, url_prefix='')

@org_admin_bp.route('users', methods=['GET'])
@token_required('org_admin', roles=['admin', 'supervisor', 'staff'])
def get_users(current_user):
    result, status = get_users_logic()
    return jsonify(result), status

@org_admin_bp.route('users/<int:user_id>', methods=['GET'])
@token_required('org_admin', roles=['admin', 'supervisor', 'staff'])
def get_user(current_user, user_id):
    result, status = get_user_logic(user_id)
    return jsonify(result), status

@org_admin_bp.route('users', methods=['POST'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def create_user(current_user):
    data = request.get_json()
    result, status = create_user_logic(data)
    return jsonify(result), status

@org_admin_bp.route('users/<int:user_id>', methods=['PUT'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def update_user(current_user, user_id):
    data = request.get_json()
    result, status = update_user_logic(user_id, data)
    return jsonify(result), status

@org_admin_bp.route('users/<int:user_id>/inactivate', methods=['POST'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def inactivate_user(current_user, user_id):
    result, status = inactivate_user_logic(user_id)
    return jsonify(result), status

@org_admin_bp.route('stores', methods=['POST'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def create_store(current_user):
    data = request.get_json()
    result, status = create_store_logic(current_user, data)
    return jsonify(result), status

@org_admin_bp.route('stores/<int:store_id>', methods=['PUT'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def update_store(current_user, store_id):
    data = request.get_json()
    result, status = update_store_logic(current_user, store_id, data)
    return jsonify(result), status

@org_admin_bp.route('stores/<int:store_id>/inactivate', methods=['POST'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def inactivate_store(current_user, store_id):
    result, status = inactivate_store_logic(current_user, store_id)
    return jsonify(result), status

@org_admin_bp.route('create-store-product-service', methods=['POST'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def create_store_product_service(current_user):
    data = request.get_json()
    result, status = create_store_product_service_logic(current_user, data)
    return jsonify(result), status

@org_admin_bp.route('update-store-product-service/<int:store_product_service_id>', methods=['PUT'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def update_store_product_service(current_user, store_product_service_id):
    data = request.get_json()
    result, status = update_store_product_service_logic(current_user, store_product_service_id, data)
    return jsonify(result), status

@org_admin_bp.route('inactivate-store-product-service/<int:store_product_service_id>', methods=['POST'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def inactivate_store_product_service(current_user, store_product_service_id):
    result, status = inactivate_store_product_service_logic(current_user, store_product_service_id)
    return jsonify(result), status

@org_admin_bp.route('orders/<int:order_id>/ship', methods=['PATCH'])
@token_required('org_admin', roles=['admin', 'supervisor', 'staff'])
def mark_order_shipped(current_user, order_id):
    """Signals the OrderWorkflow to handle shipping"""
    result, status = mark_order_shipped_logic(order_id)
    return jsonify(result), status

@org_admin_bp.route('orders/<int:order_id>/refund', methods=['PATCH'])
@token_required('org_admin', roles=['admin', 'supervisor'])
def refund_order(current_user, order_id):
    """Signals the OrderWorkflow to initiate a refund"""
    result, status = refund_order_logic(order_id)
    return jsonify(result), status