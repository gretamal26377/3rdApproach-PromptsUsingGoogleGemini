from flask import g, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # type: ignore
from sqlalchemy import text

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

def register_request_hooks(app):
    """Register per-request hooks (e.g., audit user propagation)"""

    @app.before_request
    def set_audit_user_from_cookie():
        """
        Set @audit_user for this DB session using a cookie-stored user email.
        This is used among others to populate audit fields like created_by, updated_by in tables such as the history ones.
        # @app.before_request: It's a Flask decorator that run this function automatically before each DB request

        """
        user_email = request.cookies.get("user_email")
        g.current_user_email = user_email
        try:
            if user_email:
                db.session.execute(text("SET @audit_user = :email"), {"email": user_email})
            else:
                db.session.execute(text("SET @audit_user = NULL"))
        # This Exception is defensive coding, it's a "safety net" if for some reason the DB isn't ready yet 
        except Exception:
            db.session.rollback()
