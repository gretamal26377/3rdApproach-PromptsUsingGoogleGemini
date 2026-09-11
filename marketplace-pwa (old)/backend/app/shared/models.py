from ..customer import db
# from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, Integer, String, Text, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# vsCode Copilot explanation after research: The red cross in PROBLEMS windows means Linter treats it as an error,
# but it isn't a Python runtime error. Your Flask app should work as expected if you run it normally.
# The error is safe to ignore using # type: ignore
class User(db.Model): # type: ignore
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    stores = relationship('Store', backref='owner', lazy=True)
    orders = relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) # type: ignore

    def __repr__(self):
        return f'<User {self.username}>'

class Store(db.Model): # type: ignore
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    products = relationship('Product', backref='store', lazy=True)

    def __repr__(self):
        return f'<Store {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    # Issue: product_stock is missing here
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    order_items = relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_date = Column(DateTime, server_default=func.now())
    #Issue: order_status is missing here
    total_amount = Column(Float, nullable=False)
    items = relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<OrderItem {self.quantity} of {self.product_id}>'