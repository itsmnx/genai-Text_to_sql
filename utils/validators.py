# utils/validators.py
import re
import html

def validate_query(query):
    """Validate user query"""
    if not query:
        return {'valid': False, 'message': 'Query cannot be empty'}
    
    if len(query) > 2000:
        return {'valid': False, 'message': 'Query is too long (max 2000 characters)'}
    
    # Check for malicious patterns
    malicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'alert\(',
        r'drop\s+table',
        r'drop\s+database',
        r'truncate\s+table'
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return {'valid': False, 'message': f'Potentially unsafe pattern: {pattern}'}
    
    return {'valid': True, 'message': 'Query validated'}

def sanitize_input(input_text):
    """Sanitize user input"""
    # Escape HTML
    sanitized = html.escape(input_text)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>]', '', sanitized)
    
    # Limit length
    sanitized = sanitized[:2000]
    
    return sanitized

def validate_sql(sql_query):
    """Validate SQL query for safety"""
    sql_lower = sql_query.lower()
    
    # Check for dangerous operations
    dangerous_keywords = ['drop', 'truncate', 'delete', 'alter', 'create', 'insert', 'update']
    
    for keyword in dangerous_keywords:
        if keyword in sql_lower:
            # Allow only if not in dangerous context
            if not _is_safe_context(sql_lower, keyword):
                return {'valid': False, 'message': f'Dangerous operation detected: {keyword}'}
    
    return {'valid': True, 'message': 'SQL query is valid'}

def _is_safe_context(sql, keyword):
    """Check if keyword is in a safe context"""
    # Simple safety check - can be expanded
    if keyword == 'delete' and 'delete from' in sql and 'where' not in sql:
        return False
    return True