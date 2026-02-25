# WSGI entrypoint for the Organisation Admin Backend used by gunicorn
# Module path: app.org_admin.wsgi -> exposes `app` for gunicorn to import.
# Bellow line imports `create_app` from app.org_admin package that in turns
#  runs/triggers __init__.py to be executed, which sets up the app

from app.org_admin import create_app

# create_app should return a Flask application
app = create_app()
