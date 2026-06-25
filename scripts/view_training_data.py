# scripts/view_training_data.py
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def view_training_data():
    """View all training examples"""
    
    data_file = 'data/query_history.csv'
    
    if not os.path.exists(data_file):
        print("❌ No training data found at:", data_file)
        return
    
    df = pd.read_csv(data_file)
    
    print("="*70)
    print(f"📊 TOTAL TRAINING EXAMPLES: {len(df)}")
    print("="*70)
    
    # Show all examples
    for i, row in df.iterrows():
        print(f"\n{i+1}. Natural Query: {row['natural_query']}")
        print(f"   SQL Query:     {row['sql_query']}")
        print("-" * 60)
    
    # Show summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total examples: {len(df)}")
    
    # Count by SQL type
    sql_types = {
        'SELECT': len(df[df['sql_query'].str.contains('SELECT', case=False)]),
        'WHERE': len(df[df['sql_query'].str.contains('WHERE', case=False)]),
        'JOIN': len(df[df['sql_query'].str.contains('JOIN', case=False)]),
        'GROUP BY': len(df[df['sql_query'].str.contains('GROUP BY', case=False)]),
        'HAVING': len(df[df['sql_query'].str.contains('HAVING', case=False)]),
        'ORDER BY': len(df[df['sql_query'].str.contains('ORDER BY', case=False)]),
    }
    
    print("\nSQL Type Distribution:")
    for qtype, count in sql_types.items():
        if count > 0:
            print(f"  - {qtype}: {count}")

if __name__ == "__main__":
    view_training_data()