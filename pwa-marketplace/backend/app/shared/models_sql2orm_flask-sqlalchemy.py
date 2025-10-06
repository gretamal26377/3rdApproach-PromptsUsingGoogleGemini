from .database import db
from sqlalchemy import Index, ForeignKeyConstraint, text

# Auto-generated models file — review before committing

class Categories(db.Model):
    __tablename__ = 'categories'
    __table_args__ = (
        Index('category_name', 'category_name', unique=True),
        Index('category_status_id', 'category_status_id'),
        ForeignKeyConstraint(['category_status_id'], ['entity_statuses.status_id']),
    )

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    category_description = db.Column(db.Text)
    category_pic_path = db.Column(db.String(255))
    category_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    category_status = db.relationship('EntityStatuses', back_populates='categories')
    products_services = db.relationship('ProductsServices', back_populates='product_service_category')


class EntityStatuses(db.Model):
    __tablename__ = 'entity_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(50), nullable=False)
    status_description = db.Column(db.Text)

    categories = db.relationship('Categories', back_populates='category_status')
    cities = db.relationship('Cities', back_populates='city_status')
    states_regions = db.relationship('StatesRegions', back_populates='state_region_status')
    countries = db.relationship('Countries', back_populates='country_status')
    customer_addresses = db.relationship('CustomerAddresses', back_populates='address_status')
    customers = db.relationship('Customers', back_populates='customer_status')
    store_products_services = db.relationship('StoreProductsServices', back_populates='status')
    stores = db.relationship('Stores', back_populates='store_status')
    products_services = db.relationship('ProductsServices', back_populates='product_service_status')
    store_user_roles = db.relationship('StoreUserRole', back_populates='status')
    users = db.relationship('Users', back_populates='user_status')


class CategoriesHistory(db.Model):
    __tablename__ = 'categories_history'
    __table_args__ = (
        Index('category_id', 'category_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    category_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class Cities(db.Model):
    __tablename__ = 'cities'
    __table_args__ = (
        Index('city_status_id', 'city_status_id'),
        Index('state_region_id', 'state_region_id'),
        ForeignKeyConstraint(['state_region_id'], ['states_regions.state_region_id']),
        ForeignKeyConstraint(['city_status_id'], ['entity_statuses.status_id']),
    )

    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), nullable=False)
    state_region_id = db.Column(db.Integer, nullable=False, db.ForeignKey('states_regions.state_region_id'))
    city_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    state_region = db.relationship('StatesRegions', back_populates='cities')
    city_status = db.relationship('EntityStatuses', back_populates='cities')
    customer_addresses = db.relationship('CustomerAddresses', back_populates='city')


class StatesRegions(db.Model):
    __tablename__ = 'states_regions'
    __table_args__ = (
        Index('country_id', 'country_id'),
        Index('state_region_status_id', 'state_region_status_id'),
        Index('state_region_code', 'state_region_code', unique=True),
        ForeignKeyConstraint(['country_id'], ['countries.country_id']),
        ForeignKeyConstraint(['state_region_status_id'], ['entity_statuses.status_id']),
    )

    state_region_id = db.Column(db.Integer, primary_key=True)
    state_region_name = db.Column(db.String(100), nullable=False)
    state_region_code = db.Column(db.String(10), nullable=False)
    country_id = db.Column(db.Integer, nullable=False, db.ForeignKey('countries.country_id'))
    state_region_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    country = db.relationship('Countries', back_populates='states_regions')
    state_region_status = db.relationship('EntityStatuses', back_populates='states_regions')
    cities = db.relationship('Cities', back_populates='state_region')


class Countries(db.Model):
    __tablename__ = 'countries'
    __table_args__ = (
        Index('country_status_id', 'country_status_id'),
        Index('country_code', 'country_code', unique=True),
        ForeignKeyConstraint(['country_status_id'], ['entity_statuses.status_id']),
    )

    country_id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    country_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    country_status = db.relationship('EntityStatuses', back_populates='countries')
    states_regions = db.relationship('StatesRegions', back_populates='country')


