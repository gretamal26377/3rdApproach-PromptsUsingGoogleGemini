# from venv import create
import platform
from .database import db
from sqlalchemy import Index, ForeignKeyConstraint, text

class Categories(db.Model):
    __tablename__ = 'categories'
    __table_args__ = (
        Index('category_name', 'category_name', unique=True),
    )

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    category_description = db.Column(db.Text)
    category_pic_path = db.Column(db.String(255))
    category_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    category_status = db.relationship('EntityStatuses', back_populates='categories')
    products_services = db.relationship('ProductsServices', back_populates='product_service_category')


class EntityStatuses(db.Model):
    __tablename__ = 'entity_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.Integer, primary_key=True)
    # e.g., 'active', 'inactive', 'banned'
    status_code = db.Column(db.String(50), nullable=False)
    status_display = db.Column(db.String(100), nullable=False)
    status_description = db.Column(db.Text)

    categories = db.relationship('Categories', back_populates='category_status')
    cities_towns = db.relationship('CitiesTowns', back_populates='city_town_status')
    states_regions = db.relationship('StatesRegions', back_populates='state_region_status')
    countries = db.relationship('Countries', back_populates='country_status')
    # customers_addresses = db.relationship('CustomersAddresses', back_populates='address_status')
    customers = db.relationship('Customers', back_populates='customer_status')
    stores_products_services = db.relationship('StoresProductsServices', back_populates='status')
    organisations = db.relationship('Organisations', back_populates='organisations_status')
    roles = db.relationship('Roles', back_populates='role_status')
    stores = db.relationship('Stores', back_populates='store_status')
    products_services = db.relationship('ProductsServices', back_populates='product_service_status')
    stores_users = db.relationship('StoresUsers', back_populates='status')
    users = db.relationship('Users', back_populates='user_status')
    platform_users = db.relationship('PlatformUsers', back_populates='platform_user_status')

