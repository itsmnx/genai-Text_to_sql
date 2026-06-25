# training/generate_synthetic_data.py
import pandas as pd
import random
import os

class SyntheticDataGenerator:
    def __init__(self, data_path='data/'):
        self.data_path = data_path
        
        # Sample data for generating synthetic queries
        self.tables = ['customers', 'orders', 'products', 'order_items']
        self.columns = {
            'customers': ['id', 'name', 'email', 'city', 'country', 'created_at'],
            'orders': ['id', 'customer_id', 'order_date', 'total_amount', 'status'],
            'products': ['id', 'name', 'category', 'price', 'stock_quantity'],
            'order_items': ['id', 'order_id', 'product_id', 'quantity', 'price']
        }
        
        self.conditions = [
            'recent', 'last month', 'last week', 'today',
            'greater than 100', 'less than 50', 'contains',
            'starts with', 'between 10 and 20'
        ]
        
        self.aggregations = ['sum', 'average', 'count', 'max', 'min']
        self.actions = ['show', 'get', 'find', 'list', 'display']
    
    def generate_queries(self, num_samples=1000):
        """Generate synthetic query-SQL pairs"""
        
        queries = []
        sqls = []
        
        for _ in range(num_samples):
            # Randomly choose pattern
            pattern_type = random.choice(['select', 'filter', 'aggregate', 'join'])
            
            if pattern_type == 'select':
                query, sql = self._generate_select()
            elif pattern_type == 'filter':
                query, sql = self._generate_filter()
            elif pattern_type == 'aggregate':
                query, sql = self._generate_aggregate()
            else:
                query, sql = self._generate_join()
            
            queries.append(query)
            sqls.append(sql)
        
        # Create DataFrame
        df = pd.DataFrame({
            'natural_query': queries,
            'sql_query': sqls
        })
        
        # Save to CSV
        output_file = os.path.join(self.data_path, 'synthetic_queries.csv')
        df.to_csv(output_file, index=False)
        
        print(f"✅ Generated {num_samples} synthetic query examples")
        return df
    
    def _generate_select(self):
        """Generate SELECT query"""
        table = random.choice(self.tables)
        action = random.choice(self.actions)
        limit = random.randint(10, 200)
        
        query = f"{action} me all {table}"
        sql = f"SELECT * FROM {table} LIMIT {limit}"
        
        return query, sql
    
    def _generate_filter(self):
        """Generate FILTER query"""
        table = random.choice(self.tables)
        column = random.choice(self.columns[table])
        condition = random.choice(self.conditions)
        
        query = f"Show {table} where {column} is {condition}"
        sql = f"SELECT * FROM {table} WHERE {column} LIKE '%{condition}%' LIMIT 100"
        
        return query, sql
    
    def _generate_aggregate(self):
        """Generate AGGREGATE query"""
        table = random.choice(self.tables)
        agg = random.choice(self.aggregations)
        column = random.choice(self.columns[table])
        
        query = f"{agg} of {column} in {table}"
        sql = f"SELECT {agg.upper()}({column}) FROM {table}"
        
        return query, sql
    
    def _generate_join(self):
        """Generate JOIN query"""
        table1 = random.choice(self.tables)
        table2 = random.choice([t for t in self.tables if t != table1])
        
        query = f"Join {table1} with {table2}"
        sql = f"SELECT * FROM {table1} JOIN {table2} ON {table1}.id = {table2}.{table1[:-1]}_id LIMIT 100"
        
        return query, sql

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.generate_queries(500)