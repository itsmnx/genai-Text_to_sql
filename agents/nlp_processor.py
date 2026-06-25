# agents/nlp_processor.py - Without spaCy (using regex + keyword matching)
import re
from typing import Dict, List, Tuple
from collections import Counter

class NLPProcessor:
    """Natural Language Processing for understanding queries (No spaCy required)"""
    
    def __init__(self):
        # Common SQL keywords for intent detection
        self.sql_keywords = {
            'select': ['show', 'get', 'find', 'list', 'display', 'retrieve', 'fetch', 'all'],
            'aggregate': ['sum', 'total', 'average', 'avg', 'count', 'number of', 'max', 'min', 'maximum', 'minimum'],
            'filter': ['where', 'with', 'having', 'containing', 'including', 'filter', 'condition'],
            'join': ['join', 'together', 'combine', 'relationship', 'related', 'connect'],
            'order': ['sort', 'order', 'rank', 'top', 'bottom', 'highest', 'lowest', 'ascending', 'descending'],
            'group': ['group', 'categorize', 'classify', 'breakdown', 'by']
        }
        
        # Common entity patterns (regex)
        self.entity_patterns = {
            'date': r'\b(\d{1,2}(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}|\btoday\b|\byesterday\b|\btomorrow\b|\blast\s+(day|week|month|year)\b)',
            'money': r'\$\d+(\.\d{2})?',
            'number': r'\b\d+\b',
            'operator': r'\b(>|<|>=|<=|=|!=|like|between)\b'
        }
        
        # Known tables and columns (will be populated from CSV data)
        self.known_tables = ['customers', 'orders', 'products', 'order_items', 'train', 'test', 'validation']
        self.known_columns = ['id', 'name', 'email', 'city', 'country', 'created_at', 'customer_id', 
                             'order_date', 'total_amount', 'status', 'price', 'quantity', 'category',
                             'amount', 'value', 'date', 'time', 'product_id', 'order_id']
        
        # Common stopwords
        self.stopwords = {'the', 'a', 'an', 'of', 'for', 'on', 'at', 'to', 'in', 'with', 
                         'without', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'has', 
                         'have', 'had', 'be', 'been', 'being', 'do', 'does', 'did'}
    
    def process(self, text: str) -> Dict:
        """
        Process natural language query and extract structured information
        """
        text_lower = text.lower()
        tokens = self._tokenize(text)
        
        result = {
            'original_text': text,
            'tokens': tokens,
            'lemmas': tokens,  # Simplified - no lemmatization
            'pos_tags': self._simple_pos_tag(tokens),  # Simplified POS tagging
            'entities': self._extract_entities(text),
            'intent': self._detect_intent(text),
            'keywords': self._extract_keywords(text),
            'tables': self._find_tables(text),
            'columns': self._find_columns(text),
            'conditions': self._extract_conditions(text),
            'aggregations': self._find_aggregations(text),
            'operators': self._find_operators(text)
        }
        
        return result
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization without spaCy"""
        # Remove punctuation and split
        text_clean = re.sub(r'[^\w\s]', ' ', text)
        return text_clean.lower().split()
    
    def _simple_pos_tag(self, tokens: List[str]) -> List[str]:
        """Simple POS tagging without spaCy"""
        # Basic mapping based on common patterns
        pos_tags = []
        
        # Common words and their POS tags
        word_pos_map = {
            'show': 'VERB', 'get': 'VERB', 'find': 'VERB', 'list': 'VERB', 'display': 'VERB',
            'customers': 'NOUN', 'orders': 'NOUN', 'products': 'NOUN', 'order': 'NOUN',
            'all': 'DET', 'the': 'DET', 'a': 'DET', 'an': 'DET',
            'sum': 'NOUN', 'total': 'NOUN', 'average': 'NOUN', 'avg': 'NOUN', 'count': 'NOUN',
            'recent': 'ADJ', 'last': 'ADJ', 'newest': 'ADJ', 'oldest': 'ADJ',
            'where': 'ADP', 'with': 'ADP', 'having': 'ADP',
            'join': 'VERB', 'group': 'VERB', 'order': 'VERB', 'sort': 'VERB'
        }
        
        for token in tokens:
            if token in word_pos_map:
                pos_tags.append(word_pos_map[token])
            elif token.endswith('ed') or token.endswith('ing'):
                pos_tags.append('VERB')
            elif token.endswith('s') and len(token) > 3:
                pos_tags.append('NOUN')
            elif re.match(r'\d+', token):
                pos_tags.append('NUM')
            else:
                pos_tags.append('NOUN')
        
        return pos_tags
    
    def _extract_entities(self, text: str) -> Dict:
        """Extract entities using regex patterns"""
        entities = {
            'persons': [],
            'organizations': [],
            'dates': [],
            'money': [],
            'percentages': [],
            'quantities': [],
            'numbers': [],
            'operators': []
        }
        
        # Extract dates
        date_matches = re.findall(self.entity_patterns['date'], text, re.IGNORECASE)
        entities['dates'] = [match[0] if isinstance(match, tuple) else match for match in date_matches]
        
        # Extract money
        money_matches = re.findall(self.entity_patterns['money'], text)
        entities['money'] = money_matches
        
        # Extract numbers
        number_matches = re.findall(self.entity_patterns['number'], text)
        entities['numbers'] = number_matches
        entities['quantities'] = number_matches[:3]  # First 3 numbers as quantities
        
        # Extract operators
        operator_matches = re.findall(self.entity_patterns['operator'], text, re.IGNORECASE)
        entities['operators'] = operator_matches
        
        # Simple person detection (capitalized words that aren't at start)
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 1 and i > 0:
                if word.lower() not in ['the', 'a', 'an', 'and', 'or', 'but']:
                    entities['persons'].append(word)
        
        return entities
    
    def _detect_intent(self, text: str) -> str:
        """Detect the intent of the query"""
        text_lower = text.lower()
        intents = {}
        
        for intent, keywords in self.sql_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intents[intent] = score
        
        if not intents:
            return 'select'
        
        # Return the intent with highest score
        return max(intents, key=intents.get)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Remove stopwords and short words
        keywords = [word for word in words 
                   if word not in self.stopwords and len(word) > 2]
        
        return keywords
    
    def _find_tables(self, text: str) -> List[str]:
        """Find table names in text"""
        text_lower = text.lower()
        found_tables = []
        
        for table in self.known_tables:
            if table in text_lower:
                found_tables.append(table)
        
        return found_tables
    
    def _find_columns(self, text: str) -> List[str]:
        """Find column names in text"""
        text_lower = text.lower()
        found_columns = []
        
        for col in self.known_columns:
            if col in text_lower:
                found_columns.append(col)
        
        return found_columns
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Extract conditions from text"""
        text_lower = text.lower()
        conditions = []
        
        # Pattern for condition: [column] [operator] [value]
        condition_pattern = r'(\w+)\s+(is|are|was|were|has|have|>|<|>=|<=|=|!=)\s+(\w+|\d+)'
        matches = re.findall(condition_pattern, text_lower)
        
        for match in matches:
            conditions.append(f"{match[0]} {match[1]} '{match[2]}'")
        
        # Time-based conditions
        if 'last' in text_lower and 'month' in text_lower:
            conditions.append("created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
        if 'last' in text_lower and 'day' in text_lower:
            conditions.append("created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        if 'last' in text_lower and 'week' in text_lower:
            conditions.append("created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        if 'last' in text_lower and 'year' in text_lower:
            conditions.append("created_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)")
        
        # Numeric conditions
        if 'greater than' in text_lower or '>' in text_lower:
            numbers = re.findall(r'\b\d+\b', text_lower)
            if numbers:
                conditions.append(f"amount > {numbers[0]}")
        
        if 'less than' in text_lower or '<' in text_lower:
            numbers = re.findall(r'\b\d+\b', text_lower)
            if numbers:
                conditions.append(f"amount < {numbers[0]}")
        
        # Status conditions
        if 'active' in text_lower:
            conditions.append("status = 'active'")
        elif 'pending' in text_lower:
            conditions.append("status = 'pending'")
        elif 'completed' in text_lower:
            conditions.append("status = 'completed'")
        
        return conditions
    
    def _find_aggregations(self, text: str) -> List[str]:
        """Find aggregation operations"""
        text_lower = text.lower()
        aggregations = []
        agg_keywords = {
            'sum': ['sum', 'total', 'add', 'addition'],
            'avg': ['avg', 'average', 'mean'],
            'count': ['count', 'number of', 'how many', 'total count'],
            'max': ['max', 'maximum', 'highest', 'top', 'largest'],
            'min': ['min', 'minimum', 'lowest', 'bottom', 'smallest']
        }
        
        for agg, keywords in agg_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                aggregations.append(agg)
        
        return aggregations
    
    def _find_operators(self, text: str) -> List[str]:
        """Find SQL operators in text"""
        text_lower = text.lower()
        found_operators = []
        operator_map = {
            '>': ['greater than', 'more than', 'above', 'over'],
            '<': ['less than', 'fewer than', 'below', 'under'],
            '=': ['equals', 'is', 'are', 'equal to', 'equivalent to'],
            '!=': ['not equal', 'different from', 'not equal to'],
            'like': ['contains', 'includes', 'starts with', 'ends with', 'like', 'matches'],
            'between': ['between', 'from', 'to', 'range']
        }
        
        for operator, keywords in operator_map.items():
            if any(keyword in text_lower for keyword in keywords):
                found_operators.append(operator)
        
        return found_operators
    
    def get_query_summary(self, text: str) -> Dict:
        """
        Get a summary of what the query means
        """
        result = self.process(text)
        
        summary = {
            'what': f"Query is asking to {result['intent']} data",
            'tables': result['tables'] if result['tables'] else ['main table'],
            'conditions': result['conditions'] if result['conditions'] else ['all records'],
            'aggregations': result['aggregations'] if result['aggregations'] else ['none'],
            'entities': {
                'dates': result['entities']['dates'],
                'numbers': result['entities']['numbers'],
                'operators': result['entities']['operators']
            }
        }
        
        return summary

# Create instance
nlp_processor = NLPProcessor()

# Test function (only runs when script is executed directly)
if __name__ == "__main__":
    # Test the NLP processor
    test_queries = [
        "Show me all customers",
        "Get recent orders from last month",
        "Average purchase amount",
        "Find customers from New York",
        "Count total sales by product",
        "Show me customers who bought products in the last 30 days"
    ]
    
    print("Testing NLP Processor without spaCy\n" + "="*50)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = nlp_processor.process(query)
        print(f"   Intent: {result['intent']}")
        print(f"   Tables: {result['tables']}")
        print(f"   Columns: {result['columns']}")
        print(f"   Aggregations: {result['aggregations']}")
        print(f"   Conditions: {result['conditions']}")
        print(f"   Keywords: {result['keywords'][:5]}")