# agents/security_agent.py - Updated with comprehensive SQL injection prevention
import re
import sqlparse
from typing import Dict, Tuple, List

class SecurityAgent:
    """Agent responsible for security checks and SQL injection prevention on SQL queries"""
    
    def __init__(self):
        # Blocked SQL keywords (destructive operations)
        self.blocked_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
            'INSERT', 'UPDATE', 'REPLACE', 'MERGE', 'EXEC',
            'EXECUTE', 'CALL', 'GRANT', 'REVOKE',
            'INTO OUTFILE', 'INTO DUMPFILE', 'LOAD_FILE'
        ]
        
        # Allowed SQL operations (whitelist)
        self.allowed_keywords = [
            'SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN'
        ]
        
        # SQL injection patterns
        self.injection_patterns = [
            r"'\s*or\s*1\s*=\s*1",           # Classic OR injection
            r"'\s*or\s*true",                 # Boolean OR injection
            r"'\s*or\s*'x'\s*=\s*'x",         # String OR injection
            r"'\s*or\s*'",                    # Incomplete OR injection
            r"'\s*and\s*1\s*=\s*1",           # AND injection
            r"'\s*union\s+select",            # UNION injection
            r"'\s*union\s+all\s+select",      # UNION ALL injection
            r"'\s*;.*--",                     # Terminator + comment
            r"'\s*;.*#",                      # Terminator + comment (MySQL)
            r"'\s*or\s+1=1\s*--",             # OR with comment
            r"'\s*or\s+1=1\s*#",              # OR with comment (MySQL)
            r"\bexec\b",                      # EXEC command
            r"xp_cmdshell",                   # xp_cmdshell (MSSQL)
            r"sp_executesql",                 # sp_executesql (MSSQL)
            r"@@version",                     # Version disclosure
            r"benchmark\s*\(",                # Benchmark injection
            r"sleep\s*\(",                    # Sleep injection (time-based)
            r"waitfor\s+delay",               # WAITFOR DELAY (MSSQL)
            r"pg_sleep\s*\(",                 # pg_sleep (PostgreSQL)
            r"dbms_pipe\.receive_message",    # Oracle injection
            r"user\s*\(\)",                   # User function
            r"database\s*\(\)",               # Database function
            r"version\s*\(\)",                # Version function
        ]
        
        # Suspicious patterns (comment injection, multi-statement, etc.)
        self.suspicious_patterns = [
            r'--',                           # SQL comments
            r'/\*.*\*/',                     # Multi-line comments
            r';.*;',                         # Multiple statements
            r';\s*$',                        # Trailing semicolon
        ]
    
    def check_security(self, sql_query: str) -> Dict:
        """
        Check if query is safe to execute (ENFORCES BLOCKING)
        
        Returns:
            Dict: {
                'safe': bool,
                'issues': List[str],
                'sanitized_query': str or None,
                'is_blocked': bool,
                'block_reason': str or None
            }
        """
        if not sql_query:
            return {
                'safe': False,
                'issues': ['Empty query'],
                'sanitized_query': None,
                'is_blocked': True,
                'block_reason': 'Empty query'
            }
        
        issues = []
        sql_upper = sql_query.upper()
        is_safe = True
        
        # 1. Check for blocked keywords (destructive operations)
        for keyword in self.blocked_keywords:
            if re.search(r'\b' + keyword + r'\b', sql_upper):
                issues.append(f'Blocked operation detected: {keyword}')
                is_safe = False
        
        # 2. Check for SQL injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                issues.append(f'Suspicious SQL injection pattern detected')
                is_safe = False
                break
        
        # 3. Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                # Don't block comments unless they're part of injection
                if pattern != '--' or self._is_comment_injection(sql_query):
                    issues.append(f'Suspicious pattern detected: {pattern}')
                    is_safe = False
        
        # 4. Check for multiple statements
        if self._has_multiple_statements(sql_query):
            issues.append('Multiple SQL statements detected')
            is_safe = False
        
        # 5. Check for allowed operations (whitelist)
        if is_safe and not self._is_allowed_operation(sql_upper):
            # Check if it's a valid SELECT with CTE
            if self._is_valid_select_with_cte(sql_upper):
                pass  # Allow CTEs with SELECT
            else:
                issues.append('Only SELECT/WITH/SHOW/DESCRIBE/EXPLAIN operations are allowed')
                is_safe = False
        
        # 6. Check for dangerous function calls
        if self._has_dangerous_functions(sql_query):
            issues.append('Dangerous function calls detected')
            is_safe = False
        
        # 7. Check for system table access
        if self._accesses_system_tables(sql_query):
            issues.append('Access to system tables detected')
            is_safe = False
        
        return {
            'safe': is_safe,
            'issues': issues,
            'sanitized_query': self._sanitize_query(sql_query) if is_safe else None,
            'is_blocked': not is_safe,
            'block_reason': issues[0] if issues else None
        }
    
    def validate_and_block(self, sql_query: str) -> Tuple[bool, str, str]:
        """
        Validate and block unsafe queries immediately
        
        Returns:
            Tuple: (is_safe, error_message, sanitized_sql)
        """
        result = self.check_security(sql_query)
        
        if not result['safe']:
            return False, result['block_reason'] or 'Unsafe query detected', None
        
        return True, None, result['sanitized_query']
    
    def _has_multiple_statements(self, sql: str) -> bool:
        """Check if SQL contains multiple statements"""
        # Remove comments first
        sql_clean = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)
        
        # Split by semicolon and check
        statements = [s.strip() for s in sql_clean.split(';') if s.strip()]
        return len(statements) > 1
    
    def _is_allowed_operation(self, sql_upper: str) -> bool:
        """Check if operation is allowed"""
        for keyword in self.allowed_keywords:
            if sql_upper.startswith(keyword):
                return True
        return False
    
    def _is_valid_select_with_cte(self, sql_upper: str) -> bool:
        """Check if it's a valid SELECT with CTE"""
        return sql_upper.startswith('WITH') and 'SELECT' in sql_upper
    
    def _is_comment_injection(self, sql: str) -> bool:
        """Check if comment is part of an injection attempt"""
        # Check if comment is followed by dangerous keywords
        patterns = [
            r'--\s*(DROP|DELETE|TRUNCATE|ALTER|CREATE|INSERT|UPDATE|EXEC)',
            r'--\s*(OR|AND)\s+1=1',
            r'--\s*(SELECT|UNION)',
        ]
        for pattern in patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                return True
        return False
    
    def _has_dangerous_functions(self, sql: str) -> bool:
        """Check for dangerous function calls"""
        dangerous_functions = [
            'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE',
            'BENCHMARK', 'SLEEP', 'PG_SLEEP', 'WAITFOR',
            'EXEC', 'EXECUTE', 'XP_CMDSHELL', 'SP_EXECUTESQL'
        ]
        sql_upper = sql.upper()
        for func in dangerous_functions:
            if func in sql_upper:
                return True
        return False
    
    def _accesses_system_tables(self, sql: str) -> bool:
        """Check if SQL accesses system tables"""
        system_tables = [
            'sqlite_master', 'sqlite_temp_master', 'sqlite_sequence',
            'mysql', 'information_schema', 'performance_schema',
            'sys', 'pg_catalog', 'pg_class', 'pg_tables'
        ]
        sql_lower = sql.lower()
        for table in system_tables:
            if table in sql_lower:
                return True
        return False
    
    def _detect_sql_injection(self, query: str) -> bool:
        """Detect potential SQL injection patterns"""
        for pattern in self.injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _sanitize_query(self, query: str) -> str:
        """Basic sanitization of query"""
        # Remove comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        # Remove extra whitespace
        query = ' '.join(query.split())
        return query
    
    def validate_input(self, user_input: str) -> Dict:
        """
        Validate user input for security
        
        Returns:
            Dict: {'valid': bool, 'message': str}
        """
        if not user_input:
            return {'valid': False, 'message': 'Input is empty'}
        
        # Check length (prevent DoS)
        if len(user_input) > 2000:
            return {'valid': False, 'message': 'Input too long (max 2000 characters)'}
        
        # Check for XSS patterns
        xss_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'alert\(',
            r'<iframe',
            r'<img.*onerror',
            r'<body.*onload'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return {'valid': False, 'message': 'Potentially malicious XSS input detected'}
        
        # Check for SQL injection patterns in user input
        injection_patterns = [
            r"'or",
            r"OR\s+1=1",
            r"UNION\s+SELECT",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r";\s*DROP",
            r";\s*DELETE",
            r"SELECT\s+.*\s+FROM",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                # Check if it's actually a SQL command attempt
                if self._is_sql_command_attempt(user_input, pattern):
                    return {'valid': False, 'message': 'Potentially malicious SQL input detected'}
        
        return {'valid': True, 'message': 'Input validated successfully'}
    
    def _is_sql_command_attempt(self, user_input: str, pattern: str) -> bool:
        """Check if the pattern is part of a SQL command attempt"""
        # Check for SQL-like keywords in context
        sql_keywords = ['select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate']
        
        # Check if the input contains SQL-like structure
        has_sql_keyword = any(keyword in user_input.lower() for keyword in sql_keywords)
        has_sql_structure = bool(re.search(r'\b(select|from|where|join|group by|order by)\b', user_input.lower()))
        
        return has_sql_keyword or has_sql_structure
    
    def get_safety_report(self, sql_query: str) -> Dict:
        """
        Get a detailed safety report for a SQL query
        
        Returns:
            Dict: {
                'safety_score': int (0-100),
                'issues_detected': List[str],
                'recommendations': List[str]
            }
        """
        result = self.check_security(sql_query)
        
        safety_score = 100
        recommendations = []
        
        if result['issues']:
            safety_score = max(0, 100 - (len(result['issues']) * 20))
        
        # Generate recommendations
        if 'DROP' in sql_query.upper():
            recommendations.append('Avoid using DROP operations in production')
        if 'DELETE' in sql_query.upper() and 'WHERE' not in sql_query.upper():
            recommendations.append('Always use WHERE clause with DELETE')
        if result['issues'] and 'suspicious' in str(result['issues']):
            recommendations.append('Review query for potential SQL injection patterns')
        
        return {
            'safety_score': safety_score,
            'is_safe': result['safe'],
            'issues_detected': result['issues'],
            'recommendations': recommendations,
            'sanitized_query': result['sanitized_query']
        }

# Create instance for import
security_agent = SecurityAgent()

# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Security Agent...")
    print("=" * 60)
    
    # Test cases
    test_queries = [
        # Safe queries
        ("SELECT * FROM users", True),
        ("WITH cte AS (SELECT 1) SELECT * FROM cte", True),
        ("SELECT name, age FROM customers WHERE city = 'NY'", True),
        ("SELECT COUNT(*) FROM orders", True),
        
        # Blocked queries
        ("DROP TABLE users", False),
        ("DELETE FROM users WHERE 1=1", False),
        ("TRUNCATE TABLE orders", False),
        ("INSERT INTO users VALUES (1, 'admin')", False),
        ("UPDATE users SET password = 'hacked'", False),
        ("ALTER TABLE users ADD COLUMN new_col", False),
        ("CREATE TABLE new_table (id INT)", False),
        
        # SQL injection attempts
        ("SELECT * FROM users WHERE id = '1' OR '1'='1'", False),
        ("SELECT * FROM users WHERE id = 1; DROP TABLE users", False),
        ("SELECT * FROM users WHERE name = 'admin' --", False),
        ("' UNION SELECT * FROM users", False),
        
        # System table access
        ("SELECT * FROM sqlite_master", False),
        ("SELECT * FROM information_schema.tables", False),
    ]
    
    for query, should_be_safe in test_queries:
        result = security_agent.check_security(query)
        status = "✅ SAFE" if result['safe'] else "❌ BLOCKED"
        expected = "✅" if should_be_safe else "❌"
        print(f"\nQuery: {query[:50]}...")
        print(f"  Status: {status} | Expected: {expected}")
        if result['issues']:
            print(f"  Issues: {', '.join(result['issues'][:2])}")
    
    print("\n" + "=" * 60)
    print("✅ Security Agent test complete!")
    print("=" * 60)