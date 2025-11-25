from .database import db
from ..shared.models import (
    Customers, Stores, FeaturedStores, ProductsServices, StoreProductsServices, Orders, OrderDetails, EntityStatuses, OrderStatuses
)
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

def get_orders_logic(current_user):
    # Only return orders with relevant order_statuses.status_code
    valid_statuses = ['open', 'pending', 'partial', 'complete', 'shipped', 'delivered', 'canceled']
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(valid_statuses)).all()]

    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    customer = Customers.query.filter_by(customer_id=current_user.customer_id, customer_status_id=active_status_id).first()

    if not customer:
        return {'message': 'Customer not found or Inactive'}, 403
    orders = Orders.query.filter_by(customer_id=current_user.customer_id).all()
    result = []
    for order in orders:
        details = OrderDetails.query.filter_by(order_id=order.order_id).all()
        items = [
            {
                'store_product_service_id': d.store_product_service_id,
                'quantity': d.product_service_quantity,
                'price': float(d.product_service_price),
                'total_price': float(d.product_service_tot_price)
            }
            for d in details
        ]
        result.append({
            'order_id': order.order_id,
            'total_quantity': order.order_tot_quantity,
            'total_price': float(order.order_tot_price),
            'status_id': order.order_status_id,
            'items': items,
            'created_at': order.created_at
        })
    return {'orders': result}, 200

def get_order_logic(current_customer, order_id):
    active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
    customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
    if not customer:
        return {'message': 'Customer not found or Inactive'}, 403

    # order = Orders.query.filter_by(order_id=order_id, customer_id=current_customer.customer_id).first()

    valid_statuses = ['open', 'pending', 'partial', 'complete', 'shipped', 'delivered', 'canceled']
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(valid_statuses)).all()]
    
    order = Orders.query.filter(
        Orders.customer_id == current_customer.customer_id,
        Orders.order_status_id.in_(status_ids)
    ).first()
    if not order:
        return {'message': 'Order not found or Inactive'}, 404
    
    # order_data = {
    #    'id': order.order_id,
    #    'customer_id': order.customer_id,

    # Orders.customer_id == current_user.customer_id,
    # Orders.order_status_id.in_(status_ids)


    # ).first()
    # if not order:
    #    return {'message': 'Order not found or unauthorized'}, 404
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

def create_order_logic(current_customer, data):
    required_fields = ['items']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    if not isinstance(data['items'], list):
        return {'message': 'Items must be a list'}, 400
    if not data['items']:
        return {'message': 'Items list cannot be empty'}, 400
    total_quantity = 0
    total_price = 0
    order_details = []
    try:
        active_status_id = EntityStatuses.query.filter_by(status_code='active').first().status_id
        # Check customer is active
        customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
        if not customer:
            return {'message': 'Customer not found or Inactive'}, 403
        for item in data['items']:
            if not all(field in item for field in ['store_product_service_id', 'quantity']):
                return {'message': 'Each item must contain store_product_service_id and quantity'}, 400
            sps = StoreProductsServices.query.filter_by(id=item['store_product_service_id'], status_id=active_status_id).first()
            if not sps:
                return {'message': f"Store Product/Service with id {item['store_product_service_id']} not found or Inactive"}, 400
            quantity = item['quantity']
            if quantity <= 0:
                return {'message': f"Quantity for Store Product/Service {item['store_product_service_id']} must be positive"}, 400
            price = float(sps.price)
            total_quantity += quantity
            total_price += price * quantity
            order_details.append({'store_product_service_id': sps.id, 'quantity': quantity, 'price': price})
        # Set initial order status to 'open'
        open_status = OrderStatuses.query.filter_by(status_code='open').first()
        if not open_status:
            return {'message': 'Order Status "Open" not found'}, 500
        new_order = Orders(
            order_tot_quantity=total_quantity,
            order_tot_price=total_price,
            customer_id=customer.customer_id,
            order_status_id=open_status.status_id
        )
        db.session.add(new_order)
        db.session.flush()  # Get order_id
        for od in order_details:
            detail = OrderDetails(
                order_id=new_order.order_id,
                store_product_service_id=od['store_product_service_id'],
                product_service_quantity=od['quantity'],
                product_service_price=od['price'],
                product_service_tot_price=od['price'] * od['quantity'],
                product_service_status_id=open_status.status_id,
                product_service_filled_quantity=0,
                product_service_filled_tot_price=0
            )
            db.session.add(detail)
        db.session.commit()
        return {'message': 'Order created successfully', 'order_id': new_order.order_id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Order: {e}")
        return {'message': 'Failed to Create Order'}, 500

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
