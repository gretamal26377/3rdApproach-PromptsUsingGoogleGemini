import asyncio
import logging
from datetime import datetime

import bleach
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash

from ..shared.auth import decode_token, generate_token
from ..shared.database import db
from ..shared.models import ( Customers, Stores, FeaturedStores, StoresProductsServices, Orders, OrdersDetails,
    EntityStatuses, OrderStatuses, Categories, ProductsServices )
from ..shared.utils import get_temporal_client
from workflows.order_workflow import OrderWorkflow

VALID_STATUS_CODES = [
        'open', 'paid', 'pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
        'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
        'refunded', 'partial_refunded', 'customer_accepted'
    ]

def create_customer_logic(data):
    if not data:
        logging.warning("No data provided during create_customer_logic")
        return {'message': 'No data provided'}, 400
    required_fields = ['customer_name', 'customer_password', 'customer_email', 'customer_phone']
    if not all(field in data for field in required_fields):
        logging.warning("Missing required fields during create_customer_logic")
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
        logging.error("Active Status not found during create_customer_logic")
        return {'message': 'Active Status not found'}, 500
    try:
    
        password_hash = generate_password_hash(data['customer_password'])
        # Instantiate without kwargs to avoid constructor signature mismatch, then assign attributes
        new_customer = Customers()
        new_customer.customer_name = customer_name
        new_customer.customer_email = customer_email
        new_customer.customer_password_hash = password_hash
        new_customer.customer_phone = customer_phone
        new_customer.customer_status_id = active_status.status_id
        db.session.add(new_customer)
        db.session.commit()
        token = generate_token(new_customer.customer_id)
        return {'message': 'Customer created successfully', 'token': token}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Customer: {e}")
        return {'message': 'Failed to create Customer'}, 500

def login_customer_logic(data):
    if not data:
        logging.warning("No data provided during login_customer_logic")
        return {'message': 'No data provided'}, 400
    required_fields = ['customer_email', 'customer_password']
    if not all(field in data for field in required_fields):
        logging.warning("Missing required fields during login_customer_logic")
        return {'message': 'Missing required fields'}, 400
    customer = Customers.query.filter_by(customer_email=data['customer_email']).first()
    if not customer:
        return {'message': 'Invalid Credentials'}, 401
    # Check status is active
    if not customer.customer_status or customer.customer_status.status_code != 'active':
        return {'message': 'Customer is not Active'}, 403
    if not check_password_hash(customer.customer_password_hash, data['customer_password']):
        return {'message': 'Invalid Password'}, 401
    token = generate_token(customer.customer_id)
    return {
        'message': 'Login Successful',
        'token': token
    }, 200

def decode_customer_logic(data):
    # Prefer explicit token in payload; fall back to auth_token cookie for HttpOnly flows
    token = None
    if data and 'token' in data:
        token = data['token']
    if not token:
        token = request.cookies.get('auth_token')
    if not token:
        return {'message': 'No token provided'}, 400
    decoded = decode_token(token)
    if decoded:
        customer = Customers.query.get(decoded['user_id'])
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

# --- Categories Logic ---
def get_categories_logic():
    try:
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            return {'error': 'Active Status not found'}, 404
        active_status_id = active_status.status_id
        categories = Categories.query.filter_by(category_status_id=active_status_id).all()
        categories_data = [
            {
                'id': category.category_id,
                'name': category.category_name,
                'description': category.category_description,
                'picture_path': category.category_pic_path,
            }
            for category in categories
        ]
        return categories_data, 200
    except Exception as e:
        return {'error': str(e)}, 500

# --- Category Products/Services Logic ---
def get_category_products_services_logic(category_id):
    try:
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            return {'error': 'Active status not found'}, 404
        active_status_id = active_status.status_id
        products_services = ProductsServices.query.filter_by(category_id=category_id, product_service_status_id=active_status_id).all()
        products_services_data = [
            {
                'id': product_service.product_service_id,
                'name': product_service.product_service_name,
                'description': product_service.product_service_description,
                'price': product_service.product_service_price,
                # getattr used to avoid AttributeError if picture_path is not defined
                'picture_path': getattr(product_service, 'product_service_pic_path', None),
            }
            for product_service in products_services
        ]
        return products_services_data, 200
    except Exception as e:
        return {'error': str(e)}, 500

