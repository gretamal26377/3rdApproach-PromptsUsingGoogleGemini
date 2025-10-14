from .database import db
from typing import List, Optional

from sqlalchemy import db.BigInteger, db.DECIMAL, Enum, ForeignKeyConstraint, Index, db.Integer, db.JSON, db.String, db.TIMESTAMP, db.Text, text
import datetime
import decimal

class CategoriesHistory(db.Model):
    __tablename__ = 'categories_history'
    __table_args__ = (
        Index('category_id', 'category_id'),
        Index('changed_at', 'changed_at')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    category_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class CitiesHistory(db.Model):
    __tablename__ = 'cities_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('city_id', 'city_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    city_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class CountriesHistory(db.Model):
    __tablename__ = 'countries_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('country_id', 'country_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    country_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class CustomerAddressesHistory(db.Model):
    __tablename__ = 'customer_addresses_history'
    __table_args__ = (
        Index('address_id', 'address_id'),
        Index('changed_at', 'changed_at'),
        Index('customer_id', 'customer_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    address_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class CustomersHistory(db.Model):
    __tablename__ = 'customers_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('customer_id', 'customer_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    customer_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class EntityStatuses(db.Model):
    __tablename__ = 'entity_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(50))
    status_description = db.Column(db.Text)
    categories = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    status_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class OrderDetailsHistory(db.Model):
    __tablename__ = 'order_details_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('order_id', 'order_id'),
        Index('store_product_service_id', 'store_product_service_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    order_id = db.Column(db.Integer)
    store_product_service_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class OrderStatuses(db.Model):
    __tablename__ = 'order_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(50))
    status_description = db.Column(db.Text)
    orders = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    status_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class OrdersHistory(db.Model):
    __tablename__ = 'orders_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('order_id', 'order_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    order_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class ProductsServicesHistory(db.Model):
    __tablename__ = 'products_services_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('product_service_id', 'product_service_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    product_service_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class Roles(db.Model):
    __tablename__ = 'roles'
    __table_args__ = (
        Index('role_code', 'role_code', unique=True),
    )

    role_id = db.Column(db.Integer, primary_key=True)
    role_code = db.Column(db.String(50))
    role_description = db.Column(db.Text)
    store_user_role = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    role_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class StatesRegionsHistory(db.Model):
    __tablename__ = 'states_regions_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('state_region_id', 'state_region_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    state_region_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class StoreProductsServicesHistory(db.Model):
    __tablename__ = 'store_products_services_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('id', 'id'),
        Index('product_service_id', 'product_service_id'),
        Index('store_id', 'store_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    id = db.Column(db.Integer)
    store_id = db.Column(db.Integer)
    product_service_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class StoreUserRoleHistory(db.Model):
    __tablename__ = 'store_user_role_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('store_id', 'store_id'),
        Index('user_id', 'user_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    store_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class StoresHistory(db.Model):
    __tablename__ = 'stores_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('store_id', 'store_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    store_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class UsersHistory(db.Model):
    __tablename__ = 'users_history'
    __table_args__ = (
        Index('idx_users_history_time', 'changed_at'),
        Index('idx_users_history_user', 'user_id')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'))
    user_id = db.Column(db.Integer)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
class Categories(db.Model):
    __tablename__ = 'categories'
    __table_args__ = (
        ForeignKeyConstraint(['category_status_id'], ['entity_statuses.status_id'], name='categories_ibfk_1'),
        Index('category_name', 'category_name', unique=True),
        Index('category_status_id', 'category_status_id')
    )

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100))
    category_status_id = db.Column(db.Integer)
    category_description = db.Column(db.Text)
    category_pic_path = db.Column(db.String(255))
    category_status = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100))
    country_code = db.Column(db.String(10))
    country_status_id = db.Column(db.Integer)
    country_status = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String(100))
    customer_name = db.Column(db.String(100))
    customer_password_hash = db.Column(db.String(255))
    customer_phone = db.Column(db.String(20))
    customer_status_id = db.Column(db.Integer)
    customer_status = db.Column(db.Integer, primary_key=True)
    store_email = db.Column(db.String(100))
    store_name = db.Column(db.String(100))
    store_address = db.Column(db.Text)
    store_status_id = db.Column(db.Integer)
    store_description = db.Column(db.Text)
    store_phone = db.Column(db.String(20))
    store_status = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    user_name = db.Column(db.String(50))
    user_password_hash = db.Column(db.String(255))
    user_phone = db.Column(db.String(20))
    user_status_id = db.Column(db.Integer)
    user_status = db.Column(db.Integer, primary_key=True)
    order_tot_quantity = db.Column(db.Integer)
    order_tot_price = db.Column(db.DECIMAL(10, 2))
    customer_id = db.Column(db.Integer)
    order_status_id = db.Column(db.Integer)
    customer = db.Column(db.Integer, primary_key=True)
    product_service_name = db.Column(db.String(100))
    product_service_category_id = db.Column(db.Integer)
    product_service_status_id = db.Column(db.Integer)
    product_service_description = db.Column(db.Text)
    product_service_pic_path = db.Column(db.String(255))
    product_service_category = db.Column(db.Integer, primary_key=True)
    state_region_name = db.Column(db.String(100))
    state_region_code = db.Column(db.String(10))
    country_id = db.Column(db.Integer)
    state_region_status_id = db.Column(db.Integer)
    country = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer)
    status_id = db.Column(db.Integer)
    role = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100))
    state_region_id = db.Column(db.Integer)
    city_status_id = db.Column(db.Integer)
    city_status = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer)
    product_service_id = db.Column(db.Integer)
    price = db.Column(db.DECIMAL(10, 2))
    stock = db.Column(db.Integer)
    status_id = db.Column(db.Integer)
    product_service = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    address_line1 = db.Column(db.String(255))
    city_id = db.Column(db.Integer)
    google_maps_url = db.Column(db.String(255))
    address_status_id = db.Column(db.Integer)
    postal_code = db.Column(db.String(20))
    address_line2 = db.Column(db.String(255))
    address_status = db.Column(db.Integer, primary_key=True)
    store_product_service_id = db.Column(db.Integer, primary_key=True)
    product_service_quantity = db.Column(db.Integer)
    product_service_price = db.Column(db.DECIMAL(10, 2))
    product_service_tot_price = db.Column(db.DECIMAL(10, 2))
    product_service_status_id = db.Column(db.Integer)
    product_service_filled_quantity = db.Column(db.Integer, server_default=text("'0'"))
    product_service_filled_tot_price = db.Column(db.DECIMAL(10, 2), server_default=text("'0.00'"))
    order = db.relationship('Orders', back_populates='order_details')
    product_service_status = db.relationship('OrderStatuses', back_populates='order_details')
    store_product_service = db.relationship('StoreProductsServices', back_populates='order_details')