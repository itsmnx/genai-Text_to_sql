# training/evaluate_model.py
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

class ModelEvaluator:
    def __init__(self, model_path='models/'):
        self.model_path = model_path
    
    def evaluate(self, test_data=None):
        """Evaluate the trained model"""
        
        # Load model
        model_path = os.path.join(self.model_path, 'text_to_sql_model.pkl')
        vectorizer_path = os.path.join(self.model_path, 'vectorizer.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
            print("❌ Model not found. Train first!")
            return None
        
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        # Use test data if provided
        if test_data and os.path.exists(test_data):
            df = pd.read_csv(test_data)
            X_test = df['natural_query'].values
            y_test = df['sql_query'].values
        else:
            # Use validation data
            val_file = 'data/validation.csv'
            if os.path.exists(val_file):
                df = pd.read_csv(val_file)
                X_test = df['natural_query'].values
                y_test = df['sql_query'].values
            else:
                print("❌ No test data found")
                return None
        
        # Transform and predict
        X_test_vectors = vectorizer.transform(X_test)
        y_pred = model.predict(X_test_vectors)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 Model Evaluation Results:")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Samples: {len(y_test)}")
        
        return {
            'accuracy': accuracy,
            'samples': len(y_test),
            'predictions': y_pred.tolist()
        }

if __name__ == "__main__":
    evaluator = ModelEvaluator()
    evaluator.evaluate()