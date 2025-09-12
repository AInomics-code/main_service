from fastapi import Request
from pydantic import BaseModel, Field
from services.chat_history import chat_history_service
import threading
import openai
from langchain_openai import ChatOpenAI
from config.settings import settings
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from tools.database_tools import query_database
from tools.product_search_tools import find_product_by_name, get_best_product_id, search_products_batch, check_product_index_status
# Schema summarizer removed - using static schema for demo

import operator
from typing import Annotated, List, Tuple, Dict, Any
from typing_extensions import TypedDict

# Short-term memory for sharing context between agents
class ShortTermMemory:
    def __init__(self):
        self.memory: Dict[str, Any] = {}
        self.execution_context: Dict[str, Any] = {}
        self.step_results: List[Dict[str, Any]] = []
        self.executed_sqls: List[str] = []  # Track SQL queries in execution order
    
    def store(self, key: str, value: Any):
        """Store a value in short-term memory"""
        self.memory[key] = value
    
    def get(self, key: str, default=None):
        """Retrieve a value from short-term memory"""
        return self.memory.get(key, default)
    
    def update_execution_context(self, context: Dict[str, Any]):
        """Update the execution context"""
        self.execution_context.update(context)
    
    def add_step_result(self, step_number: int, step_description: str, result: str, tools_used: List[str] = None):
        """Add result from a step execution"""
        self.step_results.append({
            "step_number": step_number,
            "step_description": step_description,
            "result": result,
            "tools_used": tools_used or [],
            "timestamp": threading.current_thread().getName()  # Simple timestamp
        })
    
    def add_executed_sql(self, sql_query: str):
        """Add an executed SQL query to the sources list"""
        self.executed_sqls.append(sql_query)
    
    def get_memory_context(self, max_items: int = 2) -> str:
        """🧠 Get optimized memory context (limited for performance)"""
        if not self.memory and not self.step_results:
            return "No previous context.\n"
        
        context = ""
        
        # Only show most recent stored data
        if self.memory:
            recent_items = list(self.memory.items())[-max_items:]
            context += "RECENT DATA:\n"
            for key, value in recent_items:
                context += f"- {key}: {str(value)[:100]}...\n"
        
        # Only show last 2 step results
        if self.step_results:
            recent_steps = self.step_results[-max_items:]
            context += "PREVIOUS STEPS:\n"
            for step in recent_steps:
                context += f"Step {step['step_number']}: {step['result'][:150]}...\n"
        
        return context

# Custom tool for mathematical calculations
@tool
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression"""
    print(f"🧮 CALCULATE TOOL CALLED with expression: {expression}")
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

# Global variable to store current memory instance during execution
current_memory: ShortTermMemory = None

# Agent tools - these are real agents with LLMs with memory access
@tool
def sales_agent(query: str) -> str:
    """Sales agent that handles sales-related queries and provides sales insights"""
    print(f"   🏢 Sales agent analyzing...")
    
    global current_memory
    from tools.database_tools import query_database
    
    sales_llm = llm_pool.agents  # Reuse pooled instance
    
    memory_context = ""
    if current_memory:
        memory_context = current_memory.get_memory_context()
    
    sales_prompt = f"""🏢 SALES AGENT - Manufacturing Company Analysis

🎭 DEMO MODE: Actúa como un analista senior de ventas con datos reales de la empresa.
Proporciona análisis profesionales y detallados como si todos los datos fueran completamente auténticos.

{memory_context}

Query: {query}

CONTEXT: Manufacturing company producing 30 products (bakery, prepared foods, sauces, snacks, beverages) serving distributors/wholesale/retail customers.

ANALYZE:
- Sales performance by category/customer type
- Revenue & profit margins (unit_price vs production_cost)  
- Customer segmentation insights
- Product performance & trends
- Order fulfillment metrics
- Market opportunities and growth strategies

Use query_database for data from: customer_orders, order_details, customers, products, delivery_details.
Presenta los resultados con confianza y profesionalismo, incluyendo recomendaciones específicas."""
    
    # Create a simple agent that can use database queries
    sales_agent_executor = sales_llm.bind_tools([query_database])
    response = sales_agent_executor.invoke([HumanMessage(content=sales_prompt)])
    
    # Store result in memory if available
    if current_memory:
        current_memory.store("sales_analysis_result", response.content)
    
    return response.content

@tool
def finance_agent(query: str) -> str:
    """Finance agent that handles financial calculations and analysis"""
    print(f"   💰 Finance agent analyzing...")
    
    global current_memory
    from tools.database_tools import query_database
    
    finance_llm = llm_pool.agents  # Reuse pooled instance
    
    memory_context = ""
    if current_memory:
        memory_context = current_memory.get_memory_context()
    
    finance_prompt = f"""💰 FINANCE AGENT - Manufacturing Financial Analysis

🎭 DEMO MODE: Actúa como un CFO o analista financiero senior con acceso completo a datos financieros reales.
Proporciona análisis rigurosos y recomendaciones estratégicas como si fuera una consultoría de primer nivel.

{memory_context}

Query: {query}

CONTEXT: Manufacturing with raw materials, production costs, waste tracking, and profitability analysis.

ANALYZE:
- Production costs (materials + waste + labor)
- Product profitability by category
- Inventory valuation (raw materials + finished goods)
- Cash flow & payment terms
- Cost variance (planned vs actual)
- ROI calculations & supplier costs
- Financial KPIs and performance metrics

