# tests/test_history.py
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_jwt_extended import JWTManager
from database.db_utils import get_db
from database.init_db import init_db
from database.models import DatabaseModels
from routes.history_routes import history_bp


class HistoryTestCase(unittest.TestCase):
    """Test query history functionality"""
    
    def setUp(self):
        """Set up test environment with JWTManager"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.app.config['SECRET_KEY'] = 'test-secret-key-32-bytes-long-here!!!'
        self.app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-32-bytes-long-here!!!'
        
        # Initialize JWTManager
        self.jwt = JWTManager(self.app)
        
        self.app.register_blueprint(history_bp)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            init_db()
            self._create_test_user()
            self._clear_history()  # ← FIXED: Clear history before each test
    
    def _create_test_user(self):
        """Create a test user"""
        from auth.auth import auth_manager
        result = auth_manager.register_user('testuser', 'password123', 'test@example.com')
        # Make sure user was created
        self.assertTrue(result['success'], "Test user creation failed")
    
    def _clear_history(self):
        """Clear all history before each test"""
        with get_db() as conn:
            DatabaseModels.clear_history(conn)
    
    def _get_token(self):
        """Get JWT token for test user"""
        from auth.auth import auth_manager
        result = auth_manager.login_user('testuser', 'password123')
        self.assertTrue(result['success'], "Login failed")
        return result['access_token']
    
    def test_save_query_history_authenticated(self):
        """Test saving query history for authenticated user"""
        from routes.history_routes import save_query_history
        
        # First clear any existing history
        self._clear_history()
        
        with self.app.app_context():
            save_query_history(
                username='testuser',
                natural_query='Show me all customers',
                generated_sql='SELECT * FROM customers'
            )
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM query_history WHERE username = 'testuser'"
                )
                results = cursor.fetchall()
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['natural_query'], 'Show me all customers')
    
    def test_get_history_authenticated(self):
        """Test getting history for authenticated user"""
        from routes.history_routes import save_query_history
        
        # First clear any existing history
        self._clear_history()
        
        with self.app.app_context():
            save_query_history('testuser', 'Query 1', 'SELECT 1')
            save_query_history('testuser', 'Query 2', 'SELECT 2')
            
            token = self._get_token()
            response = self.client.get('/api/history', headers={
                'Authorization': f'Bearer {token}'
            })
            
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['history']), 2)
            # Check ordering (newest first)
            self.assertEqual(data['history'][0]['natural_query'], 'Query 2')
            self.assertEqual(data['history'][1]['natural_query'], 'Query 1')
    
    def test_guest_query_not_saved(self):
        """Test guest queries are not saved to history"""
        from routes.history_routes import save_query_history
        
        # First clear any existing history
        self._clear_history()
        
        with self.app.app_context():
            save_query_history(
                username=None,
                natural_query='Guest query',
                generated_sql='SELECT * FROM guest'
            )
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM query_history WHERE username IS NULL")
                results = cursor.fetchall()
                self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()