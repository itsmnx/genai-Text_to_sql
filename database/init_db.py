# database/init_db.py - Updated with created_at column fix and customers table
import sqlite3
import os
from datetime import datetime

from database.models import DatabaseModels
from database.db_utils import get_db

def init_db(db_path=None):
    """Initialize database with all tables"""
    if db_path is None:
        db_path = os.getenv('DATABASE_PATH', 'database/company.db')
    
    print(f"🔧 Initializing database: {db_path}")
    
    with get_db(db_path) as conn:
        # Create all tables
        DatabaseModels.create_all_tables(conn)
        
        cursor = conn.cursor()
        
        # ============================================
        # FIX: Check and add created_at column if missing
        # ============================================
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("📝 Adding created_at column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("✅ created_at column added to users table!")
        
        # ============================================
        # FIX: Create customers table if not exists
        # ============================================
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        if not cursor.fetchone():
            print("📝 Creating customers table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    city TEXT,
                    country TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add sample data
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] == 0:
                sample_customers = [
                    ('John Doe', 'john.doe@example.com', 'New York', 'USA'),
                    ('Jane Smith', 'jane.smith@example.com', 'London', 'UK'),
                    ('Bob Johnson', 'bob.johnson@example.com', 'Tokyo', 'Japan'),
                    ('Alice Brown', 'alice.brown@example.com', 'Sydney', 'Australia'),
                    ('Charlie Wilson', 'charlie.wilson@example.com', 'Berlin', 'Germany'),
                    ('Eva Davis', 'eva.davis@example.com', 'Paris', 'France'),
                    ('Frank Miller', 'frank.miller@example.com', 'Toronto', 'Canada'),
                ]
                cursor.executemany(
                    "INSERT INTO customers (name, email, city, country) VALUES (?, ?, ?, ?)",
                    sample_customers
                )
                conn.commit()
                print(f"✅ Added {len(sample_customers)} sample customers")
        
        # ============================================
        # Create indexes for performance
        # ============================================
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_history_username
            ON query_history(username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_history_created
            ON query_history(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_session_id
            ON sessions(session_id)
        """)
        
        # Index for customers table
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customers_name
            ON customers(name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customers_city
            ON customers(city)
        """)
        
        conn.commit()
    
    print("✅ Database initialized successfully")

def get_schema_info(db_path=None):
    """Get database schema information"""
    if db_path is None:
        db_path = os.getenv('DATABASE_PATH', 'database/company.db')
    
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        schema_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema_info[table_name] = [col[1] for col in columns]
        
        return schema_info

def reset_db(db_path=None):
    """Reset database - drop all tables and recreate"""
    if db_path is None:
        db_path = os.getenv('DATABASE_PATH', 'database/company.db')
    
    print(f"⚠️ Resetting database: {db_path}")
    
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Drop all tables
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        conn.commit()
    
    print("✅ Database reset complete")
    init_db(db_path)

def add_customers_table(db_path=None):
    """Add customers table with sample data"""
    if db_path is None:
        db_path = os.getenv('DATABASE_PATH', 'database/company.db')
    
    print(f"📝 Adding customers table to: {db_path}")
    
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                city TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add sample data if empty
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] == 0:
            sample_customers = [
                ('John Doe', 'john.doe@example.com', 'New York', 'USA'),
                ('Jane Smith', 'jane.smith@example.com', 'London', 'UK'),
                ('Bob Johnson', 'bob.johnson@example.com', 'Tokyo', 'Japan'),
                ('Alice Brown', 'alice.brown@example.com', 'Sydney', 'Australia'),
                ('Charlie Wilson', 'charlie.wilson@example.com', 'Berlin', 'Germany'),
                ('Eva Davis', 'eva.davis@example.com', 'Paris', 'France'),
                ('Frank Miller', 'frank.miller@example.com', 'Toronto', 'Canada'),
                ('Grace Lee', 'grace.lee@example.com', 'Seoul', 'South Korea'),
                ('Henry Kim', 'henry.kim@example.com', 'Singapore', 'Singapore'),
                ('Ivy Chen', 'ivy.chen@example.com', 'Shanghai', 'China'),
            ]
            cursor.executemany(
                "INSERT INTO customers (name, email, city, country) VALUES (?, ?, ?, ?)",
                sample_customers
            )
            conn.commit()
            print(f"✅ Added {len(sample_customers)} sample customers")
        else:
            print("✅ Customers table already has data")
    
    print("✅ Customers table ready")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_db()
    elif len(sys.argv) > 1 and sys.argv[1] == '--add-customers':
        add_customers_table()
    else:
        init_db()
        print("\n📊 Schema Info:")
        schema_info = get_schema_info()
        for table, columns in schema_info.items():
            print(f"  📁 {table}: {', '.join(columns)}")
        print("\n💡 To reset database: python database/init_db.py --reset")
        print("💡 To add customers table: python database/init_db.py --add-customers")