Use query_database for data from: products, raw_materials, production_orders, raw_material_consumption, customer_orders, order_details.
Presenta análisis con gráficos conceptuales, proyecciones y recomendaciones financieras específicas."""
    
    # Create a simple agent that can use database queries
    finance_agent_executor = finance_llm.bind_tools([query_database])
    response = finance_agent_executor.invoke([HumanMessage(content=finance_prompt)])
    
    # Store result in memory if available
    if current_memory:
        current_memory.store("finance_analysis_result", response.content)
    
    return response.content

@tool
def inventory_agent(query: str) -> str:
    """Inventory agent that handles inventory management and stock queries"""
    print(f"   📦 Inventory agent analyzing...")
    
    global current_memory
    
    inventory_llm = llm_pool.agents  # Reuse pooled instance
    
    memory_context = ""
    if current_memory:
        memory_context = current_memory.get_memory_context()
    
    inventory_prompt = f"""You are a specialized inventory management agent with access to advanced product search capabilities.

🎭 DEMO MODE: Actúa como un Director de Supply Chain con 15+ años de experiencia en manufactura.
Proporciona análisis de inventario de nivel ejecutivo con insights estratégicos y operacionales.

CRITICAL: Users often don't use exact product names. ALWAYS use product search tools before querying inventory data.

{memory_context}

Query: {query}

WORKFLOW FOR PRODUCT QUERIES:
1. If user mentions products by name/description, FIRST use get_best_product_id() to find the correct producto_id
2. Then use query_database with the exact producto_id found
3. Provide detailed inventory analysis with the correct product data

AVAILABLE TOOLS:
- get_best_product_id: Find correct producto_id for user's product description
- find_product_by_name: Search products with detailed similarity results
- query_database: Execute SQL queries with exact producto_id values

INSTRUCTIONS:
- Review the short-term memory context above for relevant information from previous steps
- ALWAYS search for products by description BEFORE running inventory queries
- Use exact producto_id values in your SQL queries (never guess names)
- Provide comprehensive inventory analysis including:
  - Current stock levels and backorder status
  - Inventory optimization recommendations with specific metrics
  - Supply chain insights and lead time analysis
  - Cost implications and savings projections
  - Backorder reduction strategies with expected outcomes
  - Risk assessment and mitigation strategies
  - Performance benchmarking against industry standards

EXAMPLE WORKFLOW:
User: "cuánta mayonesa de 350grs hay en bodega 01?"
1. Use get_best_product_id("mayonesa de 350grs") → get exact producto_id
2. Use query_database("SELECT i.cantidad FROM inventario i WHERE i.producto_id = 'FOUND_ID' AND i.deposito_id = 'bodega 01'")
3. Provide detailed analysis with the correct data
"""
    
    # Create an inventory agent executor with access to product search tools
    inventory_tools = [query_database, find_product_by_name, get_best_product_id, search_products_batch]
    inventory_agent_executor = create_react_agent(inventory_llm, inventory_tools)
    
    # Execute with tools using react agent
    agent_input = {"messages": [HumanMessage(content=inventory_prompt)]}
    response = inventory_agent_executor.invoke(agent_input)
    
    # Extract the final message from react agent response
    if 'messages' in response:
        messages = response['messages']
        ai_messages = [msg for msg in messages if hasattr(msg, 'content') and hasattr(msg, 'type') and msg.type == 'ai']
        if ai_messages:
            final_content = ai_messages[-1].content
        else:
            final_content = str(response)
    else:
        final_content = str(response)
    
    # Store result in memory if available
    if current_memory:
        current_memory.store("inventory_analysis_result", final_content)
    
    return final_content

@tool
def field_ops_agent(query: str) -> str:
    """Field operations agent that handles field operations and logistics"""
    print(f"   🚛 Field ops agent analyzing...")
    
    global current_memory
    
    field_ops_llm = llm_pool.agents  # Reuse pooled instance
    
    memory_context = ""
    if current_memory:
        memory_context = current_memory.get_memory_context()
    
    field_ops_prompt = f"""You are a specialized field operations agent for a MANUFACTURING COMPANY. Analyze the following query and provide detailed operational insights for our production-to-distribution operations.

🎭 DEMO MODE: Actúa como un VP de Operaciones con experiencia en optimización de cadena de suministro.
Proporciona análisis operacional estratégico con recomendaciones de mejora continua y eficiencia operacional.

{memory_context}

Query: {query}

MANUFACTURING COMPANY OPERATIONS CONTEXT:
- We operate 6 specialized warehouses (production, distribution, cold storage, raw materials, quality control)
- We have 10 delivery routes with assigned vehicles (trucks/vans) and drivers
- We manage production scheduling across 4 production lines (Line_A through Line_D)
- Operations include production planning, inventory management, quality control, and distribution logistics
- We track shipments, delivery performance, warehouse capacity utilization, and route efficiency

INSTRUCTIONS:
- Review the short-term memory context above for relevant information from previous steps
- Use data and analysis from previous steps when available and relevant
- Provide a comprehensive manufacturing operations analysis including:
  - Production line efficiency and capacity utilization metrics
  - Warehouse operations optimization (capacity utilization, storage efficiency)
  - Distribution and logistics performance (route efficiency, delivery success rates)
  - Inventory flow optimization (raw materials → production → finished goods → customers)
  - Quality control impact on operations (grade A/B/C distribution, waste reduction)
  - Supply chain coordination (supplier delivery, production scheduling, customer fulfillment)
  - Backorder reduction strategies through operational improvements
  - Cross-functional operational insights (production-warehouse-distribution coordination)
  - Resource allocation recommendations for production lines, warehouses, and delivery routes
  - Digital transformation opportunities and automation potential
  - Lean manufacturing implementation strategies
- Build upon previous analysis results when applicable

