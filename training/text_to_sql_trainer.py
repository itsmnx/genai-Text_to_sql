# training/text_to_sql_trainer.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class TextToSQLTrainer:
    def __init__(self, data_path='data/', model_path='models/'):
        self.data_path = data_path
        self.model_path = model_path
        self.vectorizer = None
        self.model = None
    
    def train(self):
        """Train the Text-to-SQL model"""
        
        # Load training data
        data_file = os.path.join(self.data_path, 'query_history.csv')
        
        if not os.path.exists(data_file):
            print("❌ No training data found. Run prepare_training_data.py first.")
            return False
        
        df = pd.read_csv(data_file)
        print(f"📊 Loaded {len(df)} training examples")
        
        # Prepare features and labels
        X = df['natural_query'].values
        y = df['sql_query'].values
        
        # Convert SQL to labels
        y_labels = self._sql_to_labels(y)
        
        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 3),
            stop_words='english'
        )
        X_vectors = self.vectorizer.fit_transform(X)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_vectors, y_labels)
        
        # Evaluate
        y_pred = self.model.predict(X_vectors)
        accuracy = accuracy_score(y_labels, y_pred)
        
        print(f"✅ Model trained with accuracy: {accuracy:.2%}")
        
        # Save model
        self._save_model()
        
        return True
    
    def _sql_to_labels(self, sqls):
        """Convert SQL queries to labels"""
        labels = []
        for sql in sqls:
            sql_lower = sql.lower()
            
            if 'select *' in sql_lower:
                if 'join' in sql_lower:
                    labels.append(2)  # JOIN
                elif 'where' in sql_lower:
                    labels.append(0)  # SELECT with WHERE
                else:
                    labels.append(1)  # SELECT without WHERE
            elif 'avg(' in sql_lower or 'sum(' in sql_lower:
                labels.append(4)  # Aggregation
            elif 'group by' in sql_lower:
                labels.append(5)  # GROUP BY
            elif 'order by' in sql_lower:
                labels.append(6)  # ORDER BY
            elif 'insert' in sql_lower:
                labels.append(7)  # INSERT
            elif 'update' in sql_lower:
                labels.append(8)  # UPDATE
            elif 'delete' in sql_lower:
                labels.append(9)  # DELETE
            else:
                labels.append(1)  # Default SELECT
        
        return labels
    
    def _save_model(self):
        """Save trained model"""
        os.makedirs(self.model_path, exist_ok=True)
        
        vectorizer_path = os.path.join(self.model_path, 'vectorizer.pkl')
        model_path = os.path.join(self.model_path, 'text_to_sql_model.pkl')
        
        joblib.dump(self.vectorizer, vectorizer_path)
        joblib.dump(self.model, model_path)
        
        print(f"💾 Model saved to {self.model_path}")

if __name__ == "__main__":
    trainer = TextToSQLTrainer()
    trainer.train()