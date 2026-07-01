# database/models.py - Complete fixed version
"""
Database models for GenialQuery
"""

import sqlite3
from datetime import datetime

class DatabaseModels:
    """Define all database tables and schemas"""
    
    @staticmethod
    def get_users_table():
        """Users table schema"""
        return """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    @staticmethod
    def get_query_history_table():
        """Query history table schema"""
        return """
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            natural_query TEXT NOT NULL,
            generated_sql TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        )
        """
    
    @staticmethod
    def create_all_tables(conn):
        """Create all tables"""
        cursor = conn.cursor()
        cursor.executescript(f"""
            {DatabaseModels.get_users_table()};
            {DatabaseModels.get_query_history_table()};
        """)
        conn.commit()
    
    # ============================================
    # USER METHODS - FIXED (no created_at in SELECT)
    # ============================================
    
    @staticmethod
    def get_user_by_username(conn, username):
        """Get user by username"""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ?",  # ← FIXED
            (username,)
        )
        return cursor.fetchone()
    
    @staticmethod
    def get_user_by_id(conn, user_id):
        """Get user by id"""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE id = ?",  # ← FIXED
            (user_id,)
        )
        return cursor.fetchone()
    
    @staticmethod
    def create_user(conn, username, password_hash, email=None):
        """Create a new user"""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    
    # ============================================
    # QUERY HISTORY METHODS
    # ============================================
    
    @staticmethod
    def save_query_history(conn, username, natural_query, generated_sql):
        """Save query to history"""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO query_history (username, natural_query, generated_sql)
            VALUES (?, ?, ?)
            """,
            (username, natural_query, generated_sql)
        )
        conn.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_user_history(conn, username, limit=100):
        """Get user's query history"""
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, natural_query, generated_sql, created_at
            FROM query_history
            WHERE username = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (username, limit)
        )
        return cursor.fetchall()
    
    @staticmethod
    def clear_history(conn, username=None):
        """Clear query history"""
        cursor = conn.cursor()
        if username:
            cursor.execute(
                "DELETE FROM query_history WHERE username = ?",
                (username,)
            )
        else:
            cursor.execute("DELETE FROM query_history")
        conn.commit()
        return cursor.rowcount