FOCUS AREAS: Production scheduling, warehouse management, distribution logistics, quality control, and end-to-end supply chain optimization."""
    
    response = field_ops_llm.invoke([HumanMessage(content=field_ops_prompt)])
    
    # Store result in memory if available
    if current_memory:
        current_memory.store("field_ops_analysis_result", response.content)
    
    return response.content

# State definition
class PlanExecute(TypedDict):
    input: str
    schema_context: str  # Contexto del esquema de BD
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
    short_term_memory: ShortTermMemory  # Memoria a corto plazo

class Plan(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

# 🚀 OPTIMIZED LLM Pool - Reusable instances to avoid recreation overhead
class LLMPool:
    def __init__(self):
        # Core instances with optimized settings
        self.planner = ChatOpenAI(
            api_key=settings.OPENAI_KEY,
            model="gpt-4o-mini", 
            temperature=0,
            verbose=False  # Reduce logging overhead
        )
        
        self.executor = ChatOpenAI(
            api_key=settings.OPENAI_KEY,
            model="gpt-4o-mini",
            temperature=0.1,
            verbose=False
        )
        
        self.agents = ChatOpenAI(  # For sales/finance/inventory/field_ops
            api_key=settings.OPENAI_KEY,
            model="gpt-4o-mini", 
            temperature=0.3,
            verbose=False
        )
        
        self.synthesis = ChatOpenAI(  # For final response
            api_key=settings.OPENAI_KEY,
            model="gpt-4o-mini",
            temperature=0.2,
            verbose=False
        )

# Global pool instance
llm_pool = LLMPool()

# Backward compatibility
llm = llm_pool.executor
planner_llm = llm_pool.planner

# Planner prompt
planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """For the given objective, come up with an OPTIMIZED step by step plan with MINIMAL steps. \
Combine related database operations into single, comprehensive queries whenever possible. \
Each step should accomplish as much as possible in one operation to optimize execution time.

OPTIMIZATION GUIDELINES:
- Combine SELECT, JOIN, and WHERE operations into single queries
- Use subqueries or CTEs instead of multiple separate queries
- Group related analysis tasks together
- Aim for 2-4 steps maximum for most queries
- Only separate steps when they require fundamentally different operations or tools

IMPORTANT: You have access to the database schema context that shows the most relevant tables for this query.
Use this schema context to understand which tables are available and structure OPTIMIZED SQL queries that combine multiple operations.

EXAMPLE - Instead of 6 steps like:
1. Query backorder table
2. Join with products table  
3. Filter active products
4. Sort by backorder quantity
5. Check inventory levels
6. Analyze strategies

Do this in 2-3 optimized steps:
1. Execute comprehensive query joining backorder, products, and inventory tables with filters and sorting to get complete product backorder analysis
2. Analyze results and provide strategic recommendations for backorder reduction

SCHEMA CONTEXT:
{schema_context}""",
        ),
        ("placeholder", "{messages}"),
    ]
)

# Static demo database schema
DEMO_DATABASE_SCHEMA = """
MANUFACTURING COMPANY DATABASE SCHEMA (2024-2025 Data):

==== RAW MATERIALS & PRODUCTION ====
TABLE: raw_materials
- Description: Raw materials used in production with supplier information
- Columns:
  * raw_material_id (TEXT): Unique ID (format: RM_XXX)
  * name (TEXT): Material name (Wheat Flour, Sugar, Cocoa Powder, etc.)
  * description (TEXT): Material description
  * unit_measure (TEXT): kg, liter, ton, bag
  * cost_per_unit (REAL): Cost per unit in USD
  * supplier_name (TEXT): Supplier company name
  * supplier_contact (TEXT): Contact email
  * min_stock_level (INTEGER): Minimum stock threshold
  * max_stock_level (INTEGER): Maximum stock capacity

TABLE: products
- Description: Manufactured products with costs and pricing
- Columns:
  * product_id (TEXT): Unique ID (format: PROD_XXX)
  * name (TEXT): Product name (Artisan Bread, Chocolate Chip Cookies, etc.)
  * description (TEXT): Product description
  * category (TEXT): Bakery, Prepared Foods, Sauces, Snacks, Beverages
  * unit_price (REAL): Selling price in USD
  * production_cost (REAL): Cost to produce in USD
  * unit_measure (TEXT): loaf, dozen, cake, pizza, can, jar, box, etc.
  * shelf_life_days (INTEGER): Product shelf life in days
  * is_active (BOOLEAN): 1=active, 0=inactive

TABLE: recipes
- Description: Bill of Materials (BOM) - raw materials needed per product
- Columns:
  * recipe_id (TEXT): Unique ID (format: RCP_XXXXXX)
  * product_id (TEXT): References products.product_id
  * raw_material_id (TEXT): References raw_materials.raw_material_id
  * quantity_needed (REAL): Amount of raw material needed
  * waste_percentage (REAL): Expected waste percentage (2-8%)
  * is_active (BOOLEAN): Recipe status

TABLE: production_orders
- Description: Orders for manufacturing products
- Columns:
  * production_order_id (TEXT): Unique ID (format: PO_XXXXXX)
  * product_id (TEXT): Product to manufacture
  * planned_quantity (INTEGER): Quantity to produce
  * order_date (DATETIME): When order was placed
  * planned_start_date (DATETIME): Planned production start
  * planned_end_date (DATETIME): Planned completion
  * actual_start_date (DATETIME): Actual start (if started)
  * actual_end_date (DATETIME): Actual completion (if completed)
  * status (TEXT): planned, in_progress, completed, cancelled
  * warehouse_id (TEXT): Production warehouse
  * priority (TEXT): low, normal, high, urgent

