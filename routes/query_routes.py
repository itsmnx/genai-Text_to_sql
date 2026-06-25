# routes/query_routes.py - COMPLETE FIXED VERSION
from flask import Blueprint, request, jsonify
from datetime import datetime
import sqlparse
import os
import re

from utils.schema_discovery import schema_discovery
from auth.auth import optional_auth, get_current_user_identity

# Import agents
from agents.query_agent import query_agent
from agents.explanation_agent import explanation_agent
from agents.optimizer_agent import optimizer_agent
from agents.security_agent import security_agent
from agents.impact_agent import impact_agent

# Try to import Groq
try:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    HAS_GROQ = True
    print("✅ Groq AI initialized")
except Exception as e:
    HAS_GROQ = False
    print(f"⚠️ Groq not available: {e}")

query_bp = Blueprint('query', __name__, url_prefix='/api')

def clean_sql(sql):
    """Clean SQL query - remove syntax errors"""
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
    
    # Remove trailing semicolon if it's the last character (but keep if it's needed)
    sql = sql.strip()
    if sql.endswith(';'):
        # Check if it's a valid semicolon at the end of a statement
        if not sql.rstrip(';').strip().upper().endswith('LIMIT'):
            sql = sql.rstrip(';')
    
    # Fix any remaining issues
    sql = re.sub(r';\s*$', '', sql)  # Remove trailing semicolon
    sql = re.sub(r';\s+LIMIT', ' LIMIT', sql, flags=re.IGNORECASE)  # Fix ; LIMIT
    
    return sql

def detect_unknown_tables(query):
    """Check if query mentions tables not in discovered schema"""
    query_lower = query.lower()
    known_tables = schema_discovery.get_table_names()
    
    for table in known_tables:
        if table in query_lower:
            return False
    
    all_columns = schema_discovery.get_all_columns()
    for table, columns in all_columns.items():
        for col in columns:
            if col in query_lower:
                return False
    
    return True

def get_relevant_tables(query):
    """Find which tables might be relevant to the query"""
    query_lower = query.lower()
    relevant = []
    
    for table in schema_discovery.get_table_names():
        if table in query_lower:
            relevant.append(table)
        else:
            schema = schema_discovery.get_table_schema(table)
            if schema:
                for col in schema['columns']:
                    if col in query_lower:
                        relevant.append(table)
                        break
    
    return relevant if relevant else schema_discovery.get_table_names()[:3]

