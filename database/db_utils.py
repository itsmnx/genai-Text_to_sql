# database/db_utils.py
"""
Database utility functions
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
import hashlib
import secrets

class DatabaseUtils:
    """Database utility functions"""
    
    @staticmethod
    @contextmanager
    def get_connection(db_path=None):
        """Get database connection with context manager"""
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'database/company.db')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
        finally:
            conn.close()
    
    @staticmethod
    def dict_factory(cursor, row):
        """Convert row to dictionary"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    @staticmethod
    def execute_query(conn, query, params=None):
        """Execute a query and return results"""
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def execute_many(conn, query, params_list):
        """Execute many queries"""
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
    
    @staticmethod
    def generate_session_id():
        """Generate a secure session ID"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token):
        """Hash a token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def save_session(conn, user_id, session_id, expires_in_hours=24):
        """Save a session"""
        from datetime import datetime, timedelta
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (session_id, user_id, expires_at)
            VALUES (?, ?, ?)
            """,
            (session_id, user_id, expires_at)
        )
        conn.commit()
        return session_id
    
    @staticmethod
    def get_session(conn, session_id):
        """Get a session"""
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM sessions
            WHERE session_id = ? AND expires_at > datetime('now')
            """,
            (session_id,)
        )
        return cursor.fetchone()
    
    @staticmethod
    def delete_session(conn, session_id):
        """Delete a session"""
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        conn.commit()
    
    @staticmethod
    def cleanup_expired_sessions(conn):
        """Delete expired sessions"""
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM sessions WHERE expires_at <= datetime('now')"
        )
        conn.commit()
        return cursor.rowcount

# Create instance for easy import
db_utils = DatabaseUtils()

# Convenience functions
get_db = db_utils.get_connection
execute_query = db_utils.execute_query
save_session = db_utils.save_session