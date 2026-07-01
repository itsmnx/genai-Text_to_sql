# utils/schema_validator.py
"""
Schema validation for SQL queries
"""

import re
import sqlparse
from typing import Dict, List, Tuple, Set

class SchemaValidator:
    """Validate SQL queries against database schema"""
    
    def __init__(self):
        self.schema = {}
        self._load_schema()
    
    def _load_schema(self):
        """Load schema from database or discovery"""
        try:
            from utils.schema_discovery import schema_discovery
            tables = schema_discovery.get_table_names()
            for table in tables:
                schema_info = schema_discovery.get_table_schema(table)
                if schema_info:
                    self.schema[table] = {
                        'columns': schema_info['columns']
                    }
        except:
            # Fallback to basic schema
            self.schema = {
                'test': {'columns': ['id', 'context', 'question', 'answer']},
                'train': {'columns': ['id', 'context', 'question', 'answer']},
                'validation': {'columns': ['id', 'context', 'question', 'answer']},
                'train_split': {'columns': ['id', 'context', 'question', 'answer']},
                'query_history': {'columns': ['natural_query', 'sql_query']}
            }
    
    def get_tables(self) -> List[str]:
        """Get all table names"""
        return list(self.schema.keys())
    
    def get_columns(self, table: str) -> List[str]:
        """Get columns for a table"""
        if table in self.schema:
            return self.schema[table]['columns']
        return []
    
    def extract_tables(self, sql: str) -> Set[str]:
        """Extract table names from SQL"""
        tables = set()
        sql_upper = sql.upper()
        
        # Find FROM clauses
        from_pattern = r'FROM\s+(\w+)'
        matches = re.findall(from_pattern, sql_upper, re.IGNORECASE)
        tables.update(matches)
        
        # Find JOIN clauses
        join_pattern = r'JOIN\s+(\w+)'
        matches = re.findall(join_pattern, sql_upper, re.IGNORECASE)
        tables.update(matches)
        
        # Find CTE names
        cte_pattern = r'WITH\s+(\w+)\s+AS'
        matches = re.findall(cte_pattern, sql_upper, re.IGNORECASE)
        tables.update(matches)
        
        return tables
    
    def extract_columns(self, sql: str) -> Set[str]:
        """Extract column names from SQL"""
        columns = set()
        
        # Find SELECT columns
        select_pattern = r'SELECT\s+(.+?)\s+FROM'
        match = re.search(select_pattern, sql, re.IGNORECASE | re.DOTALL)
        if match:
            select_part = match.group(1)
            # Split by commas (simple approach)
            parts = select_part.split(',')
            for part in parts:
                # Remove aliases and function calls
                part = part.strip()
                # Check if it's a simple column
                if ' ' in part and ' AS ' in part.upper():
                    # Has alias
                    alias_match = re.search(r'(\w+)\s+AS\s+(\w+)', part, re.IGNORECASE)
                    if alias_match:
                        columns.add(alias_match.group(1))
                elif ' ' in part and ' AS ' not in part.upper():
                    # Might be a function call
                    func_match = re.search(r'(\w+)\((\w+)\)', part, re.IGNORECASE)
                    if func_match:
                        columns.add(func_match.group(2))
                elif not '(' in part and not ')' in part:
                    # Simple column
                    columns.add(part)
        
        # Find WHERE columns
        where_pattern = r'WHERE\s+(.+?)(?:GROUP BY|ORDER BY|LIMIT|$)'
        match = re.search(where_pattern, sql, re.IGNORECASE | re.DOTALL)
        if match:
            where_part = match.group(1)
            col_matches = re.findall(r'(\w+)\s*(?:=|>|<|>=|<=|!=|LIKE)', where_part, re.IGNORECASE)
            columns.update(col_matches)
        
        # Find ORDER BY columns
        order_pattern = r'ORDER BY\s+(.+?)(?:LIMIT|$)'
        match = re.search(order_pattern, sql, re.IGNORECASE | re.DOTALL)
        if match:
            order_part = match.group(1)
            col_matches = re.findall(r'(\w+)\s*(?:ASC|DESC|,)', order_part, re.IGNORECASE)
            columns.update(col_matches)
        
        # Find GROUP BY columns
        group_pattern = r'GROUP BY\s+(.+?)(?:HAVING|ORDER BY|LIMIT|$)'
        match = re.search(group_pattern, sql, re.IGNORECASE | re.DOTALL)
        if match:
            group_part = match.group(1)
            col_matches = re.findall(r'(\w+)', group_part)
            columns.update(col_matches)
        
        return columns
    
    def validate_sql_schema(self, sql: str, schema: Dict = None) -> Dict:
        """
        Validate SQL against schema
        
        Returns:
            {
                'valid': bool,
                'tables_found': list,
                'columns_found': list,
                'invalid_objects': list,
                'errors': list
            }
        """
        if schema is None:
            schema = self.schema
        
        tables = self.extract_tables(sql)
        columns = self.extract_columns(sql)
        
        # Validate tables
        valid_tables = []
        invalid_tables = []
        for table in tables:
            if table in schema:
                valid_tables.append(table)
            else:
                # Check if it's a common SQL keyword
                if table.upper() not in ['AS', 'ON', 'AND', 'OR', 'NOT', 'NULL']:
                    invalid_tables.append(table)
        
        # Validate columns
        valid_columns = []
        invalid_columns = []
        for col in columns:
            if col and col.upper() not in ['AS', 'ON', 'AND', 'OR', 'NOT', 'NULL']:
                # Check if column exists in any table
                found = False
                for table, info in schema.items():
                    if col in info.get('columns', []):
                        found = True
                        break
                if found:
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
            'errors': errors,
            'all_tables': list(tables),
            'all_columns': list(columns)
        }
    
    def is_schema_mismatch(self, sql: str) -> bool:
        """Check if SQL has schema mismatch"""
        result = self.validate_sql_schema(sql)
        return not result['valid']
    
    def get_schema_context(self, query: str) -> str:
        """Get schema context for a query"""
        context = "Database Schema:\n"
        for table, info in self.schema.items():
            context += f"- {table}: {', '.join(info['columns'])}\n"
        return context

# Create instance
schema_validator = SchemaValidator()