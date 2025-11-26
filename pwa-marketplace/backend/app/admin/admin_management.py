from ..shared.database import db
from ..shared.models import User
import logging
# bleach is used to sanitize inputs to prevent XSS attacks
import bleach

def get_users_logic():
    users = User.query.all()
    users_data = [{'id': user.id, 'username': user.username, 'email': user.email, 'is_admin': user.is_admin} for user in users]
    return users_data, 200

def get_user_logic(user_id):
    user = User.query.get_or_404(user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin
    }
    return user_data, 200

def update_user_logic(user_id, data):
    user = User.query.get_or_404(user_id)
    if not data:
        return {'message': 'No data provided'}, 400
    try:
        if 'username' in data:
            user.username = bleach.clean(data['username'], strip=True)
        if 'email' in data:
            user.email = bleach.clean(data['email'], strip=True)
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        db.session.commit()
        return {'message': 'User updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating user: {e}")
        return {'message': 'Failed to update user'}, 500

def delete_user_logic(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting user: {e}")
        return {'message': 'Failed to delete user'}, 500

def create_store_logic(current_user, data):
    required_fields = ['name', 'description']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    try:
        # Sanitize store name and description
        name = bleach.clean(data['name'], strip=True)
        description = bleach.clean(data['description'], strip=True)
        new_store = Store(name=name, description=description, owner_id=current_user.id)
        db.session.add(new_store)
        db.session.commit()
        return {'message': 'Store created successfully', 'store_id': new_store.id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating store: {e}")
        return {'message': 'Failed to create store'}, 500

def update_store_logic(current_user, store_id, data):
    store = Store.query.get_or_404(store_id)
    if store.owner_id != current_user.id:
        return {'message': 'Unauthorized'}, 403
    try:
        if 'name' in data:
            store.name = bleach.clean(data['name'], strip=True)
        if 'description' in data:
            store.description = bleach.clean(data['description'], strip=True)
        db.session.commit()
        return {'message': 'Store updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating store: {e}")
        return {'message': 'Failed to update store'}, 500

def delete_store_logic(current_user, store_id):
    store = Store.query.get_or_404(store_id)
    if store.owner_id != current_user.id:
        return {'message': 'Unauthorized'}, 403
    try:
        db.session.delete(store)
        db.session.commit()
        return {'message': 'Store deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting store: {e}")
        return {'message': 'Failed to delete store'}, 500

def create_product_logic(current_customer, data):
    required_fields = ['product_service_name', 'product_service_description', 'product_service_category_id', 'product_service_pic_path', 'store_id', 'price', 'stock']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    try:
        # Sanitize fields
        name = bleach.clean(data['product_service_name'], strip=True)
        description = bleach.clean(data['product_service_description'], strip=True)
        pic_path = bleach.clean(data['product_service_pic_path'], strip=True)
        active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
        # Check store exists and is active
        store = Stores.query.filter_by(store_id=data['store_id'], store_status_id=active_status_id).first()
        if not store:
            return {'message': 'Store not found or Inactive'}, 404
        # Create product/service
        new_product = ProductsServices(
            product_service_name=name,
            product_service_description=description,
            product_service_pic_path=pic_path,
            product_service_category_id=data['product_service_category_id'],
            product_service_status_id=active_status_id
        )
        db.session.add(new_product)
        db.session.flush()  # Get product_service_id
        # Create store-product-service link
        sps = StoreProductsServices(
            store_id=store.store_id,
            product_service_id=new_product.product_service_id,
            price=data['price'],
            stock=data['stock'],
            status_id=active_status_id
        )
        db.session.add(sps)
        db.session.commit()
        return {'message': 'Product/Service created successfully', 'product_service_id': new_product.product_service_id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Product/Service: {e}")
        return {'message': 'Failed to create Product/Service'}, 500

def update_product_logic(current_customer, product_service_id, data):
    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    product = ProductsServices.query.filter_by(product_service_id=product_service_id, product_service_status_id=active_status_id).first()
    if not product:
        return {'message': 'Product/Service not found or Inactive'}, 404
    try:
        if 'product_service_name' in data:
            product.product_service_name = bleach.clean(data['product_service_name'], strip=True)
        if 'product_service_description' in data:
            product.product_service_description = bleach.clean(data['product_service_description'], strip=True)
        if 'product_service_pic_path' in data:
            product.product_service_pic_path = bleach.clean(data['product_service_pic_path'], strip=True)
        if 'product_service_category_id' in data:
            product.product_service_category_id = data['product_service_category_id']
        db.session.commit()
        return {'message': 'Product/Service updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating Product/Service: {e}")
        return {'message': 'Failed to update Product/Service'}, 500

def delete_product_logic(current_customer, product_service_id):
    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    product = ProductsServices.query.filter_by(product_service_id=product_service_id, product_service_status_id=active_status_id).first()
    if not product:
        return {'message': 'Product/Service not found or Inactive'}, 404
    try:
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product/Service Inactivated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error Inactivating Product/Service: {e}")
        return {'message': 'Failed to Inactivate Product/Service'}, 500

