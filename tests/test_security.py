# tests/test_security.py
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.security_agent import security_agent
from utils.validators import validate_query, validate_sql, sanitize_input


class SecurityTestCase(unittest.TestCase):
    """Test SQL injection prevention and security"""
    
    def test_sql_injection_patterns(self):
        """Test detection of SQL injection patterns"""
        malicious_queries = [
            "DROP TABLE users",
            "DELETE FROM users WHERE 1=1",
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users",
            "admin' --",
            "1; DROP TABLE users",
            "SELECT * FROM users; DROP TABLE users",
        ]
        
        for query in malicious_queries:
            result = validate_query(query)
            self.assertFalse(result['valid'], f"Query should be blocked: {query}")
            # Check for any security-related message
            self.assertIn('potentially malicious', result['message'].lower())
    
    def test_safe_queries(self):
        """Test safe queries are allowed"""
        safe_queries = [
            "Show me all customers",
            "Get orders from last month",
            "Find products with price > 100",
            "Count total sales",
            "Average order value",
        ]
        
        for query in safe_queries:
            result = validate_query(query)
            self.assertTrue(result['valid'], f"Query should be allowed: {query}")
    
    def test_dangerous_sql_keywords(self):
        """Test blocking of dangerous SQL keywords"""
        dangerous_sqls = [
            "DROP TABLE users",
            "DELETE FROM users",
            "TRUNCATE TABLE orders",
            "ALTER TABLE users",
            "CREATE TABLE new",
            "INSERT INTO users",
            "UPDATE users SET",
        ]
        
        for sql in dangerous_sqls:
            result = validate_sql(sql)
            self.assertFalse(result['valid'], f"Should block: {sql}")
            self.assertIn('Dangerous operation', result['message'])
    
    def test_allowed_sql_operations(self):
        """Test allowed SQL operations"""
        allowed_queries = [
            "SELECT * FROM users",
            "SELECT name, age FROM users WHERE id = 1",
            "SELECT COUNT(*) FROM orders",
            "SELECT DISTINCT city FROM customers",
            "SELECT * FROM users ORDER BY name",
            "SELECT * FROM users GROUP BY city",
            "SELECT * FROM users LIMIT 10",
        ]
        
        for sql in allowed_queries:
            result = validate_sql(sql)
            self.assertTrue(result['valid'], f"Query should be allowed: {sql}")
    
    def test_security_agent_blocking(self):
        """Test SecurityAgent enforces blocking"""
        dangerous_sql = "DROP TABLE users"
        result = security_agent.check_security(dangerous_sql)
        
        self.assertFalse(result['safe'])
        self.assertIn('issues', result)
        self.assertGreater(len(result['issues']), 0)
    
    def test_sanitize_input(self):
        """Test input sanitization removes XSS"""
        dirty_input = "<script>alert('xss')</script>"
        sanitized = sanitize_input(dirty_input)
        
        # Should remove script tags completely
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('</script>', sanitized)
        self.assertNotIn('alert', sanitized)
        self.assertNotIn('xss', sanitized)
    
    def test_validate_sql_safe(self):
        """Test SQL validation for safe queries"""
        safe_sql = "SELECT * FROM users WHERE id = 1"
        result = validate_sql(safe_sql)
        self.assertTrue(result['valid'])
    
    def test_validate_sql_delete_without_where(self):
        """Test DELETE without WHERE is blocked"""
        dangerous_sql = "DELETE FROM users"
        result = validate_sql(dangerous_sql)
        self.assertFalse(result['valid'])
        self.assertIn('Dangerous operation', result['message'])


if __name__ == '__main__':
    unittest.main()