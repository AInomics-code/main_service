#!/usr/bin/env python3
"""
Enhanced script to check the comprehensive demo database structure and provide business insights
"""
import sqlite3
from datetime import datetime

def check_database():
    try:
        conn = sqlite3.connect('demo_database.db')
        cursor = conn.cursor()
        
        print("🗄️ Comprehensive Business Database Check\n")
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print(f"📊 Tables found ({len(table_names)}): {table_names}\n")
        
        # Expected tables with their purpose
        expected_tables = {
            'suppliers': 'Product suppliers and vendors',
            'products': 'Product catalog with supplier relationships',
            'customers': 'Customer database (retail/wholesale)',
            'warehouses': 'Storage and distribution centers',
            'inventory': 'Stock levels per warehouse',
            'sales': 'Sales transactions (2024-2025)',
            'sale_details': 'Line items for each sale',
            'backorders': 'Pending customer orders',
            'routes': 'Delivery routes and drivers',
            'delivery_points': 'GPS points for deliveries',
            'inventory_movements': 'Stock movement history'
        }
        
        # Check each table structure
        for table_name in sorted(table_names):
            print(f"🔍 Table: {table_name}")
            if table_name in expected_tables:
                print(f"   Purpose: {expected_tables[table_name]}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   Columns ({len(columns)}): {[col[1] for col in columns]}")
            
            # Get count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Total records: {count}")
            
            # Show sample data for key tables
            if table_name in ['products', 'customers', 'sales', 'warehouses']:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                sample_data = cursor.fetchall()
                if sample_data:
                    print(f"   Sample data:")
                    for i, row in enumerate(sample_data, 1):
                        print(f"     Row {i}: {row[:4]}{'...' if len(row) > 4 else ''}")
            print()
        
        # Business insights
        print("📈 Business Data Insights:")
        
        # Date range check
        cursor.execute("SELECT MIN(sale_date), MAX(sale_date) FROM sales")
        min_date, max_date = cursor.fetchone()
        if min_date and max_date:
            print(f"   📅 Sales period: {min_date[:10]} to {max_date[:10]}")
        
        # Customer types
        cursor.execute("SELECT customer_type, COUNT(*) FROM customers GROUP BY customer_type")
        customer_stats = cursor.fetchall()
        print(f"   👥 Customer distribution: {dict(customer_stats)}")
        
        # Top product categories
        cursor.execute("SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY COUNT(*) DESC LIMIT 3")
        top_categories = cursor.fetchall()
        print(f"   📦 Top product categories: {dict(top_categories)}")
        
        # Sales summary
        cursor.execute("SELECT transaction_type, COUNT(*), SUM(total) FROM sales GROUP BY transaction_type")
        sales_summary = cursor.fetchall()
        print("   💰 Sales summary:")
        for trans_type, count, total in sales_summary:
            print(f"      {trans_type}: {count} transactions, ${total:,.2f}")
        
        # Warehouse capacity utilization
        cursor.execute("""
            SELECT w.name, w.max_capacity, 
                   COUNT(i.product_id) as products_stored,
                   SUM(i.available_quantity) as total_stock
            FROM warehouses w
            LEFT JOIN inventory i ON w.warehouse_id = i.warehouse_id
            GROUP BY w.warehouse_id
            ORDER BY total_stock DESC
            LIMIT 3
        """)
        warehouse_stats = cursor.fetchall()
        print("   🏬 Top warehouses by stock:")
        for name, capacity, products, stock in warehouse_stats:
            print(f"      {name}: {stock or 0} units across {products or 0} products")
        
        # Backorder priority distribution
        cursor.execute("SELECT priority, COUNT(*) FROM backorders GROUP BY priority ORDER BY COUNT(*) DESC")
        backorder_priorities = cursor.fetchall()
        print(f"   ⏳ Backorder priorities: {dict(backorder_priorities)}")
        
        conn.close()
        print("\n✅ Database analysis completed!")
        print("\n🎯 This database supports queries about:")
        print("   • Product sales performance and trends")
        print("   • Customer behavior analysis") 
        print("   • Inventory management across warehouses")
        print("   • Backorder management and priorities")
        print("   • Route optimization and delivery logistics")
        print("   • Supplier performance and relationships")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except FileNotFoundError:
        print("❌ Database file not found. Run 'python create_demo_db.py' first.")

if __name__ == "__main__":
    check_database()
