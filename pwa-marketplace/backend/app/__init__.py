from flask import Flask

from .shared.config import Config
from .shared.database import db
from .customer.customer_routes import customer_bp
from .shared.search import search_bp
# from .admin import create_admin_app  # Assuming admin has its own factory

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(customer_bp)
    app.register_blueprint(search_bp)

    # You could also mount the admin app as a sub-application
    # app.mount('/admin', create_admin_app())

    return app