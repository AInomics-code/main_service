from langchain_core.tools import tool
import sqlite3
import json
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# ===== SISTEMA DE DATOS DEMO REALISTAS =====

class DemoDataGenerator:
    """Generador de datos demo realistas para la empresa manufacturera"""
    
    def __init__(self):
        # Datos base realistas para la empresa manufacturera
        self.products = [
            {"id": "PROD_001", "name": "Pan Artesanal", "category": "Bakery", "price": 4.50, "cost": 2.25},
            {"id": "PROD_002", "name": "Cookies de Chocolate", "category": "Bakery", "price": 6.99, "cost": 3.50},
            {"id": "PROD_003", "name": "Mayonesa Premium 350g", "category": "Sauces", "price": 5.25, "cost": 2.80},
            {"id": "PROD_004", "name": "Salsa de Tomate", "category": "Sauces", "price": 3.75, "cost": 1.90},
            {"id": "PROD_005", "name": "Pizza Margherita", "category": "Prepared Foods", "price": 12.99, "cost": 6.50},
            {"id": "PROD_006", "name": "Empanadas de Pollo", "category": "Prepared Foods", "price": 8.50, "cost": 4.25},
            {"id": "PROD_007", "name": "Chips de Papas", "category": "Snacks", "price": 2.99, "cost": 1.50},
            {"id": "PROD_008", "name": "Galletas Saladas", "category": "Snacks", "price": 3.25, "cost": 1.60},
            {"id": "PROD_009", "name": "Jugo de Naranja 500ml", "category": "Beverages", "price": 4.25, "cost": 2.10},
            {"id": "PROD_010", "name": "Agua Mineral 1L", "category": "Beverages", "price": 1.99, "cost": 0.85}
        ]
        
        self.customers = [
            {"id": "CUST_001", "name": "Distribuidora Central", "type": "distributor", "city": "Miami", "state": "FL"},
            {"id": "CUST_002", "name": "Supermercados Unidos", "type": "wholesale", "city": "Orlando", "state": "FL"},
            {"id": "CUST_003", "name": "Tienda La Esquina", "type": "retail", "city": "Tampa", "state": "FL"},
            {"id": "CUST_004", "name": "Grupo Alimentario TX", "type": "distributor", "city": "Houston", "state": "TX"},
            {"id": "CUST_005", "name": "MegaMart", "type": "wholesale", "city": "Dallas", "state": "TX"},
        ]
        
        self.warehouses = [
            {"id": "WH_001", "name": "Producción Principal", "type": "production"},
            {"id": "WH_002", "name": "Distribución Centro", "type": "distribution"},
            {"id": "WH_003", "name": "Almacén Frío", "type": "cold_storage"},
            {"id": "WH_004", "name": "Materias Primas", "type": "raw_materials"},
        ]

    def should_generate_demo_data(self, result_rows: List[Dict], query: str) -> bool:
        """Determina si debe generar datos demo basado en la consulta y resultados"""
        # Si no hay datos o muy pocos datos
        if len(result_rows) == 0:
            return True
        
        # Si hay muy pocos resultados para consultas que esperan más datos
        if len(result_rows) < 3:
            query_lower = query.lower()
            # Consultas que típicamente deberían devolver varios resultados
            if any(word in query_lower for word in ['productos', 'products', 'clientes', 'customers', 'ventas', 'sales', 'inventario', 'inventory']):
                return True
                
        return False

    def generate_realistic_data(self, query: str, columns: List[str]) -> List[Dict[str, Any]]:
        """Genera datos demo realistas basados en la consulta SQL y columnas esperadas"""
        query_lower = query.lower()
        
        # Detectar tipo de consulta y generar datos apropiados
        if 'product' in query_lower or 'producto' in query_lower:
            return self._generate_product_data(columns, query_lower)
        elif 'customer' in query_lower or 'cliente' in query_lower:
            return self._generate_customer_data(columns, query_lower)
        elif 'order' in query_lower or 'venta' in query_lower or 'orden' in query_lower:
            return self._generate_order_data(columns, query_lower)
        elif 'inventory' in query_lower or 'inventario' in query_lower or 'stock' in query_lower:
            return self._generate_inventory_data(columns, query_lower)
        elif 'production' in query_lower or 'produccion' in query_lower:
            return self._generate_production_data(columns, query_lower)
        elif 'backorder' in query_lower or 'pendiente' in query_lower:
            return self._generate_backorder_data(columns, query_lower)
        elif 'sale' in query_lower or 'revenue' in query_lower or 'ingreso' in query_lower:
            return self._generate_sales_data(columns, query_lower)
        else:
            return self._generate_generic_data(columns, query_lower)

    def _generate_product_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos de productos"""
        data = []
        for i, product in enumerate(self.products[:7]):  # Mostrar varios productos
            row = {}
            for col in columns:
                col_lower = col.lower()
                if 'id' in col_lower and 'product' in col_lower:
                    row[col] = product["id"]
                elif 'name' in col_lower or 'nombre' in col_lower:
                    row[col] = product["name"]
                elif 'category' in col_lower or 'categoria' in col_lower:
                    row[col] = product["category"]
                elif 'price' in col_lower or 'precio' in col_lower:
                    row[col] = product["price"]
                elif 'cost' in col_lower or 'costo' in col_lower:
                    row[col] = product["cost"]
                elif 'active' in col_lower or 'activo' in col_lower:
                    row[col] = 1
                elif 'margin' in col_lower or 'margen' in col_lower:
                    row[col] = round((product["price"] - product["cost"]) / product["price"] * 100, 2)
                else:
                    row[col] = self._get_generic_value(col, i)
            data.append(row)
        return data

    def _generate_customer_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos de clientes"""
        data = []
        for i, customer in enumerate(self.customers):
            row = {}
            for col in columns:
                col_lower = col.lower()
                if 'id' in col_lower and 'customer' in col_lower:
                    row[col] = customer["id"]
                elif 'name' in col_lower or 'nombre' in col_lower:
                    row[col] = customer["name"]
                elif 'type' in col_lower or 'tipo' in col_lower:
                    row[col] = customer["type"]
                elif 'city' in col_lower or 'ciudad' in col_lower:
                    row[col] = customer["city"]
                elif 'state' in col_lower or 'estado' in col_lower:
                    row[col] = customer["state"]
                elif 'credit' in col_lower or 'credito' in col_lower:
                    row[col] = random.randint(10000, 50000)
                else:
                    row[col] = self._get_generic_value(col, i)
            data.append(row)
        return data

    def _generate_order_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos de órdenes REALISTAS para cualquier consulta"""
        data = []
        
        # Determine date range based on query context - FULLY DYNAMIC
        import re
        year_match = re.search(r'\b(20\d{2})\b', query.lower())
        target_year = int(year_match.group(1)) if year_match else datetime.now().year
        
        if 'q4' in query.lower():
            # Q4 of any year
            base_date = datetime(target_year, 10, 1)
            date_range = 90  # Q4 is 3 months
        elif 'q3' in query.lower():
            base_date = datetime(target_year, 7, 1)
            date_range = 90
        elif 'q2' in query.lower():
            base_date = datetime(target_year, 4, 1)
            date_range = 90
        elif 'q1' in query.lower():
            base_date = datetime(target_year, 1, 1)
            date_range = 90
        elif 'daily' in query.lower():
            # Daily data for target year or recent if current year
            if target_year == datetime.now().year:
                base_date = datetime.now() - timedelta(days=15)
                date_range = 15
            else:
                base_date = datetime(target_year, 6, 1)  # Mid year for historical data
                date_range = 15
        else:
            # Default period for target year
            if target_year == datetime.now().year:
                base_date = datetime.now() - timedelta(days=30)
                date_range = 30
            else:
                base_date = datetime(target_year, 6, 1)  # Mid year for historical data
                date_range = 30
            
        # Generate realistic number of data points
        num_records = min(15, max(7, date_range // 3))
        
        for i in range(num_records):
            row = {}
            # Generate realistic date progression
            order_date = base_date + timedelta(days=random.randint(0, date_range))
            
            # Generate realistic sales figures with variation
            base_daily_sales = random.uniform(1500, 4500)
            daily_variation = random.uniform(0.7, 1.4)  # ±40% daily variation
            daily_sales = round(base_daily_sales * daily_variation, 2)
            
            for col in columns:
                col_lower = col.lower()
                if 'order_date' in col_lower or 'date' in col_lower:
                    row[col] = order_date.strftime('%Y-%m-%d')
                elif 'daily_sales' in col_lower or 'total_amount' in col_lower or 'sales' in col_lower:
                    row[col] = daily_sales
                elif 'order_id' in col_lower:
                    row[col] = f"ORD_{str(i+1).zfill(6)}"
                elif 'customer_id' in col_lower:
                    row[col] = random.choice(self.customers)["id"]
                elif 'product_id' in col_lower:
                    row[col] = random.choice(self.products)["id"]
                elif 'quantity' in col_lower or 'cantidad' in col_lower:
                    # Calculate quantity based on realistic unit price
                    unit_price = random.uniform(12, 25)
                    row[col] = int(daily_sales / unit_price)
                elif 'total' in col_lower or 'amount' in col_lower:
                    row[col] = daily_sales
                elif 'status' in col_lower or 'estado' in col_lower:
                    row[col] = random.choice(['completed', 'pending', 'shipped'])
                else:
                    row[col] = self._get_generic_value(col, i)
            data.append(row)
        return data

    def _generate_inventory_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos de inventario"""
        data = []
        for i, product in enumerate(self.products[:6]):
            for warehouse in self.warehouses[:3]:
                row = {}
                for col in columns:
                    col_lower = col.lower()
                    if 'product_id' in col_lower:
                        row[col] = product["id"]
                    elif 'warehouse_id' in col_lower or 'deposito' in col_lower:
                        row[col] = warehouse["id"]
                    elif 'quantity' in col_lower or 'cantidad' in col_lower:
                        if 'available' in col_lower or 'disponible' in col_lower:
                            row[col] = random.randint(50, 500)
                        elif 'reserved' in col_lower or 'reservado' in col_lower:
                            row[col] = random.randint(0, 50)
                        else:
                            row[col] = random.randint(100, 600)
                    elif 'product_name' in col_lower or 'nombre' in col_lower:
                        row[col] = product["name"]
                    elif 'warehouse_name' in col_lower:
                        row[col] = warehouse["name"]
                    else:
                        row[col] = self._get_generic_value(col, i)
                data.append(row)
        return data[:10]  # Limitar a 10 registros

    def _generate_production_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos de producción"""
        data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(6):
            row = {}
            prod_date = base_date + timedelta(days=random.randint(0, 30))
            
            for col in columns:
                col_lower = col.lower()
                if 'production_order_id' in col_lower:
                    row[col] = f"PO_{str(i+1).zfill(6)}"
                elif 'batch_id' in col_lower:
                    row[col] = f"BATCH_{str(i+1).zfill(6)}"
                elif 'product_id' in col_lower:
                    row[col] = random.choice(self.products)["id"]
                elif 'quantity' in col_lower or 'cantidad' in col_lower:
                    if 'planned' in col_lower:
                        row[col] = random.randint(100, 500)
                    else:
                        row[col] = random.randint(80, 450)
                elif 'date' in col_lower or 'fecha' in col_lower:
                    row[col] = prod_date.strftime('%Y-%m-%d')
                elif 'status' in col_lower or 'estado' in col_lower:
                    row[col] = random.choice(['completed', 'in_progress', 'planned'])
                elif 'line' in col_lower or 'linea' in col_lower:
                    row[col] = f"Line_{random.choice(['A', 'B', 'C', 'D'])}"
                else:
                    row[col] = self._get_generic_value(col, i)
            data.append(row)
        return data

    def _generate_backorder_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos de pedidos pendientes"""
        data = []
        for i in range(5):
            row = {}
            for col in columns:
                col_lower = col.lower()
                if 'backorder_id' in col_lower:
                    row[col] = f"BO_{str(i+1).zfill(6)}"
                elif 'order_id' in col_lower:
                    row[col] = f"ORD_{str(i+10).zfill(6)}"
                elif 'product_id' in col_lower:
                    row[col] = random.choice(self.products)["id"]
                elif 'quantity' in col_lower or 'cantidad' in col_lower:
                    row[col] = random.randint(20, 150)
                elif 'reason' in col_lower or 'razon' in col_lower:
                    row[col] = random.choice(['out_of_stock', 'production_delay', 'raw_material_shortage'])
                elif 'priority' in col_lower:
                    row[col] = random.choice(['high', 'normal', 'urgent'])
                elif 'product_name' in col_lower:
                    matching_product = next((p for p in self.products if p["id"] == row.get('product_id')), self.products[0])
                    row[col] = matching_product["name"]
                else:
                    row[col] = self._get_generic_value(col, i)
            data.append(row)
        return data

    def _generate_sales_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos de ventas y ingresos REALISTAS para cualquier producto"""
        data = []
        
        # Determine if query is asking for time-based data (monthly, quarterly, daily)
        is_time_series = any(word in query.lower() for word in ['month', 'quarter', 'q4', 'daily', 'weekly', 'date'])
        
        if is_time_series:
            # Generate time-based sales data
            time_periods = self._get_time_periods(query)
            base_sales = random.uniform(15000, 45000)  # Base monthly sales
            
            for i, period in enumerate(time_periods):
                row = {}
                # Add some realistic growth/decline patterns
                growth_factor = random.uniform(0.85, 1.25)  # ±25% variation
                period_sales = round(base_sales * growth_factor, 2)
                period_quantity = int(period_sales / random.uniform(12, 25))  # Price between $12-25
                
                for col in columns:
                    col_lower = col.lower()
                    if 'month' in col_lower or 'date' in col_lower or 'period' in col_lower:
                        row[col] = period
                    elif 'total_sales' in col_lower or 'total_amount' in col_lower or 'daily_sales' in col_lower or 'revenue' in col_lower:
                        row[col] = period_sales
                    elif 'quantity' in col_lower or 'units' in col_lower:
                        row[col] = period_quantity
                    elif 'orders' in col_lower:
                        row[col] = random.randint(20, 80)
                    elif 'customer_type' in col_lower or 'type' in col_lower:
                        row[col] = random.choice(['Distributor', 'Wholesale', 'Retail'])
                    elif 'total_spent' in col_lower or 'spent' in col_lower:
                        row[col] = round(period_sales * random.uniform(0.8, 1.2), 2)
                    elif 'city' in col_lower:
                        row[col] = random.choice(['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Austin', 'Dallas'])
                    elif 'average_price' in col_lower or 'price' in col_lower:
                        row[col] = round(period_sales / period_quantity, 2)
                    else:
                        row[col] = self._get_generic_value(col, i)
                data.append(row)
        else:
            # Standard product sales data
            for i, product in enumerate(self.products[:7]):
                row = {}
                for col in columns:
                    col_lower = col.lower()
                    if 'product_id' in col_lower:
                        row[col] = product["id"]
                    elif 'product_name' in col_lower or 'nombre' in col_lower:
                        row[col] = product["name"]
                    elif 'revenue' in col_lower or 'ingreso' in col_lower or 'total_sales' in col_lower:
                        row[col] = round(random.uniform(15000, 45000), 2)
                    elif 'quantity' in col_lower or 'cantidad' in col_lower:
                        row[col] = random.randint(500, 2000)
                    elif 'profit' in col_lower or 'ganancia' in col_lower:
                        revenue = row.get('revenue', 25000)
                        row[col] = round(revenue * random.uniform(0.3, 0.5), 2)
                    elif 'category' in col_lower:
                        row[col] = product["category"]
                    else:
                        row[col] = self._get_generic_value(col, i)
                data.append(row)
        return data

    def _get_time_periods(self, query: str) -> List[str]:
        """Generate appropriate time periods based on query context - FULLY DYNAMIC"""
        query_lower = query.lower()
        
        # Extract year from query or use current year as default
        import re
        year_match = re.search(r'\b(20\d{2})\b', query)
        target_year = int(year_match.group(1)) if year_match else datetime.now().year
        
        if 'q4' in query_lower:
            # Q4 months for any year
            return [f'{target_year}-10', f'{target_year}-11', f'{target_year}-12']
        elif 'q3' in query_lower:
            return [f'{target_year}-07', f'{target_year}-08', f'{target_year}-09']
        elif 'q2' in query_lower:
            return [f'{target_year}-04', f'{target_year}-05', f'{target_year}-06']
        elif 'q1' in query_lower:
            return [f'{target_year}-01', f'{target_year}-02', f'{target_year}-03']
        elif 'daily' in query_lower:
            # Generate daily dates for requested year or recent if current year
            if target_year == datetime.now().year:
                base_date = datetime.now() - timedelta(days=10)
            else:
                base_date = datetime(target_year, 1, 15)  # Mid January of target year
            return [(base_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10)]
        elif 'month' in query_lower:
            # Generate monthly periods for target year
            months = []
            for month in range(max(1, target_year == datetime.now().year and datetime.now().month - 4 or 1), 
                             min(13, target_year == datetime.now().year and datetime.now().month + 2 or 13)):
                months.append(f'{target_year}-{str(month).zfill(2)}')
            return months[-5:]  # Last 5 months
        else:
            # Default to recent quarters around target year
            if target_year == datetime.now().year:
                return [f'Q3 {target_year-1}', f'Q4 {target_year-1}', f'Q1 {target_year}']
            else:
                return [f'Q2 {target_year}', f'Q3 {target_year}', f'Q4 {target_year}']

    def _generate_generic_data(self, columns: List[str], query: str) -> List[Dict[str, Any]]:
        """Genera datos genéricos cuando no se puede determinar el tipo específico"""
        data = []
        for i in range(5):
            row = {}
            for col in columns:
                row[col] = self._get_generic_value(col, i)
            data.append(row)
        return data

    def _get_generic_value(self, column_name: str, index: int) -> Any:
        """Genera un valor genérico REALISTA basado en el nombre de la columna"""
        col_lower = column_name.lower()
        
        if 'id' in col_lower:
            return f"ID_{str(index+1).zfill(3)}"
        elif 'name' in col_lower or 'nombre' in col_lower:
            return f"Item {index+1}"
        elif 'date' in col_lower or 'fecha' in col_lower:
            return (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d')
        elif 'price' in col_lower or 'precio' in col_lower or 'cost' in col_lower:
            return round(random.uniform(1.99, 99.99), 2)
        elif 'quantity' in col_lower or 'cantidad' in col_lower:
            return random.randint(1, 100)
        elif 'status' in col_lower or 'estado' in col_lower:
            return random.choice(['active', 'inactive', 'pending'])
        elif 'email' in col_lower:
            return f"demo{index+1}@empresa.com"
        elif 'phone' in col_lower:
            return f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        # 🔧 FIXED: Generate realistic values instead of placeholders
        elif 'sales' in col_lower or 'revenue' in col_lower or 'amount' in col_lower:
            return round(random.uniform(12500.00, 45750.00), 2)
        elif 'total' in col_lower:
            if 'quantity' in col_lower or 'order' in col_lower:
                return random.randint(25, 150)
            else:
                return round(random.uniform(8500.00, 32500.00), 2)
        elif 'spent' in col_lower or 'spend' in col_lower:
            return round(random.uniform(15000.00, 85000.00), 2)
        elif 'customer_type' in col_lower or 'type' in col_lower:
            return random.choice(['Distributor', 'Wholesale', 'Retail'])
        elif 'city' in col_lower or 'ciudad' in col_lower:
            return random.choice(['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Austin', 'Dallas', 'Houston'])
        elif 'orders' in col_lower:
            return random.randint(15, 85)
        else:
            # Generate realistic numeric values instead of "Value X"
            return round(random.uniform(1250.50, 8750.99), 2)

    def generate_aggregate_data(self, query: str, columns: List[str]) -> List[Dict[str, Any]]:
        """🎯 Generates single-row results for aggregate queries (COUNT, SUM, AVG, etc.)"""
        import random
        
        data = []
        row = {}
        
        for col in columns:
            col_lower = col.lower()
            
            # Generate appropriate values based on aggregate type and column name
            if 'count' in col_lower or col_lower.startswith('total_'):
                if 'sku' in col_lower or 'product' in col_lower:
                    row[col] = random.randint(25, 45)  # Realistic SKU count
                elif 'customer' in col_lower:
                    row[col] = random.randint(85, 150)  # Customer count
                elif 'order' in col_lower:
                    row[col] = random.randint(150, 350)  # Order count
                else:
                    row[col] = random.randint(15, 200)  # Generic count
            
            elif 'sum' in col_lower or 'total' in col_lower:
                if any(word in col_lower for word in ['sales', 'revenue', 'amount']):
                    row[col] = round(random.uniform(125000, 750000), 2)  # Total sales
                elif 'quantity' in col_lower or 'units' in col_lower:
                    row[col] = random.randint(2500, 15000)  # Total units
                else:
                    row[col] = round(random.uniform(10000, 100000), 2)
            
            elif 'avg' in col_lower or 'average' in col_lower:
                if 'price' in col_lower:
                    row[col] = round(random.uniform(15.50, 85.75), 2)  # Average price
                elif 'quantity' in col_lower:
                    row[col] = round(random.uniform(25.5, 150.0), 1)  # Average quantity
                else:
                    row[col] = round(random.uniform(50.0, 500.0), 2)
            
            elif 'max' in col_lower:
                if 'price' in col_lower:
                    row[col] = round(random.uniform(150.00, 500.00), 2)  # Max price
                elif 'quantity' in col_lower:
                    row[col] = random.randint(500, 2000)  # Max quantity
                else:
                    row[col] = round(random.uniform(500.0, 2000.0), 2)
            
            elif 'min' in col_lower:
                if 'price' in col_lower:
                    row[col] = round(random.uniform(5.00, 25.00), 2)  # Min price
                elif 'quantity' in col_lower:
                    row[col] = random.randint(1, 50)  # Min quantity
                else:
                    row[col] = round(random.uniform(1.0, 50.0), 2)
            
            else:
                # Fallback for unknown aggregate columns - assume COUNT if not specified
                if any(word in col_lower for word in ['sku', 'product', 'customer', 'client', 'order', 'item']):
                    row[col] = random.randint(25, 150)  # Most likely COUNT
                elif any(word in col_lower for word in ['price', 'amount', 'cost', 'revenue', 'sales']):
                    row[col] = round(random.uniform(25.50, 250000.00), 2)  # Most likely SUM
                else:
                    # Default to COUNT for single-row results
                    row[col] = random.randint(15, 200)
        
        data.append(row)
        return data

# Instancia global del generador
demo_generator = DemoDataGenerator()

def get_demo_context_message() -> str:
    """
    Retorna un mensaje de contexto para agentes cuando están usando datos demo
    """
    return """
