# agents/schema_agent.py

class SchemaAgent:
    """Agent responsible for schema-related operations"""
    
    def __init__(self):
        self.schema = {
            'customers': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                    {'name': 'name', 'type': 'VARCHAR(255)', 'nullable': False},
                    {'name': 'email', 'type': 'VARCHAR(255)', 'nullable': False},
                    {'name': 'city', 'type': 'VARCHAR(100)'},
                    {'name': 'country', 'type': 'VARCHAR(100)'},
                    {'name': 'created_at', 'type': 'DATETIME', 'default': 'CURRENT_TIMESTAMP'}
                ]
            },
            'orders': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                    {'name': 'customer_id', 'type': 'INTEGER', 'foreign_key': 'customers.id'},
                    {'name': 'order_date', 'type': 'DATETIME'},
                    {'name': 'total_amount', 'type': 'DECIMAL(10,2)'},
                    {'name': 'status', 'type': 'VARCHAR(50)'}
                ]
            },
            'products': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                    {'name': 'name', 'type': 'VARCHAR(255)'},
                    {'name': 'category', 'type': 'VARCHAR(100)'},
                    {'name': 'price', 'type': 'DECIMAL(10,2)'},
                    {'name': 'stock_quantity', 'type': 'INTEGER'}
                ]
            },
            'order_items': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                    {'name': 'order_id', 'type': 'INTEGER', 'foreign_key': 'orders.id'},
                    {'name': 'product_id', 'type': 'INTEGER', 'foreign_key': 'products.id'},
                    {'name': 'quantity', 'type': 'INTEGER'},
                    {'name': 'price', 'type': 'DECIMAL(10,2)'}
                ]
            }
        }
    
    def get_table_schema(self, table_name):
        """
        Get schema for a specific table
        """
        return self.schema.get(table_name, None)
    
    def get_all_tables(self):
        """
        Get list of all tables
        """
        return list(self.schema.keys())
    
    def get_relationships(self):
        """
        Get table relationships
        """
        relationships = []
        for table, info in self.schema.items():
            for column in info['columns']:
                if 'foreign_key' in column:
                    relationships.append({
                        'from_table': table,
                        'from_column': column['name'],
                        'to_table': column['foreign_key'].split('.')[0],
                        'to_column': column['foreign_key'].split('.')[1]
                    })
        return relationships
    
    def suggest_tables(self, query):
        """
        Suggest which tables might be relevant for a query
        """
        query_lower = query.lower()
        suggested = []
        
        if 'customer' in query_lower:
            suggested.append('customers')
        if 'order' in query_lower:
            suggested.append('orders')
            suggested.append('order_items')
        if 'product' in query_lower:
            suggested.append('products')
            suggested.append('order_items')
        
        return suggested if suggested else ['customers', 'orders', 'products']


# Create instance for import
schema_agent = SchemaAgent()