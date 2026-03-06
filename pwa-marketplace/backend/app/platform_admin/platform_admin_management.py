# Platform Admin Business Logic

import logging
from backend.app.shared.models import EntityStatuses, ProductsServices


def get_organisations():
    # In real app, query Organisations table
    return ["OrgA", "OrgB"]

def create_product_service_logic(current_user, data):
    required_fields = ['product_service_name', 'product_service_description', 'product_service_category_id', 'product_service_pic_path']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    try:
        # Sanitize fields
        name = bleach.clean(data['product_service_name'], strip=True)
        description = bleach.clean(data['product_service_description'], strip=True)
        pic_path = bleach.clean(data['product_service_pic_path'], strip=True)
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            logging.error("Active Status not found")
            return {'message': 'Active Status not configured'}, 500
        active_status_id = active_status.status_id
        # Create Product/Service
        new_product_service = ProductsServices()
        new_product_service.product_service_name = name
        new_product_service.product_service_description = description
        new_product_service.product_service_pic_path = pic_path
        new_product_service.product_service_category_id = data['product_service_category_id']
        new_product_service.product_service_status_id = active_status_id
        db.session.add(new_product_service)
        db.session.commit()
        return {'message': 'Product/Service created successfully'}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Product/Service: {e}")
        return {'message': 'Failed to create Product/Service'}, 500
