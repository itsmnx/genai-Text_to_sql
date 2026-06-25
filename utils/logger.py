# utils/logger.py
import logging
import os
from datetime import datetime

def setup_logger(name, log_file='logs/app.log'):
    """Setup logger with file and console handlers"""
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_query(user_query, sql_query, intent, method):
    """Log query for analysis"""
    logger = logging.getLogger('query_logger')
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_query': user_query,
        'sql_query': sql_query,
        'intent': intent,
        'method': method
    }
    
    logger.info(f"QUERY: {log_entry}")
    return log_entry