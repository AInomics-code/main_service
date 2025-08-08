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
            """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

# Create planner
planner = planner_prompt | planner_llm.with_structured_output(Plan)

# Execution prompt
execution_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI who executes plans step by step. You have access to a calculator tool.
            Execute each step of the plan and provide the final answer.
            Use the calculator tool when you need to perform calculations.
            Always provide a clear, complete response with the final result.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

# Create executor with multiple agent tools
executor = execution_prompt | llm.bind_tools([calculate, sales_agent, finance_agent, inventory_agent, field_ops_agent])

# Define the state graph
def create_plan_and_execute_graph():
    workflow = StateGraph(PlanExecute)
    
    # Add nodes
    workflow.add_node("planner", planner)
    workflow.add_node("executor", executor)
    
    # Add edges
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", END)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
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
        user_query = body.get("query", "Cuales son los productos con mas backorder de mi inventario y como puedo reducirlo?")
    except:
        user_query = "Cuales son los productos con mas backorder de mi inventario y como puedo reducirlo?"
    
    # Get the plan first
    plan_result = planner.invoke({
        "messages": [
            ("user", user_query)
        ]
    })
    
    # Track past steps
    past_steps = [("planner", f"Generated plan with {len(plan_result.steps)} steps")]
    
    # Execute the plan step by step with re-planning
    print(f"Starting execution of plan with {len(plan_result.steps)} steps")
    
    current_context = f"User Query: {user_query}\n\nFull Plan:\n{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(plan_result.steps)])}\n\nPrevious Steps Results:"
    step_results = []
    
    for i, step in enumerate(plan_result.steps):
        print(f"\n--- Executing Step {i+1}: {step} ---")
        
        # Determine which agent to use based on the step content
        step_lower = step.lower()
        
        if any(word in step_lower for word in ['inventario', 'backorder', 'stock', 'producto']):
            agent_to_use = inventory_agent
            agent_name = "inventory_agent"
        elif any(word in step_lower for word in ['venta', 'demanda', 'cliente', 'mercado']):
            agent_to_use = sales_agent
            agent_name = "sales_agent"
        elif any(word in step_lower for word in ['financiero', 'costo', 'roi', 'ganancia', 'compra']):
            agent_to_use = finance_agent
            agent_name = "finance_agent"
        elif any(word in step_lower for word in ['operacional', 'logística', 'proveedor', 'entrega']):
            agent_to_use = field_ops_agent
            agent_name = "field_ops_agent"
        else:
            # Default to inventory agent for general queries
            agent_to_use = inventory_agent
            agent_name = "inventory_agent"
        
        print(f"Using {agent_name} for step {i+1}")
        
        # Execute the step with the appropriate agent, including previous results
        step_prompt = f"""Step {i+1}: {step}

Original Query: {user_query}

Previous Steps Results:
{current_context}

Please execute this step using the information from previous steps and provide detailed analysis with realistic simulated data."""
        
        step_content = agent_to_use(step_prompt)
        
        print(f"Step {i+1} result: {step_content[:100]}...")
        step_results.append(step_content)
        
        # Update context with this step's result
        current_context += f"\n\nStep {i+1} Result:\n{step_content}"
        
        # Add to past_steps
        past_steps.append(("executor", f"Executed step {i+1} with {agent_name}: {step[:50]}..."))
        
        print(f"Step {i+1} completed")
    
    # Combine all step results
    combined_analysis = f"""
# EJECUCIÓN PASO A PASO COMPLETADA

## PLAN EJECUTADO:
{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(plan_result.steps)])}

## RESULTADOS POR PASO:

{chr(10).join([f'### Paso {i+1}: {plan_result.steps[i]}\n{result}\n' for i, result in enumerate(step_results)])}

## RESUMEN EJECUTIVO
Se ha completado exitosamente la ejecución del plan paso a paso, utilizando los agentes especializados según las necesidades de cada etapa.
"""
    
    execution_result = type('obj', (object,), {'content': combined_analysis})()
    
    # Add execution step to past_steps
    past_steps.append(("executor", "Executed all plan steps"))
    
    return {
        "input": user_query,
        "plan": plan_result.steps,
        "response": execution_result.content,
        "past_steps": past_steps
    }