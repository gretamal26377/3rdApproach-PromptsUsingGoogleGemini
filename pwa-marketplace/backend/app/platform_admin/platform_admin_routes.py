from urllib import request
from backend.app.shared.auth import token_required
from flask import Blueprint, jsonify
from .platform_admin_management import get_organisations, create_product_service_logic
from ..shared.management import (
    get_users_logic, get_user_logic, create_user_logic, update_user_logic, inactivate_user_logic,
    create_store_logic, update_store_logic, inactivate_store_logic,
    create_product_logic, update_product_logic, inactivate_product_logic,
    mark_order_shipped_logic, refund_order_logic, accept_order_logic
)

platform_admin_bp = Blueprint('platform_admin_bp', __name__, url_prefix='')

@platform_admin_bp.route('/organisations', methods=['GET'])
def list_organisations():
    # Placeholder: In real app, query Organisations model
    return jsonify({"organisations": ["OrgA", "OrgB"]}), 200

@platform_admin_bp.route('create-product-service', methods=['POST'])
@token_required('platform_admin', roles=['admin', 'supervisor'])
def create_product_service(current_user):
    data = request.get_json()
    result, status = create_product_service_logic(current_user, data)
    return jsonify(result), status

