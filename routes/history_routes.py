# routes/history_routes.py
"""
Query history routes
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from auth.auth import require_auth, get_current_user_identity
from database.db_utils import get_db
from database.models import DatabaseModels

history_bp = Blueprint('history', __name__, url_prefix='/api')

@history_bp.route('/history', methods=['GET'])
@require_auth
def get_history():
    """Get user's query history"""
    try:
        current_user = get_current_user_identity()
        limit = request.args.get('limit', 100, type=int)
        
        with get_db() as conn:
            history = DatabaseModels.get_user_history(conn, current_user, limit)
        
        return jsonify({
            'success': True,
            'history': [dict(row) for row in history],
            'count': len(history)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_query_history(username, natural_query, generated_sql):
    """Save query to history (called from query_routes)"""
    if not username:
        return None  # Don't save for guests
    
    try:
        with get_db() as conn:
            return DatabaseModels.save_query_history(
                conn,
                username,
                natural_query,
                generated_sql
            )
    except Exception as e:
        # Don't fail the request if history save fails
        print(f"⚠️ Failed to save query history: {e}")
        return None

@history_bp.route('/history/clear', methods=['POST'])
@require_auth
def clear_history():
    """Clear user's query history"""
    try:
        current_user = get_current_user_identity()
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM query_history WHERE username = ?",
                (current_user,)
            )
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'History cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@history_bp.route('/history/<int:history_id>', methods=['DELETE'])
@require_auth
def delete_history_item(history_id):
    """Delete a specific history item"""
    try:
        current_user = get_current_user_identity()
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM query_history WHERE id = ? AND username = ?",
                (history_id, current_user)
            )
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'History item not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'History item deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500