def generate_sample_results(sql):
    """Generate sample results based on SQL query"""
    if not sql:
        return {'columns': ['message'], 'data': [{'message': 'No results to display'}], 'rowCount': 1}
    
    sql_lower = sql.lower()
    columns = ['id', 'name', 'email']
    data = []
    
    # Detect what kind of query it is
    if 'employee' in sql_lower or 'employees' in sql_lower:
        columns = ['id', 'name', 'email', 'department', 'position', 'hire_date', 'salary']
        data = [
            {'id': 1, 'name': 'John Doe', 'email': 'john.doe@company.com', 'department': 'Engineering', 'position': 'Senior Developer', 'hire_date': '2026-05-15', 'salary': 85000},
            {'id': 2, 'name': 'Jane Smith', 'email': 'jane.smith@company.com', 'department': 'Sales', 'position': 'Sales Manager', 'hire_date': '2026-05-20', 'salary': 78000},
            {'id': 3, 'name': 'Bob Johnson', 'email': 'bob.johnson@company.com', 'department': 'Marketing', 'position': 'Marketing Lead', 'hire_date': '2026-06-01', 'salary': 72000},
            {'id': 4, 'name': 'Alice Brown', 'email': 'alice.brown@company.com', 'department': 'Engineering', 'position': 'Developer', 'hire_date': '2026-06-10', 'salary': 65000},
            {'id': 5, 'name': 'Charlie Wilson', 'email': 'charlie.wilson@company.com', 'department': 'Sales', 'position': 'Sales Rep', 'hire_date': '2026-06-15', 'salary': 58000}
        ]
    elif 'customer' in sql_lower:
        columns = ['id', 'name', 'email', 'city', 'country', 'total_spent']
        data = [
            {'id': 1, 'name': 'Acme Corp', 'email': 'info@acme.com', 'city': 'New York', 'country': 'USA', 'total_spent': 25000},
            {'id': 2, 'name': 'TechStart Inc', 'email': 'contact@techstart.com', 'city': 'San Francisco', 'country': 'USA', 'total_spent': 18000},
            {'id': 3, 'name': 'Global Solutions', 'email': 'hello@globalsolutions.com', 'city': 'London', 'country': 'UK', 'total_spent': 32000}
        ]
    elif 'order' in sql_lower:
        columns = ['order_id', 'customer_id', 'order_date', 'total_amount', 'status']
        data = [
            {'order_id': 1001, 'customer_id': 1, 'order_date': '2026-06-20', 'total_amount': 1250.00, 'status': 'Completed'},
            {'order_id': 1002, 'customer_id': 2, 'order_date': '2026-06-21', 'total_amount': 850.50, 'status': 'Processing'},
            {'order_id': 1003, 'customer_id': 3, 'order_date': '2026-06-22', 'total_amount': 2100.75, 'status': 'Completed'}
        ]
    elif 'product' in sql_lower:
        columns = ['product_id', 'name', 'category', 'price', 'stock_quantity']
        data = [
            {'product_id': 1, 'name': 'Laptop Pro', 'category': 'Electronics', 'price': 1299.99, 'stock_quantity': 45},
            {'product_id': 2, 'name': 'Wireless Mouse', 'category': 'Accessories', 'price': 29.99, 'stock_quantity': 120},
            {'product_id': 3, 'name': 'USB-C Hub', 'category': 'Accessories', 'price': 49.99, 'stock_quantity': 78}
        ]
    elif 'train' in sql_lower or 'test' in sql_lower or 'validation' in sql_lower:
        columns = ['id', 'context', 'question', 'answer']
        data = [
            {'id': 1, 'context': 'Machine learning is a subset of AI that enables systems to learn from data.', 'question': 'What is machine learning?', 'answer': 'A subset of AI that learns from data'},
            {'id': 2, 'context': 'Python is a popular programming language for data science and web development.', 'question': 'Which language is popular for data science?', 'answer': 'Python'},
            {'id': 3, 'context': 'Data science combines statistics, mathematics, and computing to extract insights.', 'question': 'What does data science combine?', 'answer': 'Statistics and computing'},
            {'id': 4, 'context': 'Artificial Intelligence (AI) simulates human intelligence in machines.', 'question': 'What does AI simulate?', 'answer': 'Human intelligence'},
            {'id': 5, 'context': 'Natural Language Processing (NLP) enables machines to understand human language.', 'question': 'What does NLP enable?', 'answer': 'Understanding human language'}
        ]
    elif 'count' in sql_lower or 'sum' in sql_lower or 'avg' in sql_lower:
        columns = ['metric', 'value']
        data = [
            {'metric': 'Total Records', 'value': 1247},
            {'metric': 'Average Value', 'value': 453.72},
            {'metric': 'Sum Total', 'value': 462387.50}
        ]
    else:
        columns = ['id', 'name', 'created_at']
        data = [
            {'id': 1, 'name': 'Record 1', 'created_at': '2026-06-20 10:30:00'},
            {'id': 2, 'name': 'Record 2', 'created_at': '2026-06-21 14:15:00'},
            {'id': 3, 'name': 'Record 3', 'created_at': '2026-06-22 09:45:00'}
        ]
    
    # Limit to 5 rows
    data = data[:5]
    
    return {
        'columns': columns,
        'data': data,
        'rowCount': len(data)
    }

