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
from schema_summarizer.schema_summarizer import SchemaSummarizer

import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict

# Custom tool for mathematical calculations
@tool
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression"""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

# Agent tools - these are real agents with LLMs
@tool
def sales_agent(query: str) -> str:
    """Sales agent that handles sales-related queries and provides sales insights"""
    sales_llm = ChatOpenAI(
        api_key=settings.OPENAI_KEY,
        model="gpt-4o-mini",
        temperature=0.3,
        verbose=True
    )
    sales_prompt = f"""You are a specialized sales agent. Analyze the following query and provide detailed sales insights with realistic simulated data.

Query: {query}

Provide a comprehensive sales analysis including:
- Sales performance metrics (use realistic simulated numbers)
- Market insights and trends
- Recommendations for improvement
- Revenue projections if applicable

IMPORTANT: Use realistic simulated data and numbers. Do not mention that the data is simulated - present it as if it were real analysis."""
    
    response = sales_llm.invoke([HumanMessage(content=sales_prompt)])
    return response.content

@tool
def finance_agent(query: str) -> str:
    """Finance agent that handles financial calculations and analysis"""
    finance_llm = ChatOpenAI(
        api_key=settings.OPENAI_KEY,
        model="gpt-4o-mini",
        temperature=0.1,
        verbose=True
    )
    finance_prompt = f"""You are a specialized finance agent. Analyze the following query and provide detailed financial analysis with realistic simulated financial data.

Query: {query}

Provide a comprehensive financial analysis including:
- Financial calculations with realistic numbers
- Cost analysis and impact assessment
- Profitability metrics and projections
- Financial recommendations with ROI estimates

IMPORTANT: Use realistic simulated financial data and calculations. Do not mention that the data is simulated - present it as if it were real financial analysis."""
    
    response = finance_llm.invoke([HumanMessage(content=finance_prompt)])
    return response.content

@tool
def inventory_agent(query: str) -> str:
    """Inventory agent that handles inventory management and stock queries"""
    inventory_llm = ChatOpenAI(
        api_key=settings.OPENAI_KEY,
        model="gpt-4o-mini",
        temperature=0.2,
        verbose=True
    )
    inventory_prompt = f"""You are a specialized inventory management agent. Analyze the following query and provide detailed inventory insights with realistic simulated inventory data.

Query: {query}

Provide a comprehensive inventory analysis including:
- Current stock levels and backorder status (use realistic simulated numbers)
- Inventory optimization recommendations with specific metrics
- Supply chain insights and lead time analysis
- Cost implications and savings projections
- Backorder reduction strategies with expected outcomes

IMPORTANT: Use realistic simulated inventory data, stock levels, and backorder numbers. Do not mention that the data is simulated - present it as if it were real inventory analysis."""
    
    response = inventory_llm.invoke([HumanMessage(content=inventory_prompt)])
    return response.content

@tool
def field_ops_agent(query: str) -> str:
    """Field operations agent that handles field operations and logistics"""
    field_ops_llm = ChatOpenAI(
        api_key=settings.OPENAI_KEY,
        model="gpt-4o-mini",
        temperature=0.2,
        verbose=True
    )
    field_ops_prompt = f"""You are a specialized field operations agent. Analyze the following query and provide detailed operational insights with realistic simulated operational data.

Query: {query}

Provide a comprehensive field operations analysis including:
- Operational efficiency metrics with realistic numbers
- Logistics optimization strategies for backorder reduction
- Resource allocation recommendations with cost estimates
- Field performance insights and improvement opportunities
- Delivery and fulfillment optimization strategies

IMPORTANT: Use realistic simulated operational data and metrics. Do not mention that the data is simulated - present it as if it were real operational analysis."""
    
    response = field_ops_llm.invoke([HumanMessage(content=field_ops_prompt)])
    return response.content

# State definition
class PlanExecute(TypedDict):
    input: str
    schema_context: str  # Contexto del esquema de BD
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str

class Plan(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

# LLM instances
llm = ChatOpenAI(
    api_key=settings.OPENAI_KEY,
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,
    verbose=True
)

planner_llm = ChatOpenAI(
    api_key=settings.OPENAI_KEY,
    model="gpt-4o-mini",
    temperature=0,
    verbose=True
)

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

# Schema summarizer instance
schema_summarizer = SchemaSummarizer()

# Schema summarizer instance
schema_summarizer = SchemaSummarizer()

# Function to get relevant schema
def get_schema_context(state):
    """Obtiene el esquema relevante para la consulta del usuario"""
    try:
        query = state["input"]
        print(f"🔍 Getting schema for query: {query}")
        
        schema_summary = schema_summarizer.get_schema_summary(query, top_k=5)
        
        # Crear contexto del esquema
        schema_context = f"""SCHEMA CONTEXT for query: "{query}"

