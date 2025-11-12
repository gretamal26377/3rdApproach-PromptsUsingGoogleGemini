# WSGI: Web Server Gateway Interface
# WSGI entrypoint for the customer backend used by gunicorn
# Module path: app.customer.wsgi -> exposes `app` for gunicorn to import

from app.customer import create_app

# create_app should return a Flask application
app = create_app()
