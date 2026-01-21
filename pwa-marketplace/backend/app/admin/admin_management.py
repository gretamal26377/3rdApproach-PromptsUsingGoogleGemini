import os
from ..shared.database import db
from ..shared.models import (
    Customers, Users, Stores, ProductsServices, StoreProductsServices,
    EntityStatuses, Orders
)
from ..shared.utils import get_temporal_client
import logging
from temporalio.client import Client
import asyncio
from workflows.order_workflow import OrderWorkflow
from workflows.item_workflow import ItemWorkflow
# bleach is used to sanitize inputs to prevent XSS attacks
import bleach

TEMPORAL_HOST = os.environ.get('TEMPORAL_HOST', "localhost:7233")

def get_users_logic():
    users = Users.query.all()
    users_data = [{'id': user.id, 'username': user.username, 'email': user.email, 'is_admin': user.is_admin} for user in users]
    return users_data, 200

def get_user_logic(user_id):
    user = Users.query.get(user_id)
    if not user:
        logging.warning(f"User: {user_id} not found during get_user_logic")
        return {'message': 'User not found'}, 404
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin
    }
    return user_data, 200

def update_user_logic(user_id, data):
    user = Users.query.get(user_id)
    if not user:
        logging.warning(f"User: {user_id} not found during update_user_logic")
        return {'message': 'User not found'}, 404
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

