# agents/explanation_agent.py

class ExplanationAgent:
    """Agent responsible for explaining SQL queries"""
    
    def __init__(self):
        self.explanation_templates = {
            'select': "This query selects data from the {table} table.",
            'join': "This query joins multiple tables to combine related data.",
            'aggregate': "This query performs aggregation to summarize the data.",
            'filter': "This query filters data based on specific conditions.",
            'order': "This query orders the results by specific columns.",
            'insert': "This query inserts new records into the {table} table.",
            'update': "This query updates existing records in the {table} table.",
            'delete': "This query removes records from the {table} table."
        }
    
    def explain_query(self, sql_query):
        """
        Generate explanation for a SQL query
        """
        if not sql_query:
            return "No query provided for explanation."
        
        sql_lower = sql_query.lower()
        explanation_parts = []
        
        # Detect query type
        if 'select' in sql_lower:
            explanation_parts.append("SELECT Query")
            
            # Check for joins
            if 'join' in sql_lower:
                explanation_parts.append("This query joins multiple tables to combine related data.")
            else:
                # Try to detect table
                if 'from customers' in sql_lower:
                    explanation_parts.append("This query retrieves data from the customers table.")
                elif 'from orders' in sql_lower:
                    explanation_parts.append("This query retrieves data from the orders table.")
                elif 'from products' in sql_lower:
                    explanation_parts.append("This query retrieves data from the products table.")
                else:
                    explanation_parts.append("This query retrieves data from the specified table.")
            
            # Check for filters
            if 'where' in sql_lower:
                explanation_parts.append("It filters results based on specific conditions.")
            
            # Check for aggregations
            if any(agg in sql_lower for agg in ['count(', 'sum(', 'avg(', 'max(', 'min(']):
                explanation_parts.append("It performs aggregation to summarize the data.")
            
            # Check for ordering
            if 'order by' in sql_lower:
                explanation_parts.append("Results are sorted in a specific order.")
            
            # Check for limits
            if 'limit' in sql_lower:
                explanation_parts.append("Results are limited to a specific number of rows.")
            
        elif 'insert' in sql_lower:
            explanation_parts.append("INSERT Query")
            explanation_parts.append("This query adds new records to the database.")
        elif 'update' in sql_lower:
            explanation_parts.append("UPDATE Query")
            explanation_parts.append("This query modifies existing records in the database.")
        elif 'delete' in sql_lower:
            explanation_parts.append("DELETE Query")
            explanation_parts.append("This query removes records from the database.")
        else:
            explanation_parts.append("Complex Query")
            explanation_parts.append("This query performs multiple operations on the database.")
        
        return " ".join(explanation_parts)
    
    def explain_natural_language(self, query):
        """
        Explain natural language query intent
        """
        query_lower = query.lower()
        explanations = []
        
        if 'show' in query_lower or 'get' in query_lower or 'select' in query_lower:
            explanations.append("You want to retrieve data.")
        
        if 'customer' in query_lower:
            explanations.append("The data relates to customers.")
        
        if 'order' in query_lower:
            explanations.append("The data relates to orders.")
        
        if 'product' in query_lower:
            explanations.append("The data relates to products.")
        
        if 'recent' in query_lower or 'last' in query_lower:
            explanations.append("You want recent data.")
        
        if 'total' in query_lower or 'sum' in query_lower or 'average' in query_lower:
            explanations.append("You want aggregated data.")
        
        if 'top' in query_lower or 'best' in query_lower:
            explanations.append("You want the top results.")
        
        if not explanations:
            explanations.append("You want to query the database.")
        
        return " ".join(explanations)


# Create instance for import
explanation_agent = ExplanationAgent()