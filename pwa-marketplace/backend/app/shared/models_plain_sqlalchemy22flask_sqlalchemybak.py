from .database import db
from sqlalchemy import text, Index, ForeignKeyConstraint

from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, DECIMAL, Enum, ForeignKeyConstraint, Index, Integer, JSON, String, TIMESTAMP, Text, text
class CategoriesHistory(db.Model):
    __tablename__ = 'categories_history'
    __table_args__ = (
        Index('category_id', 'category_id'),
        Index('changed_at', 'changed_at')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    category_id = db.Column(db.db.Integer|Optional[int])
    changed_by: Mapped[Optional[str]] = db.Column(db.String(100))

    category_id: Mapped[Optional[int]] = db.Column(db.db.Integer)
    changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)
    data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)

class CitiesHistory(db.Model):
    __tablename__ = 'cities_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('city_id', 'city_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    city_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class CountriesHistory(db.Model):
    __tablename__ = 'countries_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('country_id', 'country_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    country_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class CustomerAddressesHistory(db.Model):
    __tablename__ = 'customer_addresses_history'
    __table_args__ = (
        Index('address_id', 'address_id'),
        Index('changed_at', 'changed_at'),
        Index('customer_id', 'customer_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    address_id: Mapped[Optional[int]] = db.Column(db.db.Integer)customer_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class CustomersHistory(db.Model):
    __tablename__ = 'customers_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('customer_id', 'customer_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    customer_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class EntityStatuses(db.Model):
    __tablename__ = 'entity_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.db.Integer, primary_key=True)
    status_code = db.Column(db.db.String(50), nullable=False)
    status_description: Mapped[Optional[str]] = db.Column(db.db.Text)categories: Mapped[list['Categories']] = db.relationship('Categories', back_populates='category_status')
    countries: Mapped[list['Countries']] = db.relationship('Countries', back_populates='country_status')
    customers: Mapped[list['Customers']] = db.relationship('Customers', back_populates='customer_status')
    stores: Mapped[list['Stores']] = db.relationship('Stores', back_populates='store_status')
    users: Mapped[list['Users']] = db.relationship('Users', back_populates='user_status')
    products_services: Mapped[list['ProductsServices']] = db.relationship('ProductsServices', back_populates='product_service_status')
    states_regions: Mapped[list['StatesRegions']] = db.relationship('StatesRegions', back_populates='state_region_status')
    store_user_role: Mapped[list['StoreUserRole']] = db.relationship('StoreUserRole', back_populates='status')
    cities: Mapped[list['Cities']] = db.relationship('Cities', back_populates='city_status')
    store_products_services: Mapped[list['StoreProductsServices']] = db.relationship('StoreProductsServices', back_populates='status')
    customer_addresses: Mapped[list['CustomerAddresses']] = db.relationship('CustomerAddresses', back_populates='address_status')

class EntityStatusesHistory(db.Model):
    __tablename__ = 'entity_statuses_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('status_id', 'status_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    status_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class OrderDetailsHistory(db.Model):
    __tablename__ = 'order_details_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('order_id', 'order_id'),
        Index('store_product_service_id', 'store_product_service_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    order_id: Mapped[Optional[int]] = db.Column(db.db.Integer)store_product_service_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class OrderStatuses(db.Model):
    __tablename__ = 'order_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.db.Integer, primary_key=True)
    status_code = db.Column(db.db.String(50), nullable=False)
    status_description: Mapped[Optional[str]] = db.Column(db.db.Text)orders: Mapped[list['Orders']] = db.relationship('Orders', back_populates='order_status')
    order_details: Mapped[list['OrderDetails']] = db.relationship('OrderDetails', back_populates='product_service_status')

class OrderStatusesHistory(db.Model):
    __tablename__ = 'order_statuses_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('status_id', 'status_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    status_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class OrdersHistory(db.Model):
    __tablename__ = 'orders_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('order_id', 'order_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    order_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class ProductsServicesHistory(db.Model):
    __tablename__ = 'products_services_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('product_service_id', 'product_service_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    product_service_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class Roles(db.Model):
    __tablename__ = 'roles'
    __table_args__ = (
        Index('role_code', 'role_code', unique=True),
    )

    role_id = db.Column(db.db.Integer, primary_key=True)
    role_code = db.Column(db.db.String(50), nullable=False)
    role_description: Mapped[Optional[str]] = db.Column(db.db.Text)store_user_role: Mapped[list['StoreUserRole']] = db.relationship('StoreUserRole', back_populates='role')

class RolesHistory(db.Model):
    __tablename__ = 'roles_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('role_id', 'role_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    role_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class StatesRegionsHistory(db.Model):
    __tablename__ = 'states_regions_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('state_region_id', 'state_region_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    state_region_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class StoreProductsServicesHistory(db.Model):
    __tablename__ = 'store_products_services_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('id', 'id'),
        Index('product_service_id', 'product_service_id'),
        Index('store_id', 'store_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    id: Mapped[Optional[int]] = db.Column(db.db.Integer)store_id: Mapped[Optional[int]] = db.Column(db.db.Integer)product_service_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class StoreUserRoleHistory(db.Model):
    __tablename__ = 'store_user_role_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('store_id', 'store_id'),
        Index('user_id', 'user_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    store_id: Mapped[Optional[int]] = db.Column(db.db.Integer)user_id: Mapped[Optional[int]] = db.Column(db.db.Integer)role_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class StoresHistory(db.Model):
    __tablename__ = 'stores_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('store_id', 'store_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    store_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class UsersHistory(db.Model):
    __tablename__ = 'users_history'
    __table_args__ = (
        Index('idx_users_history_time', 'changed_at'),
        Index('idx_users_history_user', 'user_id')
    )

    hist_id = db.Column(db.db.BigInteger, primary_key=True)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    user_id: Mapped[Optional[int]] = db.Column(db.db.Integer)changed_by: Mapped[Optional[str]] = db.Column(db.String(100))
    changed_at: Mapped[Optional[datetime.datetime]] = db.Column(db.db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    data_before: Mapped[Optional[dict]] = db.Column(db.db.JSON)data_after: Mapped[Optional[dict]] = db.Column(db.db.JSON)class Categories(db.Model):
    __tablename__ = 'categories'
    __table_args__ = (
        ForeignKeyConstraint(['category_status_id'], ['entity_statuses.status_id'], name='categories_ibfk_1'),
        Index('category_name', 'category_name', unique=True),
        Index('category_status_id', 'category_status_id')
    )

    category_id = db.Column(db.db.Integer, primary_key=True)
    category_name = db.Column(db.db.String(100), nullable=False)
    category_status_id = db.Column(db.db.Integer, nullable=False)
    category_description: Mapped[Optional[str]] = db.Column(db.db.Text)category_pic_path: Mapped[Optional[str]] = db.Column(db.String(255))

    category_status = db.relationship('EntityStatuses', back_populates='categories')
    products_services: Mapped[list['ProductsServices']] = db.relationship('ProductsServices', back_populates='product_service_category')

class Countries(db.Model):
    __tablename__ = 'countries'
    __table_args__ = (
        ForeignKeyConstraint(['country_status_id'], ['entity_statuses.status_id'], name='countries_ibfk_1'),
        Index('country_code', 'country_code', unique=True),
        Index('country_status_id', 'country_status_id')
    )

    country_id = db.Column(db.db.Integer, primary_key=True)
    country_name = db.Column(db.db.String(100), nullable=False)
    country_code = db.Column(db.db.String(10), nullable=False)
    country_status_id = db.Column(db.db.Integer, nullable=False)
    country_status = db.relationship('EntityStatuses', back_populates='countries')
    states_regions: Mapped[list['StatesRegions']] = db.relationship('StatesRegions', back_populates='country')

class Customers(db.Model):
    __tablename__ = 'customers'
    __table_args__ = (
        ForeignKeyConstraint(['customer_status_id'], ['entity_statuses.status_id'], name='customers_ibfk_1'),
        Index('customer_email', 'customer_email', unique=True),
        Index('customer_status_id', 'customer_status_id')
    )

    customer_id = db.Column(db.db.Integer, primary_key=True)
    customer_email = db.Column(db.db.String(100), nullable=False)
    customer_name = db.Column(db.db.String(100), nullable=False)
    customer_password_hash = db.Column(db.db.String(255), nullable=False)
    customer_phone = db.Column(db.db.String(20), nullable=False)
    customer_status_id = db.Column(db.db.Integer, nullable=False)
    customer_status = db.relationship('EntityStatuses', back_populates='customers')
    orders: Mapped[list['Orders']] = db.relationship('Orders', back_populates='customer')
    customer_addresses: Mapped[list['CustomerAddresses']] = db.relationship('CustomerAddresses', back_populates='customer')

class Stores(db.Model):
    __tablename__ = 'stores'
    __table_args__ = (
        ForeignKeyConstraint(['store_status_id'], ['entity_statuses.status_id'], name='stores_ibfk_1'),
        Index('store_email', 'store_email', unique=True),
        Index('store_status_id', 'store_status_id')
    )

    store_id = db.Column(db.db.Integer, primary_key=True)
    store_email = db.Column(db.db.String(100), nullable=False)
    store_name = db.Column(db.db.String(100), nullable=False)
    store_address = db.Column(db.db.Text, nullable=False)
    store_status_id = db.Column(db.db.Integer, nullable=False)
    store_description: Mapped[Optional[str]] = db.Column(db.db.Text)store_phone: Mapped[Optional[str]] = db.Column(db.String(20))

    store_status = db.relationship('EntityStatuses', back_populates='stores')
    store_user_role: Mapped[list['StoreUserRole']] = db.relationship('StoreUserRole', back_populates='store')
    store_products_services: Mapped[list['StoreProductsServices']] = db.relationship('StoreProductsServices', back_populates='store')

class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['user_status_id'], ['entity_statuses.status_id'], name='users_ibfk_1'),
        Index('user_email', 'user_email', unique=True),
        Index('user_status_id', 'user_status_id')
    )

    user_id = db.Column(db.db.Integer, primary_key=True)
    user_email = db.Column(db.db.String(100), nullable=False)
    user_name = db.Column(db.db.String(50), nullable=False)
    user_password_hash = db.Column(db.db.String(255), nullable=False)
    user_phone = db.Column(db.db.String(20), nullable=False)
    user_status_id = db.Column(db.db.Integer, nullable=False)
    user_status = db.relationship('EntityStatuses', back_populates='users')
    store_user_role: Mapped[list['StoreUserRole']] = db.relationship('StoreUserRole', back_populates='user')

class Orders(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], name='orders_ibfk_1'),
        ForeignKeyConstraint(['order_status_id'], ['order_statuses.status_id'], name='orders_ibfk_2'),
        Index('customer_id', 'customer_id'),
        Index('order_status_id', 'order_status_id')
    )

    order_id = db.Column(db.db.Integer, primary_key=True)
    order_tot_quantity = db.Column(db.db.Integer, nullable=False)
    order_tot_price = db.Column(db.db.DECIMAL(10, 2), nullable=False)
    customer_id = db.Column(db.db.Integer, nullable=False)
    order_status_id = db.Column(db.db.Integer, nullable=False)
    customer = db.relationship('Customers', back_populates='orders')
    order_status = db.relationship('OrderStatuses', back_populates='orders')
    order_details: Mapped[list['OrderDetails']] = db.relationship('OrderDetails', back_populates='order')

class ProductsServices(db.Model):
    __tablename__ = 'products_services'
    __table_args__ = (
        ForeignKeyConstraint(['product_service_category_id'], ['categories.category_id'], name='products_services_ibfk_1'),
        ForeignKeyConstraint(['product_service_status_id'], ['entity_statuses.status_id'], name='products_services_ibfk_2'),
        Index('product_service_category_id', 'product_service_category_id'),
        Index('product_service_name', 'product_service_name', unique=True),
        Index('product_service_status_id', 'product_service_status_id')
    )

    product_service_id = db.Column(db.db.Integer, primary_key=True)
    product_service_name = db.Column(db.db.String(100), nullable=False)
    product_service_category_id = db.Column(db.db.Integer, nullable=False)
    product_service_status_id = db.Column(db.db.Integer, nullable=False)
    product_service_description: Mapped[Optional[str]] = db.Column(db.db.Text)product_service_pic_path: Mapped[Optional[str]] = db.Column(db.String(255))

    product_service_category = db.relationship('Categories', back_populates='products_services')
    product_service_status = db.relationship('EntityStatuses', back_populates='products_services')
    store_products_services: Mapped[list['StoreProductsServices']] = db.relationship('StoreProductsServices', back_populates='product_service')

class StatesRegions(db.Model):
    __tablename__ = 'states_regions'
    __table_args__ = (
        ForeignKeyConstraint(['country_id'], ['countries.country_id'], name='states_regions_ibfk_1'),
        ForeignKeyConstraint(['state_region_status_id'], ['entity_statuses.status_id'], name='states_regions_ibfk_2'),
        Index('country_id', 'country_id'),
        Index('state_region_code', 'state_region_code', unique=True),
        Index('state_region_status_id', 'state_region_status_id')
    )

    state_region_id = db.Column(db.db.Integer, primary_key=True)
    state_region_name = db.Column(db.db.String(100), nullable=False)
    state_region_code = db.Column(db.db.String(10), nullable=False)
    country_id = db.Column(db.db.Integer, nullable=False)
    state_region_status_id = db.Column(db.db.Integer, nullable=False)
    country = db.relationship('Countries', back_populates='states_regions')
    state_region_status = db.relationship('EntityStatuses', back_populates='states_regions')
    cities: Mapped[list['Cities']] = db.relationship('Cities', back_populates='state_region')

class StoreUserRole(db.Model):
    __tablename__ = 'store_user_role'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.role_id'], name='store_user_role_ibfk_3'),
        ForeignKeyConstraint(['status_id'], ['entity_statuses.status_id'], name='store_user_role_ibfk_4'),
        ForeignKeyConstraint(['store_id'], ['stores.store_id'], name='store_user_role_ibfk_1'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], name='store_user_role_ibfk_2'),
        Index('role_id', 'role_id'),
        Index('status_id', 'status_id'),
        Index('user_id', 'user_id')
    )

    store_id = db.Column(db.db.Integer, primary_key=True)
    user_id = db.Column(db.db.Integer, primary_key=True)
    role_id = db.Column(db.db.Integer, nullable=False)
    status_id = db.Column(db.db.Integer, nullable=False)
    role = db.relationship('Roles', back_populates='store_user_role')
    status = db.relationship('EntityStatuses', back_populates='store_user_role')
    store = db.relationship('Stores', back_populates='store_user_role')
    user = db.relationship('Users', back_populates='store_user_role')
