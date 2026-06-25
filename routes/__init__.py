# routes/__init__.py
from routes.auth_routes import auth_bp
from routes.query_routes import query_bp
from routes.data_routes import data_bp
from routes.page_routes import page_bp

__all__ = ['auth_bp', 'query_bp', 'data_bp', 'page_bp']