# scripts/discover_schema.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.schema_discovery import SchemaDiscovery

def discover_schema():
    """Run schema discovery and display results"""
    print("="*70)
    print("🔍 SCHEMA DISCOVERY")
    print("="*70)
    
    discovery = SchemaDiscovery()
    
    print("\n📊 Discovered Tables:")
    for table, info in discovery.schema.items():
        print(f"\n  📁 {table}")
        print(f"     Columns: {', '.join(info['columns'][:5])}{'...' if len(info['columns']) > 5 else ''}")
        print(f"     Total: {len(info['columns'])} columns, {info['row_count']} rows")
        
        if 'relationships' in info and info['relationships']:
            print(f"     Relationships:")
            for rel in info['relationships']:
                print(f"       → {rel['from_column']} → {rel['to_table']}.{rel['to_column']}")
    
    print("\n" + "="*70)
    print(f"✅ Discovered {len(discovery.schema)} tables")
    print("="*70)

if __name__ == "__main__":
    discover_schema()