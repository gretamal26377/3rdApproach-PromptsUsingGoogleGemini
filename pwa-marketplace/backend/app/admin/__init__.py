from flask import Flask
from ..shared.config import Config
from ..shared.database import init_extensions, register_request_hooks
from .admin_routes import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize shared db/migrate via helper and connect to the DB
    # through SQLALCHEMY_DATABASE_URI setting in config
    init_extensions(app)
    register_request_hooks(app)

    # Register only the admin blueprint
    app.register_blueprint(admin_bp)

    return app
