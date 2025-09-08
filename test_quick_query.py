#!/usr/bin/env python3
"""
Quick test to verify SQLite queries work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.database_tools import query_database

def test_sqlite_connection():
    """Test basic SQLite queries"""
    
    print("🧪 Testing SQLite connection and queries...\n")
    
    # Test basic count queries
    test_queries = [
        "SELECT COUNT(*) as total_products FROM products",
        "SELECT COUNT(*) as total_customers FROM customers", 
        "SELECT COUNT(*) as total_orders FROM orders",
        "SELECT name, brand FROM products LIMIT 5",
        "SELECT name, city FROM customers LIMIT 3"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {query}")
        try:
            result = query_database.invoke({
                "query": query,
                "db_type": "sqlite"
            })
            
            if "Error" not in result:
                print(f"✅ Success!")
                # Show first 200 chars of result
                print(f"   Result: {result[:200]}...")
            else:
                print(f"❌ Failed: {result[:200]}...")
            
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    # Check if database exists first
    if not os.path.exists('demo_database.db'):
        print("❌ Database not found! Run 'python create_demo_db.py' first.")
        sys.exit(1)
    
    test_sqlite_connection()
    print("\n🎉 SQLite connection test completed!")
