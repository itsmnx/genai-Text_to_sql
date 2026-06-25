# tests/test_text_to_sql.py
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.text_to_sql_engine import text_to_sql_engine

class TestTextToSQL(unittest.TestCase):
    
    def test_sql_generation(self):
        """Test SQL generation"""
        query = "Show me all customers"
        result = text_to_sql_engine.generate_sql(query)
        
        self.assertIsNotNone(result)
        self.assertIn('sql', result)
        self.assertIn('SELECT', result['sql'].upper())
    
    def test_explanation(self):
        """Test query explanation"""
        query = "Show me all customers"
        explanation = text_to_sql_engine.explain(query)
        
        self.assertIsNotNone(explanation)
        self.assertIn('original_query', explanation)
    
    def test_confidence(self):
        """Test confidence scoring"""
        query = "Show me all customers"
        result = text_to_sql_engine.generate_sql(query)
        
        self.assertIn('confidence', result)
        self.assertIsNotNone(result['confidence'])

if __name__ == '__main__':
    unittest.main()