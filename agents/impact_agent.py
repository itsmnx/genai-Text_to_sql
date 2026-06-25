# agents/impact_agent.py

class ImpactAgent:
    """Agent responsible for analyzing query impact"""
    
    def __init__(self):
        self.impact_levels = {
            'low': 'Minimal impact. Query will execute quickly.',
            'medium': 'Moderate impact. May affect performance on large datasets.',
            'high': 'High impact. Consider optimizing or running during off-peak hours.'
        }
    
    def analyze_impact(self, sql_query):
        """
        Analyze the impact of a query
        """
        if not sql_query:
            return {'level': 'low', 'message': 'No query provided'}
        
        sql_lower = sql_query.lower()
        impact_score = 0
        
        # Check for factors that increase impact
        if 'select *' in sql_lower:
            impact_score += 2
        
        if 'join' in sql_lower:
            impact_score += 2
        
        if 'where' not in sql_lower:
            impact_score += 1
        
        if 'limit' not in sql_lower:
            impact_score += 1
        
        if 'order by' in sql_lower:
            impact_score += 1
        
        if 'group by' in sql_lower:
            impact_score += 1
        
        # Determine impact level
        if impact_score <= 2:
            level = 'low'
        elif impact_score <= 4:
            level = 'medium'
        else:
            level = 'high'
        
        # Generate recommendations
        recommendations = []
        if 'select *' in sql_lower:
            recommendations.append('Specify only needed columns instead of using *')
        if 'join' in sql_lower and 'index' not in sql_lower:
            recommendations.append('Ensure join columns have indexes')
        if 'where' not in sql_lower:
            recommendations.append('Add WHERE clause to filter data')
        if 'limit' not in sql_lower:
            recommendations.append('Consider adding LIMIT to reduce result set')
        
        return {
            'level': level,
            'score': impact_score,
            'message': self.impact_levels[level],
            'recommendations': recommendations if recommendations else ['Query appears well-optimized']
        }
    
    def estimate_time(self, sql_query, row_count=10000):
        """
        Estimate query execution time
        """
        sql_lower = sql_query.lower()
        
        # Base time based on query complexity
        base_time = 0.01  # seconds
        
        if 'join' in sql_lower:
            base_time += 0.1
        
        if 'group by' in sql_lower:
            base_time += 0.05
        
        if 'order by' in sql_lower:
            base_time += 0.05
        
        if 'select *' in sql_lower:
            base_time *= 1.5
        
        # Scale with row count
        estimated_time = base_time * (row_count / 1000)
        
        return min(estimated_time, 5.0)  # Cap at 5 seconds


# Create instance for import
impact_agent = ImpactAgent()