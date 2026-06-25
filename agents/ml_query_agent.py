# agents/ml_query_agent.py - Updated with better error handling
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from typing import Optional

class MLQueryAgent:
    """Machine Learning-based query generation"""
    
    def __init__(self, model_path='models/'):
        self.model_path = model_path
        self.vectorizer = None
        self.model = None
        self.query_patterns = []
        self.sql_patterns = []
        self.is_trained = False
        
        # Try to load existing model
        self._load_model()
        
        # If no model, try to train
        if not self.is_trained:
            self._try_train()
    
    def _load_model(self):
        """Load saved model if exists"""
        try:
            vectorizer_path = os.path.join(self.model_path, 'vectorizer.pkl')
            model_path = os.path.join(self.model_path, 'text_to_sql_model.pkl')
            
            if os.path.exists(vectorizer_path) and os.path.exists(model_path):
                self.vectorizer = joblib.load(vectorizer_path)
                self.model = joblib.load(model_path)
                self.is_trained = True
                print("✅ Loaded existing ML model")
                return True
            else:
                print("ℹ️ No trained model found. Will train if data available.")
                return False
        except Exception as e:
            print(f"⚠️ Could not load model: {e}")
            return False
    
    def _try_train(self):
        """Try to train on available data"""
        data_file = 'data/query_history.csv'
        
        if not os.path.exists(data_file):
            # Try to create training data from existing CSVs
            self._create_training_data_from_csv()
            data_file = 'data/query_history.csv'
        
        if os.path.exists(data_file):
            self.train(data_file)
        else:
            print("ℹ️ No training data available. ML agent disabled.")
            self.is_trained = False
    
    def _create_training_data_from_csv(self):
        """Create training data from existing CSV files"""
        try:
            data_dir = 'data/'
            training_data = []
            
            # Look for CSV files
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and f != 'query_history.csv']
            
            for csv_file in csv_files[:3]:  # Use first 3 CSV files
                filepath = os.path.join(data_dir, csv_file)
                df = pd.read_csv(filepath)
                columns = df.columns.tolist()
                table_name = csv_file.replace('.csv', '')
                
                # Generate training examples from this CSV
                # 1. SELECT examples
                training_data.append({
                    'natural_query': f"Show me all {table_name}",
                    'sql_query': f"SELECT * FROM {table_name} LIMIT 100"
                })
                training_data.append({
                    'natural_query': f"Get data from {table_name}",
                    'sql_query': f"SELECT * FROM {table_name} LIMIT 100"
                })
                
                # 2. Column-specific examples
                for col in columns[:3]:
                    training_data.append({
                        'natural_query': f"Show {col} from {table_name}",
                        'sql_query': f"SELECT {col} FROM {table_name} LIMIT 100"
                    })
                
                # 3. Aggregation examples (if numeric columns exist)
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                for col in numeric_cols[:2]:
                    training_data.append({
                        'natural_query': f"Sum of {col} in {table_name}",
                        'sql_query': f"SELECT SUM({col}) FROM {table_name}"
                    })
                    training_data.append({
                        'natural_query': f"Average {col} in {table_name}",
                        'sql_query': f"SELECT AVG({col}) FROM {table_name}"
                    })
                
                # 4. Filter examples (if categorical columns exist)
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                for col in categorical_cols[:2]:
                    training_data.append({
                        'natural_query': f"Count by {col} in {table_name}",
                        'sql_query': f"SELECT {col}, COUNT(*) FROM {table_name} GROUP BY {col}"
                    })
            
            if training_data:
                df = pd.DataFrame(training_data)
                df.to_csv('data/query_history.csv', index=False)
                print(f"✅ Created {len(training_data)} training examples from CSV files")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"⚠️ Could not create training data: {e}")
            return False
    
    def train(self, data_file='data/query_history.csv'):
        """
        Train the ML model on query history
        """
        if not os.path.exists(data_file):
            print(f"ℹ️ Training data not found at {data_file}. Skipping ML training.")
            return False
        
        try:
            # Load training data
            df = pd.read_csv(data_file)
            
            if len(df) < 5:
                print(f"ℹ️ Not enough training data (need at least 5 examples). Have {len(df)}.")
                return False
            
            # Extract features
            queries = df['natural_query'].tolist()
            sqls = df['sql_query'].tolist()
            
            # Convert SQL to labels
            labels = self._sql_to_labels(sqls)
            
            # Create TF-IDF vectors
            self.vectorizer = TfidfVectorizer(
                max_features=1000,  # Reduced for speed
                ngram_range=(1, 2),
                stop_words='english'
            )
            X = self.vectorizer.fit_transform(queries)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=50,  # Reduced for speed
                max_depth=5,
                random_state=42
            )
            self.model.fit(X, labels)
            
            # Save patterns
            self.query_patterns = queries
            self.sql_patterns = sqls
            self.is_trained = True
            
            # Save model
            self._save_model()
            
            print(f"✅ Model trained on {len(queries)} examples")
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return False
    
    def _sql_to_labels(self, sqls):
        """Convert SQL queries to labels"""
        labels = []
        for sql in sqls:
            sql_lower = sql.lower()
            
            if 'select *' in sql_lower and 'join' not in sql_lower:
                if 'where' in sql_lower:
                    labels.append(0)
                else:
                    labels.append(1)
            elif 'join' in sql_lower:
                labels.append(2)
            elif 'avg(' in sql_lower or 'sum(' in sql_lower:
                if 'where' in sql_lower:
                    labels.append(3)
                else:
                    labels.append(4)
            elif 'group by' in sql_lower:
                labels.append(5)
            elif 'order by' in sql_lower:
                labels.append(6)
            else:
                labels.append(7)
            
        return labels
    
    def _save_model(self):
        """Save trained model"""
        try:
            os.makedirs(self.model_path, exist_ok=True)
            
            vectorizer_path = os.path.join(self.model_path, 'vectorizer.pkl')
            model_path = os.path.join(self.model_path, 'text_to_sql_model.pkl')
            
            joblib.dump(self.vectorizer, vectorizer_path)
            joblib.dump(self.model, model_path)
        except Exception as e:
            print(f"⚠️ Could not save model: {e}")
    
    def predict(self, user_query):
        """
        Predict SQL query from natural language
        """
        if not self.is_trained or not self.model:
            return None
        
        try:
            # Transform query
            X = self.vectorizer.transform([user_query])
            
            # Predict label
            label = self.model.predict(X)[0]
            
            # If we have patterns, try to find similar
            if self.query_patterns:
                similarities = cosine_similarity(X, self.vectorizer.transform(self.query_patterns)).flatten()
                best_idx = np.argmax(similarities)
                best_score = similarities[best_idx]
                
                # If very similar, return the exact SQL
                if best_score > 0.8:
                    return self.sql_patterns[best_idx]
            
            # Otherwise generate from template
            return self._generate_from_label(label, user_query)
            
        except Exception as e:
            print(f"⚠️ Prediction failed: {e}")
            return None
    
    def _generate_from_label(self, label, query):
        """Generate SQL from label and query"""
        templates = {
            0: "SELECT * FROM {table} WHERE {condition} LIMIT 100",
            1: "SELECT {columns} FROM {table} LIMIT 100",
            2: "SELECT * FROM {table1} JOIN {table2} ON {join_condition} LIMIT 100",
            3: "SELECT {agg}({column}) FROM {table} WHERE {condition}",
            4: "SELECT {agg}({column}) FROM {table}",
            5: "SELECT {column}, COUNT(*) FROM {table} GROUP BY {column}",
            6: "SELECT * FROM {table} ORDER BY {order_column} LIMIT 100",
            7: "SELECT * FROM {table} LIMIT 100"
        }
        
        # Extract information from query
        query_lower = query.lower()
        table = 'train'
        for t in ['customers', 'orders', 'products', 'order_items']:
            if t in query_lower:
                table = t
                break
        
        template = templates.get(label, templates[1])
        
        # Fill template
        sql = template
        sql = sql.replace('{table}', table)
        sql = sql.replace('{columns}', '*')
        sql = sql.replace('{condition}', '1=1')
        sql = sql.replace('{agg}', 'SUM')
        sql = sql.replace('{table1}', table)
        sql = sql.replace('{table2}', 'orders')
        sql = sql.replace('{join_condition}', f'{table}.id = orders.customer_id')
        sql = sql.replace('{order_column}', 'created_at')
        sql = sql.replace('{column}', 'id')
        
        return sql

# Create instance - won't throw errors if training fails
try:
    ml_query_agent = MLQueryAgent()
except:
    ml_query_agent = None
    print("⚠️ ML Agent initialization failed")