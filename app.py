# app.py - Now very small and clean!
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from datetime import timedelta

# Load environment variables
load_dotenv()

# Import blueprints
from routes import auth_bp, query_bp, data_bp, page_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))
    
    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(page_bp)      # Page routes: /, /dashboard, /login, /register
    app.register_blueprint(auth_bp)      # Auth routes: /api/register, /api/login, /api/protected
    app.register_blueprint(query_bp)     # Query routes: /api/query, /api/explain, /api/optimize
    app.register_blueprint(data_bp)      # Data routes: /api/data/preview, /api/data/schema
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.getenv('DEBUG', 'True').lower() == 'true',
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000))
    )