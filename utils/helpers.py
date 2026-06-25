# utils/helpers.py
from datetime import datetime
import json
import os

def format_timestamp(dt=None):
    """Format timestamp for API responses"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()

def safe_json_loads(data, default=None):
    """Safely load JSON data"""
    try:
        return json.loads(data) if data else default
    except:
        return default

def get_env(key, default=None):
    """Get environment variable with default"""
    return os.getenv(key, default)

def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def truncate_text(text, max_length=200):
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

def extract_numbers(text):
    """Extract all numbers from text"""
    import re
    return re.findall(r'\d+', text)

def extract_keywords(text, min_length=3):
    """Extract keywords from text"""
    import re
    # Remove punctuation and split
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter by min length and remove common stopwords
    stopwords = {'the', 'a', 'an', 'of', 'for', 'on', 'at', 'to', 'in', 'with', 
                 'without', 'and', 'or', 'but', 'is', 'are', 'was', 'were'}
    return [w for w in words if len(w) >= min_length and w not in stopwords]

def format_sql(sql):
    """Format SQL query"""
    try:
        import sqlparse
        return sqlparse.format(sql, reindent=True, keyword_case='upper')
    except:
        return sql