class CategoriesHistory(db.Model):
    __tablename__ = 'categories_history'
    __table_args__ = (
        Index('category_id', 'category_id'),
        Index('changed_at', 'changed_at'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    category_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)


class CitiesTowns(db.Model):
    __tablename__ = 'cities_towns'

    city_town_id = db.Column(db.Integer, primary_key=True)
    city_town_name = db.Column(db.String(100), nullable=False)
    state_region_id = db.Column(db.Integer, db.ForeignKey('states_regions.state_region_id'), nullable=False)
    city_town_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    state_region = db.relationship('StatesRegions', back_populates='cities_towns')
    city_town_status = db.relationship('EntityStatuses', back_populates='cities_towns')
    customers_addresses = db.relationship('CustomersAddresses', back_populates='city_town')


class StatesRegions(db.Model):
    __tablename__ = 'states_regions'
    __table_args__ = (
        Index('state_region_code', 'state_region_code', unique=True),
    )

    state_region_id = db.Column(db.Integer, primary_key=True)
    state_region_name = db.Column(db.String(100), nullable=False)
    state_region_code = db.Column(db.String(10), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.country_id'), nullable=False)
    state_region_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    country = db.relationship('Countries', back_populates='states_regions')
    state_region_status = db.relationship('EntityStatuses', back_populates='states_regions')
    cities_towns = db.relationship('CitiesTowns', back_populates='state_region')


class Countries(db.Model):
    __tablename__ = 'countries'
    __table_args__ = (
        Index('country_code', 'country_code', unique=True),
    )

    country_id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    country_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    country_status = db.relationship('EntityStatuses', back_populates='countries')
    states_regions = db.relationship('StatesRegions', back_populates='country')


class CitiesTownsHistory(db.Model):
    __tablename__ = 'cities_towns_history'
    __table_args__ = (
        Index('city_town_id', 'city_town_id'),
        Index('changed_at', 'changed_at'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    city_town_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class CountriesHistory(db.Model):
    __tablename__ = 'countries_history'
    __table_args__ = (
        Index('country_id', 'country_id'),
        Index('changed_at', 'changed_at'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    country_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)



class CustomersAddresses(db.Model):
    __tablename__ = 'customers_addresses'

    address_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city_town_id = db.Column(db.Integer, db.ForeignKey('cities_towns.city_town_id'), nullable=False)
    google_maps_url = db.Column(db.String(255), nullable=False)
    address_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)
    postal_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    customer = db.relationship('Customers', back_populates='customers_addresses')
    city_town = db.relationship('CitiesTowns', back_populates='customers_addresses')
    # address_status = db.relationship('EntityStatuses', back_populates='customers_addresses')


class Customers(db.Model):
    __tablename__ = 'customers'
    __table_args__ = (
        Index('customer_email', 'customer_email', unique=True),
    )

    customer_id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_password_hash = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)
    customer_created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    customer_status = db.relationship('EntityStatuses', back_populates='customers')
    customers_addresses = db.relationship('CustomersAddresses', back_populates='customer')
    orders = db.relationship('Orders', back_populates='customer')


class CustomersAddressesHistory(db.Model):
    __tablename__ = 'customers_addresses_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('customer_id', 'customer_id'),
        Index('address_id', 'address_id'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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
        Index('changed_at', 'changed_at'),
        Index('status_id', 'status_id'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    status_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)


class OrdersDetails(db.Model):
    __tablename__ = 'orders_details'
    __table_args__ = (
        Index('product_service_status_id', 'product_service_status_id'),
        # Add index for Temporal Item Workflow ID
        Index('temporal_workflow_id', 'temporal_workflow_id', unique=True),
    )

    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), primary_key=True)
    store_product_service_id = db.Column(db.Integer, db.ForeignKey('store_products_services.id'), primary_key=True)
    product_service_quantity = db.Column(db.Integer, nullable=False)
    product_service_price = db.Column(db.Numeric, nullable=False)
    product_service_tot_price = db.Column(db.Numeric, nullable=False)
    product_service_status_id = db.Column(db.Integer, db.ForeignKey('order_statuses.status_id'), nullable=False)
    product_service_filled_quantity = db.Column(db.Integer, nullable=False)
    product_service_filled_tot_price = db.Column(db.Numeric, nullable=False)
    product_service_created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    temporal_workflow_id = db.Column(db.String(100), nullable=False, unique=True)  # Field for Temporal Item Workflow ID

    order = db.relationship('Orders', back_populates='orders_details')
    stores_product_service = db.relationship('StoresProductsServices', back_populates='orders_details')
    product_service_status = db.relationship('OrderStatuses', back_populates='orders_details')


class OrderStatuses(db.Model):
    __tablename__ = 'order_statuses'
    __table_args__ = (
        Index('status_code', 'status_code', unique=True),
    )

    status_id = db.Column(db.Integer, primary_key=True)
    # eg: 'open', 'paid', 'pending', 
    #     'filled', 'partial_filled', 'shipped', 'partial_shipped',
    #     'delivered', 'partial_delivered', 'canceled', 'partial_canceled', 'returned', 'partial_returned',
    #     'refunded', 'partial_refunded', 'customer_accepted'
    status_code = db.Column(db.String(50), nullable=False)
    status_display = db.Column(db.String(100), nullable=False)
    status_description = db.Column(db.Text)

    orders_details = db.relationship('OrdersDetails', back_populates='product_service_status')
    orders = db.relationship('Orders', back_populates='order_status')


class Orders(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        Index('customer_id', 'customer_id'),
        Index('order_status_id', 'order_status_id'),
        # Add index for Temporal Workflow ID for efficient lookups
        Index('temporal_workflow_id', 'temporal_workflow_id', unique=True),
    )

    order_id = db.Column(db.Integer, primary_key=True)
    order_tot_quantity = db.Column(db.Integer, nullable=False)
    order_tot_price = db.Column(db.Numeric, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    order_status_id = db.Column(db.Integer, db.ForeignKey('order_statuses.status_id'), nullable=False)
    # text(): Ensures that value in parentheses is treated as a literal SQL expression and not as a string
    order_created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    temporal_workflow_id = db.Column(db.String(100), nullable=False, unique=True)  # Field for Temporal Workflow ID

    customer = db.relationship('Customers', back_populates='orders')
    order_status = db.relationship('OrderStatuses', back_populates='orders')
    orders_details = db.relationship('OrdersDetails', back_populates='order')


class Organisations(db.Model):
    __tablename__ = 'organisations'
    __table_args__ = (
        Index('organisation_email', 'organisation_email', unique=True),
    )

    organisation_id = db.Column(db.Integer, primary_key=True)
    organisation_email = db.Column(db.String(100), nullable=False)
    organisation_name = db.Column(db.String(100), nullable=False)
    organisation_description = db.Column(db.Text)
    organisation_phone = db.Column(db.String(20))
    organisation_address = db.Column(db.Text, nullable=False)
    organisation_pic_path = db.Column(db.String(255))
    organisation_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)
    organisation_created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    organisations_status = db.relationship('EntityStatuses', back_populates='organisations')
    organisations_stores = db.relationship('Stores', back_populates='organisation')
    organisations_users = db.relationship('Users', back_populates='organisation')


class Stores(db.Model):
    __tablename__ = 'stores'
    __table_args__ = (
        Index('store_email', 'store_email', unique=True),
    )

    store_id = db.Column(db.Integer, primary_key=True)
    store_email = db.Column(db.String(100), nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    store_description = db.Column(db.Text)
    store_phone = db.Column(db.String(20))
    store_type = db.Column(db.Enum('PHYSICAL', 'ONLINE', 'BOTH', name='store_type_enum'), nullable=False)
    store_city_town_id = db.Column(db.Integer, db.ForeignKey('cities_towns.city_town_id'), nullable=False)
    store_address = db.Column(db.Text, nullable=False)
    store_pic_path = db.Column(db.String(255))
    store_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)
    store_organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.organisation_id'), nullable=False)
    store_created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    store_status = db.relationship('EntityStatuses', back_populates='stores')
    stores_products_services = db.relationship('StoresProductsServices', back_populates='store')
    stores_users = db.relationship('StoresUsers', back_populates='store')
    organisation = db.relationship('Organisations', back_populates='organisations_stores')


class StoresProductsServices(db.Model):
    __tablename__ = 'stores_products_services'
    __table_args__ = (
        Index('uk_store_product', 'store_id', 'product_service_id', unique=True),
    )

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), nullable=False)
    product_service_id = db.Column(db.Integer, db.ForeignKey('products_services.product_service_id'), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    store = db.relationship('Stores', back_populates='stores_products_services')
    product_service = db.relationship('ProductsServices', back_populates='stores_products_services')
    status = db.relationship('EntityStatuses', back_populates='stores_products_services')
    orders_details = db.relationship('OrdersDetails', back_populates='stores_product_service')


# --- FeaturedStores Model ---
class FeaturedStores(db.Model):
    __tablename__ = 'featured_stores'
    __table_args__ = (
        Index('idx_featured_priority_order', 'priority_order'),
        Index('idx_featured_store_id', 'store_id'),
        Index('idx_featured_end_date', 'end_date'),
    )

    featured_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), nullable=False)
    priority_order = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    featured_type = db.Column(db.Enum('MANUAL', 'ALGORITHM', 'PAID', name='featured_type_enum'), nullable=False)

    store = db.relationship('Stores', backref='featured_stores')

