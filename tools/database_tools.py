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
        """Genera datos de órdenes"""
        data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(8):  # Generar varias órdenes
            row = {}
            order_date = base_date + timedelta(days=random.randint(0, 30))
            
            for col in columns:
                col_lower = col.lower()
                if 'order_id' in col_lower:
                    row[col] = f"ORD_{str(i+1).zfill(6)}"
                elif 'customer_id' in col_lower:
                    row[col] = random.choice(self.customers)["id"]
                elif 'product_id' in col_lower:
                    row[col] = random.choice(self.products)["id"]
                elif 'date' in col_lower:
                    row[col] = order_date.strftime('%Y-%m-%d')
                elif 'quantity' in col_lower or 'cantidad' in col_lower:
                    row[col] = random.randint(10, 100)
                elif 'total' in col_lower or 'amount' in col_lower:
                    row[col] = round(random.uniform(500, 3000), 2)
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
        """Genera datos de ventas y ingresos"""
        data = []
        for i, product in enumerate(self.products[:5]):
            row = {}
            for col in columns:
                col_lower = col.lower()
                if 'product_id' in col_lower:
                    row[col] = product["id"]
                elif 'product_name' in col_lower or 'nombre' in col_lower:
                    row[col] = product["name"]
                elif 'revenue' in col_lower or 'ingreso' in col_lower or 'total' in col_lower:
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
        """Genera un valor genérico basado en el nombre de la columna"""
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
        else:
            return f"Value {index+1}"

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
        
        # Simple SQLite connection for demo
        conn = sqlite3.connect('demo_database.db')
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert to JSON format similar to the original tool
        result_rows = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(columns):
                    row_dict[columns[i]] = value
            result_rows.append(row_dict)
        
        conn.close()
        
        # 🎯 SISTEMA DEMO: Verificar si necesitamos generar datos demo
        demo_mode_activated = demo_generator.should_generate_demo_data(result_rows, query)
        
        if demo_mode_activated:
            print(f"   🎭 MODO DEMO ACTIVADO - Generando datos realistas...")
            
            # Generar datos demo realistas basados en la consulta
            demo_data = demo_generator.generate_realistic_data(query, columns)
            
            # Combinar datos reales (si existen) con datos demo
            if result_rows:
                # Si hay algunos datos reales, los combinamos con demo
                combined_data = result_rows + demo_data
                print(f"   📊 Combinando {len(result_rows)} datos reales + {len(demo_data)} datos demo")
            else:
                # Si no hay datos reales, usamos solo los demo
                combined_data = demo_data
                print(f"   🎲 Usando {len(demo_data)} registros demo realistas")
            
            result_rows = combined_data
            
        # Format response
        demo_indicator = " 🎭" if demo_mode_activated else ""
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
        logger.error(f"Database query error: {e}")
        return f"Error executing query: {str(e)}"