class Cities(db.Model):
    __tablename__ = 'cities'
    __table_args__ = (
        ForeignKeyConstraint(['city_status_id'], ['entity_statuses.status_id'], name='cities_ibfk_2'),
        ForeignKeyConstraint(['state_region_id'], ['states_regions.state_region_id'], name='cities_ibfk_1'),
        Index('city_status_id', 'city_status_id'),
        Index('state_region_id', 'state_region_id')
    )

    city_id = db.Column(db.db.Integer, primary_key=True)
    city_name = db.Column(db.db.String(100), nullable=False)
    state_region_id = db.Column(db.db.Integer, nullable=False)
    city_status_id = db.Column(db.db.Integer, nullable=False)
    city_status = db.relationship('EntityStatuses', back_populates='cities')
    state_region = db.relationship('StatesRegions', back_populates='cities')
    customer_addresses: Mapped[list['CustomerAddresses']] = db.relationship('CustomerAddresses', back_populates='city')

class StoreProductsServices(db.Model):
    __tablename__ = 'store_products_services'
    __table_args__ = (
        ForeignKeyConstraint(['product_service_id'], ['products_services.product_service_id'], name='store_products_services_ibfk_3'),
        ForeignKeyConstraint(['status_id'], ['entity_statuses.status_id'], name='store_products_services_ibfk_1'),
        ForeignKeyConstraint(['store_id'], ['stores.store_id'], name='store_products_services_ibfk_2'),
        Index('idx_product_service', 'product_service_id'),
        Index('idx_store', 'store_id'),
        Index('status_id', 'status_id'),
        Index('uk_store_product', 'store_id', 'product_service_id', unique=True)
    )

    id = db.Column(db.db.Integer, primary_key=True)
    store_id = db.Column(db.db.Integer, nullable=False)
    product_service_id = db.Column(db.db.Integer, nullable=False)
    price = db.Column(db.db.DECIMAL(10, 2), nullable=False)
    stock = db.Column(db.db.Integer, nullable=False)
    status_id = db.Column(db.db.Integer, nullable=False)
    product_service = db.relationship('ProductsServices', back_populates='store_products_services')
    status = db.relationship('EntityStatuses', back_populates='store_products_services')
    store = db.relationship('Stores', back_populates='store_products_services')
    order_details: Mapped[list['OrderDetails']] = db.relationship('OrderDetails', back_populates='store_product_service')

