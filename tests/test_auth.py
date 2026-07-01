# tests/test_auth.py
import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import session
from app import create_app
from database.db_utils import get_db  # ← FIXED
from database.init_db import init_db   # ← FIXED

class AuthTestCase(unittest.TestCase):
    """Test authentication flows"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            init_db()
            self._create_test_user()
    
    def _create_test_user(self):
        """Create a test user for authentication tests"""
        from auth.auth import auth_manager
        auth_manager.register_user('testuser', 'password123', 'test@example.com')
    
    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/register', json={
            'username': 'newuser',
            'password': 'password123',
            'email': 'newuser@example.com'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'newuser')
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        response = self.client.post('/api/register', json={
            'username': 'testuser',
            'password': 'password123',
            'email': 'test2@example.com'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn('Username already exists', data['error'])
    
    def test_register_short_password(self):
        """Test registration with short password"""
        response = self.client.post('/api/register', json={
            'username': 'shortpass',
            'password': '123',
            'email': 'short@example.com'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn('Password must be at least 8 characters', data['error'])
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['access_token'])
        self.assertEqual(data['user']['username'], 'testuser')
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'])
        self.assertIn('Invalid password', data['error'])
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post('/api/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        data= response.get_json()
         # Accept 401 OR 404
        self.assertIn(response.status_code, [401, 404])
        if 'success' in data:
            self.assertFalse(data['success'])
        else:
            self.assertIn('error', data)
        
        
    def test_me_endpoint_authenticated(self):
        """Test /api/me with valid token"""
        login_response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']
        
        response = self.client.get('/api/me', headers={
            'Authorization': f'Bearer {token}'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'testuser')
    
    def test_me_endpoint_unauthenticated(self):
        """Test /api/me without token"""
        response = self.client.get('/api/me')
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_logout(self):
        """Test logout clears session"""
        self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = self.client.post('/api/logout')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Logged out successfully')

if __name__ == '__main__':
    unittest.main()