@query_bp.route('/query', methods=['POST'])
@optional_auth
def process_query():
    """Process natural language query with dynamic schema"""
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        current_user = get_current_user_identity() if hasattr(request, 'user') and request.user else 'guest'
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"📝 Processing query: {user_query}")
        print(f"👤 User: {current_user}")
        print(f"{'='*60}")
        
        # Get discovered schema
        known_tables = schema_discovery.get_table_names()
        print(f"📊 Known tables: {known_tables}")
        
        # Check for unknown tables using simple keyword matching
        query_lower = user_query.lower()
        unknown_keywords = ['employee', 'staff', 'worker', 'hire', 'salary', 'department', 'manager', 'candidate']
        has_unknown = any(keyword in query_lower for keyword in unknown_keywords)
        
        print(f"🔍 Unknown keyword detected: {has_unknown}")
        
        # FORCE GROQ if unknown keywords found
        if has_unknown and HAS_GROQ:
            print("🔄 Unknown keyword detected - FORCING Groq...")
            
            # Build schema context
            schema_context = schema_discovery.generate_schema_context()
            
            # Enhanced prompt for unknown tables
            prompt = f"""
            You are a SQL expert. The user is asking about something that might not be in the schema.

            {schema_context}

            User Query: "{user_query}"

            Important: If this query mentions a table that is NOT in the schema above (like employees, staff, etc.), 
            GENERATE THE QUERY ANYWAY assuming the table exists with standard columns.

            Rules:
            1. If the table doesn't exist in schema, assume it exists with appropriate columns
            2. Use standard column names for the table
            3. For employees, use columns like: id, name, email, department, position, hire_date, salary
            4. Use DATE_SUB(CURDATE(), INTERVAL N DAY) for date ranges
            5. Do NOT put a semicolon (;) before LIMIT. Use "LIMIT 100" directly
            6. Return ONLY the SQL query, no explanation

            Generate SQL for: "{user_query}"
            """
            
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert SQL developer. Generate clean SQL queries without syntax errors."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                
                sql = response.choices[0].message.content.strip()
                sql = sql.replace('```sql', '').replace('```', '').strip()
                
                # Clean the SQL
                sql = clean_sql(sql)
                
                if sql:
                    print("✅ Groq generated SQL for unknown table")
                    return format_response(user_query, sql, 'groq', current_user)
                else:
                    print("⚠️ Groq returned empty response")
                    
            except Exception as e:
                print(f"❌ Groq API error: {e}")
                import traceback
                traceback.print_exc()
        
        # Try ML
        from agents.ml_query_agent import ml_query_agent
        if ml_query_agent and ml_query_agent.is_trained:
            try:
                X = ml_query_agent.vectorizer.transform([user_query])
                probs = ml_query_agent.model.predict_proba(X)
                confidence = max(probs[0])
                print(f"📊 ML confidence: {confidence:.2%}")
                
                if confidence > 0.5:
                    sql = ml_query_agent.predict(user_query)
                    if sql:
                        sql = clean_sql(sql)
                        print(f"✅ ML generated SQL")
                        return format_response(user_query, sql, 'ml', current_user)
            except Exception as e:
                print(f"⚠️ ML error: {e}")
        
        # Try Groq as fallback for anything else
        if HAS_GROQ:
            print("🔄 Trying Groq fallback...")
            schema_context = schema_discovery.generate_schema_context()
            prompt = f"""
            {schema_context}
            
            Convert this to SQL: "{user_query}"
            
            Rules:
            1. Do NOT put a semicolon (;) before LIMIT
            2. Return ONLY the SQL query
            
            Generate SQL for: "{user_query}"
            """
            
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a SQL expert. Generate clean SQL queries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                
                sql = response.choices[0].message.content.strip()
                sql = sql.replace('```sql', '').replace('```', '').strip()
                sql = clean_sql(sql)
                
                if sql:
                    print("✅ Groq fallback generated SQL")
                    return format_response(user_query, sql, 'groq', current_user)
            except Exception as e:
                print(f"❌ Groq fallback error: {e}")
        
        # Ultimate fallback
        print("🔄 Using rule-based fallback")
        sql = query_agent.generate_query(user_query)
        sql = clean_sql(sql)
        return format_response(user_query, sql, 'rule_based', current_user)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def format_response(user_query, sql, method, user):
    """Format the response"""
    explanation = explanation_agent.explain_query(sql)
    security_check = security_agent.check_security(sql)
    impact = impact_agent.analyze_impact(sql)
    optimized_sql = optimizer_agent.optimize(sql)
    
    # Clean the SQL again
    optimized_sql = clean_sql(optimized_sql)
    
    return jsonify({
        'query': user_query,
        'sql': optimized_sql,
        'explanation': explanation,
        'method': method,
        'security_check': security_check,
        'impact': impact,
        'has_groq': HAS_GROQ,
        'user': user,
        'timestamp': datetime.now().isoformat(),
        'discovered_tables': schema_discovery.get_table_names()
    })

@query_bp.route('/groq/status', methods=['GET'])
def groq_status():
    """Check Groq API status"""
    try:
        import os
        api_key = os.getenv('GROQ_API_KEY')
        
        return jsonify({
            'available': HAS_GROQ,
            'api_key_set': bool(api_key),
            'ml_available': True,
            'schema_available': True,
            'message': 'Groq is configured and ready' if HAS_GROQ and api_key else 'Groq not configured or no API key',
            'has_groq': HAS_GROQ
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'api_key_set': False,
            'error': str(e)
        })

@query_bp.route('/status', methods=['GET'])
def full_status():
    """Full system status"""
    try:
        from agents.ml_query_agent import ml_query_agent
        
        return jsonify({
            'groq': {
                'available': HAS_GROQ,
                'api_key_set': bool(os.getenv('GROQ_API_KEY'))
            },
            'ml': {
                'available': ml_query_agent.is_trained if ml_query_agent else False,
                'examples': len(ml_query_agent.query_patterns) if ml_query_agent and ml_query_agent.is_trained else 0
            },
            'schema': {
                'available': True,
                'tables': schema_discovery.get_table_names()
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@query_bp.route('/explain', methods=['POST'])
def explain_query():
    """Explain a SQL query"""
    try:
        data = request.get_json()
        sql = data.get('sql', '')
        
        if not sql:
            return jsonify({'error': 'No SQL provided'}), 400
        
        explanation = explanation_agent.explain_query(sql)
        
        return jsonify({
            'sql': sql,
            'explanation': explanation,
            'formatted_sql': sqlparse.format(sql, reindent=True, keyword_case='upper')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@query_bp.route('/optimize', methods=['POST'])
def optimize_query():
    """Optimize a SQL query"""
    try:
        data = request.get_json()
        sql = data.get('sql', '')
        
        if not sql:
            return jsonify({'error': 'No SQL provided'}), 400
        
        optimized = optimizer_agent.optimize(sql)
        impact = impact_agent.analyze_impact(optimized)
        
        return jsonify({
            'original': sql,
            'optimized': optimized,
            'impact': impact
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@query_bp.route('/security/check', methods=['POST'])
def check_security():
    """Check SQL query security"""
    try:
        data = request.get_json()
        sql = data.get('sql', '')
        
        if not sql:
            return jsonify({'error': 'No SQL provided'}), 400
        
        result = security_agent.check_security(sql)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500