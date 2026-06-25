# routes/auth_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from auth.auth import auth_manager, require_auth, optional_auth, get_current_user_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        result = auth_manager.register_user(username, password, email)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        result = auth_manager.login_user(username, password)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/protected', methods=['GET'])
@require_auth
def protected():
    """Protected route - requires authentication"""
    try:
        current_user = get_current_user_identity()
        return jsonify({
            'message': f'Hello {current_user}!',
            'user': current_user,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/optional', methods=['GET'])
@optional_auth
def optional():
    """Optional authentication route"""
    user = request.user if hasattr(request, 'user') else None
    return jsonify({
        'user': user,
        'message': 'This route is optional!',
        'authenticated': user is not None
    })

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info"""
    try:
        current_user = get_current_user_identity()
        user_info = auth_manager.get_user(current_user)
        
        if user_info:
            return jsonify({
                'success': True,
                'user': user_info
            })
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 401