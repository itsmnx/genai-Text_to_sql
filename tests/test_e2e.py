# tests/test_e2e.py
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.init_db import init_db  # ← FIXED

class E2ETestCase(unittest.TestCase):
    """End-to-end tests for complete user flow"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            init_db()
    
    def test_complete_user_flow(self):
        """Test complete user flow: register → login → query → history → logout"""
        
        # 1. Register
        reg_response = self.client.post('/api/register', json={
            'username': 'e2euser',
            'password': 'password123',
            'email': 'e2e@example.com'
        })
        self.assertEqual(reg_response.status_code, 200)
        reg_data = reg_response.get_json()
        self.assertTrue(reg_data['success'])
        
        # 2. Login
        login_response = self.client.post('/api/login', json={
            'username': 'e2euser',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.get_json()
        self.assertTrue(login_data['success'])
        token = login_data['access_token']
        
        # 3. Query
        query_response = self.client.post('/api/query', 
            json={'query': 'Show me all customers'},
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(query_response.status_code, 200)
        query_data = query_response.get_json()
        self.assertIsNotNone(query_data.get('sql'))
        
        # 4. Check history
        history_response = self.client.get('/api/history',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(history_response.status_code, 200)
        history_data = history_response.get_json()
        self.assertTrue(history_data['success'])
        
        # 5. Check /api/me
        me_response = self.client.get('/api/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(me_response.status_code, 200)
        me_data = me_response.get_json()
        self.assertEqual(me_data['user']['username'], 'e2euser')
        
        # 6. Logout
        logout_response = self.client.post('/api/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(logout_response.status_code, 200)

if __name__ == '__main__':
    unittest.main()