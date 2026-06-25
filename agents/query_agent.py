# agents/query_agent.py
import re
import random

class QueryAgent:
    """Agent responsible for generating SQL queries from natural language"""
    
    def __init__(self):
        self.table_schema = {
            'customers': ['id', 'name', 'email', 'city', 'country', 'created_at'],
            'orders': ['id', 'customer_id', 'order_date', 'total_amount', 'status'],
            'products': ['id', 'name', 'category', 'price', 'stock_quantity'],
            'order_items': ['id', 'order_id', 'product_id', 'quantity', 'price']
        }
    
    def generate_query(self, natural_language_query):
        """
        Convert natural language to SQL query
        """
        query_lower = natural_language_query.lower()
        
        # Detect query type and generate appropriate SQL
        if 'select' in query_lower or 'show' in query_lower or 'get' in query_lower:
            return self._generate_select_query(natural_language_query)
        elif 'insert' in query_lower or 'add' in query_lower:
            return self._generate_insert_query(natural_language_query)
        elif 'update' in query_lower or 'modify' in query_lower or 'change' in query_lower:
            return self._generate_update_query(natural_language_query)
        elif 'delete' in query_lower or 'remove' in query_lower:
            return self._generate_delete_query(natural_language_query)
        else:
            return self._generate_complex_query(natural_language_query)
    
    def _generate_select_query(self, query):
        """Generate SELECT queries"""
        query_lower = query.lower()
        
        # Check for JOIN patterns
        if 'join' in query_lower or 'with' in query_lower:
            return self._generate_join_query(query)
        
        # Check for aggregation
        if any(word in query_lower for word in ['sum', 'total', 'average', 'avg', 'count', 'max', 'min']):
            return self._generate_aggregation_query(query)
        
        # Basic SELECT
        if 'customers' in query_lower:
            return self._generate_customer_query(query)
        elif 'order' in query_lower:
            return self._generate_order_query(query)
        elif 'product' in query_lower:
            return self._generate_product_query(query)
        else:
            return self._generate_generic_select(query)
    
    def _generate_customer_query(self, query):
        """Generate customer-related queries"""
        query_lower = query.lower()
        
        sql = "SELECT * FROM customers"
        
        if 'recent' in query_lower or 'last month' in query_lower:
            sql = "SELECT * FROM customers WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        elif 'active' in query_lower:
            sql = "SELECT * FROM customers WHERE status = 'active'"
        elif 'city' in query_lower or 'country' in query_lower:
            # Extract city/country if mentioned
            sql = "SELECT * FROM customers WHERE city = 'New York'"
        elif 'top' in query_lower:
            sql = "SELECT * FROM customers ORDER BY created_at DESC LIMIT 10"
        
        return sql
    
    def _generate_order_query(self, query):
        """Generate order-related queries"""
        query_lower = query.lower()
        
        sql = "SELECT * FROM orders"
        
        if 'recent' in query_lower or 'last month' in query_lower:
            sql = "SELECT * FROM orders WHERE order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        elif 'amount' in query_lower and '>' in query_lower:
            # Extract amount if mentioned
            sql = "SELECT * FROM orders WHERE total_amount > 100"
        elif 'pending' in query_lower:
            sql = "SELECT * FROM orders WHERE status = 'pending'"
        
        return sql
    
    def _generate_product_query(self, query):
        """Generate product-related queries"""
        query_lower = query.lower()
        
        sql = "SELECT * FROM products"
        
        if 'category' in query_lower:
            sql = "SELECT * FROM products WHERE category = 'Electronics'"
        elif 'price' in query_lower and '>' in query_lower:
            sql = "SELECT * FROM products WHERE price > 100"
        elif 'stock' in query_lower or 'inventory' in query_lower:
            sql = "SELECT * FROM products WHERE stock_quantity > 0"
        
        return sql
    
    def _generate_join_query(self, query):
        """Generate JOIN queries"""
        return """
        SELECT 
            c.name as customer_name,
            o.order_date,
            o.total_amount,
            p.name as product_name
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
    
    def _generate_aggregation_query(self, query):
        """Generate aggregation queries"""
        query_lower = query.lower()
        
        if 'customer' in query_lower and 'count' in query_lower:
            return "SELECT COUNT(*) as total_customers FROM customers"
        elif 'order' in query_lower and 'total' in query_lower:
            return "SELECT SUM(total_amount) as total_sales FROM orders"
        elif 'product' in query_lower and 'count' in query_lower:
            return "SELECT COUNT(*) as total_products FROM products"
        elif 'average' in query_lower or 'avg' in query_lower:
            return "SELECT AVG(total_amount) as avg_order_value FROM orders"
        else:
            return "SELECT COUNT(*) as total_records FROM customers"
    
    def _generate_insert_query(self, query):
        """Generate INSERT queries"""
        return """
        INSERT INTO customers (name, email, city, country, created_at)
        VALUES ('John Doe', 'john@example.com', 'New York', 'USA', NOW())
        """
    
    def _generate_update_query(self, query):
        """Generate UPDATE queries"""
        query_lower = query.lower()
        
        if 'customer' in query_lower:
            return "UPDATE customers SET status = 'active' WHERE id = 1"
        elif 'product' in query_lower and 'price' in query_lower:
            return "UPDATE products SET price = price * 1.1 WHERE category = 'Electronics'"
        else:
            return "UPDATE customers SET status = 'active' WHERE id = 1"
    
    def _generate_delete_query(self, query):
        """Generate DELETE queries"""
        return "DELETE FROM customers WHERE id = 1"
    
    def _generate_complex_query(self, query):
        """Generate complex queries for ambiguous inputs"""
        return """
        SELECT 
            c.name,
            COUNT(o.id) as order_count,
            SUM(o.total_amount) as total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id
        ORDER BY total_spent DESC
        LIMIT 10
        """
    
    def _generate_generic_select(self, query):
        """Generate generic SELECT"""
        return "SELECT * FROM customers LIMIT 10"


# Create instance for import
query_agent = QueryAgent()