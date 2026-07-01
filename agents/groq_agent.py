# agents/groq_agent.py - Updated with better prompt
import os
import re
from typing import Dict, List, Optional

# Try to import Groq
try:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    groq_client = None
except Exception as e:
    HAS_GROQ = False
    groq_client = None
    print(f"⚠️ Groq initialization error: {e}")


class GroqAgent:
    """
    Schema-aware Groq agent for SQL generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.schema = {}
        self._load_schema()
    
    def _load_schema(self):
        """Load schema from discovery or fallback"""
        try:
            from utils.schema_discovery import schema_discovery
            tables = schema_discovery.get_table_names()
            for table in tables:
                schema_info = schema_discovery.get_table_schema(table)
                if schema_info:
                    self.schema[table] = {
                        'columns': schema_info['columns']
                    }
            print(f"📊 GroqAgent loaded {len(self.schema)} tables")
        except:
            self.schema = {
                'test': {'columns': ['id', 'context', 'question', 'answer']},
                'train': {'columns': ['id', 'context', 'question', 'answer']},
                'validation': {'columns': ['id', 'context', 'question', 'answer']},
                'train_split': {'columns': ['id', 'context', 'question', 'answer']},
                'query_history': {'columns': ['natural_query', 'sql_query']}
            }
            print("⚠️ GroqAgent using fallback schema")
    
    def set_schema(self, schema: Dict):
        """Set custom schema"""
        self.schema = schema
    
    def get_schema_context(self) -> str:
        """Generate schema context for prompting"""
        context = "Database Schema:\n"
        for table, info in self.schema.items():
            columns = ', '.join(info.get('columns', []))
            context += f"- {table}: {columns}\n"
        return context
    
    def build_schema_prompt(self, user_query: str) -> str:
        """Build schema-aware prompt WITHOUT automatic date filters"""
        schema_context = self.get_schema_context()
        
        prompt = f"""
You are an expert SQL developer. Use ONLY the following tables and columns.

{schema_context}

Important Rules:
1. Use ONLY the tables and columns listed above
2. If the query asks for something that doesn't exist, respond with: SCHEMA_MISMATCH
3. Do NOT invent tables or columns
4. Use standard SQL syntax
5. ONLY add date filters IF the user explicitly mentions:
   - "recent", "last 30 days", "today", "yesterday", "last month", "last week"
6. For LIKE queries, just use: WHERE column LIKE '%keyword%'
7. Do NOT add LIMIT for aggregation queries (COUNT, SUM, AVG, MAX, MIN)
8. Add LIMIT 100 only for SELECT queries
9. Return ONLY the SQL query or SCHEMA_MISMATCH, no explanation

User Query: "{user_query}"

Generate SQL:
"""
        return prompt
    
    def generate_sql(self, user_query: str) -> Dict:
        """Generate SQL using Groq with schema awareness"""
        if not HAS_GROQ or not groq_client:
            return {
                'success': False,
                'sql': None,
                'error': 'Groq not available',
                'method': 'groq_unavailable',
                'schema_mismatch': False
            }
        
        try:
            # Build schema-aware prompt
            prompt = self.build_schema_prompt(user_query)
            
            # Call Groq API
            response = groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert SQL developer. Use ONLY the provided schema. DO NOT add date filters unless the user explicitly mentions time-related keywords like 'recent', 'last 30 days', 'today', 'yesterday', 'last month', 'last week'. For LIKE queries, just use WHERE column LIKE '%keyword%'. Never hallucinate tables or columns."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            raw_response = response.choices[0].message.content.strip()
            
            # Check for schema mismatch
            if 'SCHEMA_MISMATCH' in raw_response.upper():
                return {
                    'success': False,
                    'sql': None,
                    'error': 'The requested tables or columns do not exist in the database.',
                    'method': 'groq_schema_mismatch',
                    'schema_mismatch': True
                }
            
            # Clean the SQL
            sql = raw_response.replace('```sql', '').replace('```', '').strip()
            sql = self._clean_sql(sql)
            
            if not sql:
                return {
                    'success': False,
                    'sql': None,
                    'error': 'Empty response from Groq',
                    'method': 'groq_empty',
                    'schema_mismatch': False
                }
            
            return {
                'success': True,
                'sql': sql,
                'error': None,
                'method': 'groq',
                'schema_mismatch': False
            }
            
        except Exception as e:
            return {
                'success': False,
                'sql': None,
                'error': str(e),
                'method': 'groq_error',
                'schema_mismatch': False
            }
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL query"""
        if not sql:
            return sql
        
        # Remove semicolon before LIMIT
        sql = sql.replace('; LIMIT', ' LIMIT')
        sql = sql.replace(';\nLIMIT', ' LIMIT')
        sql = sql.replace('; \nLIMIT', ' LIMIT')
        sql = sql.replace(';  LIMIT', ' LIMIT')
        
        # Fix multiple semicolons
        while ';;' in sql:
            sql = sql.replace(';;', ';')
        
        # Remove trailing semicolon
        sql = sql.strip()
        if sql.endswith(';'):
            if not sql.rstrip(';').strip().upper().endswith('LIMIT'):
                sql = sql.rstrip(';')
        
        # Fix ; LIMIT
        sql = re.sub(r';\s*$', '', sql)
        sql = re.sub(r';\s+LIMIT', ' LIMIT', sql, flags=re.IGNORECASE)
        
        return sql


# Create instance
groq_agent = GroqAgent()