# --- Featured Stores Logic ---
def get_featured_stores_logic():
    try:
        # Get status_id for 'active' status
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            logging.error("Active Status not found during get_featured_stores_logic")
            return {'message': 'Active Status not found'}, 500
        active_status_id = active_status.status_id
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
        logging.error(f"Error fetching Featured Stores: {e}")
        return {'message': 'Failed to fetch Featured Stores'}, 500

def get_stores_logic():
    # Only return stores with active status
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during get_stores_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    stores = Stores.query.filter_by(store_status_id=active_status_id).all()
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
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during get_store_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    store = Stores.query.filter_by(store_id=store_id, store_status_id=active_status_id).first()
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

def get_store_products_services_logic(store_id):
    # Return all active products/services for a given store, using StoreProductsServices as join table
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during get_store_products_services_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    sps_list = StoresProductsServices.query.filter_by(store_id=store_id, status_id=active_status_id).all()
    store_products_services_data = []
    for sps in sps_list:
        ps = sps.product_service
        # Filter for active product_service as well
        if ps and ps.product_service_status_id == active_status_id:
            # Get category info if available
            category = None
            if ps.product_service_category:
                category = {
                    'id': ps.product_service_category.category_id,
                    'name': ps.product_service_category.category_name,
                    'picture_path': ps.product_service_category.category_pic_path
                }
            store_products_services_data.append({
                'id': ps.product_service_id,
                'name': ps.product_service_name,
                'description': ps.product_service_description,
                'price': float(sps.price),
                'store_id': sps.store_id,
                'picture_path': ps.product_service_pic_path,
                'stock': sps.stock,
                'category': category
            })
    return store_products_services_data, 200

def get_store_product_service_logic(store_product_service_id):
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during get_store_product_service_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    sps = StoreProductsServices.query.filter_by(id=store_product_service_id, status_id=active_status_id).first()
    if not sps:
        return {'message': 'Store Product/Service not found or Inactive'}, 404
    ps = sps.product_service
    if not ps or ps.product_service_status_id != active_status_id:
        return {'message': 'Product/Service not found or Inactive'}, 404
    # Get category info if available
    category = None
    if ps.product_service_category:
        category = {
            'id': ps.product_service_category.category_id,
            'name': ps.product_service_category.category_name,
            'description': ps.product_service_category.category_description,
            'picture_path': ps.product_service_category.category_pic_path
        }
    store_product_service_data = {
        'id': ps.product_service_id,
        'name': ps.product_service_name,
        'description': ps.product_service_description,
        'price': float(sps.price),
        'stock': sps.stock,
        'store_id': sps.store_id,
        'picture_path': ps.product_service_pic_path,
        'category': category
    }
    return store_product_service_data, 200

# --- Stores for Product/Service Logic ---
def get_stores_for_product_service_logic(product_service_id):
    try:
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            return {'error': 'Active status not found'}, 404
        active_status_id = active_status.status_id
        # Join StoresProductsServices and Stores, filter by product_service_id and active status
        sps_list = StoresProductsServices.query.filter_by(product_service_id=product_service_id, status_id=active_status_id).all()
        product_service_stores = []
        for sps in sps_list:
            store = Stores.query.filter_by(store_id=sps.store_id, store_status_id=active_status_id).first()
            if store and sps.stock > 0:
                product_service_stores.append({
                    'id': store.store_id,
                    'name': store.store_name,
                    'description': store.store_description,
                    'picture_path': store.store_pic_path,
                    'store_product_service': sps,
                    'price': getattr(sps, 'price', None),
                    'stock': getattr(sps, 'stock', None),
                })
        return product_service_stores, 200
    except Exception as e:
        return {'error': str(e)}, 500

def get_orders_logic(current_customer):
    # Only return orders with relevant order_statuses.status_code
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(VALID_STATUS_CODES)).all()]
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during get_orders_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
    if not customer:
        return {'message': 'Customer not found or Inactive'}, 403
    orders = Orders.query.filter(
        Orders.customer_id == current_customer.customer_id,
        Orders.order_status_id.in_(status_ids)
        ).all()

    result = []
    for order in orders:
        # Use the relationship for order details
        items = [
            {
                'store_product_service_id': d.store_product_service_id,
                'quantity': d.product_service_quantity,
                'price': float(d.product_service_price),
                'total_price': float(d.product_service_tot_price),
                'filled_quantity': d.product_service_filled_quantity,
                'filled_total_price': float(d.product_service_filled_tot_price),
                'status_code': d.product_service_status.status_code if d.product_service_status else None,
                'created_at': d.product_service_created_at
            }
            for d in order.order_details
        ]
        result.append({
            'order_id': order.order_id,
            'customer_id': order.customer_id,
            'total_quantity': order.order_tot_quantity,
            'total_price': float(order.order_tot_price),
            'order_status_code': order.order_status.status_code if order.order_status else None,
            'order_created_at': order.order_created_at,
            'items': items,
        })
    return {'orders': result}, 200