TABLE: production_batches
- Description: Individual production batches with quality data
- Columns:
  * batch_id (TEXT): Unique ID (format: BATCH_XXXXXX)
  * production_order_id (TEXT): References production_orders
  * batch_number (TEXT): Human-readable batch number
  * produced_quantity (INTEGER): Actual quantity produced
  * quality_grade (TEXT): A, B, C quality grades
  * production_date (DATETIME): When batch was produced
  * expiry_date (DATETIME): Product expiration date
  * production_line (TEXT): Line_A, Line_B, Line_C, Line_D
  * operator_name (TEXT): Production operator

==== CUSTOMERS & ORDERS ====
TABLE: customers
- Description: Customer information (distributors, wholesale, retail)
- Columns:
  * customer_id (TEXT): Unique ID (format: CUST_XXX)
  * name (TEXT): Customer full name
  * email (TEXT): Email address
  * phone (TEXT): Phone number
  * address (TEXT): Street address
  * city (TEXT): City name
  * state (TEXT): US state code (FL, TX, CA, etc.)
  * postal_code (TEXT): ZIP code
  * customer_type (TEXT): distributor, wholesale, retail
  * credit_limit (REAL): Credit limit in USD
  * payment_terms (TEXT): Payment terms (cash, 7 days, 15 days, 30 days)

TABLE: customer_orders
- Description: Customer orders with delivery requirements
- Columns:
  * order_id (TEXT): Unique ID (format: ORD_XXXXXX)
  * customer_id (TEXT): References customers.customer_id
  * order_date (DATETIME): Order placement date
  * requested_delivery_date (DATETIME): Customer requested delivery
  * order_status (TEXT): pending, confirmed, in_production, ready, shipped, delivered
  * total_amount (REAL): Total order value in USD
  * payment_method (TEXT): cash, credit_card, bank_transfer, check, credit_terms
  * sales_rep (TEXT): Sales representative name
  * special_instructions (TEXT): Special delivery/handling notes

TABLE: order_details
- Description: Line items for customer orders
- Columns:
  * order_id (TEXT): References customer_orders.order_id
  * product_id (TEXT): References products.product_id
  * quantity_ordered (INTEGER): Quantity requested
  * unit_price (REAL): Price per unit
  * line_total (REAL): Total for this line item
  * production_priority (TEXT): low, normal, high, urgent

==== INVENTORY & WAREHOUSES ====
TABLE: warehouses
- Description: Storage facilities with capacity and management
- Columns:
  * warehouse_id (TEXT): Unique ID (format: WH_XXX)
  * name (TEXT): Warehouse name
  * address (TEXT): Physical address
  * city (TEXT): City location
  * warehouse_type (TEXT): production, distribution, cold_storage, raw_materials, quality_control
  * max_capacity (INTEGER): Maximum capacity
  * current_utilization (REAL): Current usage percentage
  * manager_name (TEXT): Warehouse manager

TABLE: product_inventory
- Description: Finished product inventory by warehouse and batch
- Columns:
  * product_id (TEXT): References products.product_id
  * warehouse_id (TEXT): References warehouses.warehouse_id
  * batch_id (TEXT): References production_batches.batch_id
  * available_quantity (INTEGER): Available for sale
  * reserved_quantity (INTEGER): Reserved for orders
  * production_date (DATETIME): When produced
  * expiry_date (DATETIME): Expiration date
  * quality_grade (TEXT): A, B, C quality
  * location_code (TEXT): Physical location in warehouse

TABLE: raw_material_inventory
- Description: Raw material inventory by warehouse
- Columns:
  * raw_material_id (TEXT): References raw_materials.raw_material_id
  * warehouse_id (TEXT): References warehouses.warehouse_id
  * available_quantity (INTEGER): Available for production
  * reserved_quantity (INTEGER): Reserved for production orders
  * last_received_date (DATETIME): Last delivery date
  * location_code (TEXT): Physical location code

TABLE: backorders
- Description: Orders that cannot be fulfilled immediately
- Columns:
  * backorder_id (TEXT): Unique ID (format: BO_XXXXXX)
  * order_id (TEXT): References customer_orders.order_id
  * product_id (TEXT): References products.product_id
  * quantity_pending (INTEGER): Quantity still needed
  * original_due_date (DATETIME): Original promised date
  * new_promised_date (DATETIME): New promised delivery
  * priority (TEXT): low, normal, high, urgent
  * reason (TEXT): out_of_stock, production_delay, quality_issue, raw_material_shortage
  * warehouse_id (TEXT): Fulfillment warehouse

==== DISTRIBUTION & LOGISTICS ====
TABLE: routes
- Description: Delivery routes with vehicle and driver information
- Columns:
  * route_id (TEXT): Unique ID (format: RT_XXX)
  * route_name (TEXT): Route name
  * description (TEXT): Route description
  * assigned_vehicle (TEXT): Vehicle ID (TRUCK-XXX, VAN-XXX)
  * driver_name (TEXT): Driver full name
  * driver_phone (TEXT): Driver contact number
  * max_capacity_kg (REAL): Weight capacity in kg
  * max_capacity_volume (REAL): Volume capacity
  * coverage_zone (TEXT): Coverage area
  * is_active (BOOLEAN): Route status

TABLE: shipments
- Description: Shipment tracking with capacity utilization
- Columns:
  * shipment_id (TEXT): Unique ID (format: SHIP_XXXXXX)
  * route_id (TEXT): References routes.route_id
  * shipment_date (DATETIME): Shipment date
  * departure_warehouse_id (TEXT): Origin warehouse
  * total_weight (REAL): Total shipment weight
  * total_volume (REAL): Total shipment volume
  * number_of_orders (INTEGER): Orders in shipment
  * departure_time (DATETIME): Departure time
  * estimated_return_time (DATETIME): Expected return
  * shipment_status (TEXT): loading, in_transit, delivered, returned

