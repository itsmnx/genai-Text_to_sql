# utils/schema_discovery.py
import os
import pandas as pd
import json
from datetime import datetime
import re

class SchemaDiscovery:
    """Automatically discover schema from CSV files"""
    
    def __init__(self, data_path='data/'):
        self.data_path = data_path
        self.schema = {}
        self.table_info = {}
        self.column_patterns = {}
        self._discover_schema()
    
    def _discover_schema(self):
        """Discover all tables and columns from CSV files"""
        print("🔍 Discovering schema from data files...")
        
        # Get all CSV files
        csv_files = [f for f in os.listdir(self.data_path) if f.endswith('.csv')]
        
        for file in csv_files:
            filepath = os.path.join(self.data_path, file)
            table_name = file.replace('.csv', '')
            
            try:
                df = pd.read_csv(filepath)
                
                # Store schema info
                self.schema[table_name] = {
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.astype(str).to_dict(),
                    'row_count': len(df),
                    'sample_data': df.head(5).to_dict('records')
                }
                
                # Detect column patterns
                self._detect_column_patterns(table_name, df)
                
                # Detect relationships
                self._detect_relationships(table_name, df)
                
                print(f"  ✅ Discovered table: {table_name} ({len(df.columns)} columns, {len(df)} rows)")
                
            except Exception as e:
                print(f"  ❌ Error reading {file}: {e}")
        
        # Save schema to JSON for quick loading
        self._save_schema()
    
    def _detect_column_patterns(self, table_name, df):
        """Detect patterns in columns (dates, IDs, names, etc.)"""
        patterns = {}
        
        for col in df.columns:
            col_lower = col.lower()
            patterns[col] = {
                'type': str(df[col].dtype),
                'is_date': any(word in col_lower for word in ['date', 'time', 'day', 'month', 'year']),
                'is_id': any(word in col_lower for word in ['id', 'key', 'number']),
                'is_name': any(word in col_lower for word in ['name', 'title', 'label']),
                'is_email': 'email' in col_lower,
                'is_amount': any(word in col_lower for word in ['amount', 'price', 'cost', 'salary', 'total']),
                'is_quantity': any(word in col_lower for word in ['quantity', 'count', 'number']),
                'is_status': any(word in col_lower for word in ['status', 'state', 'type', 'category']),
                'sample_values': df[col].dropna().head(3).tolist() if len(df) > 0 else []
            }
        
        self.column_patterns[table_name] = patterns
    
    def _detect_relationships(self, table_name, df):
        """Detect potential relationships between tables"""
        relationships = []
        
        # Look for columns that might be foreign keys
        for col in df.columns:
            col_lower = col.lower()
            if '_id' in col_lower or 'id' in col_lower:
                # Check if this might reference another table
                potential_table = col_lower.replace('_id', '').replace('id', '')
                if potential_table and potential_table in self.schema:
                    relationships.append({
                        'from_table': table_name,
                        'from_column': col,
                        'to_table': potential_table,
                        'to_column': 'id',
                        'type': 'foreign_key'
                    })
        
        if relationships:
            self.schema[table_name]['relationships'] = relationships
    
    def _save_schema(self):
        """Save schema to JSON file for quick loading"""
        schema_file = os.path.join(self.data_path, 'schema_discovery.json')
        with open(schema_file, 'w') as f:
            json.dump(self.schema, f, indent=2, default=str)
        print(f"💾 Schema saved to: {schema_file}")
    
    def get_table_names(self):
        """Get all discovered table names"""
        return list(self.schema.keys())
    
    def get_table_schema(self, table_name):
        """Get schema for a specific table"""
        return self.schema.get(table_name, None)
    
    def get_all_columns(self):
        """Get all columns across all tables"""
        all_columns = {}
        for table, info in self.schema.items():
            all_columns[table] = info['columns']
        return all_columns
    
    def search_columns(self, keyword):
        """Search for columns containing a keyword"""
        results = []
        keyword_lower = keyword.lower()
        for table, info in self.schema.items():
            for col in info['columns']:
                if keyword_lower in col.lower():
                    results.append({
                        'table': table,
                        'column': col,
                        'type': info['dtypes'].get(col, 'unknown')
                    })
        return results
    
    def get_table_summary(self):
        """Get a summary of all tables"""
        summary = {}
        for table, info in self.schema.items():
            summary[table] = {
                'columns': len(info['columns']),
                'rows': info['row_count'],
                'column_names': info['columns'][:5]  # First 5 columns
            }
        return summary
    
    def generate_schema_context(self):
        """Generate a schema context string for Groq"""
        context = "Database Schema:\n"
        for table, info in self.schema.items():
            context += f"\n- {table}: {', '.join(info['columns'])}"
            
            # Add relationships if they exist
            if 'relationships' in info and info['relationships']:
                for rel in info['relationships']:
                    context += f"\n  → {rel['from_column']} references {rel['to_table']}.{rel['to_column']}"
        
        return context

# Create instance
schema_discovery = SchemaDiscovery()