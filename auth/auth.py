# auth/auth.py - Complete rewrite with SQLite persistence
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
from flask import request, jsonify

# Import database utilities
from database.db_utils import get_db
from database.models import DatabaseModels


def _row_to_dict(row):
    """Convert sqlite3.Row to dict"""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


class AuthManager:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'dev-secret-key')
        self.access_expires = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))
    
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
    
    def register_user(self, username, password, email=None, auto_login=False):
        """
        Register a new user in SQLite
        
        Args:
            username: User's username
            password: User's password
            email: User's email (optional)
            auto_login: Whether to auto-login after registration
        
        Returns:
            dict: Success/failure with user data and optional token
        """
        # Validation
        if not username or len(username) < 3:
            return {'success': False, 'error': 'Username must be at least 3 characters'}
        
        if len(password) < 8:
            return {'success': False, 'error': 'Password must be at least 8 characters'}
        
        with get_db() as conn:
            # Check if username exists
            existing = DatabaseModels.get_user_by_username(conn, username)
            if existing:
                return {'success': False, 'error': 'Username already exists'}
            
            # Check if email exists (if provided)
            if email:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE email = ?",
                    (email,)
                )
                if cursor.fetchone():
                    return {'success': False, 'error': 'Email already registered'}
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user
            user_id = DatabaseModels.create_user(
                conn, 
                username, 
                hashed_password, 
                email
            )
            
            # Get created user
            user = DatabaseModels.get_user_by_id(conn, user_id)
            user_dict = _row_to_dict(user)
            
            # Handle missing created_at
            created_at = user_dict.get('created_at')
            if created_at is None:
                created_at = datetime.now().isoformat()
            
            result = {
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user_dict['id'],
                    'username': user_dict['username'],
                    'email': user_dict.get('email'),
                    'created_at': created_at
                }
            }
            
            # Auto-login if requested
            if auto_login:
                token = self.generate_token(identity=username)
                result['access_token'] = token
            
            return result
    
    def login_user(self, username, password):
        """
        Login a user from SQLite
        
        Args:
            username: User's username
            password: User's password
        
        Returns:
            dict: Success/failure with user data and token
        """
        try:
            with get_db() as conn:
                # Get user
                user = DatabaseModels.get_user_by_username(conn, username)
                
                if not user:
                    return {'success': False, 'error': 'User not found'}
                
                user_dict = _row_to_dict(user)
                
                if not self.verify_password(password, user_dict.get('password_hash')):
                    return {'success': False, 'error': 'Invalid password'}
                
                # Generate token
                token = self.generate_token(identity=username)
                
                # Handle missing created_at
                created_at = user_dict.get('created_at')
                if created_at is None:
                    created_at = datetime.now().isoformat()
                
                return {
                    'success': True,
                    'access_token': token,
                    'user': {
                        'id': user_dict.get('id'),
                        'username': user_dict.get('username'),
                        'email': user_dict.get('email'),
                        'created_at': created_at
                    }
                }
        except Exception as e:
            print(f"❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def get_user(self, username):
        """
        Get user information from SQLite
        
        Args:
            username: User's username
        
        Returns:
            dict: User information or None
        """
        with get_db() as conn:
            user = DatabaseModels.get_user_by_username(conn, username)
            if not user:
                return None
            
            user_dict = _row_to_dict(user)
            
            # Handle missing created_at
            created_at = user_dict.get('created_at')
            if created_at is None:
                created_at = datetime.now().isoformat()
            
            return {
                'id': user_dict.get('id'),
                'username': user_dict.get('username'),
                'email': user_dict.get('email'),
                'created_at': created_at
            }
    
    def get_user_by_id(self, user_id):
        """
        Get user by id from SQLite
        
        Args:
            user_id: User's ID
        
        Returns:
            dict: User information or None
        """
        with get_db() as conn:
            user = DatabaseModels.get_user_by_id(conn, user_id)
            if not user:
                return None
            
            user_dict = _row_to_dict(user)
            
            # Handle missing created_at
            created_at = user_dict.get('created_at')
            if created_at is None:
                created_at = datetime.now().isoformat()
            
            return {
                'id': user_dict.get('id'),
                'username': user_dict.get('username'),
                'email': user_dict.get('email'),
                'created_at': created_at
            }
    
    def update_user(self, username, **updates):
        """
        Update user information
        
        Args:
            username: User's username
            **updates: Fields to update (email, etc.)
        
        Returns:
            dict: Success/failure with updated user data
        """
        with get_db() as conn:
            user = DatabaseModels.get_user_by_username(conn, username)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            cursor = conn.cursor()
            
            # Build update query
            allowed_fields = ['email']
            update_fields = []
            values = []
            
            for field in allowed_fields:
                if field in updates:
                    update_fields.append(f"{field} = ?")
                    values.append(updates[field])
            
            if not update_fields:
                return {'success': False, 'error': 'No valid fields to update'}
            
            values.append(username)
            
            cursor.execute(
                f"UPDATE users SET {', '.join(update_fields)} WHERE username = ?",
                values
            )
            conn.commit()
            
            # Get updated user
            updated_user = DatabaseModels.get_user_by_username(conn, username)
            user_dict = _row_to_dict(updated_user)
            
            # Handle missing created_at
            created_at = user_dict.get('created_at')
            if created_at is None:
                created_at = datetime.now().isoformat()
            
            return {
                'success': True,
                'message': 'User updated successfully',
                'user': {
                    'id': user_dict.get('id'),
                    'username': user_dict.get('username'),
                    'email': user_dict.get('email'),
                    'created_at': created_at
                }
            }
    
    def delete_user(self, username):
        """
        Delete a user
        
        Args:
            username: User's username
        
        Returns:
            dict: Success/failure
        """
        with get_db() as conn:
            user = DatabaseModels.get_user_by_username(conn, username)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM users WHERE username = ?",
                (username,)
            )
            conn.commit()
            
            return {
                'success': True,
                'message': 'User deleted successfully'
            }

# Create instance
auth_manager = AuthManager()

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
    print("=" * 60)
    print("Testing Auth Manager with SQLite...")
    print("=" * 60)
    
    # Register a user
    print("\n1. Registering user...")
    result = auth_manager.register_user("testuser", "password123", "test@email.com")
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   User: {result['user']}")
    
    # Try to register duplicate
    print("\n2. Registering duplicate user...")
    result = auth_manager.register_user("testuser", "password123", "test@email.com")
    print(f"   Result: {result['success']}")
    print(f"   Error: {result.get('error', 'None')}")
    
    # Login
    print("\n3. Logging in...")
    result = auth_manager.login_user("testuser", "password123")
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   User: {result['user']}")
        print(f"   Token: {result['access_token'][:50]}...")
    
    # Login with wrong password
    print("\n4. Logging in with wrong password...")
    result = auth_manager.login_user("testuser", "wrongpass")
    print(f"   Result: {result['success']}")
    print(f"   Error: {result.get('error', 'None')}")
    
    # Get user
    print("\n5. Getting user info...")
    user = auth_manager.get_user("testuser")
    print(f"   User: {user}")
    
    # Update user
    print("\n6. Updating user email...")
    result = auth_manager.update_user("testuser", email="updated@email.com")
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Updated User: {result['user']}")
    
    print("\n" + "=" * 60)
    print("✅ Auth Manager test complete!")
    print("=" * 60)