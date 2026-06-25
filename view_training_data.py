# view_training_data.py
import pandas as pd
import os

def view_training_data():
    """View the actual training examples"""
    data_file = 'data/query_history.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        print(f"📊 Total training examples: {len(df)}")
        print("\n" + "="*70)
        print("First 10 Examples:")
        print("="*70)
        
        for i, row in df.head(10).iterrows():
            print(f"\nExample {i+1}:")
            print(f"  Natural Query: {row['natural_query']}")
            print(f"  SQL Query:     {row['sql_query']}")
            print("-" * 50)
        
        if len(df) > 10:
            print(f"\n... and {len(df) - 10} more examples")
            
        print("\n" + "="*70)
        print("All Examples Summary:")
        print("="*70)
        for i, row in df.iterrows():
            print(f"{i+1}. {row['natural_query']}")
            
    else:
        print("❌ No training data found!")

if __name__ == "__main__":
    view_training_data()