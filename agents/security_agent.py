# agents/security_agent.py
import re

class SecurityAgent:
    """Agent responsible for security checks on SQL queries"""
    
    def __init__(self):
        self.forbidden_patterns = [
            r'drop\s+table',
            r'drop\s+database',
            r'truncate\s+table',
            r'delete\s+from\s+\w+\s+where\s+1\s*=\s*1',
            r'--',
            r';.*;',
            r'union\s+select',
            r'insert\s+into.*values.*\(.*\).*\(.*\)'
        ]
    
    def check_security(self, sql_query):
        """
        Check if query is safe to execute
        """
        if not sql_query:
            return {'safe': False, 'issues': ['Empty query']}
        
        issues = []
        sql_lower = sql_query.lower()
        
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.search(pattern, sql_lower, re.IGNORECASE):
                issues.append(f'Potentially unsafe pattern detected: {pattern}')
        
        # Check for potential SQL injection
        if self._detect_sql_injection(sql_query):
            issues.append('Potential SQL injection detected')
        
        # Check for destructive operations
        if 'drop' in sql_lower or 'truncate' in sql_lower:
            issues.append('Destructive operation detected')
        
        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'sanitized_query': self._sanitize_query(sql_query)
        }
    
    def _detect_sql_injection(self, query):
        """
        Detect potential SQL injection patterns
        """
        injection_patterns = [
            r"'\s*or\s*1\s*=\s*1",
            r"'\s*or\s*true",
            r"'\s*or\s*'x'\s*=\s*'x",
            r"'\s*or\s*'",
            r"\bexec\b",
            r"xp_cmdshell"
        ]
        
        query_lower = query.lower()
        for pattern in injection_patterns:
            if re.search(pattern, query_lower):
                return True
        return False
    
    def _sanitize_query(self, query):
        """
        Basic sanitization of query
        """
        # Remove comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        return query
    
    def validate_input(self, user_input):
        """
        Validate user input for security
        """
        if not user_input:
            return {'valid': False, 'message': 'Input is empty'}
        
        # Check length
        if len(user_input) > 1000:
            return {'valid': False, 'message': 'Input too long'}
        
        # Check for malicious patterns
        malicious_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'alert\('
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return {'valid': False, 'message': 'Potentially malicious input detected'}
        
        return {'valid': True, 'message': 'Input validated successfully'}


# Create instance for import
security_agent = SecurityAgent()