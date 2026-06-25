# scripts/complete_retrain.py
import os
import sys
import pandas as pd
import joblib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

def complete_retrain():
    """Complete retraining pipeline with full model rebuild"""
    
    print("="*70)
    print("🔄 COMPLETE MODEL RETRAINING PIPELINE")
    print("="*70)
    
    # 1. Check for training data
    data_file = 'data/query_history.csv'
    if not os.path.exists(data_file):
        print("❌ No training data found at:", data_file)
        print("   Run: python training/generate_complete_training_data.py")
        return False
    
    # 2. Load training data
    df = pd.read_csv(data_file)
    print(f"📊 Loaded {len(df)} training examples")
    
    if len(df) < 10:
        print("❌ Not enough training examples (need at least 10)")
        return False
    
    # 3. Import ML agent for label conversion
    from agents.ml_query_agent import ml_query_agent
    
    # 4. Convert SQL to labels
    print("🔄 Converting SQL to labels...")
    labels = ml_query_agent._sql_to_labels(df['sql_query'].tolist())
    
    # 5. Train vectorizer
    print("🔄 Training TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=2000,
        ngram_range=(1, 3),
        stop_words='english'
    )
    X = vectorizer.fit_transform(df['natural_query'].tolist())
    print(f"   - Features: {X.shape[1]}")
    
    # 6. Train model
    print("🔄 Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X, labels)
    
    # 7. Save model
    print("💾 Saving model...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(vectorizer, 'models/vectorizer.pkl')
    joblib.dump(model, 'models/text_to_sql_model.pkl')
    
    # 8. Update ML agent
    ml_query_agent.vectorizer = vectorizer
    ml_query_agent.model = model
    ml_query_agent.query_patterns = df['natural_query'].tolist()
    ml_query_agent.sql_patterns = df['sql_query'].tolist()
    ml_query_agent.is_trained = True
    
    print(f"\n✅ Model retrained successfully!")
    print(f"   - Examples: {len(df)}")
    print(f"   - Features: {X.shape[1]}")
    print(f"   - Trees: {model.n_estimators}")
    print(f"   - Max depth: {model.max_depth}")
    print(f"   - Model saved to: models/")
    
    # 9. Show distribution
    print("\n📊 Training Data Distribution:")
    sql_types = {
        'SELECT': len(df[df['sql_query'].str.contains('SELECT', case=False)]),
        'WHERE': len(df[df['sql_query'].str.contains('WHERE', case=False)]),
        'JOIN': len(df[df['sql_query'].str.contains('JOIN', case=False)]),
        'GROUP BY': len(df[df['sql_query'].str.contains('GROUP BY', case=False)]),
        'HAVING': len(df[df['sql_query'].str.contains('HAVING', case=False)]),
        'ORDER BY': len(df[df['sql_query'].str.contains('ORDER BY', case=False)]),
        'WINDOW': len(df[df['sql_query'].str.contains('OVER', case=False)]),
        'SUBQUERY': len(df[df['sql_query'].str.contains('SELECT.*SELECT', case=False)]),
        'CTE': len(df[df['sql_query'].str.contains('WITH', case=False)]),
        'CASE': len(df[df['sql_query'].str.contains('CASE', case=False)]),
        'DISTINCT': len(df[df['sql_query'].str.contains('DISTINCT', case=False)]),
    }
    
    for qtype, count in sql_types.items():
        if count > 0:
            print(f"  - {qtype}: {count} examples")
    
    return True

if __name__ == "__main__":
    complete_retrain()