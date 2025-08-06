from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from .pipeline_planner.agent import PipelinePlannerAgent
from .language_detector.agent import LanguageDetectorAgent
from .supervisor.agent import SupervisorAgent
from .clarification.agent import ClarificationAgent
from .registry import get_agent, list_available_agents, agent_exists
from config.hybrid_llm_config import AGENT_CONFIG

class AgentState(TypedDict):
    user_input: str
    clarification_result: Dict[str, Any] | None  # Nuevo campo
    pipeline_plan: Dict[str, Any] | None
    detected_language: str | None
    agent_results: Dict[str, Any] | None
    final_response: str | None

class DynamicAgentGraph:
    def __init__(self):
        self.clarification_agent = ClarificationAgent()  # Nuevo agente
        self.pipeline_planner = PipelinePlannerAgent()
        self.language_detector = LanguageDetectorAgent()
        self.supervisor = SupervisorAgent()
        
        # Cargar todos los agentes automáticamente
        import agents
        
        self.graph = self._build_graph()
    
    def _get_schema_summarizer(self):
        """Retorna una instancia del SchemaSummarizer (Singleton)"""
        from schema_summarizer.schema_summarizer import SchemaSummarizer
        return SchemaSummarizer()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Nodo de clarificación (nuevo)
        workflow.add_node("clarification", self._clarification_node)
        
        # Nodos paralelos después de clarificación
        workflow.add_node("pipeline_planner", self._pipeline_planner_node)
        workflow.add_node("detect_language", self._detect_language_node)
        
        # Nodo para ejecutar agentes del pipeline
        workflow.add_node("execute_agents", self._execute_agents_node)
        
        # Nodo supervisor final
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Punto de entrada: clarificación
        workflow.set_entry_point("clarification")
        
        # Flujo condicional basado en clarificación
        workflow.add_conditional_edges(
            "clarification",
            self._should_proceed,
            {
                "needs_clarification": END,  # Terminar si necesita clarificación
                "proceed": "pipeline_planner"  # Continuar con el pipeline
            }
        )
        
        # Flujo normal después de clarificación
        workflow.add_edge("pipeline_planner", "execute_agents")
        workflow.add_edge("detect_language", "execute_agents")
        workflow.add_edge("execute_agents", "supervisor")
        workflow.add_edge("supervisor", END)
        
        return workflow.compile()
    
    def _clarification_node(self, state: AgentState) -> AgentState:
        """Nodo que analiza si la consulta necesita clarificación"""
        try:
            # Obtener historial de chat si está disponible
            chat_history = getattr(self, '_chat_history', [])
            
            clarification_result = self.clarification_agent.analyze_query(
                state["user_input"], 
                chat_history
            )
            
            return {"clarification_result": clarification_result}
            
        except Exception as e:
            return {
                "clarification_result": {
                    "needs_clarification": False,
                    "clarification_questions": None,
                    "reason": f"Error en clarificación: {str(e)}",
                    "can_proceed": True
                }
            }
    
    def _should_proceed(self, state: AgentState) -> str:
        """Función condicional para determinar el flujo"""
        clarification_result = state.get("clarification_result", {})
        
        if clarification_result.get("needs_clarification", False):
            return "needs_clarification"
        else:
            return "proceed"
    
    def _pipeline_planner_node(self, state: AgentState) -> AgentState:
        """Nodo que planifica el pipeline de agentes"""
        try:
            plan = self.pipeline_planner.plan_pipeline(state["user_input"])
            return {"pipeline_plan": plan}
        except Exception as e:
            # Usar configuración en lugar de hardcoding
            default_agent = AGENT_CONFIG.get("StrategyAgent", {}).get("default_fallback", "StrategyAgent")
            return {
                "pipeline_plan": {
                    "pipeline": [[default_agent]],
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
            
            # Usar configuración en lugar de hardcoding
            default_agent = AGENT_CONFIG.get("StrategyAgent", {}).get("default_fallback", "StrategyAgent")
            pipeline = pipeline_plan.get("pipeline", [[default_agent]])
            results = []
            
            # Ejecutar cada paso del pipeline
            for step in pipeline:
                step_results = []
                
                # Ejecutar agentes en paralelo dentro del paso
                for agent_name in step:
                    try:
                        if agent_exists(agent_name):
                            agent = get_agent(agent_name)
                            
                            # Pasar SOLO el contenido relevante del schema
                            if agent_name == "StrategyAgent":
                                result = agent.synthesize_results(user_input, str(results), None, relevant_schema_content)
                            elif agent_name == "Supervisor":
                                # El Supervisor necesita usar combine_results para sintetizar resultados
                                result = agent.combine_results(
                                    user_input,
                                    str(state.get("pipeline_plan", {})),
                                    state.get("detected_language", "Unknown"),
                                    str(results),
                                    relevant_schema_content
                                )
                            else:
                                result = agent.run(user_input, None, relevant_schema_content)
                            
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
            
            # El supervisor ahora maneja SOLO el contenido relevante
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
    
    def process(self, user_input: str, chat_history: list = None) -> dict:
        # Guardar historial para usar en clarificación
        self._chat_history = chat_history or []
        
        initial_state = {
            "user_input": user_input,
            "clarification_result": None,  # Nuevo campo
            "pipeline_plan": None,
            "detected_language": None,
            "agent_results": None,
            "final_response": None
        }
        
        result = self.graph.invoke(initial_state)
        
        # Si necesita clarificación, generar respuesta apropiada manteniendo estructura consistente
        if result.get("clarification_result", {}).get("needs_clarification"):
            clarification_questions = result["clarification_result"].get("clarification_questions", [])
            followup_response = self.clarification_agent.generate_followup_response(clarification_questions)
            
            # Mantener la misma estructura pero con final_response para clarificación
            result["final_response"] = followup_response
            result["type"] = "clarification_needed"
            result["clarification_questions"] = clarification_questions
            result["reason"] = result["clarification_result"].get("reason")
        
        return result 