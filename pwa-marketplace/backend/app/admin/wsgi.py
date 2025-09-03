# WSGI entrypoint for the admin backend used by gunicorn
# Module path: app.admin.wsgi -> exposes `app` for gunicorn to import

from app.admin import create_app

# create_app should return a Flask application
app = create_app()
