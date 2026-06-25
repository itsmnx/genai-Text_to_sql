# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Data paths
    DATA_PATH = os.getenv('DATA_PATH', 'data/')
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/')
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', None)
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)