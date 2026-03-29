def create_user_logic(data):
    """
    Logic to create a new admin user. Expects keys:
      user_name, user_email, user_password, user_phone, user_organisation_id, user_role_code, user_store_ids (list)
    """
    required_fields = [
        'user_name', 'user_email', 'user_password', 'user_phone', 'user_organisation_id', 'user_role_code', 'user_store_ids'
    ]
    if not all(field in data for field in required_fields):
        return {"error": "Missing required fields"}, 400
    try:
        # Sanitize inputs
        import bleach
        name = bleach.clean(data['user_name'], strip=True)
        email = bleach.clean(data['user_email'], strip=True)
        password = bleach.clean(data['user_password'], strip=True)
        phone = bleach.clean(data['user_phone'], strip=True)
        organisation_id = data['user_organisation_id']
        role_code = data['user_role_code']
        store_ids = data['user_store_ids'] if isinstance(data['user_store_ids'], list) else []

        # Check for existing user
        existing = Users.query.filter_by(email=email).first()
        if existing:
            return {"error": "User with this email already exists"}, 409

        # Get active status
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            return {"error": "Active status not found"}, 500

        # Create user
        new_user = Users()
        new_user.username = name
        new_user.email = email
        new_user.password = password  # TODO: hash password in production
        new_user.phone = phone
        new_user.organisation_id = organisation_id
        new_user.role_code = role_code
        new_user.user_status_id = active_status.status_id
        db.session.add(new_user)
        db.session.flush()  # Get user_id

        # Link user to stores (if applicable)
        # TODO: Implement UserStoreRoles or similar association if model exists
        # for store_id in store_ids:
        #     ...

        db.session.commit()
        return {"message": "User created", "user_id": new_user.id}, 201
    except Exception as e:
        db.session.rollback()
        import logging
        logging.error(f"Error creating user: {e}")
        return {"error": "Failed to create user"}, 500
    

import os
from .database import db
from .models import (
    Customers, Users, Stores, ProductsServices, StoreProductsServices,
    EntityStatuses, Orders
)
from .utils import get_temporal_client
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

def get_user_logic(app_type, org_id, user_id):
    """
    Retrieve User based on app_type and org_id
    - app_type: 'org-admin', 'platform-admin', or 'customer'
    - org_id: organisation_id for org-admin, None for platform-admin/customer
    - user_id: user_id (or customer_id for Customer app)
    """
    user = None
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found during get_user_logic")
        return {'message': 'Active Status not found'}, 500
    active_status_id = active_status.status_id

    if app_type == 'org-admin':
        # Only allow User if he belongs to the given Organisation and is active
        user = Users.query.filter_by(id=user_id, organisation_id=org_id, user_status_id=active_status_id).first()
        if not user:
            logging.warning(f"User: {user_id} not found or Inactive in Org {org_id} during get_user_logic (org-admin)")
            return {'message': 'User not found or Inactive in Organisation'}, 404
    elif app_type == 'platform-admin':
        # Platform Admin can access any active User
        user = Users.query.filter_by(id=user_id, user_status_id=active_status_id).first()
        if not user:
            logging.warning(f"User: {user_id} not found or Inactive during get_user_logic (platform-admin)")
            return {'message': 'User not found or Inactive'}, 404
    elif app_type == 'customer':
        # For Customer, user_id is actually customer_id
        customer = Customers.query.filter_by(customer_id=user_id, customer_status_id=active_status_id).first()
        if not customer:
            logging.warning(f"Customer: {user_id} not found or Inactive during get_user_logic (customer)")
            return {'message': 'Customer not found or Inactive'}, 404
        # Return Customer data in user_data format for compatibility
        user_data = {
            'id': customer.customer_id,
            'user_name': customer.customer_name,
            'email': customer.customer_email
        }
        return user_data, 200
    else:
        logging.warning(f"Unknown app_type: {app_type} in get_user_logic")
        return {'message': 'Invalid app_type'}, 400

    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'organisation_id': user.organisation_id,
        'role_code': user.role.role_code if user.role else None
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
            logging.error("Inactive Status not found")
            return {'message': 'Inactive Status not found'}, 500
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
            logging.error("Active Status not found")
            return {'message': 'Active Status not found'}, 500
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
            return {'message': 'Inactive Status not found'}, 500
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

def create_store_product_service_logic(current_user, data):
    required_fields = ['store_id', 'product_service_id', 'price', 'stock']
    if not all(field in data for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    try:
        # Sanitize fields
        store_id = bleach.clean(data['store_id'], strip=True)
        product_service_id = bleach.clean(data['product_service_id'], strip=True)
        price = bleach.clean(data['price'], strip=True)
        stock = bleach.clean(data['stock'], strip=True)
        active_status = EntityStatuses.query.filter_by(status_code='active').first()
        if not active_status:
            logging.error("Active Status not found")
            return {'message': 'Active Status not found'}, 500
        active_status_id = active_status.status_id
        # Check store exists and is active
        store = Stores.query.filter_by(store_id=data['store_id'], store_status_id=active_status_id).first()
        if not store:
            return {'message': 'Store not found or Inactive'}, 404

        # Create Store Product/Service
        sps = StoreProductsServices()
        sps.store_id = store.store_id
        sps.product_service_id = product_service_id
        sps.price = data['price']
        sps.stock = data['stock']
        sps.status_id = active_status_id
        db.session.add(sps)
        db.session.commit()
        return {'message': 'Product/Service created successfully at Store'}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating Store Product/Service: {e}")
        return {'message': 'Failed to create Product/Service at Store'}, 500

def update_product_service_logic(current_customer, product_service_id, data):
    active_status = EntityStatuses.query.filter_by(status_code='active').first()
    if not active_status:
        logging.error("Active Status not found")
        return {'message': 'Active Status not found'}, 500
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
        return {'message': 'Active Status not found'}, 500
    product_service = ProductsServices.query.filter_by(product_service_id=product_service_id, product_service_status_id=active_status.status_id).first()
    if not product_service:
        return {'message': 'Product/Service not found or Inactive'}, 404
    try:
        inactive = EntityStatuses.query.filter_by(status_code='inactive').first()
        if not inactive:
            logging.error("Inactive Status not found")
            return {'message': 'Inactive Status not found'}, 500
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
