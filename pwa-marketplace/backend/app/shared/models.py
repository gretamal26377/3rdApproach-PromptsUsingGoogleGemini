from .database import db

# vsCode Copilot explanation after research: The red cross in PROBLEMS windows means Linter treats it as an error,
# but it isn't a Python runtime error. Your Flask app should work as expected if you run it normally.
# The error is safe to ignore using # type: ignore

# Static models generated to match init SQL schema. These inherit from the
# Flask-SQLAlchemy `db.Model` so they work with Flask-Migrate and the app

class EntityStatus(db.Model):
    __tablename__ = 'entity_statuses'

    status_id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(50), unique=True, nullable=False)
    status_description = db.Column(db.Text)

    def __repr__(self):
        return f"<EntityStatus {self.status_code}>"


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    user_password_hash = db.Column(db.String(255), nullable=False)
    user_phone = db.Column(db.String(20), nullable=True)
    user_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    status = db.relationship('EntityStatus', backref='users')

    def __repr__(self):
        return f"<User {self.user_email}>"


class Store(db.Model):
    __tablename__ = 'stores'

    store_id = db.Column(db.Integer, primary_key=True)
    store_email = db.Column(db.String(100), unique=True, nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    store_description = db.Column(db.Text)
    store_phone = db.Column(db.String(20))
    store_address = db.Column(db.Text, nullable=True)
    store_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    status = db.relationship('EntityStatus', backref='stores')

    def __repr__(self):
        return f"<Store {self.store_name}>"


class Role(db.Model):
    __tablename__ = 'roles'

    role_id = db.Column(db.Integer, primary_key=True)
    role_code = db.Column(db.String(50), unique=True, nullable=False)
    role_description = db.Column(db.Text)

    def __repr__(self):
        return f"<Role {self.role_code}>"


class StoreUserRole(db.Model):
    __tablename__ = 'store_user_role'

    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    store = db.relationship('Store', backref='user_roles')
    user = db.relationship('User', backref='store_roles')
    role = db.relationship('Role')
    status = db.relationship('EntityStatus')

    def __repr__(self):
        return f"<StoreUserRole store={self.store_id} user={self.user_id} role={self.role_id}>"


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    category_description = db.Column(db.Text)
    category_pic_path = db.Column(db.String(255))
    category_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'), nullable=False)

    status = db.relationship('EntityStatus')

    def __repr__(self):
        return f"<Category {self.category_name}>"


class ProductService(db.Model):
    __tablename__ = 'products_services'

    product_service_id = db.Column(db.Integer, primary_key=True)
    product_service_name = db.Column(db.String(100), unique=True, nullable=False)
    product_service_description = db.Column(db.Text)
    product_service_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'))

    status = db.relationship('EntityStatus')

    def __repr__(self):
        return f"<ProductService {self.product_service_name}>"


class StoreProductService(db.Model):
    __tablename__ = 'store_products_services'

    id = db.Column(db.Integer, primary_key=True)
    product_service_id = db.Column(db.Integer, db.ForeignKey('products_services.product_service_id'))

    product_service = db.relationship('ProductService')

    def __repr__(self):
        return f"<StoreProductService id={self.id} product={self.product_service_id}>"


class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True)
    customer_status_id = db.Column(db.Integer, db.ForeignKey('entity_statuses.status_id'))

    status = db.relationship('EntityStatus')

    def __repr__(self):
        return f"<Customer {self.customer_id}>"