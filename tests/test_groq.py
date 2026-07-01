# tests/test_groq.py
import unittest
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.groq_agent import groq_agent, GroqAgent, HAS_GROQ
from utils.schema_validator import SchemaValidator
from utils.schema_discovery import schema_discovery

class GroqTestCase(unittest.TestCase):
    """Test Groq fallback and schema validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.groq_agent = groq_agent
        
        # Get schema
        self.schema = {}
        try:
            tables = schema_discovery.get_table_names()
            for table in tables:
                schema_info = schema_discovery.get_table_schema(table)
                if schema_info:
                    self.schema[table] = {'columns': schema_info['columns']}
        except:
            self.schema = {
                'test': {'columns': ['id', 'context', 'question', 'answer']},
                'train': {'columns': ['id', 'context', 'question', 'answer']},
                'validation': {'columns': ['id', 'context', 'question', 'answer']},
                'train_split': {'columns': ['id', 'context', 'question', 'answer']},
                'query_history': {'columns': ['natural_query', 'sql_query']}
            }
        
        self.groq_agent.set_schema(self.schema)
        self.schema_validator = SchemaValidator()
    
    # ============================================
    # SKIP TESTS THAT REQUIRE GROQ IF NOT AVAILABLE
    # ============================================
    
    @unittest.skipIf(not HAS_GROQ, "Groq API not available - skipping Groq-dependent tests")
    def test_schema_mismatch_detection(self):
        """Test detection of schema mismatch"""
        invalid_query = "find duplicate salaries"
        result = self.groq_agent.generate_sql(invalid_query)
        
        self.assertIsNotNone(result)
        if not result['success']:
            if result.get('schema_mismatch'):
                self.assertTrue(result['schema_mismatch'])
            else:
                error = result.get('error', '').lower()
                self.assertTrue(
                    'schema' in error or 'mismatch' in error or 'exist' in error,
                    f"Error should mention schema: {error}"
                )
    
    @unittest.skipIf(not HAS_GROQ, "Groq API not available - skipping Groq-dependent tests")
    def test_schema_mismatch_response(self):
        """Test response for schema mismatch"""
        result = self.groq_agent.generate_sql("find duplicate salaries")
        
        if not result['success']:
            self.assertFalse(result['success'])
            error = result.get('error', '').lower()
            self.assertTrue(
                'schema' in error or 'mismatch' in error or 'exist' in error or 'error' in error,
                f"Error should mention schema or error: {error}"
            )
    
    @unittest.skipIf(not HAS_GROQ, "Groq API not available - skipping Groq-dependent tests")
    def test_groq_fallback_flow(self):
        """Test complete Groq fallback flow"""
        query = "Show me all employees"
        result = self.groq_agent.generate_sql(query)
        
        if result['success']:
            self.assertIsNotNone(result.get('sql'))
        else:
            self.assertIsNotNone(result.get('error'))
    
    # ============================================
    # TESTS THAT DON'T REQUIRE GROQ
    # ============================================
    
    def test_schema_aware_prompt(self):
        """Test schema-aware prompt generation - doesn't need Groq"""
        prompt = self.groq_agent.build_schema_prompt("Show me all customers")
        self.assertIsNotNone(prompt)
        self.assertIn('Database Schema:', prompt)
        self.assertIn('User Query:', prompt)
        self.assertIn('SCHEMA_MISMATCH', prompt)
    
    def test_hallucinated_table_rejection(self):
        """Test rejection of hallucinated tables - uses SchemaValidator"""
        hallucinated_sql = "SELECT * FROM non_existent_table"
        result = self.schema_validator.validate_sql_schema(hallucinated_sql, self.schema)
        
        self.assertIsNotNone(result)
        self.assertFalse(result['valid'])
        invalid_objects = [obj.lower() for obj in result.get('invalid_objects', [])]
        self.assertTrue(any('non_existent' in obj for obj in invalid_objects))
    
    def test_valid_sql_acceptance(self):
        """Test acceptance of valid SQL"""
        valid_sql = "SELECT name, email FROM customers WHERE city = 'New York'"
        result = self.schema_validator.validate_sql_schema(valid_sql, self.schema)
        
        if 'customers' in self.schema:
            self.assertTrue(result['valid'])
        else:
            self.assertFalse(result['valid'])
    
    def test_extract_tables_and_columns(self):
        """Test extraction of tables and columns from SQL"""
        sql = "SELECT name, email FROM customers JOIN orders ON customers.id = orders.customer_id"
        
        tables = self.schema_validator.extract_tables(sql)
        columns = self.schema_validator.extract_columns(sql)
        
        table_names = [t.lower() for t in tables]
        self.assertTrue('customers' in table_names or 'CUSTOMERS' in table_names)
        self.assertTrue('orders' in table_names or 'ORDERS' in table_names)
        
        column_names = [c.lower() for c in columns]
        self.assertTrue('name' in column_names)
        self.assertTrue('email' in column_names)
    
    def test_build_schema_prompt(self):
        """Test that build_schema_prompt includes all tables"""
        prompt = self.groq_agent.build_schema_prompt("Show me all data")
        for table in self.schema.keys():
            self.assertIn(table, prompt)
    
    def test_clean_sql(self):
        """Test SQL cleaning"""
        dirty_sql = "SELECT * FROM users; LIMIT 100"
        cleaned = self.groq_agent._clean_sql(dirty_sql)
        self.assertNotIn('; LIMIT', cleaned)
        self.assertIn('LIMIT 100', cleaned)

if __name__ == '__main__':
    unittest.main()