class CustomerAddresses(db.Model):
    __tablename__ = 'customer_addresses'
    __table_args__ = (
        ForeignKeyConstraint(['address_status_id'], ['entity_statuses.status_id'], name='customer_addresses_ibfk_3'),
        ForeignKeyConstraint(['city_id'], ['cities.city_id'], name='customer_addresses_ibfk_2'),
        ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], name='customer_addresses_ibfk_1'),
        Index('address_status_id', 'address_status_id'),
        Index('city_id', 'city_id'),
        Index('customer_id', 'customer_id')
    )

    address_id = db.Column(db.db.Integer, primary_key=True)
    customer_id = db.Column(db.db.Integer, nullable=False)
    address_line1 = db.Column(db.db.String(255), nullable=False)
    city_id = db.Column(db.db.Integer, nullable=False)
    google_maps_url = db.Column(db.db.String(255), nullable=False)
    address_status_id = db.Column(db.db.Integer, nullable=False)
    postal_code = db.Column(db.db.String(20), nullable=False)
    address_line2: Mapped[Optional[str]] = db.Column(db.String(255))

    address_status = db.relationship('EntityStatuses', back_populates='customer_addresses')
    city = db.relationship('Cities', back_populates='customer_addresses')
    customer = db.relationship('Customers', back_populates='customer_addresses')
