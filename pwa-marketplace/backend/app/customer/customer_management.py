import os
from temporalio.client import Client
import asyncio
from ...workflows.order_workflow import OrderWorkflow
from ..shared.database import db
from ..shared.models import Customers, Stores, FeaturedStores, StoreProductsServices, Orders, OrderDetails, EntityStatuses, OrderStatuses
import logging
from ..shared.auth import generate_token, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
import bleach
from datetime import datetime

TEMPORAL_HOST = os.environ.get('TEMPORAL_HOST', "localhost:7233")

# Temporary Temporal Client connection helper
async def get_temporal_client():
    # Note: Using localhost for dev. In production, use environment variables.
    return await Client.connect(TEMPORAL_HOST)

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
        token = generate_token({'customer_id': new_customer.customer_id, 'customer_email': new_customer.customer_email})
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
        return {'message': 'Invalid credentials'}, 401
    # Check status is active
    if not customer.customer_status or customer.customer_status.status_code != 'active':
        return {'message': 'Customer is not Active'}, 403
    if not check_password_hash(customer.customer_password_hash, data['customer_password']):
        return {'message': 'Invalid credentials'}, 401
    token = generate_token({'customer_id': customer.customer_id, 'customer_email': customer.customer_email})
    return {'message': 'Login successful', 'token': token}, 200

def decode_customer_logic(data):
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
    sps_list = StoreProductsServices.query.filter_by(store_id=store_id, status_id=active_status_id).all()
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

def get_orders_logic(current_customer):
    # Only return orders with relevant order_statuses.status_code
    valid_status_codes = [
        'open', 'paid', 'pending', 'partial_pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
        'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
        'refunded', 'partial_refunded', 'customer_accepted'
    ]
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(valid_status_codes)).all()]
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
    valid_status_codes = [
        'open', 'paid', 'pending', 'partial_pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
        'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
        'refunded', 'partial_refunded', 'customer_accepted'
    ]
    status_ids = [s.status_id for s in OrderStatuses.query.filter(OrderStatuses.status_code.in_(valid_status_codes)).all()]
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
    total_quantity = 0
    total_price = 0
    order_details = []
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
        item_ids = []
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
            price = float(sps.price)
            total_quantity += quantity
            total_price += price * quantity
            # Add data to order_details list using append method
            order_details.append({'store_product_service_id': sps.id, 'quantity': quantity, 'price': price})
            item_ids.append(sps.id)
        # Set initial order status to 'open' in DB for reference
        open_status = OrderStatuses.query.filter_by(status_code='open').first()
        if not open_status:
            logging.error("Order Status 'Open' not found during create_order_logic")
            return {'message': 'Order Status "Open" not found'}, 500
        new_order = Orders()
        new_order.order_tot_quantity = total_quantity
        new_order.order_tot_price = total_price
        new_order.customer_id = customer.customer_id
        new_order.order_status_id = open_status.status_id
        db.session.add(new_order)
        db.session.flush()  # Get order_id
        for od in order_details:
            detail = OrderDetails()
            detail.order_id = new_order.order_id
            detail.store_product_service_id = od['store_product_service_id']
            detail.product_service_quantity = od['quantity']
            detail.product_service_price = od['price']
            detail.product_service_tot_price = od['price'] * od['quantity']
            detail.product_service_status_id = open_status.status_id
            detail.product_service_filled_quantity = 0
            detail.product_service_filled_tot_price = 0
            detail.product_service_created_at = datetime.utcnow()
            db.session.add(detail)
        db.session.commit()
        # Start Temporal workflow for order
        async def start_order_workflow():
            client = await Client.connect("localhost:7233")
            # await client.start_workflow(OrderWorkflow.run, new_order.order_id, item_ids, id=f"order-{new_order.order_id}")
            await client.start_workflow(OrderWorkflow.run, new_order.order_id, item_ids, total_price)
        asyncio.run(start_order_workflow())
        return {'message': 'Order created successfully', 'order_id': new_order.order_id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Order: {e}")
        return {'message': 'Failed to Create Order'}, 500

def cancel_order_logic(current_customer, order_id):
    """
    Allows the customer to request order cancellation (pre-shipment only).
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
        return {'message': 'Customer not found or Inactive'}, 403
    order = Orders.query.get_or_404(order_id)
    if order.customer_id != current_customer.customer_id:
        logging.warning("Order does not belong to Customer during cancel_order_logic")
        return {'message': 'Order does not belong to Customer'}, 403
    # Only allow cancellation if order status is in allowed list
    # allowed_status_codes = ['open', 'paid', 'pending', 'filled', 'partial_filled']
    # if not order.order_status or order.order_status.status_code not in allowed_status_codes:
    #    return {'message': f"Order cannot be Cancelled in its current Status: {order.order_status.status_display if order.order_status else 'Unknown'}"}, 400
    try:
        # Signal Temporal workflow to cancel order
        async def cancel_order_workflow():
            client = await get_temporal_client()
            handle = client.get_workflow_handle(f"order-{order_id}")
            # handle = client.get_workflow_handle(f"order-{order_id}", workflow_id=f"order-{order_id}")
            # Ensure your signal name matches the one in order_workflow.py/Parent Workflow
            await handle.signal("cancel_order")
        asyncio.run(cancel_order_workflow())
        # Issue: Order Cancellation might fail cause Order Status is far from cancellable
        # --- The DB update is handled by the Activity in order_activities.py ---
        return {'message': 'Order Cancellation initiated successfully. Status Update pending workflow execution'}, 202 # Use 202 Accepted
    except Exception as e:
        logging.error(f"Error signalling order cancellation: {e}")
        return {'message': 'Failed to Signal Order Cancellation'}, 500
    
def return_item_logic(order_id, item_id, current_customer):
    """
    Allows the customer to request a return for a specific item (post-delivery only).
    The Order Workflow handles the item-level signaling and the 10-day window check
    """
    # Issue: Check customer is active
    if not current_customer:
        return {'message': 'Customer not found or Inactive'}, 403
    order = Orders.query.get_or_404(order_id)
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
            await handle.signal("initiate_return", item_id)
        
        asyncio.run(return_item_workflow())
        
        return {'message': f'Return initiated successfully for Item {item_id}. Status Update pending workflow execution.'}, 202
    except Exception as e:
        logging.error(f"Error signalling Item Return for {order_id}/{item_id}: {e}")
        return {'message': 'Failed to Signal Item Return'}, 500