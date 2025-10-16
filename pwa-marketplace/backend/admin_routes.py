from flask import Blueprint, jsonify, request
from ..shared.auth import token_required, admin_required
from .admin_management import get_users_logic, get_user_logic, update_user_logic, delete_user_logic

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin/api')

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
def delete_user(current_user, user_id):
    result, status = delete_user_logic(user_id)
    return jsonify(result), status
