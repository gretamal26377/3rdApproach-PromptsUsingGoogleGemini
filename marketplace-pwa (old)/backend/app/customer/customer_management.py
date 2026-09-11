from ..shared.models import User, Store, Product, Order, OrderItem, db
import logging
from ..shared.auth import generate_token, decode_token
import bleach

def register_user_logic(data):
    if not data:
        return {'message': 'No data provided'}, 400
    required_fields = ['username', 'password', 'email']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    # Sanitize username and email
    username = bleach.clean(data['username'], strip=True)
    email = bleach.clean(data['email'], strip=True)
    if User.query.filter_by(username=username).first():
        return {'message': 'Username already exists'}, 400
    if User.query.filter_by(email=email).first():
        return {'message': 'e-mail already exists'}, 400
    try:
        new_user = User(username=username, email=email) # type: ignore
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        token = generate_token(new_user)
        return {'message': 'User created successfully', 'token': token}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating user: {e}")
        return {'message': 'Failed to create user'}, 500

def login_user_logic(data):
    if not data:
        return {'message': 'No data provided'}, 400
    required_fields = ['username', 'password']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return {'message': 'Invalid credentials'}, 401
    token = generate_token(user)
    return {'message': 'Login successful', 'token': token}, 200

def decode_user_logic(data):
    if not data or 'token' not in data:
        return {'message': 'No token provided'}, 400
    token = data['token']
    user_id = decode_token(token)
    if user_id:
        user = User.query.get(user_id)
        if user:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            return {'message': 'Token decoded successfully', 'user': user_data}, 200
        else:
            return {'message': 'User not found for this token'}, 404
    else:
        return {'message': 'Invalid or expired token'}, 401

def get_stores_logic():
    stores = Store.query.all()
    stores_data = [{'id': store.id, 'name': store.name, 'description': store.description, 'owner_id': store.owner_id} for store in stores]
    return stores_data, 200

def get_store_logic(store_id):
    store = Store.query.get_or_404(store_id)
    store_data = {
        'id': store.id,
        'name': store.name,
        'description': store.description,
        'owner_id': store.owner_id
    }
    return store_data, 200

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

def get_products_logic():
    products = Product.query.all()
    products_data = [{'id': product.id, 'name': product.name, 'description': product.description, 'price': product.price, 'store_id': product.store_id} for product in products]
    return products_data, 200

def get_product_logic(product_id):
    product = Product.query.get_or_404(product_id)
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'store_id': product.store_id
    }
    return product_data, 200

def create_product_logic(current_user, data):
    required_fields = ['name', 'description', 'price', 'store_id']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    try:
        store = Store.query.get_or_404(data['store_id'])
        if store.owner_id != current_user.id:
            return {'message': 'Unauthorized to add product to this store'}, 403
        # Sanitize product name and description
        name = bleach.clean(data['name'], strip=True)
        description = bleach.clean(data['description'], strip=True)
        new_product = Product(name=name, description=description, price=data['price'], store_id=data['store_id'])
        db.session.add(new_product)
        db.session.commit()
        return {'message': 'Product created successfully', 'product_id': new_product.id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating product: {e}")
        return {'message': 'Failed to create product'}, 500

def update_product_logic(current_user, product_id, data):
    product = Product.query.get_or_404(product_id)
    store = Store.query.get(product.store_id)
    if store.owner_id != current_user.id:
        return {'message': 'Unauthorized'}, 403
    try:
        if 'name' in data:
            product.name = bleach.clean(data['name'], strip=True)
        if 'description' in data:
            product.description = bleach.clean(data['description'], strip=True)
        if 'price' in data:
            product.price = data['price']
        if 'store_id' in data:
            product.store_id = data['store_id']
        db.session.commit()
        return {'message': 'Product updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating product: {e}")
        return {'message': 'Failed to update product'}, 500

def delete_product_logic(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    store = Store.query.get(product.store_id)
    if store.owner_id != current_user.id:
        return {'message': 'Unauthorized'}, 403
    try:
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting product: {e}")
        return {'message': 'Failed to delete product'}, 500

def get_orders_logic(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).all()
    orders_data = [{
        'id': order.id,
        'user_id': order.user_id,
        'order_date': order.order_date,
        'total_amount': order.total_amount,
        'items': [{'product_id': item.product_id, 'quantity': item.quantity} for item in order.items]
    } for order in orders]
    return orders_data, 200

def get_order_logic(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return {'message': 'Unauthorized'}, 403
    order_data = {
        'id': order.id,
        'user_id': order.user_id,
        'order_date': order.order_date,
        'total_amount': order.total_amount,
        'items': [{'product_id': item.product_id, 'quantity': item.quantity} for item in order.items]
    }
    return order_data, 200

def create_order_logic(current_user, data):
    required_fields = ['items']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    if not isinstance(data['items'], list):
        return {'message': 'Items must be a list'}, 400
    if not data['items']:
        return {'message': 'Items list cannot be empty'}, 400
    total_amount = 0
    order_items = []
    try:
        for item in data['items']:
            if not all(field in item for field in ['product_id', 'quantity']):
                return {'message': 'Each item must contain product_id and quantity'}, 400
            product = Product.query.get(item['product_id'])
            if not product:
                return {'message': f"Product with id {item['product_id']} not found"}, 400
            quantity = item['quantity']
            if quantity <= 0:
                return {'message': f"Quantity for product {item['product_id']} must be greater than zero"}, 400
            total_amount += product.price * quantity
            order_items.append(OrderItem(product_id=item['product_id'], quantity=quantity))
        new_order = Order(user_id=current_user.id, total_amount=total_amount, items=order_items)
        db.session.add(new_order)
        db.session.commit()
        return {'message': 'Order created successfully', 'order_id': new_order.id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating order: {e}")
        return {'message': 'Failed to create order'}, 500

def delete_order_logic(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return {'message': 'Unauthorized'}, 403
    try:
        db.session.delete(order)
        db.session.commit()
        return {'message': 'Order deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting order: {e}")
        return {'message': 'Failed to delete order'}, 500
