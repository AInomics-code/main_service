#!/usr/bin/env python3
"""
Manufacturing Company Database - Complete Production to Distribution Flow
Empresa Productora con distribución completa desde materias primas hasta entrega
"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    """Create all manufacturing and distribution tables"""
    conn = sqlite3.connect('demo_database.db')
    cursor = conn.cursor()
    
    # 1. Raw Materials Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS raw_materials (
        raw_material_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        unit_measure TEXT,
        cost_per_unit REAL,
        supplier_name TEXT,
        supplier_contact TEXT,
        min_stock_level INTEGER,
        max_stock_level INTEGER
    )
    ''')
    
    # 2. Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        unit_price REAL,
        production_cost REAL,
        unit_measure TEXT,
        shelf_life_days INTEGER,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # 3. Recipes (BOM - Bill of Materials)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        recipe_id TEXT PRIMARY KEY,
        product_id TEXT,
        raw_material_id TEXT,
        quantity_needed REAL,
        waste_percentage REAL DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (raw_material_id) REFERENCES raw_materials (raw_material_id)
    )
    ''')
    
    # 4. Production Orders
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS production_orders (
        production_order_id TEXT PRIMARY KEY,
        product_id TEXT,
        planned_quantity INTEGER,
        order_date DATETIME,
        planned_start_date DATETIME,
        planned_end_date DATETIME,
        actual_start_date DATETIME,
        actual_end_date DATETIME,
        status TEXT DEFAULT 'planned',
        warehouse_id TEXT,
        priority TEXT DEFAULT 'normal',
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
    )
    ''')
    
    # 5. Production Batches
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS production_batches (
        batch_id TEXT PRIMARY KEY,
        production_order_id TEXT,
        batch_number TEXT,
        produced_quantity INTEGER,
        quality_grade TEXT DEFAULT 'A',
        production_date DATETIME,
        expiry_date DATETIME,
        production_line TEXT,
        operator_name TEXT,
        FOREIGN KEY (production_order_id) REFERENCES production_orders (production_order_id)
    )
    ''')
    
    # 6. Customers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        customer_type TEXT DEFAULT 'retail',
        credit_limit REAL,
        payment_terms TEXT
    )
    ''')
    
    # 7. Customer Orders
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer_orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        order_date DATETIME,
        requested_delivery_date DATETIME,
        order_status TEXT DEFAULT 'pending',
        total_amount REAL,
        payment_method TEXT,
        sales_rep TEXT,
        special_instructions TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')
    
    # 8. Order Details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_details (
        order_id TEXT,
        product_id TEXT,
        quantity_ordered INTEGER,
        unit_price REAL,
        line_total REAL,
        production_priority TEXT DEFAULT 'normal',
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (order_id) REFERENCES customer_orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    # 9. Warehouses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS warehouses (
        warehouse_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT,
        city TEXT,
        warehouse_type TEXT,
        max_capacity INTEGER,
        current_utilization REAL DEFAULT 0,
        manager_name TEXT
    )
    ''')
    
    # 10. Product Inventory
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_inventory (
        product_id TEXT,
        warehouse_id TEXT,
        batch_id TEXT,
        available_quantity INTEGER DEFAULT 0,
        reserved_quantity INTEGER DEFAULT 0,
        production_date DATETIME,
        expiry_date DATETIME,
        quality_grade TEXT DEFAULT 'A',
        location_code TEXT,
        PRIMARY KEY (product_id, warehouse_id, batch_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id),
        FOREIGN KEY (batch_id) REFERENCES production_batches (batch_id)
    )
    ''')
    
    # 11. Raw Material Inventory
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS raw_material_inventory (
        raw_material_id TEXT,
        warehouse_id TEXT,
        available_quantity INTEGER DEFAULT 0,
        reserved_quantity INTEGER DEFAULT 0,
        last_received_date DATETIME,
        location_code TEXT,
        PRIMARY KEY (raw_material_id, warehouse_id),
        FOREIGN KEY (raw_material_id) REFERENCES raw_materials (raw_material_id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
    )
    ''')
    
    # 12. Backorders
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backorders (
        backorder_id TEXT PRIMARY KEY,
        order_id TEXT,
        product_id TEXT,
        quantity_pending INTEGER,
        original_due_date DATETIME,
        new_promised_date DATETIME,
        priority TEXT DEFAULT 'normal',
        reason TEXT,
        warehouse_id TEXT,
        FOREIGN KEY (order_id) REFERENCES customer_orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
    )
    ''')
    
    # 13. Routes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS routes (
        route_id TEXT PRIMARY KEY,
        route_name TEXT NOT NULL,
        description TEXT,
        assigned_vehicle TEXT,
        driver_name TEXT,
        driver_phone TEXT,
        max_capacity_kg REAL,
        max_capacity_volume REAL,
        coverage_zone TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # 14. Shipments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shipments (
        shipment_id TEXT PRIMARY KEY,
        route_id TEXT,
        shipment_date DATETIME,
        departure_warehouse_id TEXT,
        total_weight REAL,
        total_volume REAL,
        number_of_orders INTEGER,
        departure_time DATETIME,
        estimated_return_time DATETIME,
        shipment_status TEXT DEFAULT 'loading',
        FOREIGN KEY (route_id) REFERENCES routes (route_id),
        FOREIGN KEY (departure_warehouse_id) REFERENCES warehouses (warehouse_id)
    )
    ''')
    
    # 15. Delivery Details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS delivery_details (
        delivery_id TEXT PRIMARY KEY,
        shipment_id TEXT,
        order_id TEXT,
        delivery_sequence INTEGER,
        estimated_delivery_time DATETIME,
        actual_delivery_time DATETIME,
        delivery_status TEXT DEFAULT 'pending',
        customer_signature TEXT,
        delivery_notes TEXT,
        FOREIGN KEY (shipment_id) REFERENCES shipments (shipment_id),
        FOREIGN KEY (order_id) REFERENCES customer_orders (order_id)
    )
    ''')
    
    # 16. Inventory Movements
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_movements (
        movement_id TEXT PRIMARY KEY,
        movement_type TEXT,
        product_id TEXT,
        warehouse_id TEXT,
        batch_id TEXT,
        quantity INTEGER,
        movement_date DATETIME,
        reference_id TEXT,
        notes TEXT,
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id),
        FOREIGN KEY (batch_id) REFERENCES production_batches (batch_id)
    )
    ''')
    
    # 17. Raw Material Consumption
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS raw_material_consumption (
        consumption_id TEXT PRIMARY KEY,
        production_order_id TEXT,
        raw_material_id TEXT,
        quantity_consumed REAL,
        consumption_date DATETIME,
        batch_number TEXT,
        waste_quantity REAL DEFAULT 0,
        FOREIGN KEY (production_order_id) REFERENCES production_orders (production_order_id),
        FOREIGN KEY (raw_material_id) REFERENCES raw_materials (raw_material_id)
    )
    ''')
    
    conn.commit()
    return conn

def populate_raw_materials(cursor, count=25):
    """Populate raw materials table"""
    raw_materials = [
        ('RM_001', 'Wheat Flour', 'High-grade wheat flour for bread production', 'kg', 0.85, 'Grain Mills Inc', 'grain@mills.com', 500, 2000),
        ('RM_002', 'Sugar', 'Refined white sugar', 'kg', 1.20, 'Sweet Supply Co', 'orders@sweetsupply.com', 300, 1500),
        ('RM_003', 'Cocoa Powder', 'Premium cocoa powder', 'kg', 8.50, 'Chocolate Source Ltd', 'sales@chocosource.com', 100, 500),
        ('RM_004', 'Vanilla Extract', 'Pure vanilla extract', 'liter', 45.00, 'Flavor Essentials', 'info@flavoress.com', 20, 100),
        ('RM_005', 'Eggs', 'Fresh grade A eggs', 'dozen', 2.50, 'Farm Fresh Eggs', 'orders@farmfresh.com', 200, 800),
        ('RM_006', 'Butter', 'Unsalted premium butter', 'kg', 6.80, 'Dairy Pure', 'sales@dairypure.com', 150, 600),
        ('RM_007', 'Milk Powder', 'Whole milk powder', 'kg', 4.20, 'Milk Products Inc', 'supply@milkprod.com', 400, 1200),
        ('RM_008', 'Yeast', 'Active dry yeast', 'kg', 12.00, 'Baker Supplies', 'yeast@bakersup.com', 50, 200),
        ('RM_009', 'Salt', 'Food grade salt', 'kg', 0.60, 'Salt Works', 'orders@saltworks.com', 800, 2500),
        ('RM_010', 'Tomato Paste', 'Concentrated tomato paste', 'kg', 3.80, 'Red Gold Tomatoes', 'sales@redgold.com', 200, 800),
        ('RM_011', 'Olive Oil', 'Extra virgin olive oil', 'liter', 15.50, 'Mediterranean Oils', 'orders@medoils.com', 100, 400),
        ('RM_012', 'Cheese Powder', 'Cheddar cheese powder', 'kg', 18.00, 'Cheese Factory', 'sales@cheesefact.com', 80, 300),
        ('RM_013', 'Corn Starch', 'Food grade corn starch', 'kg', 1.85, 'Starch Solutions', 'info@starchsol.com', 300, 1000),
        ('RM_014', 'Baking Powder', 'Double acting baking powder', 'kg', 5.20, 'Rise & Shine Co', 'orders@riseshine.com', 100, 400),
        ('RM_015', 'Chicken Meat', 'Fresh chicken breast', 'kg', 8.50, 'Poultry Prime', 'meat@poulprime.com', 200, 600),
    ]
    
    additional_materials = [
        'Beef Stock', 'Vegetable Oil', 'Garlic Powder', 'Onion Powder', 'Black Pepper',
        'Paprika', 'Oregano', 'Thyme', 'Food Coloring', 'Preservatives'
    ]
    
    suppliers = ['Quality Materials Ltd', 'Bulk Ingredients Co', 'Fresh Supply Inc', 'Premium Raw Materials']
    
    for i in range(16, count + 1):
        raw_materials.append((
            f'RM_{i:03d}',
            f'{random.choice(additional_materials)} {i-15}',
            f'High quality {random.choice(additional_materials).lower()}',
            random.choice(['kg', 'liter', 'ton', 'bag']),
            round(random.uniform(0.5, 25.0), 2),
            random.choice(suppliers),
            f'supplier{i}@materials.com',
            random.randint(50, 500),
            random.randint(500, 2000)
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO raw_materials VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        raw_materials
    )

def populate_products(cursor, count=30):
    """Populate manufactured products table"""
    products = [
        ('PROD_001', 'Artisan Bread Loaf', 'Fresh baked artisan bread', 'Bakery', 4.50, 2.80, 'loaf', 30, 1),
        ('PROD_002', 'Chocolate Chip Cookies', 'Premium chocolate chip cookies', 'Bakery', 8.99, 5.20, 'dozen', 14, 1),
        ('PROD_003', 'Vanilla Cake', 'Moist vanilla layer cake', 'Bakery', 25.00, 15.50, 'cake', 7, 1),
        ('PROD_004', 'Pizza Margherita', 'Classic margherita pizza', 'Prepared Foods', 12.99, 7.80, 'pizza', 3, 1),
        ('PROD_005', 'Chicken Soup', 'Homestyle chicken soup', 'Prepared Foods', 6.50, 4.20, 'can', 24, 1),
        ('PROD_006', 'Pasta Sauce', 'Traditional tomato pasta sauce', 'Sauces', 4.99, 2.90, 'jar', 18, 1),
        ('PROD_007', 'Granola Bars', 'Healthy granola energy bars', 'Snacks', 7.50, 4.30, 'box', 21, 1),
        ('PROD_008', 'Beef Stew', 'Hearty beef and vegetable stew', 'Prepared Foods', 9.99, 6.50, 'can', 24, 1),
        ('PROD_009', 'Dinner Rolls', 'Soft dinner rolls pack', 'Bakery', 3.99, 2.10, 'pack', 5, 1),
        ('PROD_010', 'Cheese Crackers', 'Crunchy cheese flavored crackers', 'Snacks', 5.49, 3.20, 'box', 12, 1),
        ('PROD_011', 'Apple Pie', 'Traditional apple pie', 'Bakery', 18.99, 11.50, 'pie', 5, 1),
        ('PROD_012', 'Vegetable Soup', 'Mixed vegetable soup', 'Prepared Foods', 5.99, 3.80, 'can', 24, 1),
        ('PROD_013', 'Breakfast Muffins', 'Blueberry breakfast muffins', 'Bakery', 6.99, 4.10, 'pack', 7, 1),
        ('PROD_014', 'BBQ Sauce', 'Smoky barbecue sauce', 'Sauces', 4.50, 2.60, 'bottle', 12, 1),
        ('PROD_015', 'Energy Bars', 'Protein energy bars', 'Snacks', 12.99, 7.80, 'box', 30, 1),
    ]
    
    additional_products = [
        'Fruit Tarts', 'Meat Pies', 'Pasta Salad', 'Sandwich Wraps', 'Protein Shakes',
        'Cookies', 'Brownies', 'Salad Dressing', 'Marinara Sauce', 'Trail Mix',
        'Yogurt Parfait', 'Smoothie Bowls', 'Quinoa Salad', 'Veggie Burgers', 'Fruit Smoothies'
    ]
    
    categories = ['Bakery', 'Prepared Foods', 'Sauces', 'Snacks', 'Beverages']
    
    for i in range(16, count + 1):
        production_cost = round(random.uniform(2.0, 12.0), 2)
        unit_price = round(production_cost * random.uniform(1.5, 2.2), 2)
        shelf_life = random.choice([3, 5, 7, 14, 21, 30, 45])
        
        products.append((
            f'PROD_{i:03d}',
            f'{random.choice(additional_products)} {i-15}',
            f'High quality {random.choice(additional_products).lower()}',
            random.choice(categories),
            unit_price,
            production_cost,
            random.choice(['piece', 'box', 'jar', 'bottle', 'pack', 'can']),
            shelf_life,
            1
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        products
    )

def populate_recipes(cursor):
    """Populate recipes (BOM) table"""
    cursor.execute('SELECT product_id FROM products')
    products = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT raw_material_id FROM raw_materials')
    raw_materials = [row[0] for row in cursor.fetchall()]
    
    recipes = []
    recipe_counter = 1
    
    for product_id in products:
        num_materials = random.randint(2, 5)
        selected_materials = random.sample(raw_materials, min(num_materials, len(raw_materials)))
        
        for raw_material_id in selected_materials:
            quantity_needed = round(random.uniform(0.1, 5.0), 2)
            waste_percentage = round(random.uniform(2.0, 8.0), 1)
            
            recipes.append((
                f'RCP_{recipe_counter:06d}',
                product_id,
                raw_material_id,
                quantity_needed,
                waste_percentage,
                1
            ))
            recipe_counter += 1
    
    cursor.executemany(
        'INSERT OR REPLACE INTO recipes VALUES (?, ?, ?, ?, ?, ?)',
        recipes
    )

def populate_warehouses(cursor, count=6):
    """Populate warehouses table"""
    warehouses = [
        ('WH_001', 'Main Production Facility', '1000 Manufacturing Blvd', 'Miami', 'production', 8000, 0.0, 'Carlos Rodriguez'),
        ('WH_002', 'Distribution Center North', '2500 Distribution Ave', 'Atlanta', 'distribution', 12000, 0.0, 'Maria Santos'),
        ('WH_003', 'Cold Storage Facility', '3300 Cold Chain Dr', 'Denver', 'cold_storage', 5000, 0.0, 'David Chen'),
        ('WH_004', 'Raw Materials Warehouse', '4400 Supply Chain Ln', 'Chicago', 'raw_materials', 6000, 0.0, 'Ana Martinez'),
        ('WH_005', 'West Coast Distribution', '5500 Pacific Way', 'Los Angeles', 'distribution', 10000, 0.0, 'Roberto Silva'),
        ('WH_006', 'Quality Control Center', '6600 QC Boulevard', 'Dallas', 'quality_control', 3000, 0.0, 'Jessica Brown'),
    ]
    
    cursor.executemany(
        'INSERT OR REPLACE INTO warehouses VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        warehouses
    )

def populate_customers(cursor, count=120):
    """Populate customers table"""
    first_names = ['Carlos', 'Maria', 'Roberto', 'Ana', 'Luis', 'Patricia', 'Miguel', 'Isabel', 'Jorge', 'Carmen',
                   'Rafael', 'Sofia', 'Fernando', 'Lucia', 'Antonio', 'Elena', 'Jose', 'Monica', 'Pedro', 'Gabriela']
    last_names = ['Rodriguez', 'Martinez', 'Garcia', 'Lopez', 'Hernandez', 'Gonzalez', 'Perez', 'Sanchez', 'Ramirez', 'Cruz',
                  'Torres', 'Flores', 'Rivera', 'Gomez', 'Diaz', 'Mendoza', 'Castro', 'Vargas', 'Morales', 'Ortega']
    cities = ['Miami', 'Houston', 'Los Angeles', 'Phoenix', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso', 'Charlotte']
    states = ['FL', 'TX', 'CA', 'AZ', 'NC', 'NV', 'CO', 'GA', 'IL', 'OR']
    
    customers = []
    for i in range(1, count + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        city = random.choice(cities)
        state = random.choice(states)
        
        if i <= 20:
            customer_type = 'distributor'
            credit_limit = random.randint(50000, 200000)
            payment_terms = '30 days'
        elif i <= 50:
            customer_type = 'wholesale'
            credit_limit = random.randint(10000, 50000)
            payment_terms = random.choice(['15 days', '30 days'])
        else:
            customer_type = 'retail'
            credit_limit = random.randint(1000, 10000)
            payment_terms = random.choice(['cash', '7 days', '15 days'])
        
        customers.append((
            f'CUST_{i:03d}',
            f'{first_name} {last_name}',
            f'{first_name.lower()}.{last_name.lower()}{i}@email.com',
            f'({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}',
            f'{random.randint(100, 9999)} {random.choice(["Main St", "Oak Ave", "Industrial Blvd", "Commerce Dr"])}',
            city,
            state,
            f'{random.randint(10000, 99999):05d}',
            customer_type,
            credit_limit,
            payment_terms
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        customers
    )

def populate_production_orders(cursor, count=300):
    """Populate production orders table"""
    cursor.execute('SELECT product_id FROM products')
    products = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT warehouse_id FROM warehouses WHERE warehouse_type = "production"')
    production_warehouses = [row[0] for row in cursor.fetchall()]
    
    statuses = ['planned', 'in_progress', 'completed', 'cancelled']
    priorities = ['low', 'normal', 'high', 'urgent']
    
    production_orders = []
    for i in range(1, count + 1):
        order_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
        planned_start = order_date + timedelta(days=random.randint(1, 7))
        planned_end = planned_start + timedelta(days=random.randint(1, 5))
        
        status = random.choice(statuses)
        actual_start = planned_start + timedelta(days=random.randint(-1, 2)) if status in ['in_progress', 'completed'] else None
        actual_end = planned_end + timedelta(days=random.randint(-2, 3)) if status == 'completed' else None
        
        production_orders.append((
            f'PO_{i:06d}',
            random.choice(products),
            random.randint(50, 500),
            order_date.isoformat(),
            planned_start.isoformat(),
            planned_end.isoformat(),
            actual_start.isoformat() if actual_start else None,
            actual_end.isoformat() if actual_end else None,
            status,
            random.choice(production_warehouses),
            random.choice(priorities)
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO production_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        production_orders
    )

def populate_production_batches(cursor):
    """Populate production batches table"""
    cursor.execute('SELECT production_order_id, product_id, planned_quantity FROM production_orders WHERE status = "completed"')
    completed_orders = cursor.fetchall()
    
    quality_grades = ['A', 'B', 'C']
    production_lines = ['Line_A', 'Line_B', 'Line_C', 'Line_D']
    operators = ['Juan Martinez', 'Sofia Rodriguez', 'Carlos Perez', 'Ana Garcia', 'Luis Torres']
    
    batches = []
    batch_counter = 1
    
    for production_order_id, product_id, planned_quantity in completed_orders:
        num_batches = random.randint(1, 3)
        remaining_quantity = planned_quantity
        
        for batch_num in range(1, num_batches + 1):
            if batch_num == num_batches:
                produced_quantity = remaining_quantity
            else:
                produced_quantity = random.randint(10, remaining_quantity // 2)
                remaining_quantity -= produced_quantity
            
            production_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
            
            cursor.execute('SELECT shelf_life_days FROM products WHERE product_id = ?', (product_id,))
            shelf_life = cursor.fetchone()[0]
            expiry_date = production_date + timedelta(days=shelf_life)
            
            batches.append((
                f'BATCH_{batch_counter:06d}',
                production_order_id,
                f'B{batch_counter:04d}',
                produced_quantity,
                random.choice(quality_grades),
                production_date.isoformat(),
                expiry_date.isoformat(),
                random.choice(production_lines),
                random.choice(operators)
            ))
            batch_counter += 1
    
    cursor.executemany(
        'INSERT OR REPLACE INTO production_batches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        batches
    )

def populate_customer_orders(cursor, count=800):
    """Populate customer orders table"""
    cursor.execute('SELECT customer_id, customer_type FROM customers')
    customers = cursor.fetchall()
    
    order_statuses = ['pending', 'confirmed', 'in_production', 'ready', 'shipped', 'delivered']
    payment_methods = ['cash', 'credit_card', 'bank_transfer', 'check', 'credit_terms']
    sales_reps = ['Miguel Santos', 'Carmen Lopez', 'Roberto Silva', 'Elena Martinez', 'Diego Fernandez']
    
    orders = []
    for i in range(1, count + 1):
        customer_id, customer_type = random.choice(customers)
        order_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
        requested_delivery = order_date + timedelta(days=random.randint(3, 21))
        
        if customer_type == 'distributor':
            total_amount = round(random.uniform(5000, 25000), 2)
        elif customer_type == 'wholesale':
            total_amount = round(random.uniform(1000, 8000), 2)
        else:
            total_amount = round(random.uniform(100, 2000), 2)
        
        orders.append((
            f'ORD_{i:06d}',
            customer_id,
            order_date.isoformat(),
            requested_delivery.isoformat(),
            random.choice(order_statuses),
            total_amount,
            random.choice(payment_methods),
            random.choice(sales_reps),
            'Standard delivery' if random.random() > 0.2 else 'Express delivery required'
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO customer_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        orders
    )

def populate_order_details(cursor):
    """Populate order details table"""
    cursor.execute('SELECT order_id FROM customer_orders')
    orders = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT product_id, unit_price FROM products')
    products = cursor.fetchall()
    
    priorities = ['low', 'normal', 'high', 'urgent']
    
    order_details = []
    for order_id in orders:
        num_products = random.randint(1, 6)
        selected_products = random.sample(products, min(num_products, len(products)))
        
        for product_id, unit_price in selected_products:
            quantity = random.randint(1, 50)
            line_total = quantity * unit_price
            
            order_details.append((
                order_id,
                product_id,
                quantity,
                unit_price,
                line_total,
                random.choice(priorities)
            ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO order_details VALUES (?, ?, ?, ?, ?, ?)',
        order_details
    )

def populate_product_inventory(cursor):
    """Populate product inventory from production batches"""
    cursor.execute('''
        SELECT b.batch_id, po.product_id, b.produced_quantity, b.quality_grade, 
               b.production_date, b.expiry_date, po.warehouse_id
        FROM production_batches b
        JOIN production_orders po ON b.production_order_id = po.production_order_id
    ''')
    batches = cursor.fetchall()
    
    inventory_records = []
    location_codes = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']
    
    for batch_id, product_id, produced_quantity, quality_grade, production_date, expiry_date, warehouse_id in batches:
        reserved = random.randint(0, min(20, produced_quantity // 2))
        available = produced_quantity - reserved
        
        inventory_records.append((
            product_id,
            warehouse_id,
            batch_id,
            available,
            reserved,
            production_date,
            expiry_date,
            quality_grade,
            random.choice(location_codes)
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO product_inventory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        inventory_records
    )

def populate_raw_material_inventory(cursor):
    """Populate raw material inventory"""
    cursor.execute('SELECT raw_material_id, min_stock_level, max_stock_level FROM raw_materials')
    raw_materials = cursor.fetchall()
    
    cursor.execute('SELECT warehouse_id FROM warehouses WHERE warehouse_type IN ("raw_materials", "production")')
    warehouses = [row[0] for row in cursor.fetchall()]
    
    inventory_records = []
    location_codes = ['RM-A1', 'RM-A2', 'RM-B1', 'RM-B2', 'RM-C1', 'RM-C2']
    
    for raw_material_id, min_stock, max_stock in raw_materials:
        for warehouse_id in warehouses:
            if random.random() < 0.8:
                available = random.randint(min_stock, max_stock)
                reserved = random.randint(0, available // 4)
                last_received = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
                
                inventory_records.append((
                    raw_material_id,
                    warehouse_id,
                    available,
                    reserved,
                    last_received.isoformat(),
                    random.choice(location_codes)
                ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO raw_material_inventory VALUES (?, ?, ?, ?, ?, ?)',
        inventory_records
    )

def populate_backorders(cursor, count=150):
    """Populate backorders table"""
    cursor.execute('SELECT order_id, customer_id FROM customer_orders WHERE order_status IN ("pending", "confirmed")')
    pending_orders = cursor.fetchall()
    
    cursor.execute('SELECT product_id FROM products')
    products = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT warehouse_id FROM warehouses')
    warehouses = [row[0] for row in cursor.fetchall()]
    
    priorities = ['low', 'normal', 'high', 'urgent']
    reasons = ['out_of_stock', 'production_delay', 'quality_issue', 'raw_material_shortage']
    
    backorders = []
    for i in range(1, min(count, len(pending_orders)) + 1):
        order_id, customer_id = random.choice(pending_orders)
        original_due = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
        new_promised = original_due + timedelta(days=random.randint(3, 21))
        
        backorders.append((
            f'BO_{i:06d}',
            order_id,
            random.choice(products),
            random.randint(1, 25),
            original_due.isoformat(),
            new_promised.isoformat(),
            random.choice(priorities),
            random.choice(reasons),
            random.choice(warehouses)
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO backorders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        backorders
    )

def populate_routes(cursor, count=10):
    """Populate delivery routes table"""
    routes = [
        ('RT_001', 'Metro North Route', 'Northern metropolitan area', 'TRUCK-001', 'Carlos Mendez', '+1-555-7001', 3000, 15, 'North Metro', 1),
        ('RT_002', 'South Side Express', 'Southern city districts', 'VAN-002', 'Maria Elena Ruiz', '+1-555-7002', 1500, 8, 'South Metro', 1),
        ('RT_003', 'Industrial Zone', 'Industrial and warehouse areas', 'TRUCK-003', 'Roberto Santos', '+1-555-7003', 5000, 25, 'Industrial', 1),
        ('RT_004', 'West Coast Route', 'Western coastal deliveries', 'TRUCK-004', 'Ana Patricia Lopez', '+1-555-7004', 4000, 20, 'West Coast', 1),
        ('RT_005', 'Downtown Express', 'City center rapid delivery', 'VAN-005', 'Luis Fernando Torres', '+1-555-7005', 1000, 5, 'Downtown', 1),
        ('RT_006', 'Suburban Circuit', 'Suburban residential areas', 'VAN-006', 'Carmen Sofia Diaz', '+1-555-7006', 2000, 12, 'Suburbs', 1),
        ('RT_007', 'Highway Corridor', 'Highway commercial route', 'TRUCK-007', 'Jorge Alberto Cruz', '+1-555-7007', 6000, 30, 'Highway', 1),
        ('RT_008', 'Local Delivery', 'Local short-distance route', 'VAN-008', 'Isabel Morales', '+1-555-7008', 800, 4, 'Local', 1),
        ('RT_009', 'Night Express', 'Overnight delivery service', 'VAN-009', 'Miguel Angel Vargas', '+1-555-7009', 1200, 6, 'Overnight', 1),
        ('RT_010', 'Weekend Special', 'Weekend delivery service', 'TRUCK-010', 'Gabriela Fernandez', '+1-555-7010', 2500, 14, 'Weekend', 1),
    ]
    
    cursor.executemany(
        'INSERT OR REPLACE INTO routes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        routes
    )

def populate_shipments(cursor, count=200):
    """Populate shipments table"""
    cursor.execute('SELECT route_id, max_capacity_kg, max_capacity_volume FROM routes')
    routes = cursor.fetchall()
    
    cursor.execute('SELECT warehouse_id FROM warehouses WHERE warehouse_type = "distribution"')
    distribution_warehouses = [row[0] for row in cursor.fetchall()]
    
    shipment_statuses = ['loading', 'in_transit', 'delivered', 'returned']
    
    shipments = []
    for i in range(1, count + 1):
        route_id, max_weight, max_volume = random.choice(routes)
        shipment_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
        departure_time = shipment_date + timedelta(hours=random.randint(6, 14))
        estimated_return = departure_time + timedelta(hours=random.randint(4, 12))
        
        total_weight = random.uniform(max_weight * 0.3, max_weight * 0.9)
        total_volume = random.uniform(max_volume * 0.4, max_volume * 0.95)
        num_orders = random.randint(5, 25)
        
        shipments.append((
            f'SHIP_{i:06d}',
            route_id,
            shipment_date.isoformat(),
            random.choice(distribution_warehouses),
            round(total_weight, 2),
            round(total_volume, 2),
            num_orders,
            departure_time.isoformat(),
            estimated_return.isoformat(),
            random.choice(shipment_statuses)
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO shipments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        shipments
    )

def populate_delivery_details(cursor):
    """Populate delivery details table"""
    cursor.execute('SELECT shipment_id, number_of_orders FROM shipments')
    shipments = cursor.fetchall()
    
    cursor.execute('SELECT order_id FROM customer_orders WHERE order_status IN ("ready", "shipped", "delivered")')
    available_orders = [row[0] for row in cursor.fetchall()]
    
    delivery_statuses = ['pending', 'delivered', 'failed', 'rescheduled']
    
    deliveries = []
    delivery_counter = 1
    
    for shipment_id, num_orders in shipments:
        orders_for_shipment = random.sample(available_orders, min(num_orders, len(available_orders)))
        
        for seq, order_id in enumerate(orders_for_shipment, 1):
            estimated_delivery = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
            
            status = random.choice(delivery_statuses)
            actual_delivery = estimated_delivery + timedelta(minutes=random.randint(-30, 120)) if status == 'delivered' else None
            
            deliveries.append((
                f'DEL_{delivery_counter:06d}',
                shipment_id,
                order_id,
                seq,
                estimated_delivery.isoformat(),
                actual_delivery.isoformat() if actual_delivery else None,
                status,
                f'Signature_{delivery_counter}' if status == 'delivered' else None,
                'Delivered successfully' if status == 'delivered' else ('Customer not available' if status == 'failed' else None)
            ))
            delivery_counter += 1
    
    cursor.executemany(
        'INSERT OR REPLACE INTO delivery_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        deliveries
    )

def populate_inventory_movements(cursor, count=1500):
    """Populate inventory movements table"""
    cursor.execute('SELECT product_id FROM products')
    products = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT warehouse_id FROM warehouses')
    warehouses = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT batch_id FROM production_batches')
    batches = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT order_id FROM customer_orders')
    orders = [row[0] for row in cursor.fetchall()]
    
    movement_types = ['production', 'sale', 'transfer', 'adjustment']
    
    movements = []
    for i in range(1, count + 1):
        movement_type = random.choice(movement_types)
        movement_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
        
        if movement_type == 'production':
            quantity = random.randint(50, 300)
            reference_id = random.choice(batches)
            notes = 'Production completed'
        elif movement_type == 'sale':
            quantity = -random.randint(1, 50)
            reference_id = random.choice(orders)
            notes = 'Customer order fulfillment'
        elif movement_type == 'transfer':
            quantity = random.choice([-1, 1]) * random.randint(10, 100)
            reference_id = f'TRANSFER_{i}'
            notes = 'Warehouse transfer'
        else:
            quantity = random.choice([-1, 1]) * random.randint(1, 20)
            reference_id = f'ADJ_{i}'
            notes = 'Inventory adjustment'
        
        movements.append((
            f'MOV_{i:06d}',
            movement_type,
            random.choice(products),
            random.choice(warehouses),
            random.choice(batches) if batches else None,
            quantity,
            movement_date.isoformat(),
            reference_id,
            notes
        ))
    
    cursor.executemany(
        'INSERT OR REPLACE INTO inventory_movements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        movements
    )

def populate_raw_material_consumption(cursor):
    """Populate raw material consumption table"""
    cursor.execute('''
        SELECT po.production_order_id, po.planned_quantity, r.raw_material_id, r.quantity_needed, r.waste_percentage
        FROM production_orders po
        JOIN recipes r ON po.product_id = r.product_id
        WHERE po.status = "completed"
    ''')
    
    consumption_data = cursor.fetchall()
    
    consumptions = []
    consumption_counter = 1
    
    for production_order_id, planned_quantity, raw_material_id, quantity_needed, waste_percentage in consumption_data:
        base_consumption = planned_quantity * quantity_needed
        waste_amount = base_consumption * (waste_percentage / 100)
        total_consumed = base_consumption + waste_amount
        
        consumption_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 700))
        
        consumptions.append((
            f'CONS_{consumption_counter:06d}',
            production_order_id,
            raw_material_id,
            round(total_consumed, 2),
            consumption_date.isoformat(),
            f'BATCH_{consumption_counter}',
            round(waste_amount, 2)
        ))
        consumption_counter += 1
    
    cursor.executemany(
        'INSERT OR REPLACE INTO raw_material_consumption VALUES (?, ?, ?, ?, ?, ?, ?)',
        consumptions
    )

def main():
    print("🏭 Creating Manufacturing Company Database...")
    print("📋 Complete Production to Distribution Flow\n")
    
    conn = create_database()
    cursor = conn.cursor()
    
    try:
        print("🧱 Populating raw materials...")
        populate_raw_materials(cursor, 25)
        
        print("📦 Populating products...")
        populate_products(cursor, 30)
        
        print("📝 Creating product recipes (BOM)...")
        populate_recipes(cursor)
        
        print("🏬 Setting up warehouses...")
        populate_warehouses(cursor, 6)
        
        print("👥 Populating customers...")
        populate_customers(cursor, 120)
        
        print("🔧 Creating production orders...")
        populate_production_orders(cursor, 300)
        
        print("📊 Generating production batches...")
        populate_production_batches(cursor)
        
        print("🛒 Populating customer orders...")
        populate_customer_orders(cursor, 800)
        
        print("📋 Creating order details...")
        populate_order_details(cursor)
        
        print("📦 Setting up product inventory...")
        populate_product_inventory(cursor)
        
        print("🧱 Setting up raw material inventory...")
        populate_raw_material_inventory(cursor)
        
        print("⏳ Creating backorders...")
        populate_backorders(cursor, 150)
        
        print("🚚 Setting up delivery routes...")
        populate_routes(cursor, 10)
        
        print("📦 Creating shipments...")
        populate_shipments(cursor, 200)
        
        print("🚛 Populating delivery details...")
        populate_delivery_details(cursor)
        
        print("📈 Recording inventory movements...")
        populate_inventory_movements(cursor, 1500)
        
        print("🔄 Recording raw material consumption...")
        populate_raw_material_consumption(cursor)
        
        conn.commit()
        
        print("""
✅ Manufacturing Company Database Created Successfully!
📊 Data Generated (2024-2025 period):

🏭 PRODUCTION:
   • 25 raw materials with supplier info
   • 30 manufactured products
   • 300 production orders
   • Bill of Materials (BOM) for all products
   • Production batches with quality grades
   • Raw material consumption tracking

👥 CUSTOMERS & ORDERS:
   • 120 customers (distributors/wholesale/retail)
   • 800 customer orders with details
   • 150 backorder records

📦 INVENTORY & WAREHOUSES:
   • 6 specialized warehouses
   • Product inventory by batch and quality
   • Raw material inventory management
   • 1,500 inventory movement records

🚚 DISTRIBUTION:
   • 10 delivery routes with drivers
   • 200 shipments with tracking
   • Complete delivery details

🎯 BUSINESS INSIGHTS READY:
   ✓ Production planning and capacity
   ✓ Raw material requirements
   ✓ Quality control by batch
   ✓ Customer order fulfillment
   ✓ Inventory optimization
   ✓ Backorder management
   ✓ Distribution efficiency
   ✓ Cost analysis by product
""")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