class Roles(db.Model):
    __tablename__ = 'roles'
    __table_args__ = (
        Index('role_code', 'role_code', unique=True),
    )

    role_id = db.Column(db.Integer, primary_key=True)
    # e.g., 'admin', 'supervisor', 'staff'
    role_code = db.Column(db.String(50), nullable=False)
    # e.g., 'Admin', 'Supervisor', 'Staff'
    role_display = db.Column(db.String(100), nullable=False)
    role_description = db.Column(db.Text)
    role_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    roles_users = db.relationship('Users', back_populates='role')
    role_status = db.relationship('EntityStatuses', back_populates='roles')


# --- FeaturedStoresHistory Model ---
class FeaturedStoresHistory(db.Model):
    __tablename__ = 'featured_stores_history'
    __table_args__ = (
        Index('idx_featured_stores_hist_featured_id', 'featured_id'),
        Index('idx_featured_stores_hist_changed_at', 'changed_at'),
        Index('idx_featured_stores_hist_changed_by', 'changed_by'),
        Index('idx_featured_stores_hist_op_type', 'op_type'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    featured_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)


class ProductsServices(db.Model):
    __tablename__ = 'products_services'
    __table_args__ = (
        Index('product_service_name', 'product_service_name', unique=True),
    )

    product_service_id = db.Column(db.Integer, primary_key=True)
    product_service_name = db.Column(db.String(100), nullable=False)
    product_service_description = db.Column(db.Text)
    product_service_pic_path = db.Column(db.String(255))
    product_service_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    product_service_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    product_service_category = db.relationship('Categories', back_populates='products_services')
    product_service_status = db.relationship('EntityStatuses', back_populates='products_services')
    stores_products_services = db.relationship('StoresProductsServices', back_populates='product_service')


class OrdersDetailsHistory(db.Model):
    __tablename__ = 'orders_details_history'
    __table_args__ = (
        Index('store_product_service_id', 'store_product_service_id'),
        Index('order_id', 'order_id'),
        Index('changed_at', 'changed_at'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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
        Index('product_service_id', 'product_service_id'),
        Index('changed_at', 'changed_at'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    product_service_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)


class RolesHistory(db.Model):
    __tablename__ = 'roles_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('role_id', 'role_id'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    state_region_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)


class StoresProductsServicesHistory(db.Model):
    __tablename__ = 'stores_products_services_history'
    __table_args__ = (
        Index('id', 'id'),
        Index('store_id', 'store_id'),
        Index('changed_at', 'changed_at'),
        Index('product_service_id', 'product_service_id'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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


class StoresUsers(db.Model):
    __tablename__ = 'stores_users'

    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    store = db.relationship('Stores', back_populates='stores_users')
    user = db.relationship('Users', back_populates='stores_user')
    status = db.relationship('EntityStatuses', back_populates='stores_users')

class PlatformUsers(db.Model):
    __tablename__ = 'platform_users'
    __table_args__ = (
        Index('platform_user_email', 'platform_user_email', unique=True),
    )

    platform_user_id = db.Column(db.Integer, primary_key=True)
    platform_user_email = db.Column(db.String(100), nullable=False)
    platform_user_name = db.Column(db.String(50), nullable=False)
    platform_user_password_hash = db.Column(db.String(255), nullable=False)
    platform_user_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)
    platform_user_role_id = db.Column(db.Integer, db.ForeignKey('platform_roles.platform_role_id'), nullable=False)
    platform_user_created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    platform_user_status = db.relationship('EntityStatuses', back_populates='platform_users')
    platform_role = db.relationship('Roles', back_populates='platform_users')

class OrgUsers(db.Model):
    __tablename__ = 'org_users'
    __table_args__ = (
        Index('user_email_organisation', 'user_email', 'user_organisation_id', unique=True),
    )

    org_user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    user_password_hash = db.Column(db.String(255), nullable=False)
    user_phone = db.Column(db.String(20), nullable=False)
    user_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)
    user_organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.organisation_id'), nullable=False)
    user_role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    user_created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    user_status = db.relationship('EntityStatuses', back_populates='users')
    stores_user = db.relationship('StoresUsers', back_populates='user')
    organisation = db.relationship('Organisations', back_populates='organisations_users')
    role = db.relationship('Roles', back_populates='roles_users')


class StoresUsersHistory(db.Model):
    __tablename__ = 'stores_users_history'
    __table_args__ = (
        Index('changed_at', 'changed_at'),
        Index('store_id', 'store_id'),
        Index('user_id', 'user_id'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    store_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)


class OrganisationsHistory(db.Model):
    __tablename__ = 'organisations_history'
    __table_args__ = (
        Index('organisation_id', 'organisation_id'),
        Index('changed_at', 'changed_at'),
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    organisation_id = db.Column(db.Integer)
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
        Index('changed_by', 'changed_by'),
        Index('op_type', 'op_type')
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
        Index('idx_users_history_changed_by', 'changed_by'),
        Index('idx_users_history_op', 'op_type'),
    )

    hist_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer)
    op_type = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime)
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)