def inactivate_user_logic(user_id):
    user = Users.query.get(user_id)
    if not user:
        logging.warning(f"User: {user_id} not found during inactivate_user_logic")
        return {'message': 'User not found'}, 404
    try:
        inactive = EntityStatuses.query.filter_by(status_code='inactive').first()
        if not inactive:
            logging.error("Inactive status not found")
            return {'message': 'Inactive status not configured'}, 500
        user.user_status_id = inactive.status_id
        db.session.commit()
        return {'message': 'User Inactivated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error Inactivating User: {e}")
        return {'message': 'Failed to Inactivate User'}, 500

def create_store_logic(current_user, data):
    required_fields = ['name', 'description', 'store_email', 'store_address']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    try:
        # Sanitize store name and description
        name = bleach.clean(data['name'], strip=True)
        description = bleach.clean(data['description'], strip=True)
        store_email = bleach.clean(data['store_email'], strip=True)
        store_address = bleach.clean(data['store_address'], strip=True)
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            logging.error("Active status not found")
            return {'message': 'Active status not configured'}, 500
        new_store = Stores()
        # Map to model fields; fill required columns with provided data where possible
        new_store.store_name = name
        new_store.store_description = description
        new_store.store_email = store_email
        new_store.store_address = store_address
        new_store.store_status_id = active_status.status_id
        if 'store_phone' in data:
            new_store.store_phone = bleach.clean(data['store_phone'], strip=True)
        if 'store_pic_path' in data:
            new_store.store_pic_path = bleach.clean(data['store_pic_path'], strip=True)
        db.session.add(new_store)
        db.session.commit()
        return {'message': 'Store created successfully', 'store_id': new_store.store_id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating store: {e}")
        return {'message': 'Failed to create store'}, 500

def update_store_logic(current_user, store_id, data):
    store = Stores.query.get(store_id)
    if not store:
        logging.warning(f"Store: {store_id} not found during update_store_logic")
        return {'message': 'Store not found'}, 404
    try:
        
        store.store_name = bleach.clean(data['name'], strip=True)
        if 'description' in data:
            store.store_description = bleach.clean(data['description'], strip=True)
        store.store_email = bleach.clean(data['store_email'], strip=True)
        store.store_address = bleach.clean(data['store_address'], strip=True)
        store.store_phone = bleach.clean(data['store_phone'], strip=True)
        if 'store_pic_path' in data:
            store.store_pic_path = bleach.clean(data['store_pic_path'], strip=True)
        db.session.commit()
        return {'message': 'Store updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating store: {e}")
        return {'message': 'Failed to update store'}, 500

def inactivate_store_logic(current_user, store_id):
    store = Stores.query.get(store_id)
    if not store:
        logging.warning(f"Store: {store_id} not found during inactivate_store_logic")
        return {'message': 'Store not found'}, 404
    try:
        inactive = EntityStatuses.query.filter_by(status_code='inactive').first()
        if not inactive:
            logging.error("Inactive Status not found")
            return {'message': 'Inactive Status not configured'}, 500
        store.store_status_id = inactive.status_id
        # Also inactivate linked store_products_services
        StoreProductsServices.query.filter_by(store_id=store_id).update({'status_id': inactive.status_id})
        # Issue?: Shouldn't we also inactivate Store User Roles
        db.session.commit()
        return {'message': 'Store Inactivated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error Inactivating Store: {e}")
        return {'message': 'Failed to Inactivate Store'}, 500

def create_product_service_logic(current_customer, data):
    required_fields = ['product_service_name', 'product_service_description', 'product_service_category_id', 'product_service_pic_path', 'store_id', 'price', 'stock']
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
        # Check store exists and is active
        store = Stores.query.filter_by(store_id=data['store_id'], store_status_id=active_status_id).first()
        if not store:
            return {'message': 'Store not found or Inactive'}, 404
        # Create product/service
        new_product_service = ProductsServices()
        new_product_service.product_service_name = name
        new_product_service.product_service_description = description
        new_product_service.product_service_pic_path = pic_path
        new_product_service.product_service_category_id = data['product_service_category_id']
        new_product_service.product_service_status_id = active_status_id
        db.session.add(new_product_service)
        db.session.flush()  # Get product_service_id

        # Create store-product-service link
        # Issue: There would be another function to handle linking SPS
        sps = StoreProductsServices()
        sps.store_id = store.store_id
        sps.product_service_id = new_product_service.product_service_id
        sps.price = data['price']
        sps.stock = data['stock']
        sps.status_id = active_status_id
        db.session.add(sps)
        db.session.commit()
        return {'message': 'Product/Service created successfully', 'product_service_id': new_product_service.product_service_id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Product/Service: {e}")
        return {'message': 'Failed to create Product/Service'}, 500

def update_product_service_logic(current_customer, product_service_id, data):
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found")
        return {'message': 'Active Status not configured'}, 500
    product_service = ProductsServices.query.filter_by(product_service_id=product_service_id, product_service_status_id=active_status.status_id).first()
    if not product_service:
        return {'message': 'Product/Service not found or Inactive'}, 404
    try:
        if 'product_service_name' in data:
            product_service.product_service_name = bleach.clean(data['product_service_name'], strip=True)
        if 'product_service_description' in data:
            product_service.product_service_description = bleach.clean(data['product_service_description'], strip=True)
        if 'product_service_pic_path' in data:
            product_service.product_service_pic_path = bleach.clean(data['product_service_pic_path'], strip=True)
        if 'product_service_category_id' in data:
            product_service.product_service_category_id = data['product_service_category_id']
        db.session.commit()
        return {'message': 'Product/Service updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating Product/Service: {e}")
        return {'message': 'Failed to update Product/Service'}, 500

def inactivate_product_service_logic(current_customer, product_service_id):
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found")
        return {'message': 'Active Status not configured'}, 500
    product_service = ProductsServices.query.filter_by(product_service_id=product_service_id, product_service_status_id=active_status.status_id).first()
    if not product_service:
        return {'message': 'Product/Service not found or Inactive'}, 404
    try:
        inactive = EntityStatuses.query.filter_by(status_code='inactive').first()
        if not inactive:
            logging.error("Inactive Status not found")
            return {'message': 'Inactive Status not configured'}, 500
        product_service.product_service_status_id = inactive.status_id
        # Inactivate linked store products/services rows
        StoreProductsServices.query.filter_by(product_service_id=product_service_id).update({'status_id': inactive.status_id})
        db.session.commit()
        return {'message': 'Product/Service Inactivated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error Inactivating Product/Service: {e}")
        return {'message': 'Failed to Inactivate Product/Service'}, 500

def mark_order_shipped_logic(order_id):
    """
    Admin function to signal the OrderWorkflow that the order has been shipped
    GRL: Outdated
    """
    try:
        order = Orders.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Admin check: Ensure order is in a state ready to be shipped
        allowed_status_codes = ['paid', 'filled', 'partial_filled']
        if not order.order_status or order.order_status.status_code not in allowed_status_codes:
            return {'message': f"Order status is {order.order_status.status_code}. Cannot mark as shipped"}, 400

        # Signal Temporal workflow
        async def ship_order_workflow():
            client = await Client.connect(TEMPORAL_HOST)
            handle = client.get_workflow_handle(f"order-{order_id}")
            # Ensure your signal name matches the one in order_workflow.py
            await handle.signal("ship_order")
        asyncio.run(ship_order_workflow())
        # --- The DB update is handled by the Activity in order_activities.py ---
        return {'message': f'Order {order_id} shipment initiated. Process pending workflow execution'}, 202
    except Exception as e:
        logging.error(f"Error signalling Order Shipment: {e}")
        return {'message': 'Failed to Signal Order Shipment'}, 500

def refund_order_logic(current_customer, order_id):
    """
    Admin function to request an Order Refund (if eligible).
    Triggers the Order Workflow's Refund Signal
    """
    # Check customer is active
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during refund_order_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
    if not customer:
        return {'message': 'Customer not found or Inactive'}, 403
    order = Orders.query.get(order_id)
    if not order:
        logging.warning(f"Order: {order_id} not found during refund_order_logic")
        return {'message': 'Order not found'}, 404
    if order.customer_id != current_customer.customer_id:
        logging.warning("Order does not belong to Customer during refund_order_logic")
        return {'message': 'Order does not belong to Customer'}, 403
    
    # Only allow a refund if order status is in allowed list
    allowed_status_codes = ["cancelled", "partial_cancelled", "returned", "partial_returned", "partial_refunded",
                            "partial_delivered", "partial_shipped"]
    if not order.order_status or order.order_status.status_code not in allowed_status_codes:
        return {'message': f"Order cannot be Refunded in its current Status: {order.order_status.status_display if order.order_status else 'Unknown'}"}, 400

    try:
        async def refund_order_workflow():
            client = await get_temporal_client()
            handle = client.get_workflow_handle(f"order-{order_id}")
            await handle.signal("start_refund")

        asyncio.run(refund_order_workflow())
        return {'message': 'Order Refund initiated successfully. Status Update pending workflow execution'}, 202
    except Exception as e:
        logging.error(f"Error signalling Order Refund: {e}")
        return {'message': 'Failed to Signal Order Refund'}, 500
    
def accept_order_logic(current_customer, order_id):
    """
    Admin function to mark an Order as customer_accepted (Order Status Terminal).
    Triggers the acceptance signal on the Order Workflow
    """
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during accept_order_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id
    customer = Customers.query.filter_by(customer_id=current_customer.customer_id, customer_status_id=active_status_id).first()
    if not customer:
        return {'message': 'Customer not found or Inactive'}, 403
    order = Orders.query.get(order_id)
    if not order:
        logging.warning(f"Order: {order_id} not found during accept_order_logic")
        return {'message': 'Order not found'}, 404
    if order.customer_id != current_customer.customer_id:
        logging.warning("Order does not belong to Customer during accept_order_logic")
        return {'message': 'Order does not belong to Customer'}, 403
    
    # Only allow acceptance if order status is in allowed list
    allowed_status_codes = ["delivered", "partial_delivered", "refunded", "partial_refunded"]
    if not order.order_status or order.order_status.status_code not in allowed_status_codes:
        return {'message': f"Order cannot be Refunded in its current Status: {order.order_status.status_display if order.order_status else 'Unknown'}"}, 400


    try:
        async def accept_order_workflow():
            client = await get_temporal_client()
            handle = client.get_workflow_handle(f"order-{order_id}")
            await handle.signal("start_acceptance")

        asyncio.run(accept_order_workflow())
        return {'message': 'Order Acceptance initiated successfully. Status Update pending workflow execution.'}, 202
    except Exception as e:
        logging.error(f"Error signalling order acceptance: {e}")
        return {'message': 'Failed to Signal Order Acceptance'}, 500
    
# --- LOGIC FOR BULK ORDER'S ITEM SHIPMENT ---
def bulk_ship_items_logic(order_id, items_to_update: dict):
    """Logic for Bulk Shipment of Order's Items"""

    if not items_to_update:
        return {'message': 'No items provided for update'}, 400
        
    logging.info(f"Initiating Bulk Status Update for Order {order_id}: {items_to_update}")

    # Input Validation (Simplified)
    # In a real app, you would check if the order exists and if the items belong to it
    
    try:
        # Signal Temporal Workflow
        async def bulk_update_workflow():
            client = await Client.connect(TEMPORAL_HOST)
            handle = client.get_workflow_handle(f"order-{order_id}")

            # Note: We signal the Parent Order Workflow, not the individual Item Workflows
            await handle.signal(OrderWorkflow.start_shipping)
        asyncio.run(bulk_update_workflow())
        # --- The DB update is handled by the Activity in order_activities.py ---
        return {'message': f'Order {order_id} Bulk Shipment Process initiated. Process pending workflow execution'}, 202

    except Exception as e:
        logging.error(f"Error signalling Order Bulk Shipment: {e}")
        return {'message': 'Failed to signal Order Bulk Shipment'}, 500
