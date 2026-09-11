from .models import Store, db
import logging

def create_store_logic(current_user, data):
    required_fields = ['name', 'description']
    if not all(field in data for field in required_fields):
        return {'error': 'Missing required fields'}, 400
    try:
        new_store = Store(name=data['name'], description=data['description'], owner_id=current_user.id)
        db.session.add(new_store)
        db.session.commit()
        return {'message': 'Store created successfully', 'store_id': new_store.id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating store: {e}")
        return {'error': 'Failed to create store'}, 500

def update_store_logic(current_user, store_id, data):
    store = Store.query.get_or_404(store_id)
    if store.owner_id != current_user.id and not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    try:
        if 'name' in data:
            store.name = data['name']
        if 'description' in data:
            store.description = data['description']
        db.session.commit()
        return {'message': 'Store updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating store: {e}")
        return {'error': 'Failed to update store'}, 500

def delete_store_logic(current_user, store_id):
    store = Store.query.get_or_404(store_id)
    if store.owner_id != current_user.id and not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    try:
        db.session.delete(store)
        db.session.commit()
        return {'message': 'Store deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting store: {e}")
        return {'error': 'Failed to delete store'}, 500