def get_order_logic(current_customer, order_id):
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during get_order_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
    if not customer:
        return {'message': 'Customer not found or Inactive'}, 403
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(VALID_STATUS_CODES)).all()]
    order = Orders.query.filter(
        Orders.customer_id == current_customer.customer_id,
        Orders.order_status_id.in_(status_ids), Orders.order_id == order_id
        ).first()
    if not order:
        logging.warning(f"Order {order_id} not found or does not belong to customer")
        return {'message': 'Order not found or does not belong to customer'}, 404
    order_data = {
        'order_id': order.order_id,
        'customer_id': order.customer_id,
        'total_quantity': order.order_tot_quantity,
        'total_price': float(order.order_tot_price),
        'order_status_code': order.order_status.status_code if order.order_status else None,
        'order_created_at': order.order_created_at,
        'items': [
            {
                'store_product_service_id': item.store_product_service_id,
                'quantity': item.product_service_quantity,
                'price': float(item.product_service_price),
                'total_price': float(item.product_service_tot_price),
                'filled_quantity': item.product_service_filled_quantity,
                'filled_total_price': float(item.product_service_filled_tot_price),
                'status_code': item.product_service_status.status_code if item.product_service_status else None,
                'created_at': item.product_service_created_at
            } for item in order.order_details
        ]
    }
    return {'order': order_data}, 200

def create_order_logic(current_customer, data):
    # Define an initial list containing the literal 'items'
    required_fields = ['items']
    # Check if all required fields (this case, just 'items') are present in data
    if not all(field in data for field in required_fields):
        logging.warning("Missing required fields during create_order_logic")
        return {'message': 'Missing required fields'}, 400
    if not isinstance(data['items'], list):
        logging.warning("Items must be a list during create_order_logic")
        return {'message': 'Items must be a list'}, 400
    if not data['items']:
        logging.warning("Items list cannot be empty during create_order_logic")
        return {'message': 'Items list cannot be empty'}, 400
    try:
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            logging.error("Active Status not found during create_order_logic")
            return {'message': 'Active Status not found'}, 500
        active_status_id = active_status.status_id
        # Check customer is active
        customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
        if not customer:
            return {'message': 'Customer not found or Inactive'}, 403
        # Validate and collect all item info
        order_items = []
        for item in data['items']:
            if not all(field in item for field in ['store_product_service_id', 'quantity']):
                logging.warning("Missing required fields during create_order_logic")
                return {'message': 'Each item must contain store_product_service_id and quantity'}, 400
            sps = StoreProductsServices.query.filter_by(id=item['store_product_service_id'], status_id=active_status_id).first()
            if not sps:
                return {'message': f"Store Product/Service with id {item['store_product_service_id']} not found or Inactive"}, 400
            quantity = item['quantity']
            if quantity <= 0:
                logging.warning(f"Quantity for Store Product/Service {item['store_product_service_id']} must be positive")
                return {'message': f"Quantity for Store Product/Service {item['store_product_service_id']} must be positive"}, 400
            # Collect all fields needed for OrderDetails
            order_items.append({
                'store_product_service_id': sps.id,
                'product_service_quantity': quantity,
                'product_service_price': float(sps.price),
                'product_service_tot_price': float(sps.price) * quantity,
                'product_service_status_id': None,  # Will be set in activity
                'product_service_filled_quantity': 0,
                'product_service_filled_tot_price': 0,
                'product_service_created_at': datetime.utcnow(),
                # Add any additional fields from OrderDetails model as needed
            })
        # Prepare a single input dict for the workflow containing all order and order_details data
        order_input = {
            'customer_id': customer.customer_id,
            'order_tot_quantity': sum(i['product_service_quantity'] for i in order_items),
            'order_tot_price': sum(i['product_service_tot_price'] for i in order_items),
            'order_created_at': datetime.utcnow().isoformat(),
            # Add any additional Orders fields as needed
            'items': order_items
        }

        async def create_order_via_activity():
            client = await get_temporal_client()
            # Start the workflow, passing all order data as a single input
            result = await client.start_workflow(  # type: ignore[arg-type]
                OrderWorkflow.run,
                order_input
            )
            return result
        
        workflow_result = asyncio.run(create_order_via_activity())
        # Expect workflow_result to contain order_id (if returned by workflow)
        return {'message': 'Order created successfully', 'order_id': getattr(workflow_result, 'order_id', None)}, 201
    except Exception as e:
        logging.error(f"Error creating Order: {e}")
        return {'message': 'Failed to Create Order'}, 500

