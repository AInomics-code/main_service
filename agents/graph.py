from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from .pipeline_planner.agent import PipelinePlannerAgent
from .language_detector.agent import LanguageDetectorAgent
from .supervisor.agent import SupervisorAgent
from .registry import get_agent, list_available_agents, agent_exists

class AgentState(TypedDict):
    user_input: str
    pipeline_plan: Dict[str, Any] | None
    detected_language: str | None
    agent_results: Dict[str, Any] | None
    final_response: str | None

class DynamicAgentGraph:
    def __init__(self):
        self.pipeline_planner = PipelinePlannerAgent()
        self.language_detector = LanguageDetectorAgent()
        self.supervisor = SupervisorAgent()
        
        # Cargar schema una sola vez para toda la sesión
        from tools.sqlserver_database_tool import SQLServerDatabaseTool
        temp_db_tool = SQLServerDatabaseTool()
        self.shared_schema = temp_db_tool.get_cached_schema_json()
        
        # Cargar todos los agentes automáticamente
        import agents
        
        self.graph = self._build_graph()
    
    def _get_schema_summarizer(self):
        """Obtiene la instancia Singleton del SchemaSummarizer"""
        from schema_summarizer.schema_summarizer import SchemaSummarizer
        return SchemaSummarizer()  # El Singleton se encarga de reutilizar la instancia
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Nodos paralelos iniciales
        workflow.add_node("pipeline_planner", self._pipeline_planner_node)
        workflow.add_node("detect_language", self._detect_language_node)
        
        # Nodo para ejecutar agentes del pipeline
        workflow.add_node("execute_agents", self._execute_agents_node)
        
        # Nodo supervisor final
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Puntos de entrada paralelos
        workflow.set_entry_point("pipeline_planner")
        workflow.set_entry_point("detect_language")
        
        # Flujo: paralelo inicial -> ejecutar agentes -> supervisor -> END
        workflow.add_edge("pipeline_planner", "execute_agents")
        workflow.add_edge("detect_language", "execute_agents")
        workflow.add_edge("execute_agents", "supervisor")
        workflow.add_edge("supervisor", END)
        
        return workflow.compile()
    
    def _pipeline_planner_node(self, state: AgentState) -> AgentState:
        """Nodo que planifica el pipeline de agentes"""
        try:
            plan = self.pipeline_planner.plan_pipeline(state["user_input"])
            return {"pipeline_plan": plan}
        except Exception as e:
            return {
                "pipeline_plan": {
                    "pipeline": [["StrategyAgent"]],
                    "error": f"Error en pipeline planner: {str(e)}"
                }
            }
    
    def _detect_language_node(self, state: AgentState) -> AgentState:
        """Nodo que detecta el idioma del usuario"""
        try:
            language = self.language_detector.detect_language(state["user_input"])
            return {"detected_language": language}
        except Exception as e:
            return {"detected_language": f"Error: {str(e)}"}
    
    def _get_relevant_schema_content(self, user_input: str, top_k: int = 5) -> str:
        """Obtiene el contenido completo de las tablas relevantes"""
        try:
            # Usar el Singleton del SchemaSummarizer
            schema_summarizer = self._get_schema_summarizer()
            relevant_tables = schema_summarizer.search_relevant_tables(user_input, top_k)
            
            # Construir contenido completo de las tablas relevantes
            schema_content = "SCHEMA RELEVANTE PARA LA CONSULTA:\n\n"
            
            for table in relevant_tables:
                schema_content += f"=== TABLA: {table['table_name'].upper()} ===\n"
                schema_content += f"Relevancia: {table['relevance_score']:.4f}\n"
                schema_content += f"Contenido:\n{table['content']}\n\n"
                schema_content += "=" * 50 + "\n\n"
            
            return schema_content
            
        except Exception as e:
            print(f"Error obteniendo contenido de schema relevante: {e}")
            return "Schema relevante no disponible"
    
    def _execute_agents_node(self, state: AgentState) -> AgentState:
        """Nodo que ejecuta dinámicamente los agentes según el plan"""
        try:
            pipeline_plan = state["pipeline_plan"]
            user_input = state["user_input"]
            
            # Obtener contenido completo de las tablas relevantes
            relevant_schema_content = self._get_relevant_schema_content(user_input)
            
            if not pipeline_plan or "error" in pipeline_plan:
                return {
                    "agent_results": {
                        "error": pipeline_plan.get("error", "No pipeline plan available"),
                        "results": []
                    }
                }
            
            pipeline = pipeline_plan.get("pipeline", [["StrategyAgent"]])
            results = []
            
            # Ejecutar cada paso del pipeline
            for step in pipeline:
                step_results = []
                
                # Ejecutar agentes en paralelo dentro del paso
                for agent_name in step:
                    try:
                        if agent_exists(agent_name):
                            agent = get_agent(agent_name)
                            
                            # Pasar el schema compartido y el contenido relevante
                            if agent_name == "StrategyAgent":
                                result = agent.synthesize_results(user_input, str(results), self.shared_schema, relevant_schema_content)
                            else:
                                result = agent.run(user_input, self.shared_schema, relevant_schema_content)
                            
                            step_results.append({
                                "agent": agent_name,
                                "result": result,
                                "status": "success"
                            })
                        else:
                            step_results.append({
                                "agent": agent_name,
                                "error": f"Agente {agent_name} no encontrado en el registro",
                                "status": "not_found"
                            })
                    except Exception as e:
                        step_results.append({
                            "agent": agent_name,
                            "error": str(e),
                            "status": "error"
                        })
                
                results.append({
                    "step": step,
                    "results": step_results
                })
            
            return {"agent_results": {"results": results}}
            
        except Exception as e:
            return {
                "agent_results": {
                    "error": f"Error ejecutando agentes: {str(e)}",
                    "results": []
                }
            }
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Nodo supervisor que combina todos los resultados en el idioma detectado"""
        try:
            user_input = state["user_input"]
            pipeline_plan = state["pipeline_plan"]
            detected_language = state["detected_language"]
            agent_results = state["agent_results"]
            
            # Obtener contenido completo de las tablas relevantes para el supervisor
            relevant_schema_content = self._get_relevant_schema_content(user_input)
            
            # Crear un resumen para el supervisor
            summary = {
                "user_input": user_input,
                "pipeline_plan": pipeline_plan,
                "agent_results": agent_results,
                "detected_language": detected_language
            }
            
            # El supervisor ahora maneja el idioma detectado y contenido relevante
            final_response = self.supervisor.combine_results(
                user_input,
                str(pipeline_plan),
                detected_language or "Unknown",
                str(agent_results),
                relevant_schema_content
            )
            
            return {"final_response": final_response}
            
        except Exception as e:
            return {"final_response": f"Error en supervisor: {str(e)}"}
    
    def process(self, user_input: str) -> dict:
        initial_state = {
            "user_input": user_input,
            "pipeline_plan": None,
            "detected_language": None,
            "agent_results": None,
            "final_response": None
        }
        
        result = self.graph.invoke(initial_state)
        return result 