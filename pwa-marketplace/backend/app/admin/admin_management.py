from ..shared.database import db
from ..shared.models import (
    Users, Stores, ProductsServices, StoreProductsServices, 
    EntityStatuses, Orders, OrderStatuses # Added Orders, OrderStatuses for workflow integration
)
import logging
from temporalio.client import Client
import asyncio
from workflows.order_workflow import OrderWorkflow
from workflows.item_workflow import ItemWorkflow
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

def mark_order_shipped_logic(order_id):
    """
    Admin function to signal the OrderWorkflow that the order has been shipped
    """
    try:
        order = Orders.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Admin check: Ensure order is in a state ready to be shipped
        allowed_status_codes = ['paid', 'filled', 'partial_filled']
        if not order.order_status or order.order_status.status_code not in allowed_status_codes:
            return {'message': f"Order status is {order.order_status.status_code}. Cannot mark as shipped."}, 400

        # 1. Signal Temporal workflow
        async def ship_order_workflow():
            client = await Client.connect("localhost:7233")
            handle = client.get_workflow_handle(f"order-{order_id}")
            # Assume a signal named 'ship_order' is defined in OrderWorkflow
            await handle.signal("ship_order")

        asyncio.run(ship_order_workflow())

        # 2. Update DB status for administrative confirmation/reference
        shipped_status = OrderStatuses.query.filter_by(status_code='shipped').first()
        if not shipped_status:
            return {'message': 'Order Status "shipped" not found'}, 500

        order.order_status_id = shipped_status.status_id
        db.session.commit()

        return {'message': f'Order {order_id} signalled for shipping and status updated to shipped.'}, 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error marking Order {order_id} as shipped: {e}")
        return {'message': 'Failed to signal order shipment'}, 500

def refund_order_logic(order_id):
    """
    Admin function to signal the OrderWorkflow to initiate a refund process.
    """
    try:
        order = Orders.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Admin check: Ensure order is in a state eligible for refund
        allowed_status_codes = ['paid', 'delivered', 'partial_delivered', 'returned', 'partial_returned']
        if not order.order_status or order.order_status.status_code not in allowed_status_codes:
            return {'message': f"Order status is {order.order_status.status_code}. Cannot initiate refund."}, 400

        # 1. Signal Temporal workflow
        async def refund_order_workflow():
            client = await Client.connect("localhost:7233")
            handle = client.get_workflow_handle(f"order-{order_id}")
            # Assume a signal named 'refund_order' is defined in OrderWorkflow
            await handle.signal("refund_order")

        asyncio.run(refund_order_workflow())

        # 2. Update DB status for administrative confirmation/reference
        refunded_status = OrderStatuses.query.filter_by(status_code='refunded').first()
        if not refunded_status:
            return {'message': 'Order Status "refunded" not found'}, 500

        order.order_status_id = refunded_status.status_id
        db.session.commit()

        return {'message': f'Order {order_id} signalled for refund and status updated to refunded.'}, 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error refunding Order {order_id}: {e}")
        return {'message': 'Failed to signal order refund'}, 500