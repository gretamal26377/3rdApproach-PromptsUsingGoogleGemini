from flask import Blueprint, jsonify

platform_admin_bp = Blueprint('platform_admin_bp', __name__, url_prefix='/api/platform')

@platform_admin_bp.route('/organisations', methods=['GET'])
def list_organisations():
    # Placeholder: In real app, query Organisations model
    return jsonify({"organisations": ["OrgA", "OrgB"]}), 200
