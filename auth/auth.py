# auth/auth.py - Updated with flask-jwt-extended
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
from functools import wraps
from flask import request, jsonify

class AuthManager:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'dev-secret-key')
        self.access_expires = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))
        self.users = {}  # In production, use a database
    
    def hash_password(self, password):
        """Hash password using werkzeug"""
        return generate_password_hash(password)
    
    def verify_password(self, password, hashed):
        """Verify password against hash using werkzeug"""
        return check_password_hash(hashed, password)
    
    def generate_token(self, identity):
        """Generate JWT token using flask-jwt-extended"""
        return create_access_token(
            identity=identity,
            expires_delta=self.access_expires
        )
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = decode_token(token)
            return payload
        except Exception:
            return None
    
    def get_current_user(self):
        """Get current user from JWT"""
        try:
            return get_jwt_identity()
        except Exception:
            return None
    
    def login_required(self, f):
        """Decorator for login required routes (using flask-jwt-extended)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            
            try:
                verify_jwt_in_request()
                request.user = get_jwt_identity()
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Invalid or missing token', 'details': str(e)}), 401
        
        return decorated_function
    
    def register_user(self, username, password, email=None):
        """Register a new user"""
        if username in self.users:
            return {'success': False, 'error': 'Username already exists'}
        
        if len(password) < 8:
            return {'success': False, 'error': 'Password must be at least 8 characters'}
        
        hashed_password = self.hash_password(password)
        
        self.users[username] = {
            'password': hashed_password,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'message': 'User registered successfully',
            'user': {'username': username, 'email': email}
        }
    
    def login_user(self, username, password):
        """Login a user"""
        user = self.users.get(username)
        
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        if not self.verify_password(password, user['password']):
            return {'success': False, 'error': 'Invalid password'}
        
        # Generate token
        token = self.generate_token(identity=username)
        
        return {
            'success': True,
            'access_token': token,
            'user': {
                'username': username,
                'email': user.get('email')
            }
        }
    
    def get_user(self, username):
        """Get user information"""
        user = self.users.get(username)
        if not user:
            return None
        
        return {
            'username': username,
            'email': user.get('email'),
            'created_at': user.get('created_at')
        }

# Create instance
auth_manager = AuthManager()

# Additional JWT helper functions
def get_token_from_request():
    """Extract token from request"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def is_token_valid(token):
    """Check if token is valid"""
    try:
        from flask_jwt_extended import decode_token
        decode_token(token)
        return True
    except Exception:
        return False

# User management functions (for use with database)
class UserManager:
    """Extended user management with database integration"""
    
    def __init__(self, db=None):
        self.db = db
        self.auth_manager = auth_manager
    
    def create_user(self, username, password, email=None, **kwargs):
        """Create user in database"""
        # Check if user exists
        existing = self._get_user_by_username(username)
        if existing:
            return {'success': False, 'error': 'Username already exists'}
        
        # Hash password
        hashed_password = self.auth_manager.hash_password(password)
        
        # Create user in database
        user_data = {
            'username': username,
            'password': hashed_password,
            'email': email,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        
        # In production, save to database
        self.auth_manager.users[username] = user_data
        
        return {
            'success': True,
            'message': 'User created successfully',
            'user': {'username': username, 'email': email}
        }
    
    def _get_user_by_username(self, username):
        """Get user by username"""
        return self.auth_manager.users.get(username)
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        user = self._get_user_by_username(username)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        if not self.auth_manager.verify_password(password, user['password']):
            return {'success': False, 'error': 'Invalid password'}
        
        return {
            'success': True,
            'user': user
        }
    
    def update_user(self, username, **updates):
        """Update user information"""
        user = self._get_user_by_username(username)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Update user data
        for key, value in updates.items():
            if key != 'password' and key != 'username':
                user[key] = value
        
        return {
            'success': True,
            'message': 'User updated successfully',
            'user': user
        }
    
    def delete_user(self, username):
        """Delete user"""
        if username in self.auth_manager.users:
            del self.auth_manager.users[username]
            return {'success': True, 'message': 'User deleted successfully'}
        
        return {'success': False, 'error': 'User not found'}

# Create user manager instance
user_manager = UserManager()

# Convenience functions for Flask routes
def get_current_user_identity():
    """Get current user identity from JWT"""
    try:
        from flask_jwt_extended import get_jwt_identity
        return get_jwt_identity()
    except:
        return None

def require_auth(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'details': str(e)}), 401
    return decorated

def optional_auth(f):
    """Decorator for routes that optionally require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request(optional=True)
            request.user = get_jwt_identity()
        except:
            request.user = None
        return f(*args, **kwargs)
    return decorated

# Test function
if __name__ == "__main__":
    # Test the auth manager
    print("Testing Auth Manager...")
    
    # Register a user
    result = auth_manager.register_user("testuser", "password123", "test@email.com")
    print(f"Register: {result}")
    
    # Login
    result = auth_manager.login_user("testuser", "password123")
    print(f"Login: {result}")
    
    # Get user info
    user = auth_manager.get_user("testuser")
    print(f"User: {user}")