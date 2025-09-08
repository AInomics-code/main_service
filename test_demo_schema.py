#!/usr/bin/env python3
"""
Quick test to verify the static schema is working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rest.invocation import get_schema_context, DEMO_DATABASE_SCHEMA

def test_static_schema():
    """Test that static schema is returned correctly"""
    
    print("🧪 Testing static demo schema...")
    
    # Create mock state
    test_state = {"input": "How many products do we have?"}
    
    try:
        # Get schema context
        result = get_schema_context(test_state)
        
        print(f"✅ Schema context generated successfully")
        print(f"📊 Schema length: {len(result['schema_context'])} characters")
        
        # Check that it contains expected tables
        schema_text = result['schema_context']
        expected_tables = ['products', 'customers', 'orders']
        
        for table in expected_tables:
            if table in schema_text:
                print(f"✅ Table '{table}' found in schema")
            else:
                print(f"❌ Table '{table}' missing from schema")
        
        # Check for expected columns
        expected_columns = ['product_id', 'customer_id', 'order_id', 'name', 'status']
        for column in expected_columns:
            if column in schema_text:
                print(f"✅ Column '{column}' found in schema")
            else:
                print(f"❌ Column '{column}' missing from schema")
        
        print(f"\n📋 Schema preview:")
        print("=" * 50)
        print(DEMO_DATABASE_SCHEMA[:500] + "...")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_static_schema()
    if success:
        print("\n🎉 Static schema test completed successfully!")
    else:
        print("\n❌ Static schema test failed!")
        sys.exit(1)
