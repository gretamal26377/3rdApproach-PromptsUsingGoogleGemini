from flask import Flask
from ..shared.config import Config
from ..shared.database import init_extensions
from .customer_routes import customer_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize DB and other extensions. This way other modules can import
    # "from shared.database import db, migrate" and use them directly without
    # needing to initialize them again.
    # It also connects the DB through SQLALCHEMY_DATABASE_URI setting in config
    init_extensions(app)

    # Register customer blueprint
    app.register_blueprint(customer_bp)

    return app