TABLE: delivery_details
- Description: Individual delivery tracking per order
- Columns:
  * delivery_id (TEXT): Unique ID (format: DEL_XXXXXX)
  * shipment_id (TEXT): References shipments.shipment_id
  * order_id (TEXT): References customer_orders.order_id
  * delivery_sequence (INTEGER): Order in delivery route
  * estimated_delivery_time (DATETIME): Estimated delivery
  * actual_delivery_time (DATETIME): Actual delivery time
  * delivery_status (TEXT): pending, delivered, failed, rescheduled
  * customer_signature (TEXT): Delivery confirmation
  * delivery_notes (TEXT): Delivery notes

==== TRACKING & MOVEMENTS ====
TABLE: inventory_movements
- Description: All inventory transactions and movements
- Columns:
  * movement_id (TEXT): Unique ID (format: MOV_XXXXXX)
  * movement_type (TEXT): production, sale, transfer, adjustment
  * product_id (TEXT): References products.product_id
  * warehouse_id (TEXT): References warehouses.warehouse_id
  * batch_id (TEXT): References production_batches.batch_id
  * quantity (INTEGER): Movement quantity (positive=in, negative=out)
  * movement_date (DATETIME): Movement timestamp
  * reference_id (TEXT): Reference to related transaction
  * notes (TEXT): Movement description

TABLE: raw_material_consumption
- Description: Raw material usage in production
- Columns:
  * consumption_id (TEXT): Unique ID (format: CONS_XXXXXX)
  * production_order_id (TEXT): References production_orders
  * raw_material_id (TEXT): References raw_materials
  * quantity_consumed (REAL): Amount consumed
  * consumption_date (DATETIME): Consumption date
  * batch_number (TEXT): Production batch reference
  * waste_quantity (REAL): Amount wasted

==== KEY RELATIONSHIPS ====
- recipes.product_id → products.product_id
- recipes.raw_material_id → raw_materials.raw_material_id
- production_orders.product_id → products.product_id
- production_batches.production_order_id → production_orders.production_order_id
- customer_orders.customer_id → customers.customer_id
- order_details.order_id → customer_orders.order_id
- order_details.product_id → products.product_id
- product_inventory.batch_id → production_batches.batch_id
- backorders.order_id → customer_orders.order_id
- shipments.route_id → routes.route_id
- delivery_details.shipment_id → shipments.shipment_id

==== SAMPLE DATA VOLUMES ====
- 25 raw materials with supplier info
- 30 manufactured products across 5 categories
- 300 production orders (2024-2025)
- 120 customers (20 distributors, 30 wholesale, 70 retail)
- 800 customer orders with details
- 6 specialized warehouses
- 150 backorder records
- 10 delivery routes with drivers
- 200 shipments with tracking
- 1,500 inventory movement records
"""

# 🚀 OPTIMIZED Query Analysis & Routing
def analyze_query_complexity(query: str) -> dict:
    """Determine if query needs planner or can be executed directly"""
    query_lower = query.lower()
    
    # Simple query patterns (direct execution)
    simple_patterns = [
        r'cu[aá]ntos?\s+\w+',  # "cuántos productos"
        r'qu[eé]\s+\w+\s+hay',  # "qué productos hay"  
        r'lista?\s+(de\s+)?\w+',  # "lista productos"
        r'mostrar\s+\w+',       # "mostrar clientes"
        r'total\s+de\s+\w+',    # "total de ventas"
        r'buscar\s+\w+',        # "buscar producto"
    ]
    
    # Complex analysis indicators (planner execution)
    complex_keywords = [
        'analiz', 'estrategi', 'recomend', 'optimiz', 'reduc', 'mejor',
        'plan', 'forecast', 'trend', 'insight', 'correlat', 'improv',
        'strategy', 'recommend', 'optimize', 'reduce', 'improve',
        'backorder', 'performance', 'efficiency'
    ]
    
    import re
    is_simple = any(re.search(pattern, query_lower) for pattern in simple_patterns)
    is_complex = any(keyword in query_lower for keyword in complex_keywords)
    
    if is_simple and not is_complex:
        return {"type": "simple", "execution": "direct"}
    elif len(query.split()) > 15 or is_complex:  # Long queries are complex
        return {"type": "complex", "execution": "planner"}
    else:
        return {"type": "medium", "execution": "simplified_planner"}

def get_focused_schema(query: str) -> str:
    """Return relevant schema subset based on query keywords"""
    query_lower = query.lower()
    
    # Core tables always included with clear purposes
    core_schema = """
