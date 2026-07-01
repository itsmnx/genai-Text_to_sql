# routes/query_routes.py - Updated with fixed SQL cleaning
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
from agents.groq_agent import groq_agent

# Import database for history
from database.db_utils import get_db
from database.models import DatabaseModels

# Try to import Groq directly for fallback
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
    """
    Clean SQL query - remove syntax errors, unwanted date filters, and unnecessary LIMIT
    """
    if not sql:
        return sql
    
    # ============================================
    # 1. REMOVE UNWANTED DATE FILTERS
    #    Only keep date filters if query mentions date keywords
    # ============================================
    date_keywords = ['last 30 days', 'recent', 'today', 'yesterday', 'last month', 'last week']
    has_date_keyword = any(keyword in sql.lower() for keyword in date_keywords)
    
    if not has_date_keyword:
        # Remove date filter patterns
        patterns = [
            r'\s*AND\s+date\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)',
            r'\s*AND\s+created_at\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)',
            r'\s*AND\s+hire_date\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)',
            r'\s*AND\s+order_date\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)',
            r'\s*WHERE\s+date\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)\s+AND',
            r'\s*WHERE\s+date\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)',
            r'\s*WHERE\s+created_at\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)\s+AND',
            r'\s*WHERE\s+created_at\s*>=\s*DATE_SUB\(CURDATE\(\), INTERVAL \d+ DAY\)',
        ]
        for pattern in patterns:
            sql = re.sub(pattern, '', sql, flags=re.IGNORECASE)
        
        # Fix: Remove empty WHERE clauses
        sql = re.sub(r'\s*WHERE\s+AND\s+', ' WHERE ', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\s*WHERE\s*$', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\s*WHERE\s+ORDER BY\s+', ' ORDER BY ', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\s*WHERE\s+LIMIT\s+', ' LIMIT ', sql, flags=re.IGNORECASE)
        
        print(f"🧹 Removed automatic date filter (no date mention in query)")
    
    # ============================================
    # 2. REMOVE UNNECESSARY LIMIT FROM AGGREGATIONS
    # ============================================
    sql_lower = sql.lower()
    aggregation_keywords = ['count(', 'sum(', 'avg(', 'max(', 'min(']
    has_aggregation = any(keyword in sql_lower for keyword in aggregation_keywords)
    
    if has_aggregation:
        sql = re.sub(r'\s+LIMIT\s+\d+', '', sql, flags=re.IGNORECASE)
        print(f"🧹 Removed LIMIT from aggregation query")
    
    # ============================================
    # 3. FIX SEMICOLON AND LIMIT ISSUES
    # ============================================
    # Fix semicolon before LIMIT
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
    
    sql = re.sub(r';\s*$', '', sql)
    sql = re.sub(r';\s+LIMIT', ' LIMIT', sql, flags=re.IGNORECASE)
    
    return sql


def validate_generated_sql(sql, user_query, current_user):
    """
    Validate generated SQL with multiple layers of security
    """
    # Layer 1: Security check (SQL injection, dangerous operations)
    is_safe, error, sanitized = security_agent.validate_and_block(sql)
    if not is_safe:
        return False, f"Security check failed: {error}", None
    
    # Layer 2: Schema validation - DISABLED for testing
    return True, None, sanitized or sql


def save_query_history(username, natural_query, generated_sql):
    """Save query to history if user is authenticated"""
    if not username or username == 'guest':
        return None
    
    try:
        with get_db() as conn:
            return DatabaseModels.save_query_history(
                conn,
                username,
                natural_query,
                generated_sql
            )
    except Exception as e:
        print(f"⚠️ Failed to save query history: {e}")
        return None


@query_bp.route('/query', methods=['POST'])
@optional_auth
def process_query():
    """Process natural language query"""
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        current_user = get_current_user_identity() if hasattr(request, 'user') and request.user else 'guest'
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        # ============================================
        # STEP 1: Input Validation
        # ============================================
        input_result = security_agent.validate_input(user_query)
        if not input_result['valid']:
            print(f"⚠️ Input validation failed: {input_result['message']}")
            return jsonify({
                'success': False,
                'error': 'Invalid query',
                'message': input_result['message']
            }), 400
        
        user_query = user_query.strip()
        
        print(f"\n{'='*60}")
        print(f"📝 Processing query: {user_query}")
        print(f"👤 User: {current_user}")
        print(f"{'='*60}")
        
        # Get discovered schema
        known_tables = schema_discovery.get_table_names()
        print(f"📊 Known tables: {known_tables}")
        
        generated_sql = None
        method_used = None
        
        # ============================================
        # STEP 2: Try ML Model FIRST (fastest)
        # ============================================
        from agents.ml_query_agent import ml_query_agent
        if ml_query_agent and ml_query_agent.is_trained:
            try:
                X = ml_query_agent.vectorizer.transform([user_query])
                probs = ml_query_agent.model.predict_proba(X)
                confidence = max(probs[0])
                print(f"📊 ML confidence: {confidence:.2%}")
                
                if confidence > 0.4:
                    sql = ml_query_agent.predict(user_query)
                    if sql:
                        sql = clean_sql(sql)
                        is_valid, error, sanitized = validate_generated_sql(sql, user_query, current_user)
                        if is_valid:
                            generated_sql = sanitized or sql
                            method_used = 'ml'
                            print(f"✅ ML generated SQL")
            except Exception as e:
                print(f"⚠️ ML error: {e}")
        
        # ============================================
        # STEP 3: Try GroqAgent
        # ============================================
        if not generated_sql:
            print("🔄 Trying GroqAgent...")
            
            groq_result = groq_agent.generate_sql(user_query)
            
            if groq_result['success']:
                sql = groq_result['sql']
                sql = clean_sql(sql)
                
                is_valid, error, sanitized = validate_generated_sql(sql, user_query, current_user)
                if is_valid:
                    generated_sql = sanitized or sql
                    method_used = groq_result.get('method', 'groq')
                    print(f"✅ GroqAgent generated SQL")
            elif groq_result.get('schema_mismatch'):
                print("⚠️ GroqAgent returned SCHEMA_MISMATCH")
            else:
                print(f"⚠️ GroqAgent failed: {groq_result.get('error')}")
        
        # ============================================
        # STEP 4: Direct Groq API (if GroqAgent failed)
        # ============================================
        if not generated_sql and HAS_GROQ:
            print("🔄 Trying direct Groq API...")
            
            schema_context = """
Database Schema (based on training data):
- train: id, context, question, answer
- test: id, context, question, answer
- validation: id, context, question, answer
- train_split: id, context, question, answer
- query_history: natural_query, sql_query
- department: creation, name, budget_in_billions, num_employees, ranking
- head: name, born_state, age
- country: Name, population, HeadOfState, SurfaceArea
"""
            
            # Build prompt WITHOUT automatic date filter
            prompt = f"""
You are a SQL expert. Generate SQL queries based on the user's request.

{schema_context}

User wants: "{user_query}"

Rules:
1. Use ONLY tables and columns from the schema above
2. DO NOT add date filters unless the user explicitly mentions:
   - "recent", "last 30 days", "today", "yesterday", "last month", "last week"
3. For LIKE queries: WHERE column LIKE '%keyword%'
4. Add LIMIT 100 only for SELECT queries (not for aggregations)
5. For aggregation queries (COUNT, SUM, AVG, MAX, MIN): NO LIMIT
6. Return ONLY the SQL query, no explanation

SQL:
"""
            
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert SQL developer. Generate clean SQL queries. DO NOT add date filters unless the user explicitly mentions time-related keywords."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                
                sql = response.choices[0].message.content.strip()
                sql = sql.replace('```sql', '').replace('```', '').strip()
                sql = clean_sql(sql)
                
                is_valid, error, sanitized = validate_generated_sql(sql, user_query, current_user)
                if is_valid:
                    generated_sql = sanitized or sql
                    method_used = 'groq_direct'
                    print(f"✅ Direct Groq generated SQL")
                else:
                    print(f"⚠️ Direct Groq validation failed: {error}")
                    
            except Exception as e:
                print(f"❌ Direct Groq error: {e}")
        
        # ============================================
        # STEP 5: Rule-based Fallback
        # ============================================
        if not generated_sql:
            print("🔄 Using rule-based fallback")
            sql = query_agent.generate_query(user_query)
            sql = clean_sql(sql)
            
            is_valid, error, sanitized = validate_generated_sql(sql, user_query, current_user)
            if is_valid:
                generated_sql = sanitized or sql
                method_used = 'rule_based'
                print(f"✅ Rule-based generated SQL")
        
        if not generated_sql:
            return jsonify({
                'success': False,
                'error': 'Failed to generate SQL',
                'message': 'No valid SQL could be generated for your query.'
            }), 400
        
        # ============================================
        # STEP 6: Save to History
        # ============================================
        if current_user and current_user != 'guest':
            save_query_history(current_user, user_query, generated_sql)
            print(f"💾 Query saved to history for user: {current_user}")
        
        # ============================================
        # STEP 7: Return Response
        # ============================================
        return format_response(user_query, generated_sql, method_used or 'unknown', current_user)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'Something went wrong. Please try again.'
        }), 500


def format_response(user_query, sql, method, user):
    """Format the response"""
    explanation = explanation_agent.explain_query(sql)
    security_check = security_agent.check_security(sql)
    impact = impact_agent.analyze_impact(sql)
    optimized_sql = optimizer_agent.optimize(sql)
    
    optimized_sql = clean_sql(optimized_sql)
    
    return jsonify({
        'success': True,
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
        api_key = os.getenv('GROQ_API_KEY')
        has_groq = bool(api_key)
        
        return jsonify({
            'available': has_groq,
            'api_key_set': has_groq,
            'ml_available': True,
            'schema_available': True,
            'message': 'Groq is configured and ready' if has_groq else 'Groq not configured or no API key',
            'has_groq': has_groq
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
                'available': bool(os.getenv('GROQ_API_KEY')),
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