# scripts/retrain_model.py
import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def retrain_model():
    """Retrain the ML model with current training data"""
    
    print("="*70)
    print("🔄 RETRAINING ML MODEL")
    print("="*70)
    
    # 1. Check if training data exists
    if not os.path.exists('data/query_history.csv'):
        print("❌ No training data found at data/query_history.csv")
        print("   Run: python training/generate_complete_training_data.py")
        return False
    
    # 2. Load training data
    df = pd.read_csv('data/query_history.csv')
    print(f"📊 Found {len(df)} training examples")
    
    if len(df) < 10:
        print("❌ Not enough training examples (need at least 10)")
        return False
    
    # 3. Import ML agent and train
    try:
        from agents.ml_query_agent import ml_query_agent
        
        print("🔄 Training model...")
        success = ml_query_agent.train('data/query_history.csv')
        
        if success:
            print(f"\n✅ Model retrained successfully!")
            print(f"📊 Trained on {len(ml_query_agent.query_patterns)} examples")
            print(f"💾 Model saved to: models/")
            return True
        else:
            print("❌ Retraining failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during retraining: {e}")
        return False

if __name__ == "__main__":
    retrain_model()