TABLE: products - PRODUCT CATALOG: product_id, name, category, unit_price, production_cost, is_active
TABLE: customers - CUSTOMER INFO: customer_id, name, customer_type, city, state  
TABLE: customer_orders - CUSTOMER ORDERS: order_id, customer_id, order_date, order_status, total_amount
TABLE: order_details - ORDER LINE ITEMS: order_id, product_id, quantity_ordered, unit_price, line_total
"""
    
    # Add relevant tables based on keywords
    extensions = {}
    
    if any(word in query_lower for word in ['inventory', 'inventario', 'stock', 'bodega']):
        extensions['inventory'] = "TABLE: product_inventory - FINISHED GOODS INVENTORY: product_id, warehouse_id, available_quantity, reserved_quantity, batch_id"
        extensions['warehouses'] = "TABLE: warehouses - STORAGE LOCATIONS: warehouse_id, name, warehouse_type, manager_name"
    
    if any(word in query_lower for word in ['backorder', 'pendiente', 'atras']):
        extensions['backorders'] = "TABLE: backorders - backorder_id, order_id, product_id, quantity_pending, reason"
    
    if any(word in query_lower for word in ['production', 'produccion', 'producir', 'produce', 'manufactur', 'fabric']):
        extensions['production_planning'] = "TABLE: production_orders - PRODUCTION PLANNING: production_order_id, product_id, planned_quantity, status, order_date"
        extensions['actual_production'] = "TABLE: production_batches - ACTUAL PRODUCTION (USE FOR PRODUCTION REPORTS): batch_id, production_order_id, produced_quantity, production_date, quality_grade"
        extensions['raw_materials'] = "TABLE: raw_materials - RAW MATERIALS: raw_material_id, name, cost_per_unit, supplier_name"
    
    if any(word in query_lower for word in ['delivery', 'entrega', 'route', 'ruta']):
        extensions['routes'] = "TABLE: routes - route_id, route_name, driver_name"
        extensions['shipments'] = "TABLE: shipments - shipment_id, route_id, shipment_status"
    
    # Build focused schema
    focused = f"MANUFACTURING SCHEMA (focused):\n{core_schema}"
    for table_schema in extensions.values():
        focused += f"\n{table_schema}"
    
    focused += f"\n\nQuery: '{query}'\n\n⚠️ CRITICAL RULES:\n"
    
    # Add specific production guidance if production tables are included
    if 'actual_production' in extensions:
        focused += """
