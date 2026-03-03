from flask import Blueprint, jsonify
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

@org_admin_bp.route('users/<int:user_id>', methods=['GET'])
@token_required(roles=['admin', 'supervisor', 'staff'])
def get_user(current_user, user_id):
    result, status = get_user_logic(user_id)
    return jsonify(result), status