class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    __table_args__ = (
        ForeignKeyConstraint(['order_id'], ['orders.order_id'], name='order_details_ibfk_2'),
        ForeignKeyConstraint(['product_service_status_id'], ['order_statuses.status_id'], name='order_details_ibfk_1'),
        ForeignKeyConstraint(['store_product_service_id'], ['store_products_services.id'], name='order_details_ibfk_3'),
        Index('product_service_status_id', 'product_service_status_id'),
        Index('store_product_service_id', 'store_product_service_id')
    )

    order_id = db.Column(db.db.Integer, primary_key=True)
    store_product_service_id = db.Column(db.db.Integer, primary_key=True)
    product_service_quantity = db.Column(db.db.Integer, nullable=False)
    product_service_price = db.Column(db.db.DECIMAL(10, 2), nullable=False)
    product_service_tot_price = db.Column(db.db.DECIMAL(10, 2), nullable=False)
    product_service_status_id = db.Column(db.db.Integer, nullable=False)
    product_service_filled_quantity = db.Column(db.db.Integer, nullable=False, server_default=text("'0'"))
    product_service_filled_tot_price = db.Column(db.db.DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    order = db.relationship('Orders', back_populates='order_details')
    product_service_status = db.relationship('OrderStatuses', back_populates='order_details')
    store_product_service = db.relationship('StoreProductsServices', back_populates='order_details')