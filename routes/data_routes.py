# routes/data_routes.py
from flask import Blueprint, request, jsonify
import os
import pandas as pd
from agents.schema_agent import schema_agent

data_bp = Blueprint('data', __name__, url_prefix='/api')

@data_bp.route('/data/preview')
def preview_data():
    """Preview data from CSV files"""
    try:
        results = {}
        data_dir = 'data/'
        
        for file in ['train.csv', 'test.csv', 'validation.csv']:
            filepath = os.path.join(data_dir, file)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                results[file] = {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'sample': df.head(5).to_dict('records'),
                    'dtypes': df.dtypes.astype(str).to_dict()
                }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/data/schema')
def get_schema():
    """Get database schema"""
    try:
        schema = schema_agent.get_all_tables()
        return jsonify({
            'tables': schema,
            'relationships': schema_agent.get_relationships()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/data/table/<table_name>')
def get_table_data(table_name):
    """Get data from a specific table"""
    try:
        data_dir = 'data/'
        filepath = os.path.join(data_dir, f'{table_name}.csv')
        
        if not os.path.exists(filepath):
            return jsonify({'error': f'Table {table_name} not found'}), 404
        
        df = pd.read_csv(filepath)
        
        # Get pagination parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get total rows
        total_rows = len(df)
        
        # Get paginated data
        data = df.iloc[offset:offset+limit].to_dict('records')
        
        return jsonify({
            'table': table_name,
            'total_rows': total_rows,
            'limit': limit,
            'offset': offset,
            'data': data,
            'columns': list(df.columns)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/data/columns/<table_name>')
def get_table_columns(table_name):
    """Get columns of a specific table"""
    try:
        data_dir = 'data/'
        filepath = os.path.join(data_dir, f'{table_name}.csv')
        
        if not os.path.exists(filepath):
            return jsonify({'error': f'Table {table_name} not found'}), 404
        
        df = pd.read_csv(filepath)
        
        columns_info = []
        for col in df.columns:
            columns_info.append({
                'name': col,
                'type': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'unique_values': df[col].nunique()
            })
        
        return jsonify({
            'table': table_name,
            'columns': columns_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500