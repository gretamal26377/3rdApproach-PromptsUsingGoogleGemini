from .models import Product, Store, db
import logging

def create_product_logic(current_user, data):
    required_fields = ['name', 'description', 'price', 'store_id']
    if not all(field in data for field in required_fields):
        return {'error': 'Missing required fields'}, 400
    try:
        store = Store.query.get_or_404(data['store_id'])
        if store.owner_id != current_user.id and not current_user.is_admin:
            return {'error': 'Unauthorized to add product to this store'}, 403
        new_product = Product(name=data['name'], description=data['description'], price=data['price'], store_id=data['store_id'])
        db.session.add(new_product)
        db.session.commit()
        return {'message': 'Product created successfully', 'product_id': new_product.id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating product: {e}")
        return {'error': 'Failed to create product'}, 500

def update_product_logic(current_user, product_id, data):
    product = Product.query.get_or_404(product_id)
    store = Store.query.get(product.store_id)
    if store.owner_id != current_user.id and not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'store_id' in data:
            product.store_id = data['store_id']
        db.session.commit()
        return {'message': 'Product updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating product: {e}")
        return {'error': 'Failed to update product'}, 500

def delete_product_logic(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    store = Store.query.get(product.store_id)
    if store.owner_id != current_user.id and not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    try:
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting product: {e}")
        return {'error': 'Failed to delete product'}, 500
