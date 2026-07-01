# routes/auth_routes.py - Updated with better error handling
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import traceback

from auth.auth import auth_manager, require_auth, optional_auth, get_current_user_identity
from database.db_utils import get_db
from database.models import DatabaseModels

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        auto_login = data.get('auto_login', False)
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password required'
            }), 400
        
        result = auth_manager.register_user(username, password, email, auto_login)
        
        if result['success']:
            # Set session if auto-login
            if auto_login and result.get('access_token'):
                session['user_id'] = result['user']['id']
                session['username'] = result['user']['username']
                session['email'] = result['user'].get('email')
            
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Registration failed')
            }), 400
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        remember_me = data.get('remember_me', False)
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password required'
            }), 400
        
        result = auth_manager.login_user(username, password)
        
        if result['success']:
            # Set session
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username']
            session['email'] = result['user'].get('email')
            
            # Remember me extends session expiry
            if remember_me:
                session.permanent = True
            
            return jsonify({
                'success': True,
                'access_token': result['access_token'],
                'user': {
                    'id': result['user']['id'],
                    'username': result['user']['username'],
                    'email': result['user'].get('email'),
                    'created_at': result['user'].get('created_at')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Login failed')
            }), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    try:
        # Clear Flask session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    """Get current user information"""
    try:
        current_user = get_current_user_identity()
        
        if not current_user:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        user = auth_manager.get_user(current_user)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user.get('email'),
                'created_at': user.get('created_at')
            }
        })
        
    except Exception as e:
        print(f"❌ Get me error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/session/sync', methods=['POST'])
def sync_session():
    """Sync session state"""
    try:
        # Check if user is in session
        if session.get('user_id'):
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': session['user_id'],
                    'username': session.get('username'),
                    'email': session.get('email')
                }
            })
        
        # Check JWT token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            payload = auth_manager.verify_token(token)
            if payload:
                user = auth_manager.get_user(payload.get('sub'))
                if user:
                    return jsonify({
                        'authenticated': True,
                        'user': user
                    })
        
        return jsonify({
            'authenticated': False,
            'user': None
        })
        
    except Exception as e:
        print(f"❌ Session sync error: {e}")
        return jsonify({
            'authenticated': False,
            'error': 'Session sync failed'
        }), 500

@auth_bp.route('/protected', methods=['GET'])
@require_auth
def protected():
    """Protected route - requires authentication"""
    try:
        current_user = get_current_user_identity()
        return jsonify({
            'success': True,
            'message': f'Hello {current_user}!',
            'user': current_user,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"❌ Protected route error: {e}")
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated (without requiring auth)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            payload = auth_manager.verify_token(token)
            if payload:
                user = auth_manager.get_user(payload.get('sub'))
                if user:
                    return jsonify({
                        'authenticated': True,
                        'user': {
                            'id': user['id'],
                            'username': user['username'],
                            'email': user.get('email')
                        }
                    })
        
        return jsonify({
            'authenticated': False,
            'user': None
        })
        
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'error': str(e)
        }), 500

# Error handler for auth routes
@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 'Unauthorized access'
    }), 401

@auth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 'Forbidden'
    }), 403

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404