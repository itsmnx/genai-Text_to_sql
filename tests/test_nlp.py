# tests/test_nlp.py
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.nlp_processor import nlp_processor

class TestNLP(unittest.TestCase):
    
    def test_intent_detection(self):
        """Test intent detection"""
        query = "Show me all customers"
        result = nlp_processor.process(query)
        self.assertEqual(result['intent'], 'select')
        
        query2 = "Average order amount"
        result = nlp_processor.process(query2)
        self.assertEqual(result['intent'], 'aggregate')
    
    def test_entity_extraction(self):
        """Test entity extraction"""
        query = "Show customers from New York"
        result = nlp_processor.process(query)
        self.assertIsNotNone(result['entities'])
    
    def test_keyword_extraction(self):
        """Test keyword extraction"""
        query = "Show me all customers"
        result = nlp_processor.process(query)
        self.assertIn('customers', result['keywords'])

if __name__ == '__main__':
    unittest.main()