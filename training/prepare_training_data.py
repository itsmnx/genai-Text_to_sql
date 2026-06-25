# training/prepare_training_data.py
import pandas as pd
import numpy as np
import os

class TrainingDataPreparer:
    def __init__(self, data_path='data/'):
        self.data_path = data_path
    
    def prepare_from_csv(self):
        """Create training data from CSV files"""
        
        # Create synthetic query patterns based on CSV structure
        train_file = os.path.join(self.data_path, 'train.csv')
        
        if not os.path.exists(train_file):
            print("❌ No training data found")
            return None
        
        df = pd.read_csv(train_file)
        columns = df.columns.tolist()
        
        # Generate training examples
        training_data = []
        
        # 1. SELECT queries
        for col in columns[:5]:
            training_data.append({
                'natural_query': f"Show me {col}",
                'sql_query': f"SELECT {col} FROM train LIMIT 100"
            })
            training_data.append({
                'natural_query': f"Get all {col} values",
                'sql_query': f"SELECT {col} FROM train LIMIT 100"
            })
        
        # 2. Filter queries
        for col in columns[:3]:
            training_data.append({
                'natural_query': f"Show {col} where it's not empty",
                'sql_query': f"SELECT * FROM train WHERE {col} IS NOT NULL LIMIT 100"
            })
            training_data.append({
                'natural_query': f"Get {col} for specific records",
                'sql_query': f"SELECT * FROM train WHERE {col} = 'value' LIMIT 100"
            })
        
        # 3. Aggregation queries
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        for col in numeric_cols[:3]:
            training_data.append({
                'natural_query': f"Average of {col}",
                'sql_query': f"SELECT AVG({col}) FROM train"
            })
            training_data.append({
                'natural_query': f"Sum of {col}",
                'sql_query': f"SELECT SUM({col}) FROM train"
            })
            training_data.append({
                'natural_query': f"Total {col}",
                'sql_query': f"SELECT SUM({col}) FROM train"
            })
        
        # 4. Date queries
        date_cols = [col for col in columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_cols:
            training_data.append({
                'natural_query': f"Recent data from {col}",
                'sql_query': f"SELECT * FROM train WHERE {col} >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
            })
            training_data.append({
                'natural_query': f"Last month's {col}",
                'sql_query': f"SELECT * FROM train WHERE {col} >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
            })
        
        # 5. JOIN queries (if multiple tables exist)
        tables = ['customers', 'orders', 'products']
        for i, table1 in enumerate(tables):
            for table2 in tables[i+1:]:
                training_data.append({
                    'natural_query': f"Join {table1} with {table2}",
                    'sql_query': f"SELECT * FROM {table1} JOIN {table2} ON {table1}.id = {table2}.{table1}_id LIMIT 100"
                })
        
        # Save training data
        df_train = pd.DataFrame(training_data)
        df_train.to_csv(os.path.join(self.data_path, 'query_history.csv'), index=False)
        
        print(f"✅ Generated {len(training_data)} training examples")
        return df_train

if __name__ == "__main__":
    preparer = TrainingDataPreparer()
    preparer.prepare_from_csv()