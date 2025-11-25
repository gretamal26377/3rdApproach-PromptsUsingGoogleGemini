from .database import db
from ..shared.models import Customers, Store, FeaturedStores, Product, Order, OrderItem, EntityStatuses, OrderStatuses
import logging
from ..shared.auth import generate_token, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
import bleach
from datetime import datetime


def register_user_logic(data):
    if not data:
        return {'message': 'No data provided'}, 400
    required_fields = ['customer_name', 'customer_password', 'customer_email', 'customer_phone']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    # Sanitize name and email
    customer_name = bleach.clean(data['customer_name'], strip=True)
    customer_email = bleach.clean(data['customer_email'], strip=True)
    customer_phone = bleach.clean(data['customer_phone'], strip=True)
    # Only allow registration if email is unique and status is active
    if Customers.query.filter_by(customer_email=customer_email).first():
        return {'message': 'Email already exists'}, 400
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        return {'message': 'Active status not found'}, 500
    try:
    
        password_hash = generate_password_hash(data['customer_password'])
        new_customer = Customers(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_password_hash=password_hash,
            customer_phone=customer_phone,
            customer_status_id=active_status.status_id
        )
        db.session.add(new_customer)
        db.session.commit()
        token = generate_token({'customer_id': new_customer.customer_id, 'customer_email': new_customer.customer_email})
        return {'message': 'Customer created successfully', 'token': token}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Customer: {e}")
        return {'message': 'Failed to create Customer'}, 500

def login_user_logic(data):
    if not data:
        return {'message': 'No data provided'}, 400
    required_fields = ['customer_email', 'customer_password']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    customer = Customers.query.filter_by(customer_email=data['customer_email']).first()
    if not customer:
        return {'message': 'Invalid credentials'}, 401
    # Check status is active
    if not customer.customer_status or customer.customer_status.status_code != 'active':
        return {'message': 'Customer is not Active'}, 403
    if not check_password_hash(customer.customer_password_hash, data['customer_password']):
        return {'message': 'Invalid credentials'}, 401
    token = generate_token({'customer_id': customer.customer_id, 'customer_email': customer.customer_email})
    return {'message': 'Login successful', 'token': token}, 200

def decode_user_logic(data):
    if not data or 'token' not in data:
        return {'message': 'No token provided'}, 400
    token = data['token']
    decoded = decode_token(token)
    if decoded and 'customer_id' in decoded:
        customer = Customers.query.get(decoded['customer_id'])
        if customer and customer.customer_status and customer.customer_status.status_code == 'active':
            customer_data = {
                'customer_id': customer.customer_id,
                'customer_name': customer.customer_name,
                'customer_email': customer.customer_email,
                'customer_phone': customer.customer_phone
            }
            return {'message': 'Token decoded successfully', 'customer': customer_data}, 200
        else:
            return {'message': 'Customer not found or Inactive'}, 404
    else:
        return {'message': 'Invalid or expired token'}, 401

# --- Featured Stores Logic ---
def get_featured_stores_logic():
    try:
        # Get status_id for 'active' status
        active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
        now = datetime.utcnow()
        # Query featured stores with active status and within date range
        featured = (
            FeaturedStores.query
            .join(Stores, FeaturedStores.store_id == Stores.store_id)
            .filter(
                FeaturedStores.start_date <= now,
                FeaturedStores.end_date >= now,
                Stores.store_status_id == active_status_id
            )
            .order_by(FeaturedStores.priority_order.asc())
            .all()
        )
        result = []
        for f in featured:
            store = f.store
            result.append({
                'id': store.store_id,
                'name': store.store_name,
                'picture_path': store.store_pic_path,
                'description': store.store_description,
                # Add more fields as needed
            })
        return result, 200
    except Exception as e:
        import logging
        logging.error(f"Error fetching Featured Stores: {e}")
        return {'message': 'Failed to fetch Featured Stores'}, 500

def get_stores_logic():
    # Only return stores with active status
    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    stores = Store.query.filter_by(store_status_id=active_status_id).all()
    stores_data = [
        {
            'id': store.store_id,
            'name': store.store_name,
            'description': store.store_description,
            'picture_path': store.store_pic_path,
            'email': store.store_email,
            'phone': store.store_phone,
            'address': store.store_address,
        }
        for store in stores
    ]
    return stores_data, 200

def get_store_logic(store_id):
    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    store = Store.query.filter_by(store_id=store_id, store_status_id=active_status_id).first()
    if not store:
        return {'message': 'Store not found or Inactive'}, 404
    store_data = {
        'id': store.store_id,
        'name': store.store_name,
        'description': store.store_description,
        'picture_path': store.store_pic_path,
        'email': store.store_email,
        'phone': store.store_phone,
        'address': store.store_address,
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
    # Only return products with active status and from active stores
    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    products = Product.query.join(Store, Product.store_id == Store.store_id)
    products = products.filter(
        Product.product_status_id == active_status_id,
        Store.store_status_id == active_status_id
    ).all()
    products_data = [
        {
            'id': product.product_id,
            'name': product.product_name,
            'description': product.product_description,
            'price': float(product.product_price),
            'store_id': product.store_id,
            'picture_path': product.product_pic_path,
        }
        for product in products
    ]
    return products_data, 200

def get_product_logic(product_id):
    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    product = Product.query.filter_by(product_id=product_id, product_status_id=active_status_id).first()
    if not product:
        return {'message': 'Product not found or Inactive'}, 404
    product_data = {
        'id': product.product_id,
        'name': product.product_name,
        'description': product.product_description,
        'price': float(product.product_price),
        'store_id': product.store_id,
        'picture_path': product.product_pic_path,
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
    # Only return orders with relevant order_statuses.status_code
    valid_statuses = ['open', 'pending', 'partial', 'complete', 'shipped', 'delivered', 'canceled']
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(valid_statuses)).all()]
    orders = Order.query.filter(
        Order.customer_id == current_user.customer_id,
        Order.order_status_id.in_(status_ids)
    ).all()
    orders_data = [
        {
            'id': order.order_id,
            'customer_id': order.customer_id,
            'order_date': order.order_date,
            'total_quantity': order.order_tot_quantity,
            'total_price': float(order.order_tot_price),
            'status': order.order_status.status_code if order.order_status else None,
            'items': [
                {
                    'store_product_service_id': item.store_product_service_id,
                    'quantity': item.product_service_quantity,
                    'price': float(item.product_service_price)
                } for item in order.order_details
            ]
        }
        for order in orders
    ]
    return orders_data, 200

def get_order_logic(current_user, order_id):
    valid_statuses = ['open', 'pending', 'partial', 'complete', 'shipped', 'delivered', 'canceled']
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(valid_statuses)).all()]
    order = Order.query.filter(
        Order.order_id == order_id,
        Order.customer_id == current_user.customer_id,
        Order.order_status_id.in_(status_ids)
    ).first()
    if not order:
        return {'message': 'Order not found or unauthorized'}, 404
    order_data = {
        'id': order.order_id,
        'customer_id': order.customer_id,
        'order_date': order.order_date,
        'total_quantity': order.order_tot_quantity,
        'total_price': float(order.order_tot_price),
        'status': order.order_status.status_code if order.order_status else None,
        'items': [
            {
                'store_product_service_id': item.store_product_service_id,
                'quantity': item.product_service_quantity,
                'price': float(item.product_service_price)
            } for item in order.order_details
        ]
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
