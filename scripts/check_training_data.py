# scripts/check_training_data.py
import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_training_data():
    """Check training data and model status"""
    
    print("="*70)
    print("📊 TRAINING DATA & MODEL STATUS")
    print("="*70)
    
    # 1. Check training data
    data_file = 'data/query_history.csv'
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        print(f"✅ Training data found: {len(df)} examples")
        
        # Show sample
        print("\n📝 Sample Examples:")
        for i in range(min(3, len(df))):
            print(f"\n{i+1}. Natural: {df.iloc[i]['natural_query'][:60]}...")
            print(f"   SQL:     {df.iloc[i]['sql_query'][:60]}...")
    else:
        print("❌ No training data found at data/query_history.csv")
        print("   Run: python training/generate_complete_training_data.py")
        return
    
    # 2. Check model
    model_file = 'models/text_to_sql_model.pkl'
    if os.path.exists(model_file):
        import joblib
        model = joblib.load(model_file)
        print(f"\n✅ Model exists: {type(model).__name__}")
        print(f"   - Trees: {model.n_estimators}")
        print(f"   - Max depth: {model.max_depth}")
        
        # Check if model is up to date
        data_mtime = os.path.getmtime(data_file)
        model_mtime = os.path.getmtime(model_file)
        
        if data_mtime > model_mtime:
            print("\n⚠️ Training data is NEWER than model - RETRAINING RECOMMENDED!")
            print("   Run: python scripts/retrain_model.py")
        else:
            print("\n✅ Model is up to date")
    else:
        print("\n❌ No model found - TRAINING REQUIRED!")
        print("   Run: python scripts/retrain_model.py")
    
    # 3. Check vectorizer
    vectorizer_file = 'models/vectorizer.pkl'
    if os.path.exists(vectorizer_file):
        print("\n✅ Vectorizer exists")
    else:
        print("\n❌ Vectorizer not found")

if __name__ == "__main__":
    check_training_data()