class CitiesHistory(db.Model):
    __tablename__ = 'cities_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('city_id', 'city_id'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    city_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class CountriesHistory(db.Model):
    __tablename__ = 'countries_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('country_id', 'country_id'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    country_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class CustomerAddresses(db.Model):
    __tablename__ = 'customer_addresses'
    __table_args__ = (
        Index('city_id', 'city_id'),
        Index('address_status_id', 'address_status_id'),
        Index('customer_id', 'customer_id'),
        ForeignKeyConstraint(['city_id'], ['cities.city_id']),
        ForeignKeyConstraint(['address_status_id'], ['entity_statuses.status_id']),
        ForeignKeyConstraint(['customer_id'], ['customers.customer_id']),
    )

    address_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False, db.ForeignKey('customers.customer_id'))
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city_id = db.Column(db.Integer, nullable=False, db.ForeignKey('cities.city_id'))
    google_maps_url = db.Column(db.String(255), nullable=False)
    address_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))
    postal_code = db.Column(db.String(20), nullable=False)

    customer = db.relationship('Customers', back_populates='customer_addresses')
    city = db.relationship('Cities', back_populates='customer_addresses')
    address_status = db.relationship('EntityStatuses', back_populates='customer_addresses')


class Customers(db.Model):
    __tablename__ = 'customers'
    __table_args__ = (
        Index('customer_status_id', 'customer_status_id'),
        Index('customer_email', 'customer_email', unique=True),
        ForeignKeyConstraint(['customer_status_id'], ['entity_statuses.status_id']),
    )

    customer_id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_password_hash = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    customer_status = db.relationship('EntityStatuses', back_populates='customers')
    customer_addresses = db.relationship('CustomerAddresses', back_populates='customer')
    orders = db.relationship('Orders', back_populates='customer')


class CustomerAddressesHistory(db.Model):
    __tablename__ = 'customer_addresses_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('address_id', 'address_id'),
        Index('customer_id', 'customer_id'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    address_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class CustomersHistory(db.Model):
    __tablename__ = 'customers_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('customer_id', 'customer_id'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    customer_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class EntityStatusesHistory(db.Model):
    __tablename__ = 'entity_statuses_history'
    __table_args__ = (
        Index('status_id', 'status_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    status_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    __table_args__ = (
        Index('product_service_status_id', 'product_service_status_id'),
        Index('store_product_service_id', 'store_product_service_id'),
        ForeignKeyConstraint(['product_service_status_id'], ['order_statuses.status_id']),
        ForeignKeyConstraint(['order_id'], ['orders.order_id']),
        ForeignKeyConstraint(['store_product_service_id'], ['store_products_services.id']),
    )

    order_id = db.Column(db.Integer, primary_key=True, db.ForeignKey('orders.order_id'))
    store_product_service_id = db.Column(db.Integer, primary_key=True, db.ForeignKey('store_products_services.id'))
    product_service_quantity = db.Column(db.Integer, nullable=False)
    product_service_price = db.Column(db.Numeric, nullable=False)
    product_service_tot_price = db.Column(db.Numeric, nullable=False)
    product_service_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('order_statuses.status_id'))
    product_service_filled_quantity = db.Column(db.Integer, nullable=False)
    product_service_filled_tot_price = db.Column(db.Numeric, nullable=False)

    order = db.relationship('Orders', back_populates='order_details')
    store_product_service = db.relationship('StoreProductsServices', back_populates='order_details')
    product_service_status = db.relationship('OrderStatuses', back_populates='order_details')


class OrderStatuses(db.Model):
    __tablename__ = 'order_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(50), nullable=False)
    status_description = db.Column(db.Text)

    order_details = db.relationship('OrderDetails', back_populates='product_service_status')
    orders = db.relationship('Orders', back_populates='order_status')


class Orders(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        Index('order_status_id', 'order_status_id'),
        Index('customer_id', 'customer_id'),
        ForeignKeyConstraint(['order_status_id'], ['order_statuses.status_id']),
        ForeignKeyConstraint(['customer_id'], ['customers.customer_id']),
    )

    order_id = db.Column(db.Integer, primary_key=True)
    order_tot_quantity = db.Column(db.Integer, nullable=False)
    order_tot_price = db.Column(db.Numeric, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False, db.ForeignKey('customers.customer_id'))
    order_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('order_statuses.status_id'))

    customer = db.relationship('Customers', back_populates='orders')
    order_status = db.relationship('OrderStatuses', back_populates='orders')
    order_details = db.relationship('OrderDetails', back_populates='order')