Top 5 relevant tables:
"""
        
        for table in schema_summary["relevant_tables"]:
            schema_context += f"""
Table: {table['table_name']}
Relevance Score: {table['relevance_score']:.3f}
Content: {table['content'][:500]}...
"""
        
        print(f"📋 Schema context generated with {len(schema_summary['relevant_tables'])} tables")
        return {"schema_context": schema_context}
    except Exception as e:
        print(f"❌ Error getting schema: {e}")
        return {"schema_context": f"Error getting schema: {str(e)}"}

# Function to prepare planner input
def prepare_planner_input(state):
    """Prepara el input para el planner incluyendo el contexto del esquema"""
    print(f"📝 Preparing planner input with schema context")
    print(f"📋 Schema context length: {len(state['schema_context'])} characters")
    
    planner_input = {
        "messages": [
            ("user", f"{state['input']}\n\nSchema Context:\n{state['schema_context']}")
        ]
    }
    
    print(f"📤 Planner input prepared: {planner_input}")
    return planner_input

# Create planner
planner = planner_prompt | planner_llm.with_structured_output(Plan)

# Wrapper para el planner con logging
def planner_with_logging(state):
    """Wrapper del planner con logging para debug"""
    try:
        print(f"🧠 Planner executing with input: {state}")
        
        # Ejecutar el planner
        result = planner.invoke(state)
        
        print(f"✅ Planner completed successfully")
        print(f"📋 Plan generated with {len(result.steps)} steps:")
        for i, step in enumerate(result.steps):
            print(f"   {i+1}. {step}")
        
        return {"plan": result.steps}
        
    except Exception as e:
        print(f"❌ Error in planner: {e}")
        return {"plan": [f"Error in planning: {str(e)}"]}

# Execution prompt
execution_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI who executes OPTIMIZED plans step by step. You have access to multiple tools including:
            - Calculator tool for mathematical calculations
            - Database tool (query_database) for executing SQL queries on real data
            - Specialized agent tools for different domains
            
            IMPORTANT: You have access to the database schema context that shows the most relevant tables for this query.
            Use this schema context to understand which tables to query and structure COMPREHENSIVE SQL queries that accomplish multiple objectives in single operations.
            
            EXECUTION OPTIMIZATION:
            - Write complex SQL queries that join multiple tables and perform comprehensive analysis
            - Use advanced SQL features like CTEs, window functions, and subqueries for efficiency
            - Combine filtering, sorting, and aggregation in single queries
            - Minimize database round trips by getting all needed data in fewer queries
            
            Execute each step of the plan and provide the final answer.
            Use the appropriate tools when you need to:
            - Perform calculations (calculator tool)
            - Get comprehensive data from the database (query_database tool) - write optimized SQL using schema context
            - Get specialized analysis (agent tools)
            
            Always provide a clear, complete response with the final result.
            When using the database tool, write efficient SQL queries that maximize data retrieval in minimal operations.
            
            SCHEMA CONTEXT:
            {schema_context}""",
        ),
        ("placeholder", "{messages}"),
    ]
)

# Create executor with multiple agent tools and database tool
def create_executor_with_context(state):
    """Crea el executor con el contexto del esquema"""
    return execution_prompt.partial(schema_context=state["schema_context"]) | llm.bind_tools([
        calculate, sales_agent, finance_agent, inventory_agent, field_ops_agent,
        query_database
    ])

executor = create_executor_with_context

# Function to execute plan step by step
def execute_plan(state):
    """Ejecuta el plan paso a paso usando el executor con contexto"""
    try:
        plan = state["plan"]
        schema_context = state["schema_context"]
        user_query = state["input"]
        
        # Crear el executor con el contexto del esquema
        executor_with_context = create_executor_with_context(state)
        
        # Ejecutar cada paso del plan
        step_results = []
        for i, step in enumerate(plan):
            step_prompt = f"""Step {i+1}: {step}

Original Query: {user_query}

Schema Context:
{schema_context}

Please execute this step using the appropriate tools and provide detailed analysis."""
            
            response = executor_with_context.invoke([HumanMessage(content=step_prompt)])
            step_results.append(response.content)
        
        # Combinar resultados
        combined_response = f"""
# PLAN EXECUTION COMPLETED

## ORIGINAL QUERY:
{user_query}

## SCHEMA CONTEXT:
{schema_context}

## PLAN EXECUTED:
{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(plan)])}

## RESULTS BY STEP:
{chr(10).join([f'### Step {i+1}: {plan[i]}\n{result}\n' for i, result in enumerate(step_results)])}

## EXECUTIVE SUMMARY
Successfully completed step-by-step execution using the database schema context and specialized tools.
"""
        
        return {"response": combined_response}
        
    except Exception as e:
        return {"response": f"Error executing plan: {str(e)}"}

