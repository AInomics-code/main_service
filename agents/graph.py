from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from .task_classifier.agent import TaskClassifierAgent
from .language_detector.agent import LanguageDetectorAgent
from .supervisor.agent import SupervisorAgent

class AgentState(TypedDict):
    user_input: str
    task_category: str | None
    detected_language: str | None
    final_response: str | None

class ParallelAgentGraph:
    def __init__(self):
        self.task_classifier = TaskClassifierAgent()
        self.language_detector = LanguageDetectorAgent()
        self.supervisor = SupervisorAgent()
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("classify_task", self._classify_task_node)
        workflow.add_node("detect_language", self._detect_language_node)
        workflow.add_node("supervisor", self._supervisor_node)
        
        workflow.set_entry_point("classify_task")
        workflow.set_entry_point("detect_language")
        
        workflow.add_edge("classify_task", "supervisor")
        workflow.add_edge("detect_language", "supervisor")
        
        workflow.add_edge("supervisor", END)
        
        return workflow.compile()
    
    def _classify_task_node(self, state: AgentState) -> AgentState:
        try:
            category = self.task_classifier.classify_task(state["user_input"])
            return {"task_category": category}
        except Exception as e:
            return {"task_category": f"Error: {str(e)}"}
    
    def _detect_language_node(self, state: AgentState) -> AgentState:
        try:
            language = self.language_detector.detect_language(state["user_input"])
            return {"detected_language": language}
        except Exception as e:
            return {"detected_language": f"Error: {str(e)}"}
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        try:
            final_response = self.supervisor.combine_results(
                state["user_input"],
                state["task_category"],
                state["detected_language"]
            )
            return {"final_response": final_response}
        except Exception as e:
            return {"final_response": f"Error in supervisor: {str(e)}"}
    
    def process(self, user_input: str) -> dict:
        initial_state = {
            "user_input": user_input,
            "task_category": None,
            "detected_language": None,
            "final_response": None
        }
        
        result = self.graph.invoke(initial_state)
        return result 