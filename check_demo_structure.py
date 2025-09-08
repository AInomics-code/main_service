#!/usr/bin/env python3
"""
Quick script to check the demo database structure and sample data
"""
import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('demo_database.db')
        cursor = conn.cursor()
        
        print("🗄️ Database Structure Check\n")
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Tables found: {[table[0] for table in tables]}\n")
        
        # Check each table
        for table_name in [t[0] for t in tables]:
            print(f"🔍 Table: {table_name}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   Columns: {[col[1] for col in columns]}")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()
            if sample_data:
                print(f"   Sample data:")
                for i, row in enumerate(sample_data, 1):
                    print(f"     Row {i}: {row}")
            
            # Get count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Total records: {count}\n")
        
        conn.close()
        print("✅ Database check completed!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except FileNotFoundError:
        print("❌ Database file not found. Run 'python create_demo_db.py' first.")

if __name__ == "__main__":
    check_database()
