# tests/test_agents.py
import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.query_agent import query_agent
from agents.explanation_agent import explanation_agent
from agents.security_agent import security_agent

class TestAgents(unittest.TestCase):
    
    def test_query_agent(self):
        """Test query agent generation"""
        query = "Show me all customers"
        sql = query_agent.generate_query(query)
        self.assertIsNotNone(sql)
        self.assertIn('SELECT', sql.upper())
    
    def test_explanation_agent(self):
        """Test explanation agent"""
        sql = "SELECT * FROM customers"
        explanation = explanation_agent.explain_query(sql)
        self.assertIsNotNone(explanation)
        self.assertIsInstance(explanation, str)
    
    def test_security_agent(self):
        """Test security agent"""
        sql = "SELECT * FROM customers"
        result = security_agent.check_security(sql)
        self.assertTrue(result['safe'])
        
        # Test unsafe query
        unsafe_sql = "DROP TABLE customers"
        result = security_agent.check_security(unsafe_sql)
        self.assertFalse(result['safe'])

if __name__ == '__main__':
    unittest.main()