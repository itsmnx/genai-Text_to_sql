# agents/text_to_sql_engine.py
from agents.nlp_processor import nlp_processor
from agents.ml_query_agent import ml_query_agent
from agents.query_agent import query_agent
import re

class TextToSQLEngine:
    """
    Complete Text-to-SQL engine combining NLP + ML
    """
    
    def __init__(self):
        self.nlp = nlp_processor
        self.ml_agent = ml_query_agent
        self.rule_agent = query_agent
        
        # Try to train ML agent
        try:
            self.ml_agent.train()
        except:
            print("⚠️ ML agent not trained, using rule-based fallback")
    
    def generate_sql(self, user_query):
        """
        Generate SQL query from natural language
        """
        # Step 1: NLP Understanding
        nlp_result = self.nlp.process(user_query)
        
        # Step 2: Try ML first
        try:
            sql = self.ml_agent.predict(user_query)
            if sql:
                return {
                    'sql': sql,
                    'method': 'ml',
                    'intent': nlp_result['intent'],
                    'entities': nlp_result['entities'],
                    'confidence': 'high'
                }
        except:
            pass
        
        # Step 3: Fallback to rule-based
        sql = self.rule_agent.generate_query(user_query)
        
        return {
            'sql': sql,
            'method': 'rule_based',
            'intent': nlp_result['intent'],
            'entities': nlp_result['entities'],
            'confidence': 'medium'
        }
    
    def explain(self, user_query):
        """
        Explain the query understanding
        """
        nlp_result = self.nlp.process(user_query)
        
        explanation = {
            'original_query': user_query,
            'understood_as': nlp_result['intent'],
            'entities_found': nlp_result['entities'],
            'keywords': nlp_result['keywords'],
            'tables_found': nlp_result['tables'],
            'columns_found': nlp_result['columns'],
            'conditions': nlp_result['conditions'],
            'aggregations': nlp_result['aggregations']
        }
        
        return explanation

# Create instance
text_to_sql_engine = TextToSQLEngine()