from .models import Order, OrderItem, Product, db
import logging

def get_orders_logic(current_user):
    if current_user.is_admin:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).all()
    orders_data = [
        {
            'id': order.id,
            'user_id': order.user_id,
            'order_date': order.order_date,
            'total_amount': order.total_amount,
            'items': [{'product_id': item.product_id, 'quantity': item.quantity} for item in order.items]
        } for order in orders
    ]
    return orders_data, 200

def get_order_logic(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
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
        return {'error': 'Missing required fields'}, 400
    if not isinstance(data['items'], list):
        return {'error': 'Items must be a list'}, 400
    if not data['items']:
        return {'error': 'Items list cannot be empty'}, 400
    total_amount = 0
    order_items = []
    try:
        for item in data['items']:
            if not all(field in item for field in ['product_id', 'quantity']):
                return {'error': 'Each item must contain product_id and quantity'}, 400
            product = Product.query.get(item['product_id'])
            if not product:
                return {'error': f"Product with id {item['product_id']} not found"}, 400
            quantity = item['quantity']
            if quantity <= 0:
                return {'error': f"Quantity for product {item['product_id']} must be greater than zero"}, 400
            total_amount += product.price * quantity
            order_items.append(OrderItem(product_id=item['product_id'], quantity=quantity))
        new_order = Order(user_id=current_user.id, total_amount=total_amount, items=order_items)
        db.session.add(new_order)
        db.session.commit()
        return {'message': 'Order created successfully', 'order_id': new_order.id}, 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating order: {e}")
        return {'error': 'Failed to create order'}, 500

def delete_order_logic(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    try:
        db.session.delete(order)
        db.session.commit()
        return {'message': 'Order deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting order: {e}")
        return {'error': 'Failed to delete order'}, 500