🎯 PRODUCTION QUERIES:
- For "cuánta producción" or "production this month" → USE production_batches table with produced_quantity and production_date
- For "órdenes de producción" or "production planning" → USE production_orders table with planned_quantity and order_date
- NEVER use production_order_id in date comparisons (it's TEXT, not DATE)

EXAMPLE: Production this month = SELECT SUM(produced_quantity) FROM production_batches WHERE strftime('%Y-%m', production_date) = strftime('%Y-%m', 'now')
"""
    
    focused += "\n⚠️ Use EXACT table/column names shown above."
    
    return focused

# Function to get relevant schema
def get_schema_context(state):
    """🧠 Smart schema with query analysis and routing"""
    try:
        query = state["input"]
        
        # Analyze query complexity
        analysis = analyze_query_complexity(query)
        print(f"🔍 Query analysis: {analysis['type']} → {analysis['execution']}")
        
        # Get focused schema (much smaller)
        schema_context = get_focused_schema(query)
        print(f"📋 Schema focused to ~{len(schema_context.split('TABLE:'))} tables")
        
        return {
            "schema_context": schema_context,
            "query_analysis": analysis,
            "use_simplified_flow": analysis["execution"] != "planner"
        }
    except Exception as e:
        print(f"❌ Error analyzing query: {e}")
        return {"schema_context": f"Error: {str(e)}", "query_analysis": {"type": "complex", "execution": "planner"}}

# Function to prepare planner input
def prepare_planner_input(state):
    """Prepara el input para el planner incluyendo el contexto del esquema"""
    return state  # El estado ya contiene toda la información necesaria

# Create planner
planner = planner_prompt | planner_llm.with_structured_output(Plan)

# Wrapper para el planner con logging
def planner_with_logging(planner_input):
    """Wrapper del planner con logging para debug"""
    try:
        # Ejecutar el planner con el input preparado
        result = planner.invoke(planner_input)
        
        print(f"📋 Plan: {len(result.steps)} steps generated")
        for i, step in enumerate(result.steps):
            print(f"   {i+1}. {step}")
        
        return {"plan": result.steps}
        
    except Exception as e:
        print(f"❌ Planner error: {e}")
        return {"plan": [f"Error in planning: {str(e)}"]}

# Execution prompt
execution_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI who executes plans step by step. You MUST use the appropriate tools for each step.

AVAILABLE TOOLS:
- query_database: Execute SQL queries on the database (REQUIRED for data retrieval)
- calculate: Perform mathematical calculations
- sales_agent: Get sales analysis and insights  
- finance_agent: Get financial analysis and calculations
- inventory_agent: Get inventory management insights
- field_ops_agent: Get field operations analysis

EXECUTION RULES:
1. For data queries: ALWAYS use query_database tool first with proper SQL
2. For analysis: Use the appropriate specialized agent AFTER getting data
3. For calculations: Use calculate tool when needed
4. NEVER provide answers without using tools when data is required

IMPORTANT DATABASE INFORMATION:
{schema_context}

EXECUTION PROCESS:
1. MANDATORY: If the step requires data from database, use query_database tool with SQL first
2. Pass the data results to the appropriate agent tool for analysis
3. Always use tools - do not generate answers without them
4. Show the actual results from the tools in your response

CRITICAL: You must call query_database tool when dealing with any database queries. The tool will generate appropriate SQL dynamically based on the step requirements and database schema context.

You MUST use tools to complete each step. Do not provide answers without using the appropriate tools.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

# Database Agent - Specialized for DB queries only
@tool
def database_agent(sql_query: str) -> str:
    """Specialized agent that only executes database queries"""
    print(f"🗄️ DATABASE AGENT CALLED")
    print(f"   SQL: {sql_query}")
    
    try:
        from tools.database_tools import query_database
        result = query_database(sql_query, "sqlserver")
        print(f"   ✅ Database query successful")
        return result
    except Exception as e:
        print(f"   ❌ Database query failed: {e}")
        return f"Database error: {str(e)}"

# Simple executor that uses LLM with tools for dynamic execution
def create_executor_with_context(state):
    """Creates an executor that uses LLM agents with database tools for dynamic query generation"""
    def execute_step(step_input):
        from langchain_core.messages import HumanMessage
        
        messages = step_input["messages"]
        step_content = messages[0].content
        schema_context = state.get("schema_context", "")
        
        print(f"   🤖 LLM Executor: Analyzing step requirements")
        print(f"   📊 Schema context length: {len(schema_context)} chars")
        
        # Show a preview of schema context for debugging
        if schema_context:
            schema_preview = schema_context.replace('\n', ' ')
            print(f"   🗂️ Schema preview: {schema_preview}...")
        else:
            print(f"   ⚠️ WARNING: No schema context available!")
        
        # Create an executor LLM with access to all tools
        executor_llm = llm_pool.executor  # Reuse pooled instance
        
        # Get memory context
        memory_context = ""
        if current_memory:
            memory_context = current_memory.get_memory_context()
        
        # Create executor with all tools available
        tools = [query_database, sales_agent, finance_agent, inventory_agent, field_ops_agent, calculate, 
                find_product_by_name, get_best_product_id, search_products_batch, check_product_index_status]
        executor_agent = create_react_agent(executor_llm, tools)
        
        # Enhanced prompt for dynamic tool usage
        executor_prompt = f"""🤖 STEP EXECUTOR

STEP: {step_content}

MEMORY: {memory_context}

SCHEMA: {schema_context}

TOOLS: query_database, sales_agent, finance_agent, inventory_agent, field_ops_agent, calculate, find_product_by_name, get_best_product_id

RULES:
1. For products: use find_product_by_name FIRST → get exact IDs → then query
2. Use EXACT table/column names from schema
3. Format money with $ symbol
4. Use markdown formatting

Execute now:"""
        
        try:
            # Execute with tools using react agent
            print(f"   🔧 Invoking REACT executor agent with tools...")
            
            # For react agent, we need to pass messages in the correct format
            agent_input = {"messages": [HumanMessage(content=executor_prompt)]}
            response = executor_agent.invoke(agent_input)
            
            # Extract the final message and tool usage from react agent response
            tools_used = []
            final_message = ""
            
            if 'messages' in response:
                messages = response['messages']
                print(f"   📝 Agent executed {len(messages)} messages")
                
                # Look for tool calls in messages
                for msg in messages:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call.get('name', 'unknown')
                            tools_used.append(tool_name)
                            print(f"      🛠️ Tool executed: {tool_name}")
                            
                            # Show SQL for database queries
                            if tool_name == 'query_database' and 'args' in tool_call:
                                query_arg = tool_call['args'].get('query', 'No query found')
                                print(f"      📊 SQL Preview: {query_arg[:100]}...")
                
                # Get the final AI message
                ai_messages = [msg for msg in messages if hasattr(msg, 'content') and hasattr(msg, 'type') and msg.type == 'ai']
                if ai_messages:
                    final_message = ai_messages[-1].content
                else:
                    final_message = str(response)
            else:
                final_message = str(response)
                print(f"   ⚠️ Unexpected response format from react agent")
            
            # Store results in memory if database was used
            if current_memory and 'query_database' in tools_used:
                current_memory.store(f"step_result_{len(current_memory.step_results)}", final_message)
            
            tools_summary = ', '.join(tools_used) if tools_used else 'None'
            print(f"   ✅ Tools executed: {tools_summary}")
            
            # Return response
            class MockResponse:
                def __init__(self, content, tools):
                    self.content = content
                    self.tools_used = tools
            
            return MockResponse(final_message, tools_used)
            
        except Exception as e:
            print(f"   ❌ Executor error: {e}")
            error_response = f"Error executing step: {str(e)}"
            
            class MockResponse:
                def __init__(self, content, tools):
                    self.content = content
                    self.tools_used = tools
            
            return MockResponse(error_response, ["error"])
    
    return execute_step

executor = create_executor_with_context

# Function to generate final aggregated response
def generate_final_response(user_query: str, schema_context: str, plan: List[str], 
                          step_results: List[str], tools_used_per_step: List[List[str]], 
                          memory: ShortTermMemory) -> str:
    """Genera una respuesta final agregada basada en todos los resultados de los pasos"""
    
    # Create final response with LLM to synthesize all results
    final_llm = llm_pool.synthesis  # Reuse pooled instance
    
    # Prepare comprehensive context
    step_summary = ""
    for i, (step, result, tools) in enumerate(zip(plan, step_results, tools_used_per_step)):
        step_summary += f"""
### STEP {i+1}: {step}
**Tools Used:** {', '.join(tools) if tools else 'None'}
**Result:**
{result}

---
"""
    
    memory_context = memory.get_memory_context()
    
    synthesis_prompt = f"""You are an AI assistant tasked with providing a final, comprehensive response to the user based on a multi-step analysis that has been completed.

**ORIGINAL USER QUERY:**
{user_query}

**EXECUTION CONTEXT:**
The query was processed through a {len(plan)}-step plan where each step used specialized agents and tools to gather and analyze relevant information.

**MEMORY CONTEXT:**
{memory_context}

**DETAILED STEP-BY-STEP RESULTS:**
{step_summary}

**YOUR TASK:**
Create a comprehensive, well-structured final response that:
1. Directly answers the user's original query
2. Synthesizes insights from all steps into a coherent analysis
3. Highlights key findings and actionable recommendations
4. Uses data and metrics gathered from the analysis
5. Provides a clear executive summary

**RESPONSE STRUCTURE:**
- Start with a direct answer to the user's query
- Present key findings with supporting data
- Provide actionable recommendations
- Include relevant metrics and analysis
- End with a clear executive summary

**FORMATTING REQUIREMENTS:**
- ALWAYS include "$" symbol when displaying monetary amounts (e.g., "$1,500" instead of "1500")
- Use markdown formatting extensively for better readability: **bold**, *italic*, <mark>highlight</mark>, `code`, and other markdown elements
- Present data in tables, lists, and well-formatted sections
- Use headers, bullet points, and emphasis to structure information clearly

**IMPORTANT:**
- Be comprehensive but concise
- Use the specific data and insights gathered during execution
- Maintain a professional, analytical tone
- Focus on actionable insights for the user

Generate the final response now:"""

    final_response = final_llm.invoke([HumanMessage(content=synthesis_prompt)])
    
    return final_response.content

# Function to execute plan step by step with memory
def execute_plan_with_memory(state):
    """Ejecuta el plan paso a paso con memoria a corto plazo compartida"""
    global current_memory
    
    try:
        plan = state["plan"]
        schema_context = state["schema_context"]
        user_query = state["input"]
        
        # Inicializar memoria a corto plazo
        memory = ShortTermMemory()
        current_memory = memory  # Set global memory for agent access
        
        # Establecer contexto inicial
        memory.update_execution_context({
            "original_query": user_query,
            "schema_context": schema_context,
            "total_steps": len(plan)
        })
        
        print(f"🚀 Executing {len(plan)} steps with memory")
        
        # Crear el executor con el contexto del esquema
        executor_with_context = create_executor_with_context(state)
        
        # Ejecutar cada paso del plan secuencialmente
        step_results = []
        tools_used_per_step = []
        
        for i, step in enumerate(plan):
            print(f"\n📍 Step {i+1}/{len(plan)}")
            
            # Obtener contexto de memoria para este paso
            memory_context = memory.get_memory_context()
            
            step_prompt = f"""STEP {i+1} of {len(plan)}: {step}

ORIGINAL QUERY: {user_query}

MEMORY CONTEXT FROM PREVIOUS STEPS:
{memory_context}

SCHEMA CONTEXT:
{schema_context}

INSTRUCTIONS:
- Execute this step using the appropriate tools
- Use information from previous steps stored in memory when relevant
- Provide detailed analysis and results
- Each step builds upon the previous ones

Execute this step now using the most appropriate tools."""
            
            # Execute step using hybrid executor
            response = executor_with_context({
                "messages": [HumanMessage(content=step_prompt)]
            })
            
            # Extract response content and tools used
            if hasattr(response, 'content'):
                response_content = response.content
                tools_used = getattr(response, 'tools_used', [])
            else:
                response_content = str(response)
                tools_used = []
            
            # Store step result in memory
            memory.add_step_result(i+1, step, response_content, tools_used)
            
            step_results.append(response_content)
            tools_used_per_step.append(tools_used)
            
            # Show results summary
            tools_summary = "memory" if "memory_retrieval" in tools_used else ", ".join(tools_used)
            print(f"✅ Step {i+1}: {tools_summary}")
        
        # Generate final aggregated response
        final_response = generate_final_response(
            user_query, schema_context, plan, step_results, tools_used_per_step, memory
        )
        
        # Clear global memory
        current_memory = None
        
        print(f"🎯 Execution completed")
        
        return {"response": final_response, "short_term_memory": memory}
        
    except Exception as e:
        # Clear global memory on error
        current_memory = None
        print(f"❌ Error executing plan: {e}")
        return {"response": f"Error executing plan: {str(e)}"}

# Define the state graph
def create_plan_and_execute_graph():
    workflow = StateGraph(PlanExecute)
    
    # Add nodes
    workflow.add_node("get_schema", get_schema_context)
    workflow.add_node("prepare_planner", prepare_planner_input)
    workflow.add_node("planner", planner_with_logging)
    workflow.add_node("execute_plan", execute_plan_with_memory)
    
    # Add edges
    workflow.add_edge("get_schema", "prepare_planner")
    workflow.add_edge("prepare_planner", "planner")
    workflow.add_edge("planner", "execute_plan")
    workflow.add_edge("execute_plan", END)
    
    # Set entry point
    workflow.set_entry_point("get_schema")
    
    return workflow.compile()

# Create the graph
graph = create_plan_and_execute_graph()

# Function to execute with past_steps tracking
def execute_with_tracking(input_data):
    result = graph.invoke(input_data)
    return result

# Create the graph
graph = create_plan_and_execute_graph()

async def invoke_agent(request: Request):
    # Get the user query from request body
    try:
        body = await request.json()
        user_query = body.get("message", body.get("query", ""))
    except:
        user_query = ""
    
    print(f"🚀 Starting agent invocation for query: {user_query}")
    
    # Execute the graph with schema context and memory
    initial_state = {
        "input": user_query,
        "schema_context": "",
        "plan": [],
        "past_steps": [],
        "response": "",
        "short_term_memory": ShortTermMemory()
    }
    
    result = graph.invoke(initial_state)
    
    print(f"✅ Query completed ({len(result.get('response', ''))} chars)")
    
    # Get SQL sources from memory if available
    sql_sources = []
    if result.get("short_term_memory") and hasattr(result["short_term_memory"], "executed_sqls"):
        sql_sources = result["short_term_memory"].executed_sqls
    
    return {
        "input": user_query,
        "plan": result.get("plan", []),
        "response": result.get("response", ""),
        "sources": sql_sources,  # Lista de SQLs ejecutados en orden
        "execution_successful": bool(result.get("response"))
    }