def cancel_order_logic(current_customer, order_id):
    """
    Allows the Customer to request Order Cancellation (pre-shipment only).
    The Order Workflow handles the status check and propagation
    """
    # Check customer is active
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during cancel_order_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
    if not customer:
        logging.warning(f"Customer: {current_customer.customer_id} not found or inactive during cancel_order_logic")
        return {'message': 'Customer not found or Inactive'}, 403
    order = Orders.query.get(order_id)
    if not order:
        logging.warning(f"Order: {order_id} not found during cancel_order_logic")
        return {'message': 'Order not found'}, 404
    if order.customer_id != current_customer.customer_id:
        logging.warning(f"Order: {order_id} does not belong to Customer: {current_customer.customer_id} during cancel_order_logic")
        return {'message': 'Order does not belong to Customer'}, 403
    
    # Only allow cancellation if order status is in allowed list
    allowed_status_codes = ['open', 'paid', 'filled', 'partial_filled',
                            'partial_shipped', 'partial_cancelled', 'partial_delivered', 'partial_returned',
                            'partial_refunded']
    if not order.order_status or order.order_status.status_code not in allowed_status_codes:
        return {'message': f"Order cannot be Cancelled in its current Status: {order.order_status.status_display if order.order_status else 'Unknown'}"}, 400
    
    try:
        # Signal Temporal Workflow to Cancel Order
        async def cancel_order_workflow():
            client = await get_temporal_client()
            handle = client.get_workflow_handle(f"order-{order_id}")
            # handle = client.get_workflow_handle(f"order-{order_id}", workflow_id=f"order-{order_id}")
            # Ensure your signal name matches one in order_workflow.py/Parent Workflow
            await handle.signal("cancel_order")

        asyncio.run(cancel_order_workflow())
        # --- The DB update is handled by the Activity in order_activities.py ---
        return {'message': 'Order Cancellation initiated successfully. Status Update pending workflow execution'}, 202 # Use 202 Accepted
    except Exception as e:
        logging.error(f"Error signalling Order Cancellation for Order: {order_id}, Customer: {current_customer.customer_id} during cancel_order_logic: {e}")
        return {'message': 'Failed to Signal Order Cancellation'}, 500
    
def return_item_logic(order_id, item_id, current_customer):
    """
    Allows the customer to request a return for a specific item (post-delivery only).
    The Order Workflow handles the item-level signaling and the 10-day window check
    """
    # Issue: Return process should be a Bulk process triggered by Customer
    # Issue: Check if Order Status is in possible status to return
    # Issue: Check if Customer is active
    if not current_customer:
        return {'message': 'Customer not found or Inactive'}, 403
    order = Orders.query.get(order_id)
    if not order:
        logging.warning(f"Order: {order_id} not found during return_item_logic")
        return {'message': 'Order not found'}, 404
    if order.customer_id != current_customer.customer_id:
        logging.warning("Order does not belong to Customer during return_item_logic")
        return {'message': 'Order does not belong to Customer'}, 403
    
    # Check if item exists in order (simple check, full check is in the workflow)
    if not OrderDetails.query.filter_by(order_id=order_id, item_id=item_id).first():
         return {'message': f'Item {item_id} not found in Order {order_id}.'}, 404
    try:
        # Signal Temporal workflow to initiate item return
        async def return_item_workflow():
            client = await get_temporal_client()
            handle = client.get_workflow_handle(f"order-{order_id}")
            # handle = client.get_workflow_handle(f"order-{order_id}", workflow_id=f"order-{order_id}")
            # Signal the parent workflow, which propagates the signal to the specific item
            await handle.signal("start_return")
        
        asyncio.run(return_item_workflow())
        return {'message': f'Return initiated successfully for Item {item_id}. Status Update pending workflow execution.'}, 202
    except Exception as e:
        logging.error(f"Error signalling Item Return for {order_id}/{item_id}: {e}")
        return {'message': 'Failed to Signal Item Return'}, 500