# Define the state graph
def create_plan_and_execute_graph():
    workflow = StateGraph(PlanExecute)
    
    # Add nodes
    workflow.add_node("get_schema", get_schema_context)
    workflow.add_node("prepare_planner", prepare_planner_input)
    workflow.add_node("planner", planner_with_logging)
    
    # Add edges
    workflow.add_edge("get_schema", "prepare_planner")
    workflow.add_edge("prepare_planner", "planner")
    workflow.add_edge("planner", END)
    
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
    
    # Execute the graph with schema context
    initial_state = {
        "input": user_query,
        "schema_context": "",
        "plan": [],
        "past_steps": [],
        "response": ""
    }
    
    print(f"📊 Initial state: {initial_state}")
    print(f"🔄 Executing graph...")
    
    result = graph.invoke(initial_state)
    
    print(f"✅ Graph execution completed")
    print(f"📋 Final result keys: {list(result.keys())}")
    print(f"📋 Schema context length: {len(result.get('schema_context', ''))}")
    print(f"📋 Plan steps: {len(result.get('plan', []))}")
    
    return {
        "input": user_query,
        "schema_context": result.get("schema_context", ""),
        "plan": result.get("plan", []),
        # "response": result.get("response", ""),
        # "past_steps": result.get("past_steps", [])
    }
    
#     # Track past steps
#     past_steps = [("planner", f"Generated plan with {len(plan_result.steps)} steps")]
    
#     # Execute the plan step by step with re-planning
#     print(f"Starting execution of plan with {len(plan_result.steps)} steps")
    
#     current_context = f"User Query: {user_query}\n\nFull Plan:\n{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(plan_result.steps)])}\n\nPrevious Steps Results:"
#     step_results = []
    
#     for i, step in enumerate(plan_result.steps):
#         print(f"\n--- Executing Step {i+1}: {step} ---")
        
#         # Determine which agent to use based on the step content
#         step_lower = step.lower()
        
#         if any(word in step_lower for word in ['inventario', 'backorder', 'stock', 'producto']):
#             agent_to_use = inventory_agent
#             agent_name = "inventory_agent"
#         elif any(word in step_lower for word in ['venta', 'demanda', 'cliente', 'mercado']):
#             agent_to_use = sales_agent
#             agent_name = "sales_agent"
#         elif any(word in step_lower for word in ['financiero', 'costo', 'roi', 'ganancia', 'compra']):
#             agent_to_use = finance_agent
#             agent_name = "finance_agent"
#         elif any(word in step_lower for word in ['operacional', 'logística', 'proveedor', 'entrega']):
#             agent_to_use = field_ops_agent
#             agent_name = "field_ops_agent"
#         else:
#             # Default to inventory agent for general queries
#             agent_to_use = inventory_agent
#             agent_name = "inventory_agent"
        
#         print(f"Using {agent_name} for step {i+1}")
        
#         # Execute the step with the appropriate agent, including previous results
#         step_prompt = f"""Step {i+1}: {step}

# Original Query: {user_query}

# Previous Steps Results:
# {current_context}

# Please execute this step using the information from previous steps and provide detailed analysis with realistic simulated data."""
        
#         step_content = agent_to_use(step_prompt)
        
#         print(f"Step {i+1} result: {step_content[:100]}...")
#         step_results.append(step_content)
        
#         # Update context with this step's result
#         current_context += f"\n\nStep {i+1} Result:\n{step_content}"
        
#         # Add to past_steps
#         past_steps.append(("executor", f"Executed step {i+1} with {agent_name}: {step[:50]}..."))
        
#         print(f"Step {i+1} completed")
    
#     # Combine all step results
#     combined_analysis = f"""
# # EJECUCIÓN PASO A PASO COMPLETADA

# ## PLAN EJECUTADO:
# {chr(10).join([f'{i+1}. {step}' for i, step in enumerate(plan_result.steps)])}

# ## RESULTADOS POR PASO:

# {chr(10).join([f'### Paso {i+1}: {plan_result.steps[i]}\n{result}\n' for i, result in enumerate(step_results)])}

# ## RESUMEN EJECUTIVO
# Se ha completado exitosamente la ejecución del plan paso a paso, utilizando los agentes especializados según las necesidades de cada etapa.
# """
    
#     execution_result = type('obj', (object,), {'content': combined_analysis})()
    
#     # Add execution step to past_steps
#     past_steps.append(("executor", "Executed all plan steps"))
    
#     return {
#         "input": user_query,
#         "plan": plan_result.steps,
#         "response": execution_result.content,
#         "past_steps": past_steps
#     }