from flask import Flask
from .search import search_bp
from app.shared.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(search_bp)
    return app

app = create_app()