🎭 MODO DEMO ACTIVO: Este sistema está ejecutándose con datos de demostración realistas.
Los datos mostrados son representativos de una empresa manufacturera real pero han sido 
generados para propósitos de demostración. Proporciona análisis detallados y profesionales 
como si fueran datos completamente reales de la empresa.
"""

def enhance_agent_response_for_demo(response: str, demo_activated: bool) -> str:
    """
    Mejora la respuesta del agente cuando está en modo demo
    """
    if not demo_activated:
        return response
    
    # Agregar contexto adicional para hacer la demo más convincente
    enhanced_response = response
    
    # Añadir insights adicionales típicos de una empresa manufacturera
    demo_insights = [
        "\n💡 **Insight adicional**: Estos resultados reflejan patrones típicos de la industria manufacturera.",
        "\n📊 **Contexto empresarial**: Los datos muestran el desempeño normal de una empresa con 5 categorías de productos.",
        "\n🎯 **Recomendación**: Para optimizar estos resultados, considere implementar las estrategias sugeridas.",
    ]
    
    # Agregar un insight aleatorio para enriquecer la respuesta
    import random
    enhanced_response += random.choice(demo_insights)
    
    return enhanced_response

@tool
def query_database(query: str, db_type: str = "sqlite") -> str:
    """
    Ejecuta una consulta SQL en la base de datos SQLite demo
    
    Args:
        query: Consulta SQL a ejecutar
        db_type: Tipo de base de datos (solo sqlite para demo)
    
    Returns:
        Resultado de la consulta en formato JSON
    """
    print(f"\n🗄️ QUERY_DATABASE TOOL CALLED")
    print(f"   Database: {db_type} (demo)")
    print(f"   📊 SQL Query:")
    print(f"   {query}")
    print(f"   " + "="*50)
    
    try:
        # Track SQL query in global memory if available
        from rest.invocation import current_memory
        if current_memory:
            current_memory.add_executed_sql(query)
            print(f"   📝 SQL tracked in sources")
        
        # 🎯 ALWAYS DEMO DATA: Try to execute SQL to get column structure, but always generate demo data
        try:
            conn = sqlite3.connect('demo_database.db')
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            conn.close()
        except Exception as sql_error:
            print(f"   ⚠️ SQL error (expected in demo): {sql_error}")
            # Extract probable column names from query for demo data generation
            columns = []
            query_upper = query.upper()
            if 'SELECT' in query_upper:
                select_part = query.split('SELECT')[1].split('FROM')[0] if 'FROM' in query_upper else query.split('SELECT')[1]
                if 'COUNT(' in select_part:
                    columns = ['total_count'] if 'AS' not in select_part else [select_part.split('AS')[-1].strip()]
                elif 'SUM(' in select_part:
                    columns = ['total_sum'] if 'AS' not in select_part else [select_part.split('AS')[-1].strip()]
                elif 'AVG(' in select_part:
                    columns = ['average_value'] if 'AS' not in select_part else [select_part.split('AS')[-1].strip()]
                else:
                    columns = ['id', 'name', 'value']  # Default columns for demo
        
        # 🎯 SPECIAL HANDLING for COUNT, SUM, AVG queries (should return single row)
        is_aggregate_query = any(func in query.upper() for func in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN('])
        
        if is_aggregate_query:
            print(f"   📊 Detected aggregate query - generating single result row")
            demo_data = demo_generator.generate_aggregate_data(query, columns)
        else:
            # Generate regular multi-row manufacturing/retail demo data
            demo_data = demo_generator.generate_realistic_data(query, columns)
        
        print(f"   🎭 DEMO MODE ACTIVE (Manufacturing Demo)")
        print(f"   🎲 Generated {len(demo_data)} realistic demo records")
        
        result_rows = demo_data
            
        # Format response
        demo_indicator = " 🎭 (Manufacturing Demo)"
        response = f"Query executed successfully{demo_indicator}\nRows returned: {len(result_rows)}\n\n"
        
        if result_rows:
            response += "Sample results:\n"
            for i, row in enumerate(result_rows[:7], 1):  # Mostrar más resultados para demo
                response += f"Row {i}: {json.dumps(row, default=str)}\n"
            
            if len(result_rows) > 7:
                response += f"\n... and {len(result_rows) - 7} more rows"
        else:
            response += "No rows returned"
        
        print(f"   ✅ Query executed successfully")
        print(f"   📈 Result preview: {response[:200]}...")
        
        return response
        
    except Exception as e:
        print(f"   ❌ Database query error: {e}")
        print(f"   🎭 Activating demo data generation due to SQL error...")
        
        # Extract probable column names from query for demo data generation
        columns = []
        try:
            query_upper = query.upper()
            if 'SELECT' in query_upper:
                select_part = query.split('SELECT')[1].split('FROM')[0] if 'FROM' in query_upper else query.split('SELECT')[1]
                if 'COUNT(' in select_part:
                    columns = ['total_count'] if 'AS' not in select_part else [select_part.split('AS')[-1].strip()]
                elif 'SUM(' in select_part:
                    columns = ['total_sum'] if 'AS' not in select_part else [select_part.split('AS')[-1].strip()]
                elif 'AVG(' in select_part:
                    columns = ['average_value'] if 'AS' not in select_part else [select_part.split('AS')[-1].strip()]
                else:
                    columns = ['id', 'name', 'value']  # Default columns for demo
        except:
            columns = ['id', 'name', 'value']  # Fallback default columns
        
        # Generate demo data based on query type
        is_aggregate_query = any(func in query.upper() for func in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN('])
        
        if is_aggregate_query:
            print(f"   📊 Generating single-row aggregate demo data")
            demo_data = demo_generator.generate_aggregate_data(query, columns)
        else:
            print(f"   🎲 Generating multi-row manufacturing demo data")
            demo_data = demo_generator.generate_realistic_data(query, columns)
        
        # Format response with demo data
        demo_indicator = " 🎭 (Manufacturing Demo)"
        response = f"Query executed successfully{demo_indicator}\nRows returned: {len(demo_data)}\n\n"
        
        if demo_data:
            response += "Sample results:\n"
            for i, row in enumerate(demo_data[:7], 1):
                response += f"Row {i}: {json.dumps(row, default=str)}\n"
        else:
            response += "No rows returned"
        
        print(f"   ✅ Demo data generated successfully")
        print(f"   📈 Result preview: {response[:200]}...")
        
        return response
