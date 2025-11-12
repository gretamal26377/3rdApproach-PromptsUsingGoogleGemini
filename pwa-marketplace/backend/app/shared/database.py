from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Centralized DB instances used across the application
# Import `db` and `migrate` from other modules instead of creating new instances
db = SQLAlchemy()
migrate = Migrate()


def init_extensions(app):
    """
    Initialize DB related extensions on the provided Flask app.
    Call this from the app factory (__init__.create_app) in each blueprint package
    """
    # Wires the Flask app with the SQLAlchemy instance
    db.init_app(app)
    # Wires the Flask app with the Flask-Migrate instance and
    # binds it to the SQLAlchemy instance
    migrate.init_app(app, db)