class StoreProductsServices(db.Model):
    __tablename__ = 'store_products_services'
    __table_args__ = (
        Index('idx_store', 'store_id'),
        Index('idx_product_service', 'product_service_id'),
        Index('status_id', 'status_id'),
        Index('uk_store_product', 'store_id', 'product_service_id', unique=True),
        ForeignKeyConstraint(['store_id'], ['stores.store_id']),
        ForeignKeyConstraint(['status_id'], ['entity_statuses.status_id']),
        ForeignKeyConstraint(['product_service_id'], ['products_services.product_service_id']),
    )

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=False, db.ForeignKey('stores.store_id'))
    product_service_id = db.Column(db.Integer, nullable=False, db.ForeignKey('products_services.product_service_id'))
    price = db.Column(db.Numeric, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    store = db.relationship('Stores', back_populates='store_products_services')
    product_service = db.relationship('ProductsServices', back_populates='store_products_services')
    status = db.relationship('EntityStatuses', back_populates='store_products_services')
    order_details = db.relationship('OrderDetails', back_populates='store_product_service')


class Stores(db.Model):
    __tablename__ = 'stores'
    __table_args__ = (
        Index('store_email', 'store_email', unique=True),
        Index('store_status_id', 'store_status_id'),
        ForeignKeyConstraint(['store_status_id'], ['entity_statuses.status_id']),
    )

    store_id = db.Column(db.Integer, primary_key=True)
    store_email = db.Column(db.String(100), nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    store_description = db.Column(db.Text)
    store_phone = db.Column(db.String(20))
    store_address = db.Column(db.Text, nullable=False)
    store_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    store_status = db.relationship('EntityStatuses', back_populates='stores')
    store_products_services = db.relationship('StoreProductsServices', back_populates='store')
    store_user_roles = db.relationship('StoreUserRole', back_populates='store')


class ProductsServices(db.Model):
    __tablename__ = 'products_services'
    __table_args__ = (
        Index('product_service_name', 'product_service_name', unique=True),
        Index('product_service_category_id', 'product_service_category_id'),
        Index('product_service_status_id', 'product_service_status_id'),
        ForeignKeyConstraint(['product_service_status_id'], ['entity_statuses.status_id']),
        ForeignKeyConstraint(['product_service_category_id'], ['categories.category_id']),
    )

    product_service_id = db.Column(db.Integer, primary_key=True)
    product_service_name = db.Column(db.String(100), nullable=False)
    product_service_description = db.Column(db.Text)
    product_service_pic_path = db.Column(db.String(255))
    product_service_category_id = db.Column(db.Integer, nullable=False, db.ForeignKey('categories.category_id'))
    product_service_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    product_service_category = db.relationship('Categories', back_populates='products_services')
    product_service_status = db.relationship('EntityStatuses', back_populates='products_services')
    store_products_services = db.relationship('StoreProductsServices', back_populates='product_service')


class OrderDetailsHistory(db.Model):
    __tablename__ = 'order_details_history'
    __table_args__ = (
        Index('store_product_service_id', 'store_product_service_id'),
        Index('order_id', 'order_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.Integer)
    store_product_service_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class OrderStatusesHistory(db.Model):
    __tablename__ = 'order_statuses_history'
    __table_args__ = (
        Index('status_id', 'status_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    status_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class OrdersHistory(db.Model):
    __tablename__ = 'orders_history'
    __table_args__ = (
        Index('order_id', 'order_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class ProductsServicesHistory(db.Model):
    __tablename__ = 'products_services_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('product_service_id', 'product_service_id'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    product_service_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class Roles(db.Model):
    __tablename__ = 'roles'
    __table_args__ = (
        Index('role_code', 'role_code', unique=True),
    )

    role_id = db.Column(db.Integer, primary_key=True)
    role_code = db.Column(db.String(50), nullable=False)
    role_description = db.Column(db.Text)

    store_user_roles = db.relationship('StoreUserRole', back_populates='role')


class RolesHistory(db.Model):
    __tablename__ = 'roles_history'
    __table_args__ = (
        Index('role_id', 'role_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    role_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class StatesRegionsHistory(db.Model):
    __tablename__ = 'states_regions_history'
    __table_args__ = (
        Index('state_region_id', 'state_region_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    state_region_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class StoreProductsServicesHistory(db.Model):
    __tablename__ = 'store_products_services_history'
    __table_args__ = (
        Index('store_id', 'store_id'),
        Index('product_service_id', 'product_service_id'),
        Index('id', 'id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    id = db.Column(db.Integer)
    store_id = db.Column(db.Integer)
    product_service_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class StoreUserRole(db.Model):
    __tablename__ = 'store_user_role'
    __table_args__ = (
        Index('status_id', 'status_id'),
        Index('role_id', 'role_id'),
        Index('user_id', 'user_id'),
        ForeignKeyConstraint(['user_id'], ['users.user_id']),
        ForeignKeyConstraint(['store_id'], ['stores.store_id']),
        ForeignKeyConstraint(['role_id'], ['roles.role_id']),
        ForeignKeyConstraint(['status_id'], ['entity_statuses.status_id']),
    )

    store_id = db.Column(db.Integer, primary_key=True, db.ForeignKey('stores.store_id'))
    user_id = db.Column(db.Integer, primary_key=True, db.ForeignKey('users.user_id'))
    role_id = db.Column(db.Integer, nullable=False, db.ForeignKey('roles.role_id'))
    status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    store = db.relationship('Stores', back_populates='store_user_roles')
    user = db.relationship('Users', back_populates='store_user_roles')
    role = db.relationship('Roles', back_populates='store_user_roles')
    status = db.relationship('EntityStatuses', back_populates='store_user_roles')


class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        Index('user_email', 'user_email', unique=True),
        Index('user_status_id', 'user_status_id'),
        ForeignKeyConstraint(['user_status_id'], ['entity_statuses.status_id']),
    )

    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    user_password_hash = db.Column(db.String(255), nullable=False)
    user_phone = db.Column(db.String(20), nullable=False)
    user_status_id = db.Column(db.Integer, nullable=False, db.ForeignKey('entity_statuses.status_id'))

    user_status = db.relationship('EntityStatuses', back_populates='users')
    store_user_roles = db.relationship('StoreUserRole', back_populates='user')


class StoreUserRoleHistory(db.Model):
    __tablename__ = 'store_user_role_history'
    __table_args__ = (
        Index('user_id', 'user_id'),
        Index('store_id', 'store_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    store_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class StoresHistory(db.Model):
    __tablename__ = 'stores_history'
    __table_args__ = (
        Index('store_id', 'store_id'),
        Index('changed_at', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    store_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class UsersHistory(db.Model):
    __tablename__ = 'users_history'
    __table_args__ = (
        Index('idx_users_history_user', 'user_id'),
        Index('idx_users_history_time', 'changed_at'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)


