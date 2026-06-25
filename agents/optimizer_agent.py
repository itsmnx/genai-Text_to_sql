# agents/optimizer_agent.py
import re

class OptimizerAgent:
    """Agent responsible for optimizing SQL queries"""
    
    def __init__(self):
        self.optimization_rules = []
    
    def optimize(self, sql_query):
        """
        Optimize the SQL query
        """
        if not sql_query:
            return sql_query
        
        optimized = sql_query
        
        # Rule 1: Replace SELECT * with specific columns
        if 'select *' in optimized.lower():
            optimized = self._expand_select_star(optimized)
        
        # Rule 2: Add indexes hints or optimization
        if 'join' in optimized.lower():
            optimized = self._optimize_joins(optimized)
        
        # Rule 3: Add LIMIT if not present and seems appropriate
        if 'limit' not in optimized.lower() and 'insert' not in optimized.lower() and 'update' not in optimized.lower():
            optimized += " LIMIT 100"
        
        # Rule 4: Optimize WHERE clauses
        optimized = self._optimize_where(optimized)
        
        return optimized
    
    def _expand_select_star(self, sql):
        """Expand SELECT * to specific columns"""
        # This is a simplified version - in production, you'd query the schema
        sql_lower = sql.lower()
        
        if 'from customers' in sql_lower:
            return sql.replace('*', 'id, name, email, city, country, created_at')
        elif 'from orders' in sql_lower:
            return sql.replace('*', 'id, customer_id, order_date, total_amount, status')
        elif 'from products' in sql_lower:
            return sql.replace('*', 'id, name, category, price, stock_quantity')
        else:
            # Generic expansion
            return sql.replace('*', '* /* Consider specifying columns for better performance */')
    
    def _optimize_joins(self, sql):
        """Add join hints for optimization"""
        # In production, you'd add proper join optimization
        return sql
    
    def _optimize_where(self, sql):
        """Optimize WHERE clauses"""
        # Add index hints or optimize conditions
        return sql
    
    def suggest_index(self, sql_query):
        """
        Suggest indexes based on query patterns
        """
        suggestions = []
        sql_lower = sql_query.lower()
        
        if 'where' in sql_lower:
            # Extract column names from WHERE clause
            suggestions.append("Consider adding indexes on columns used in WHERE clauses")
        
        if 'join' in sql_lower:
            suggestions.append("Consider adding indexes on join columns")
        
        if 'order by' in sql_lower:
            suggestions.append("Consider adding indexes on ORDER BY columns")
        
        return suggestions if suggestions else ["No index suggestions needed."]


# Create instance for import
optimizer_agent = OptimizerAgent()