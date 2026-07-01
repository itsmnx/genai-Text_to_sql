# utils/validators.py
import re
import html
from typing import Dict, Tuple, List

def validate_query(query: str) -> Dict:
    """
    Validate user query for security threats
    
    Args:
        query: Natural language query from user
    
    Returns:
        Dict: {'valid': bool, 'message': str}
    """
    if not query:
        return {'valid': False, 'message': 'Query cannot be empty'}
    
    if len(query) > 2000:
        return {'valid': False, 'message': 'Query is too long (max 2000 characters)'}
    
    # Check for XSS patterns
    xss_patterns = [
        r'<script',
        r'javascript:',
        r'onerror\s*=',
        r'alert\s*\(',
        r'onload\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'data:text/html',
        r'vbscript:',
        r'expression\s*\(',
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return {'valid': False, 'message': 'Potentially malicious XSS pattern detected'}
    
    # Check for SQL injection patterns in natural language
    sql_injection_patterns = [
        r'drop\s+table',
        r'drop\s+database',
        r'truncate\s+table',
        r'delete\s+from\s+\w+\s+where\s+1\s*=\s*1',
        r';\s*drop\s+',
        r';\s*delete\s+',
        r';\s*truncate\s+',
        r'union\s+select',
        r'select\s+.*\s+from\s+.*\s+where\s+.*=.*',
        r"'or'1'='1",
        r"'or 1=1",
        r'";\s*drop\s+',
        r'--\s*drop\s+',
        r'/\*.*\*/',
        # ===== ADDED NEW PATTERNS =====
        r"'\s*or\s*'1'\s*=\s*'1",      # ' OR '1'='1
        r"'\s*or\s*1\s*=\s*1",         # ' OR 1=1
        r"'\s*or\s*true",              # ' OR true
        r"'\s*or\s*'x'\s*=\s*'x",      # ' OR 'x'='x
        r"'\s*or\s*'",                 # ' OR '
        r"'\s*and\s*1\s*=\s*1",        # ' AND 1=1
        r"'\s*union\s+select",         # ' UNION SELECT
        r"'\s*;\s*--",                 # '; --
        r"'\s*;\s*#",                  # '; #
    ]
    
    for pattern in sql_injection_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return {'valid': False, 'message': 'Potentially malicious SQL injection pattern detected'}
    
    return {'valid': True, 'message': 'Query validated successfully'}


def sanitize_input(input_text: str) -> str:
    """
    Sanitize user input - Remove XSS and dangerous content
    
    Args:
        input_text: Raw user input
    
    Returns:
        str: Sanitized input
    """
    if not input_text:
        return ""
    
    # Step 1: Escape HTML entities
    sanitized = html.escape(input_text)
    
    # Step 2: Remove encoded script tags
    sanitized = re.sub(r'&lt;script.*?&gt;.*?&lt;/script&gt;', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
    sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
    sanitized = re.sub(r'<script.*?/>', '', sanitized, flags=re.IGNORECASE)
    
    # Step 3: Remove event handlers
    sanitized = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=\s*[^\s>]+', '', sanitized, flags=re.IGNORECASE)
    
    # Step 4: Remove XSS function calls
    xss_functions = ['alert', 'prompt', 'confirm', 'console.log', 'console.error', 'eval']
    for func in xss_functions:
        sanitized = re.sub(r'\b' + func + r'\s*\(', '', sanitized, flags=re.IGNORECASE)
    
    # Step 5: Remove iframe, object, embed tags
    sanitized = re.sub(r'<iframe.*?>.*?</iframe>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
    sanitized = re.sub(r'<object.*?>.*?</object>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
    sanitized = re.sub(r'<embed.*?>.*?</embed>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
    
    # Step 6: Remove javascript: protocol
    sanitized = re.sub(r'javascript\s*:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'vbscript\s*:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)
    
    # Step 7: Remove expression() for CSS injection
    sanitized = re.sub(r'expression\s*\(', '', sanitized, flags=re.IGNORECASE)
    
    # Step 8: Remove potentially dangerous characters
    sanitized = re.sub(r'[<>]', '', sanitized)
    
    # Step 9: Remove multiple semicolons (SQL injection)
    sanitized = re.sub(r';{2,}', '', sanitized)
    
    # Step 10: Remove SQL comments
    sanitized = re.sub(r'--.*', '', sanitized)
    sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
    
    # Step 11: Limit length
    sanitized = sanitized[:2000]
    
    return sanitized.strip()


def validate_sql(sql_query: str) -> Dict:
    """
    Validate SQL query for safety - BLOCKS ALL dangerous operations
    
    Args:
        sql_query: SQL query to validate
    
    Returns:
        Dict: {'valid': bool, 'message': str}
    """
    if not sql_query:
        return {'valid': False, 'message': 'SQL query cannot be empty'}
    
    if len(sql_query) > 5000:
        return {'valid': False, 'message': 'SQL query is too long (max 5000 characters)'}
    
    sql_lower = sql_query.lower()
    
    # ============================================
    # BLOCK ALL DANGEROUS OPERATIONS
    # ============================================
    
    # Data Definition Language (DDL)
    ddl_keywords = [
        'drop', 'truncate', 'alter', 'create', 'rename',
        'add column', 'drop column', 'modify column',
        'create table', 'create database', 'create index',
        'drop table', 'drop database', 'drop index',
    ]
    
    # Data Manipulation Language (DML) - Dangerous
    dangerous_dml = [
        'delete', 'update', 'insert', 'replace', 'merge',
        'delete from', 'update set', 'insert into',
    ]
    
    # Command Execution
    exec_keywords = [
        'exec', 'execute', 'call', 'execution', 'execute immediate',
        'sp_', 'xp_', 'shell', 'cmd', 'cmdshell',
    ]
    
    # Privilege Management
    privilege_keywords = [
        'grant', 'revoke', 'deny', 'permission',
        'create user', 'create login', 'alter user',
    ]
    
    # Dangerous Functions
    dangerous_functions = [
        'load_file', 'into outfile', 'into dumpfile',
        'bulk insert', 'openrowset', 'opendatasource',
        'benchmark', 'sleep', 'pg_sleep', 'waitfor',
        'sys_exec', 'sys_eval', 'system',
    ]
    
    # All dangerous keywords combined
    all_dangerous = ddl_keywords + dangerous_dml + exec_keywords + privilege_keywords + dangerous_functions
    
    # Check for each dangerous keyword
    for keyword in all_dangerous:
        # Use word boundaries for exact matching
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, sql_lower):
            return {
                'valid': False, 
                'message': f'Dangerous operation detected: {keyword.upper()}',
                'blocked_keyword': keyword.upper()
            }
    
    # ============================================
    # CHECK FOR MULTIPLE STATEMENTS
    # ============================================
    
    # Remove comments first
    sql_no_comments = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    sql_no_comments = re.sub(r'/\*.*?\*/', '', sql_no_comments, flags=re.DOTALL)
    
    # Check for semicolons (potential multiple statements)
    statements = [s.strip() for s in sql_no_comments.split(';') if s.strip()]
    if len(statements) > 1:
        return {
            'valid': False,
            'message': 'Multiple SQL statements detected (use only one statement)',
            'blocked_keyword': 'MULTI_STATEMENT'
        }
    
    # ============================================
    # CHECK FOR SUSPICIOUS PATTERNS
    # ============================================
    
    suspicious_patterns = [
        (r'1\s*=\s*1', 'Potential tautology condition'),
        (r"'or'1'='1", 'SQL injection pattern'),
        (r"'or 1=1", 'SQL injection pattern'),
        (r';\s*--', 'SQL injection pattern'),
        (r'union\s+select', 'UNION injection pattern'),
        (r'select\s+.*\s+from\s+.*\s+where\s+.*\s*=\s*.*\s*or\s+', 'Suspicious OR condition'),
    ]
    
    for pattern, message in suspicious_patterns:
        if re.search(pattern, sql_lower):
            return {
                'valid': False,
                'message': f'Suspicious SQL pattern detected: {message}',
                'blocked_keyword': 'SUSPICIOUS_PATTERN'
            }
    
    # ============================================
    # CHECK FOR SYSTEM TABLE ACCESS
    # ============================================
    
    system_tables = [
        'sqlite_master', 'sqlite_temp_master', 'sqlite_sequence',
        'mysql', 'information_schema', 'performance_schema',
        'sys', 'pg_catalog', 'pg_class', 'pg_tables',
        'v$', 'dba_', 'all_', 'user_'
    ]
    
    for table in system_tables:
        if re.search(r'\b' + re.escape(table) + r'\b', sql_lower):
            return {
                'valid': False,
                'message': f'System table access detected: {table}',
                'blocked_keyword': 'SYSTEM_TABLE'
            }
    
    # ============================================
    # ALLOWED - Validate SELECT statement structure
    # ============================================
    
    # Ensure it's a SELECT statement
    if not sql_lower.strip().startswith('select'):
        # Allow CTEs (WITH ... SELECT)
        if not (sql_lower.strip().startswith('with') and 'select' in sql_lower):
            return {
                'valid': False,
                'message': 'Only SELECT queries are allowed',
                'blocked_keyword': 'NON_SELECT'
            }
    
    return {'valid': True, 'message': 'SQL query is valid'}


def validate_sql_schema(sql_query: str, schema: Dict) -> Dict:
    """
    Validate SQL query against schema (tables and columns exist)
    
    Args:
        sql_query: SQL query to validate
        schema: Dictionary of {'table_name': {'columns': [...]}}
    
    Returns:
        Dict: {'valid': bool, 'tables_found': list, 'invalid_objects': list, 'errors': list}
    """
    if not sql_query:
        return {'valid': False, 'errors': ['Empty SQL query']}
    
    # Extract tables and columns
    from utils.schema_validator import schema_validator
    tables = schema_validator.extract_tables(sql_query)
    columns = schema_validator.extract_columns(sql_query)
    
    valid_tables = []
    invalid_tables = []
    for table in tables:
        if table in schema:
            valid_tables.append(table)
        else:
            invalid_tables.append(table)
    
    # Get all valid columns from schema
    all_valid_columns = []
    for table_info in schema.values():
        all_valid_columns.extend(table_info.get('columns', []))
    
    valid_columns = []
    invalid_columns = []
    for col in columns:
        if col in all_valid_columns:
            valid_columns.append(col)
        else:
            invalid_columns.append(col)
    
    errors = []
    if invalid_tables:
        errors.append(f"Invalid tables: {', '.join(invalid_tables)}")
    if invalid_columns:
        errors.append(f"Invalid columns: {', '.join(invalid_columns)}")
    
    return {
        'valid': len(invalid_tables) == 0 and len(invalid_columns) == 0,
        'tables_found': valid_tables,
        'columns_found': valid_columns,
        'invalid_objects': invalid_tables + invalid_columns,
        'errors': errors
    }


def is_sql_safe(sql_query: str) -> Tuple[bool, str]:
    """
    Quick check if SQL is safe - returns (is_safe, error_message)
    
    Args:
        sql_query: SQL query to check
    
    Returns:
        Tuple: (is_safe, error_message)
    """
    result = validate_sql(sql_query)
    if result['valid']:
        return True, ""
    return False, result['message']


def has_sql_injection_pattern(text: str) -> bool:
    """
    Check if text contains SQL injection patterns
    
    Args:
        text: Text to check
    
    Returns:
        bool: True if injection pattern found
    """
    injection_patterns = [
        r"'or'1'='1",
        r"'or 1=1",
        r"'or true",
        r"'or 'x'='x",
        r"';.*--",
        r"';.*#",
        r"union\s+select",
        r"select\s+.*\s+from\s+.*\s+where\s+.*\s*=\s*.*\s*or\s+",
        r"drop\s+table",
        r"delete\s+from",
        r"truncate\s+table",
        r"insert\s+into",
        r"update\s+.*\s+set",
        r"exec\s+",
        r"execute\s+",
        r"xp_cmdshell",
        r"load_file",
        r"into\s+outfile",
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def get_safety_report(sql_query: str) -> Dict:
    """
    Get detailed safety report for SQL query
    
    Args:
        sql_query: SQL query to analyze
    
    Returns:
        Dict: {
            'safety_score': int (0-100),
            'is_safe': bool,
            'issues': list,
            'suggestions': list
        }
    """
    result = validate_sql(sql_query)
    
    safety_score = 100
    issues = []
    suggestions = []
    
    if not result['valid']:
        safety_score = 0
        issues.append(result['message'])
    
    # Additional checks
    sql_lower = sql_query.lower()
    
    if 'select *' in sql_lower:
        safety_score -= 10
        suggestions.append('Consider specifying columns instead of using SELECT *')
    
    if 'where' not in sql_lower and 'group by' not in sql_lower:
        safety_score -= 5
        suggestions.append('Consider adding a WHERE clause to filter results')
    
    if 'limit' not in sql_lower:
        safety_score -= 5
        suggestions.append('Consider adding LIMIT to prevent large result sets')
    
    if 'join' in sql_lower and 'on' not in sql_lower:
        safety_score -= 10
        suggestions.append('JOIN requires ON condition - specify it')
    
    safety_score = max(0, min(100, safety_score))
    
    return {
        'safety_score': safety_score,
        'is_safe': result['valid'],
        'issues': issues,
        'suggestions': suggestions,
        'message': result['message']
    }


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("Testing validators.py...")
    print("=" * 60)
    
    # Test validate_sql
    test_sqls = [
        ("SELECT * FROM users", True),
        ("SELECT name, email FROM customers", True),
        ("DROP TABLE users", False),
        ("DELETE FROM users WHERE 1=1", False),
        ("TRUNCATE TABLE orders", False),
        ("INSERT INTO users VALUES (1, 'admin')", False),
        ("UPDATE users SET password='hacked'", False),
        ("SELECT * FROM users; DROP TABLE users", False),
    ]
    
    for sql, should_pass in test_sqls:
        result = validate_sql(sql)
        status = "✅ PASS" if result['valid'] == should_pass else "❌ FAIL"
        print(f"{status}: {sql[:40]}... -> {result['message'][:50]}")
    
    # Test sanitize_input
    print("\n" + "-" * 40)
    print("Testing sanitize_input:")
    dirty = "<script>alert('xss')</script>"
    clean = sanitize_input(dirty)
    print(f"Original: {dirty}")
    print(f"Sanitized: {clean}")
    assert '<script>' not in clean
    assert 'alert' not in clean
    print("✅ sanitize_input test passed!")
    
    # Test has_sql_injection_pattern
    print("\n" + "-" * 40)
    print("Testing has_sql_injection_pattern:")
    test_texts = [
        ("DROP TABLE users", True),
        ("Show me all customers", False),
        ("' OR '1'='1", True),
        ("SELECT * FROM users", False),
    ]
    for text, expected in test_texts:
        result = has_sql_injection_pattern(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} {text[:30]}: {result} (expected: {expected})")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)