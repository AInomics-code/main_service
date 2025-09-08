#!/usr/bin/env python3
"""
Script simple para crear base de datos demo local con SQLite
"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    """Create basic tables"""
    conn = sqlite3.connect('demo_database.db')
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        cost REAL,
        brand TEXT,
        category TEXT
    )
    ''')
    
    # Create customers table  
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        city TEXT,
        state TEXT,
        status TEXT DEFAULT 'active'
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        order_date DATETIME,
        status TEXT DEFAULT 'pending',
        total REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')
    
    conn.commit()
    return conn

def populate_products(cursor, count=30):
    """Populate products table"""
    products = [
        ('PROD_001', 'Hellmanns Mayonnaise 12oz', 'active', 4.99, 'Hellmanns', 'Condiments'),
        ('PROD_002', 'Whole Milk Gallon', 'active', 3.89, 'Organic Valley', 'Dairy'),
        ('PROD_003', 'White Rice 2lb', 'active', 2.49, 'Uncle Ben\'s', 'Grains'),
        ('PROD_004', 'Whole Chicken', 'active', 12.99, 'Perdue', 'Meat'),
        ('PROD_005', 'Coca Cola 2L', 'active', 2.99, 'Coca Cola', 'Beverages'),
        ('PROD_006', 'Greek Yogurt', 'active', 5.49, 'Chobani', 'Dairy'),
        ('PROD_007', 'Tomato Sauce', 'active', 1.99, 'Hunt\'s', 'Condiments'),
        ('PROD_008', 'Yellow Mustard', 'active', 1.79, 'French\'s', 'Condiments'),
        ('PROD_009', 'Vegetable Oil', 'active', 4.99, 'Wesson', 'Cooking'),
        ('PROD_010', 'Black Beans Can', 'active', 1.29, 'Bush\'s', 'Canned Goods'),
        ('PROD_011', 'Sliced Bread', 'active', 2.99, 'Wonder', 'Bakery'),
        ('PROD_012', 'Peanut Butter', 'active', 4.49, 'Jif', 'Spreads'),
        ('PROD_013', 'Orange Juice', 'active', 3.99, 'Tropicana', 'Beverages'),
        ('PROD_014', 'Cheddar Cheese', 'active', 5.99, 'Kraft', 'Dairy'),
        ('PROD_015', 'Ground Beef 1lb', 'active', 6.99, 'Certified Angus', 'Meat'),
        ('PROD_016', 'Bananas 3lb', 'active', 2.49, 'Chiquita', 'Produce'),
        ('PROD_017', 'Potato Chips', 'active', 3.49, 'Lay\'s', 'Snacks'),
        ('PROD_018', 'Cereal Box', 'active', 4.99, 'Kellogg\'s', 'Breakfast'),
        ('PROD_019', 'Pasta 1lb', 'active', 1.99, 'Barilla', 'Pasta'),
        ('PROD_020', 'Frozen Pizza', 'active', 5.99, 'DiGiorno', 'Frozen'),
    ]
    
    # Generate additional products to reach 30
    additional_products = [
        'Chicken Breast', 'Salmon Fillet', 'Apple Juice', 'Crackers', 'Ice Cream', 
        'Cookies', 'Soup Can', 'Bagels', 'Coffee', 'Tea Bags'
    ]
    brands = ['Generic', 'Store Brand', 'Premium', 'Organic', 'Natural']
    categories = ['Meat', 'Beverages', 'Snacks', 'Dairy', 'Pantry']
    
    for i in range(21, count + 1):
        products.append((
            f'PROD_{i:03d}',
            f'{random.choice(additional_products)} {i-20}',
            'active',
            round(random.uniform(1.99, 15.99), 2),
            random.choice(brands),
            random.choice(categories)
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?)',
        products
    )

def populate_customers(cursor, count=50):
    """Populate customers table"""  
    first_names = ['John', 'Sarah', 'Michael', 'Jennifer', 'David', 'Lisa', 'Robert', 'Maria', 'William', 'Jessica']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Miami']
    states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'FL', 'WA', 'NV', 'CO']
    
    customers = []
    for i in range(1, count + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customers.append((
            f'CUST_{i:03d}',
            f'{first_name} {last_name}',
            f'{first_name.lower()}.{last_name.lower()}{i}@email.com',
            f'({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}',
            random.choice(cities),
            random.choice(states),
            'active'
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)',
        customers
    )

def populate_orders(cursor, count=200):
    """Populate orders table"""
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    orders = []
    for i in range(1, count + 1):
        order_date = datetime.now() - timedelta(days=random.randint(0, 365))
        orders.append((
            f'ORD_{i:06d}',
            f'CUST_{random.randint(1, 50):03d}',
            order_date.isoformat(),
            random.choice(statuses),
            round(random.uniform(15.99, 299.99), 2)
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?, ?)',
        orders
    )

def main():
    print("🔧 Creating demo database...")
    
    conn = create_database()
    cursor = conn.cursor()
    
    try:
        print("📦 Populating products...")
        populate_products(cursor, 30)
        
        print("👥 Populating customers...")  
        populate_customers(cursor, 50)
        
        print("🛒 Populating orders...")
        populate_orders(cursor, 200)
        
        conn.commit()
        
        print("""
✅ Demo database created: demo_database.db
📊 Data created:
   • 30 products  
   • 50 customers
   • 200 orders
""")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
