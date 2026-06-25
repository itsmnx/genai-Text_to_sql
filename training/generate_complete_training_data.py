# generate_complete_training_data.py
import pandas as pd
import random
import os
from datetime import datetime, timedelta
import re

class CompleteTrainingDataGenerator:
    """Generate comprehensive training data covering ALL SQL patterns"""
    
    def __init__(self):
        self.tables = ['customers', 'orders', 'products', 'order_items', 
                       'employees', 'departments', 'sales', 'inventory']
        
        self.columns = {
            'customers': ['id', 'name', 'email', 'phone', 'city', 'state', 'country', 
                         'zip_code', 'created_at', 'status', 'segment', 'age', 'gender'],
            'orders': ['id', 'customer_id', 'order_date', 'total_amount', 'discount', 
                      'tax', 'shipping_cost', 'status', 'payment_method', 'delivery_date'],
            'products': ['id', 'name', 'description', 'category', 'sub_category', 
                        'price', 'cost', 'stock_quantity', 'reorder_level', 'supplier_id'],
            'order_items': ['id', 'order_id', 'product_id', 'quantity', 'unit_price', 
                           'discount_applied', 'total_price'],
            'employees': ['id', 'first_name', 'last_name', 'email', 'department_id', 
                         'hire_date', 'salary', 'manager_id', 'performance_rating'],
            'departments': ['id', 'name', 'manager_id', 'budget', 'location'],
            'sales': ['id', 'product_id', 'region', 'sales_rep_id', 'sale_date', 
                     'amount', 'quantity', 'commission'],
            'inventory': ['id', 'product_id', 'warehouse_id', 'quantity', 'last_updated', 
                         'reorder_date']
        }
        
        # Relationships for JOINs
        self.relationships = [
            ('orders', 'customer_id', 'customers', 'id'),
            ('order_items', 'order_id', 'orders', 'id'),
            ('order_items', 'product_id', 'products', 'id'),
            ('employees', 'department_id', 'departments', 'id'),
            ('employees', 'manager_id', 'employees', 'id'),
            ('sales', 'product_id', 'products', 'id'),
            ('sales', 'sales_rep_id', 'employees', 'id'),
            ('inventory', 'product_id', 'products', 'id')
        ]
        
        self.all_patterns = []

    def generate_all_patterns(self):
        """Generate ALL possible SQL query patterns"""
        
        print("🚀 Generating comprehensive training data...")
        print("="*70)
        
        # 1. BASIC SELECT
        self._generate_select_patterns()
        
        # 2. WHERE CLAUSE PATTERNS
        self._generate_where_patterns()
        
        # 3. JOIN PATTERNS (ALL TYPES)
        self._generate_join_patterns()
        
        # 4. AGGREGATION PATTERNS
        self._generate_aggregation_patterns()
        
        # 5. GROUP BY PATTERNS
        self._generate_group_by_patterns()
        
        # 6. HAVING PATTERNS
        self._generate_having_patterns()
        
        # 7. ORDER BY PATTERNS
        self._generate_order_by_patterns()
        
        # 8. WINDOW FUNCTIONS
        self._generate_window_function_patterns()
        
        # 9. SUBQUERIES
        self._generate_subquery_patterns()
        
        # 10. CTE (Common Table Expressions)
        self._generate_cte_patterns()
        
        # 11. COMPLEX COMBINATIONS
        self._generate_complex_patterns()
        
        # 12. CASE STATEMENTS
        self._generate_case_patterns()
        
        # 13. SET OPERATIONS
        self._generate_set_operation_patterns()
        
        # 14. DATE/TIME FUNCTIONS
        self._generate_date_time_patterns()
        
        # 15. STRING FUNCTIONS
        self._generate_string_patterns()
        
        # 16. ANALYTICAL FUNCTIONS
        self._generate_analytical_patterns()
        
        # 17. NATURAL LANGUAGE VARIATIONS
        self._generate_natural_language_patterns()
        
        # Remove duplicates and save
        self._save_patterns()
    
    def _generate_select_patterns(self):
        """Generate SELECT pattern variations"""
        patterns = []
        for table in self.tables:
            cols = self.columns[table]
            
            # Basic SELECT variations
            variations = [
                (f"Show me all {table}", f"SELECT * FROM {table}"),
                (f"Get all {table}", f"SELECT * FROM {table}"),
                (f"Display {table}", f"SELECT * FROM {table}"),
                (f"List {table}", f"SELECT * FROM {table}"),
                (f"Retrieve {table}", f"SELECT * FROM {table}"),
                (f"Fetch all {table}", f"SELECT * FROM {table}"),
                (f"Give me {table}", f"SELECT * FROM {table}"),
                (f"Show {table} data", f"SELECT * FROM {table}"),
                (f"View all {table}", f"SELECT * FROM {table}"),
                (f"Select everything from {table}", f"SELECT * FROM {table}"),
            ]
            patterns.extend(variations)
            
            # SELECT specific columns
            for col in cols[:3]:
                variations = [
                    (f"Show {col} from {table}", f"SELECT {col} FROM {table}"),
                    (f"Get {col} values from {table}", f"SELECT {col} FROM {table}"),
                    (f"Display {col} in {table}", f"SELECT {col} FROM {table}"),
                    (f"What is the {col} in {table}", f"SELECT {col} FROM {table}"),
                    (f"List {col} from {table}", f"SELECT {col} FROM {table}"),
                ]
                patterns.extend(variations)
            
            # SELECT multiple columns
            if len(cols) >= 3:
                patterns.append((f"Show {cols[0]}, {cols[1]}, {cols[2]} from {table}", 
                               f"SELECT {cols[0]}, {cols[1]}, {cols[2]} FROM {table}"))
                patterns.append((f"Get {cols[0]} and {cols[1]} from {table}", 
                               f"SELECT {cols[0]}, {cols[1]} FROM {table}"))
            
            # SELECT with DISTINCT
            for col in cols[:2]:
                patterns.append((f"Show distinct {col} from {table}", 
                               f"SELECT DISTINCT {col} FROM {table}"))
                patterns.append((f"Unique {col} values from {table}", 
                               f"SELECT DISTINCT {col} FROM {table}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} SELECT patterns")
    
    def _generate_where_patterns(self):
        """Generate WHERE clause patterns"""
        patterns = []
        for table in self.tables:
            cols = self.columns[table]
            
            # Basic WHERE with equals
            for col in cols[:3]:
                patterns.append((f"Show {table} where {col} is 'value'", 
                               f"SELECT * FROM {table} WHERE {col} = 'value'"))
                patterns.append((f"Find {table} with {col} = 'value'", 
                               f"SELECT * FROM {table} WHERE {col} = 'value'"))
            
            # WHERE with comparison operators
            numeric_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity', 'total_amount']]
            for col in numeric_cols[:2]:
                patterns.append((f"Show {table} where {col} is greater than 100", 
                               f"SELECT * FROM {table} WHERE {col} > 100"))
                patterns.append((f"{table} with {col} less than 50", 
                               f"SELECT * FROM {table} WHERE {col} < 50"))
                patterns.append((f"{table} where {col} between 10 and 20", 
                               f"SELECT * FROM {table} WHERE {col} BETWEEN 10 AND 20"))
            
            # WHERE with IS NULL / IS NOT NULL
            for col in cols[:2]:
                patterns.append((f"Show {table} where {col} is null", 
                               f"SELECT * FROM {table} WHERE {col} IS NULL"))
                patterns.append((f"{table} where {col} is not null", 
                               f"SELECT * FROM {table} WHERE {col} IS NOT NULL"))
            
            # WHERE with LIKE
            for col in cols[:2]:
                patterns.append((f"Find {table} where {col} contains 'test'", 
                               f"SELECT * FROM {table} WHERE {col} LIKE '%test%'"))
                patterns.append((f"{table} where {col} starts with 'A'", 
                               f"SELECT * FROM {table} WHERE {col} LIKE 'A%'"))
                patterns.append((f"{table} where {col} ends with 'ing'", 
                               f"SELECT * FROM {table} WHERE {col} LIKE '%ing'"))
            
            # WHERE with IN clause
            for col in cols[:2]:
                patterns.append((f"Show {table} where {col} is in (1, 2, 3)", 
                               f"SELECT * FROM {table} WHERE {col} IN (1, 2, 3)"))
            
            # WHERE with AND/OR
            if len(cols) >= 3:
                patterns.append((f"Show {table} where {cols[0]} = 'value1' and {cols[1]} = 'value2'", 
                               f"SELECT * FROM {table} WHERE {cols[0]} = 'value1' AND {cols[1]} = 'value2'"))
                patterns.append((f"{table} where {cols[0]} = 'value' or {cols[1]} = 'value'", 
                               f"SELECT * FROM {table} WHERE {cols[0]} = 'value' OR {cols[1]} = 'value'"))
            
            # WHERE with date conditions
            if 'created_at' in cols:
                patterns.append((f"Show {table} from last month", 
                               f"SELECT * FROM {table} WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"))
                patterns.append((f"{table} from last week", 
                               f"SELECT * FROM {table} WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"))
                patterns.append((f"{table} from today", 
                               f"SELECT * FROM {table} WHERE DATE(created_at) = CURDATE()"))
                patterns.append((f"{table} from last year", 
                               f"SELECT * FROM {table} WHERE created_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} WHERE patterns")
    
    def _generate_join_patterns(self):
        """Generate JOIN patterns (INNER, LEFT, RIGHT, FULL, CROSS)"""
        patterns = []
        
        # INNER JOIN
        for rel in self.relationships[:4]:  # Use first 4 relationships
            table1, fk, table2, pk = rel
            patterns.append((f"Join {table1} with {table2}", 
                           f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
            patterns.append((f"Show {table1} and {table2} together", 
                           f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
            patterns.append((f"Get {table1} with {table2} details", 
                           f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
            
            # JOIN with specific columns
            cols1 = self.columns[table1][:2]
            cols2 = self.columns[table2][:2]
            patterns.append((f"Show {cols1[0]}, {cols1[1]} from {table1} and {cols2[0]}, {cols2[1]} from {table2}", 
                           f"SELECT {table1}.{cols1[0]}, {table1}.{cols1[1]}, {table2}.{cols2[0]}, {table2}.{cols2[1]} FROM {table1} INNER JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
        
        # LEFT JOIN
        for rel in self.relationships[:3]:
            table1, fk, table2, pk = rel
            patterns.append((f"Show all {table1} and their {table2}", 
                           f"SELECT * FROM {table1} LEFT JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
            patterns.append((f"Get {table1} with optional {table2}", 
                           f"SELECT * FROM {table1} LEFT JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
        
        # RIGHT JOIN
        for rel in self.relationships[:2]:
            table1, fk, table2, pk = rel
            patterns.append((f"Show all {table2} with their {table1}", 
                           f"SELECT * FROM {table1} RIGHT JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
        
        # FULL OUTER JOIN
        for rel in self.relationships[:1]:
            table1, fk, table2, pk = rel
            patterns.append((f"Show all {table1} and all {table2} with matches", 
                           f"SELECT * FROM {table1} FULL OUTER JOIN {table2} ON {table1}.{fk} = {table2}.{pk}"))
        
        # Multiple JOINs
        if len(self.relationships) >= 3:
            table1, fk1, table2, pk1 = self.relationships[0]
            table2, fk2, table3, pk2 = self.relationships[1]
            patterns.append((f"Join {table1}, {table2}, and {table3}", 
                           f"SELECT * FROM {table1} JOIN {table2} ON {table1}.{fk1} = {table2}.{pk1} JOIN {table3} ON {table2}.{fk2} = {table3}.{pk2}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} JOIN patterns")
    
    def _generate_aggregation_patterns(self):
        """Generate aggregation patterns"""
        patterns = []
        
        agg_functions = [
            ('SUM', 'sum', 'total'),
            ('AVG', 'average', 'avg'),
            ('COUNT', 'count', 'number of'),
            ('MAX', 'maximum', 'max', 'highest'),
            ('MIN', 'minimum', 'min', 'lowest')
        ]
        
        for table in self.tables:
            cols = self.columns[table]
            numeric_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity', 'total_amount', 'discount', 'tax']]
            
            # SUM
            for col in numeric_cols[:2]:
                patterns.append((f"Total {col} in {table}", f"SELECT SUM({col}) FROM {table}"))
                patterns.append((f"Sum of {col} in {table}", f"SELECT SUM({col}) FROM {table}"))
                patterns.append((f"Add up {col} from {table}", f"SELECT SUM({col}) FROM {table}"))
            
            # AVG
            for col in numeric_cols[:2]:
                patterns.append((f"Average {col} in {table}", f"SELECT AVG({col}) FROM {table}"))
                patterns.append((f"Average of {col} from {table}", f"SELECT AVG({col}) FROM {table}"))
                patterns.append((f"Mean {col} in {table}", f"SELECT AVG({col}) FROM {table}"))
            
            # COUNT
            patterns.append((f"Count of {table}", f"SELECT COUNT(*) FROM {table}"))
            patterns.append((f"How many {table} are there", f"SELECT COUNT(*) FROM {table}"))
            patterns.append((f"Number of {table} entries", f"SELECT COUNT(*) FROM {table}"))
            patterns.append((f"Total records in {table}", f"SELECT COUNT(*) FROM {table}"))
            
            for col in cols[:2]:
                patterns.append((f"Count {col} in {table}", f"SELECT COUNT({col}) FROM {table}"))
                patterns.append((f"How many {col} in {table}", f"SELECT COUNT({col}) FROM {table}"))
            
            # MAX
            for col in numeric_cols[:2]:
                patterns.append((f"Maximum {col} in {table}", f"SELECT MAX({col}) FROM {table}"))
                patterns.append((f"Highest {col} in {table}", f"SELECT MAX({col}) FROM {table}"))
                patterns.append((f"Largest {col} from {table}", f"SELECT MAX({col}) FROM {table}"))
            
            # MIN
            for col in numeric_cols[:2]:
                patterns.append((f"Minimum {col} in {table}", f"SELECT MIN({col}) FROM {table}"))
                patterns.append((f"Lowest {col} in {table}", f"SELECT MIN({col}) FROM {table}"))
                patterns.append((f"Smallest {col} from {table}", f"SELECT MIN({col}) FROM {table}"))
            
            # Multiple aggregations
            if len(numeric_cols) >= 2:
                patterns.append((f"Sum and average of {numeric_cols[0]} and {numeric_cols[1]}", 
                               f"SELECT SUM({numeric_cols[0]}), AVG({numeric_cols[0]}), SUM({numeric_cols[1]}), AVG({numeric_cols[1]}) FROM {table}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Aggregation patterns")
    
    def _generate_group_by_patterns(self):
        """Generate GROUP BY patterns"""
        patterns = []
        
        for table in self.tables:
            cols = self.columns[table]
            categorical_cols = [col for col in cols if col in ['status', 'category', 'segment', 'gender', 'city', 'state', 'country', 'department_id', 'region']]
            
            for col in categorical_cols[:3]:
                patterns.append((f"Count by {col} in {table}", 
                               f"SELECT {col}, COUNT(*) FROM {table} GROUP BY {col}"))
                patterns.append((f"Group {table} by {col}", 
                               f"SELECT {col}, COUNT(*) FROM {table} GROUP BY {col}"))
                patterns.append((f"Distribution of {col} in {table}", 
                               f"SELECT {col}, COUNT(*) FROM {table} GROUP BY {col} ORDER BY COUNT(*) DESC"))
            
            # GROUP BY with aggregation
            numeric_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity', 'total_amount']]
            for cat_col in categorical_cols[:2]:
                for num_col in numeric_cols[:2]:
                    patterns.append((f"Average {num_col} by {cat_col} in {table}", 
                                   f"SELECT {cat_col}, AVG({num_col}) FROM {table} GROUP BY {cat_col}"))
                    patterns.append((f"Total {num_col} by {cat_col} in {table}", 
                                   f"SELECT {cat_col}, SUM({num_col}) FROM {table} GROUP BY {cat_col}"))
            
            # GROUP BY with multiple columns
            if len(categorical_cols) >= 2:
                patterns.append((f"Count by {categorical_cols[0]} and {categorical_cols[1]} in {table}", 
                               f"SELECT {categorical_cols[0]}, {categorical_cols[1]}, COUNT(*) FROM {table} GROUP BY {categorical_cols[0]}, {categorical_cols[1]}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} GROUP BY patterns")
    
    def _generate_having_patterns(self):
        """Generate HAVING clause patterns"""
        patterns = []
        
        for table in self.tables:
            cols = self.columns[table]
            categorical_cols = [col for col in cols if col in ['status', 'category', 'segment', 'city', 'state', 'country']]
            numeric_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity', 'total_amount']]
            
            for cat_col in categorical_cols[:2]:
                for num_col in numeric_cols[:2]:
                    patterns.append((f"Show {cat_col} with {num_col} greater than 100 in {table}", 
                                   f"SELECT {cat_col}, SUM({num_col}) FROM {table} GROUP BY {cat_col} HAVING SUM({num_col}) > 100"))
                    patterns.append((f"Show {cat_col} with {num_col} less than 50 in {table}", 
                                   f"SELECT {cat_col}, AVG({num_col}) FROM {table} GROUP BY {cat_col} HAVING AVG({num_col}) < 50"))
                    patterns.append((f"Show {cat_col} with more than 10 records in {table}", 
                                   f"SELECT {cat_col}, COUNT(*) FROM {table} GROUP BY {cat_col} HAVING COUNT(*) > 10"))
            
            # HAVING with multiple conditions
            if len(categorical_cols) >= 2 and len(numeric_cols) >= 1:
                patterns.append((f"Show {categorical_cols[0]}, {categorical_cols[1]} with {numeric_cols[0]} > 100 and count > 5", 
                               f"SELECT {categorical_cols[0]}, {categorical_cols[1]}, SUM({numeric_cols[0]}) FROM {table} GROUP BY {categorical_cols[0]}, {categorical_cols[1]} HAVING SUM({numeric_cols[0]}) > 100 AND COUNT(*) > 5"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} HAVING patterns")
    
    def _generate_order_by_patterns(self):
        """Generate ORDER BY patterns"""
        patterns = []
        
        for table in self.tables:
            cols = self.columns[table]
            
            for col in cols[:3]:
                patterns.append((f"Sort {table} by {col} ascending", 
                               f"SELECT * FROM {table} ORDER BY {col} ASC"))
                patterns.append((f"{table} sorted by {col} descending", 
                               f"SELECT * FROM {table} ORDER BY {col} DESC"))
                patterns.append((f"Top {table} by {col}", 
                               f"SELECT * FROM {table} ORDER BY {col} DESC LIMIT 10"))
                patterns.append((f"Order {table} by {col}", 
                               f"SELECT * FROM {table} ORDER BY {col}"))
            
            # ORDER BY with multiple columns
            if len(cols) >= 3:
                patterns.append((f"Sort {table} by {cols[0]} ascending, {cols[1]} descending", 
                               f"SELECT * FROM {table} ORDER BY {cols[0]} ASC, {cols[1]} DESC"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} ORDER BY patterns")
    
    def _generate_window_function_patterns(self):
        """Generate Window Function patterns"""
        patterns = []
        
        window_functions = [
            ('ROW_NUMBER', 'row number', 'rank rows'),
            ('RANK', 'rank', 'ranking'),
            ('DENSE_RANK', 'dense rank', 'dense ranking'),
            ('LAG', 'lag', 'previous value'),
            ('LEAD', 'lead', 'next value'),
            ('NTILE', 'ntile', 'percentile'),
            ('SUM OVER', 'running sum', 'cumulative total'),
            ('AVG OVER', 'running average', 'moving average'),
        ]
        
        for table in self.tables:
            cols = self.columns[table]
            order_col = cols[0] if cols else 'id'
            
            patterns.append((f"Add row number to {table} ordered by {order_col}", 
                           f"SELECT *, ROW_NUMBER() OVER (ORDER BY {order_col}) as row_num FROM {table}"))
            
            patterns.append((f"Rank {table} by {order_col}", 
                           f"SELECT *, RANK() OVER (ORDER BY {order_col} DESC) as rank FROM {table}"))
            
            patterns.append((f"Running total of {order_col} in {table}", 
                           f"SELECT *, SUM({order_col}) OVER (ORDER BY {order_col}) as running_total FROM {table}"))
            
            # Partitioned window functions
            categorical_cols = [col for col in cols if col in ['status', 'category', 'segment', 'city']]
            for cat_col in categorical_cols[:1]:
                patterns.append((f"Row number by {cat_col} in {table}", 
                               f"SELECT *, ROW_NUMBER() OVER (PARTITION BY {cat_col} ORDER BY {order_col}) as row_num FROM {table}"))
                
                patterns.append((f"Rank by {cat_col} in {table}", 
                               f"SELECT *, RANK() OVER (PARTITION BY {cat_col} ORDER BY {order_col} DESC) as rank FROM {table}"))
            
            # LAG/LEAD
            patterns.append((f"Previous value of {order_col} in {table}", 
                           f"SELECT *, LAG({order_col}) OVER (ORDER BY {order_col}) as prev_value FROM {table}"))
            
            patterns.append((f"Next value of {order_col} in {table}", 
                           f"SELECT *, LEAD({order_col}) OVER (ORDER BY {order_col}) as next_value FROM {table}"))
            
            # NTILE
            patterns.append((f"Percentile ranking of {order_col} in {table}", 
                           f"SELECT *, NTILE(4) OVER (ORDER BY {order_col}) as quartile FROM {table}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Window Function patterns")
    
    def _generate_subquery_patterns(self):
        """Generate Subquery patterns"""
        patterns = []
        
        # Subquery in WHERE
        for table in self.tables:
            cols = self.columns[table]
            numeric_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity', 'total_amount']]
            
            for col in numeric_cols[:1]:
                patterns.append((f"Show {table} with above average {col}", 
                               f"SELECT * FROM {table} WHERE {col} > (SELECT AVG({col}) FROM {table})"))
                
                patterns.append((f"Show {table} with below average {col}", 
                               f"SELECT * FROM {table} WHERE {col} < (SELECT AVG({col}) FROM {table})"))
                
                patterns.append((f"Show {table} with max {col}", 
                               f"SELECT * FROM {table} WHERE {col} = (SELECT MAX({col}) FROM {table})"))
        
        # Subquery with IN
        for table in self.tables:
            if table in ['orders', 'order_items']:
                patterns.append((f"Show customers who have orders", 
                               f"SELECT * FROM customers WHERE id IN (SELECT customer_id FROM orders)"))
                patterns.append((f"Show customers without orders", 
                               f"SELECT * FROM customers WHERE id NOT IN (SELECT customer_id FROM orders)"))
        
        # Subquery in SELECT
        for table in self.tables:
            patterns.append((f"Show {table} with count of related records", 
                           f"SELECT *, (SELECT COUNT(*) FROM orders WHERE orders.customer_id = customers.id) as order_count FROM {table}"))
        
        # Correlated subqueries
        if 'orders' in self.tables and 'customers' in self.tables:
            patterns.append((f"Show customers with total spending > 1000", 
                           f"SELECT * FROM customers WHERE (SELECT SUM(total_amount) FROM orders WHERE orders.customer_id = customers.id) > 1000"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Subquery patterns")
    
    def _generate_cte_patterns(self):
        """Generate CTE (Common Table Expression) patterns"""
        patterns = []
        
        # Simple CTE
        patterns.append(("Find customers with high spending using CTE", 
                        "WITH high_spenders AS (SELECT customer_id, SUM(total_amount) as total FROM orders GROUP BY customer_id HAVING SUM(total_amount) > 1000) SELECT * FROM customers JOIN high_spenders ON customers.id = high_spenders.customer_id"))
        
        # Multiple CTEs
        patterns.append(("CTE for sales analysis", 
                        "WITH monthly_sales AS (SELECT DATE_FORMAT(order_date, '%Y-%m') as month, SUM(total_amount) as sales FROM orders GROUP BY DATE_FORMAT(order_date, '%Y-%m')), avg_sales AS (SELECT AVG(sales) as avg_sales FROM monthly_sales) SELECT * FROM monthly_sales WHERE sales > (SELECT avg_sales FROM avg_sales)"))
        
        # Recursive CTE (if applicable)
        if 'employees' in self.tables and 'manager_id' in self.columns['employees']:
            patterns.append(("Show employee hierarchy", 
                            "WITH RECURSIVE emp_hierarchy AS (SELECT id, first_name, last_name, manager_id, 1 as level FROM employees WHERE manager_id IS NULL UNION ALL SELECT e.id, e.first_name, e.last_name, e.manager_id, eh.level + 1 FROM employees e JOIN emp_hierarchy eh ON e.manager_id = eh.id) SELECT * FROM emp_hierarchy"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} CTE patterns")
    
    def _generate_complex_patterns(self):
        """Generate Complex combination patterns"""
        patterns = []
        
        # JOIN + GROUP BY + HAVING
        for rel in self.relationships[:2]:
            table1, fk, table2, pk = rel
            cols1 = self.columns[table1]
            cols2 = self.columns[table2]
            
            cat_cols1 = [col for col in cols1 if col in ['status', 'category', 'segment', 'city']]
            num_cols2 = [col for col in cols2 if col in ['total_amount', 'amount', 'price', 'quantity']]
            
            if cat_cols1 and num_cols2:
                patterns.append((f"Show {cat_cols1[0]} with total {num_cols2[0]} > 1000 from {table1} and {table2}", 
                               f"SELECT {table1}.{cat_cols1[0]}, SUM({table2}.{num_cols2[0]}) FROM {table1} JOIN {table2} ON {table1}.{fk} = {table2}.{pk} GROUP BY {table1}.{cat_cols1[0]} HAVING SUM({table2}.{num_cols2[0]}) > 1000"))
        
        # WHERE + GROUP BY + ORDER BY
        for table in self.tables:
            cols = self.columns[table]
            cat_cols = [col for col in cols if col in ['status', 'category', 'segment', 'city']]
            num_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity']]
            
            if cat_cols and num_cols:
                patterns.append((f"Show {cat_cols[0]} with {num_cols[0]} > 50 sorted by count", 
                               f"SELECT {cat_cols[0]}, COUNT(*) FROM {table} WHERE {num_cols[0]} > 50 GROUP BY {cat_cols[0]} ORDER BY COUNT(*) DESC"))
        
        # CTE + JOIN + Window Function
        patterns.append(("CTE with window function for employee ranking", 
                        "WITH emp_stats AS (SELECT department_id, salary, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank FROM employees) SELECT * FROM emp_stats WHERE rank <= 3"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Complex combination patterns")
    
    def _generate_case_patterns(self):
        """Generate CASE statement patterns"""
        patterns = []
        
        for table in self.tables:
            cols = self.columns[table]
            cat_cols = [col for col in cols if col in ['status', 'category', 'segment', 'gender']]
            num_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity']]
            
            if cat_cols:
                patterns.append((f"Categorize {cat_cols[0]} in {table}", 
                               f"SELECT *, CASE WHEN {cat_cols[0]} = 'value1' THEN 'Category A' WHEN {cat_cols[0]} = 'value2' THEN 'Category B' ELSE 'Other' END as category FROM {table}"))
            
            if num_cols:
                patterns.append((f"Bucket {num_cols[0]} in {table}", 
                               f"SELECT *, CASE WHEN {num_cols[0]} < 50 THEN 'Low' WHEN {num_cols[0]} BETWEEN 50 AND 100 THEN 'Medium' ELSE 'High' END as bucket FROM {table}"))
            
            # CASE with aggregation
            if cat_cols and num_cols:
                patterns.append((f"Count by {cat_cols[0]} with {num_cols[0]} categories in {table}", 
                               f"SELECT {cat_cols[0]}, SUM(CASE WHEN {num_cols[0]} > 100 THEN 1 ELSE 0 END) as high_value FROM {table} GROUP BY {cat_cols[0]}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} CASE patterns")
    
    def _generate_set_operation_patterns(self):
        """Generate SET operations (UNION, INTERSECT, EXCEPT)"""
        patterns = []
        
        # UNION
        if 'customers' in self.tables and 'employees' in self.tables:
            patterns.append(("Show names from customers and employees", 
                            "SELECT name FROM customers UNION SELECT first_name || ' ' || last_name FROM employees"))
        
        # UNION ALL
        if 'products' in self.tables:
            patterns.append(("Show all products from categories A and B", 
                            "SELECT * FROM products WHERE category = 'A' UNION ALL SELECT * FROM products WHERE category = 'B'"))
        
        # INTERSECT
        if 'customers' in self.tables and 'orders' in self.tables:
            patterns.append(("Customers who have placed orders", 
                            "SELECT id FROM customers INTERSECT SELECT customer_id FROM orders"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Set Operation patterns")
    
    def _generate_date_time_patterns(self):
        """Generate Date/Time function patterns"""
        patterns = []
        
        for table in self.tables:
            if 'created_at' in self.columns[table]:
                patterns.append((f"Show year from {table} created_at", 
                               f"SELECT YEAR(created_at) as year FROM {table}"))
                patterns.append((f"Show month from {table} created_at", 
                               f"SELECT MONTH(created_at) as month FROM {table}"))
                patterns.append((f"Show day from {table} created_at", 
                               f"SELECT DAY(created_at) as day FROM {table}"))
                patterns.append((f"Show date difference in {table}", 
                               f"SELECT DATEDIFF(NOW(), created_at) as days_ago FROM {table}"))
                patterns.append((f"Show weekday from {table} created_at", 
                               f"SELECT DAYNAME(created_at) as weekday FROM {table}"))
                patterns.append((f"Show day of week from {table} created_at", 
                               f"SELECT DAYOFWEEK(created_at) as day_of_week FROM {table}"))
                patterns.append((f"Show week number from {table} created_at", 
                               f"SELECT WEEK(created_at) as week FROM {table}"))
                patterns.append((f"Show quarter from {table} created_at", 
                               f"SELECT QUARTER(created_at) as quarter FROM {table}"))
                patterns.append((f"Extract year and month from {table}", 
                               f"SELECT DATE_FORMAT(created_at, '%Y-%m') as year_month FROM {table}"))
            
            if 'order_date' in self.columns[table]:
                patterns.append((f"Show year from {table} order_date", 
                               f"SELECT YEAR(order_date) as year FROM {table}"))
                patterns.append((f"Show month from {table} order_date", 
                               f"SELECT MONTH(order_date) as month FROM {table}"))
                patterns.append((f"Date difference in {table}", 
                               f"SELECT DATEDIFF(order_date, delivery_date) as delivery_days FROM {table}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Date/Time patterns")
    
    def _generate_string_patterns(self):
        """Generate String function patterns"""
        patterns = []
        
        for table in self.tables:
            cols = self.columns[table]
            string_cols = [col for col in cols if col in ['name', 'email', 'description', 'address', 'city', 'state', 'country']]
            
            for col in string_cols[:2]:
                patterns.append((f"Show length of {col} in {table}", 
                               f"SELECT LENGTH({col}) as length FROM {table}"))
                patterns.append((f"Show uppercase {col} in {table}", 
                               f"SELECT UPPER({col}) as {col}_upper FROM {table}"))
                patterns.append((f"Show lowercase {col} in {table}", 
                               f"SELECT LOWER({col}) as {col}_lower FROM {table}"))
                patterns.append((f"Show first 10 chars of {col} in {table}", 
                               f"SELECT SUBSTRING({col}, 1, 10) as {col}_short FROM {table}"))
                patterns.append((f"Show trimmed {col} in {table}", 
                               f"SELECT TRIM({col}) as {col}_trimmed FROM {table}"))
                patterns.append((f"Count words in {col}", 
                               f"SELECT LENGTH({col}) - LENGTH(REPLACE({col}, ' ', '')) + 1 as word_count FROM {table}"))
                patterns.append((f"Find 'test' in {col}", 
                               f"SELECT POSITION('test' IN {col}) as position FROM {table}"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} String Function patterns")
    
    def _generate_analytical_patterns(self):
        """Generate Analytical function patterns"""
        patterns = []
        
        for table in self.tables:
            cols = self.columns[table]
            numeric_cols = [col for col in cols if col in ['id', 'age', 'salary', 'price', 'amount', 'quantity', 'total_amount']]
            
            for col in numeric_cols[:2]:
                patterns.append((f"Show percent rank of {col} in {table}", 
                               f"SELECT {col}, PERCENT_RANK() OVER (ORDER BY {col}) as percent_rank FROM {table}"))
                
                patterns.append((f"Show cumulative distribution of {col} in {table}", 
                               f"SELECT {col}, CUME_DIST() OVER (ORDER BY {col}) as cume_dist FROM {table}"))
                
                patterns.append((f"Show stddev of {col} in {table}", 
                               f"SELECT {col}, STDDEV({col}) OVER () as stddev FROM {table}"))
                
                patterns.append((f"Show variance of {col} in {table}", 
                               f"SELECT {col}, VARIANCE({col}) OVER () as variance FROM {table}"))
        
        # Correlation analysis
        if 'orders' in self.tables:
            patterns.append(("Show correlation between order amount and discount", 
                            "SELECT CORR(total_amount, discount) as correlation FROM orders"))
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Analytical patterns")
    
    def _generate_natural_language_patterns(self):
        """Generate Natural language variations"""
        patterns = []
        
        # Different ways to ask the same thing
        variations = [
            ("Show me", "Get", "Display", "List", "Retrieve", "Fetch", "Find", "Give me"),
            ("all", "all the", "every", "the", ""),
            ("customers", "orders", "products", "sales", "employees")
        ]
        
        for table in self.tables:
            base_queries = [
                (f"Show me all {table}", f"SELECT * FROM {table}"),
                (f"Get the {table}", f"SELECT * FROM {table}"),
                (f"Display {table}", f"SELECT * FROM {table}"),
                (f"List all {table}", f"SELECT * FROM {table}"),
                (f"Retrieve {table} data", f"SELECT * FROM {table}"),
                (f"Fetch all {table}", f"SELECT * FROM {table}"),
                (f"Find {table}", f"SELECT * FROM {table}"),
                (f"Give me the {table}", f"SELECT * FROM {table}"),
                (f"I need {table}", f"SELECT * FROM {table}"),
                (f"Can you show me {table}", f"SELECT * FROM {table}"),
                (f"Please show {table}", f"SELECT * FROM {table}"),
                (f"Show {table} please", f"SELECT * FROM {table}"),
            ]
            patterns.extend(base_queries)
        
        self.all_patterns.extend(patterns)
        print(f"✅ Added {len(patterns)} Natural Language patterns")
    
    def _save_patterns(self):
        """Save all patterns to CSV"""
        # Remove duplicates
        unique_patterns = []
        seen = set()
        for pattern in self.all_patterns:
            key = f"{pattern[0]}|{pattern[1]}"
            if key not in seen:
                seen.add(key)
                unique_patterns.append(pattern)
        
        # Create DataFrame
        df = pd.DataFrame(unique_patterns, columns=['natural_query', 'sql_query'])
        
        # Save to CSV
        output_file = 'data/query_history.csv'
        os.makedirs('data', exist_ok=True)
        df.to_csv(output_file, index=False)
        
        print("\n" + "="*70)
        print(f"✅ SUCCESS! Generated {len(df)} unique training examples")
        print("="*70)
        
        # Show distribution
        sql_types = {
            'SELECT': len(df[df['sql_query'].str.contains('SELECT', case=False)]),
            'WHERE': len(df[df['sql_query'].str.contains('WHERE', case=False)]),
            'JOIN': len(df[df['sql_query'].str.contains('JOIN', case=False)]),
            'GROUP BY': len(df[df['sql_query'].str.contains('GROUP BY', case=False)]),
            'HAVING': len(df[df['sql_query'].str.contains('HAVING', case=False)]),
            'ORDER BY': len(df[df['sql_query'].str.contains('ORDER BY', case=False)]),
            'WINDOW': len(df[df['sql_query'].str.contains('OVER', case=False)]),
            'SUBQUERY': len(df[df['sql_query'].str.contains('SELECT.*SELECT', case=False)]),
            'CTE': len(df[df['sql_query'].str.contains('WITH', case=False)]),
            'CASE': len(df[df['sql_query'].str.contains('CASE', case=False)]),
            'DISTINCT': len(df[df['sql_query'].str.contains('DISTINCT', case=False)]),
            'AGGREGATION': len(df[df['sql_query'].str.contains('SUM|AVG|COUNT|MAX|MIN', case=False)]),
        }
        
        print("\n📊 Query Type Distribution:")
        for qtype, count in sql_types.items():
            if count > 0:
                percentage = (count / len(df)) * 100
                print(f"  {qtype}: {count} ({percentage:.1f}%)")
        
        print(f"\n📁 Saved to: {output_file}")
        print(f"\n📝 Sample Examples:")
        for i in range(min(10, len(df))):
            print(f"\n{i+1}. Natural: {df.iloc[i]['natural_query']}")
            print(f"   SQL:     {df.iloc[i]['sql_query']}")

if __name__ == "__main__":
    generator = CompleteTrainingDataGenerator()
    generator.generate_all_patterns()
    print("\n🎯 Now restart your app to use the new training data!")
    print("   python app.py")