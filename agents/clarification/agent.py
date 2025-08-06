from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .prompt import CLARIFICATION_AGENT_PROMPT
from config.hybrid_llm_manager import hybrid_llm_manager
import json
from typing import Dict, Any, Optional

class ClarificationAgent:
    def __init__(self):
        # Usar el manager híbrido para obtener LLM especializado
        self.llm = hybrid_llm_manager.get_llm_for_agent("ClarificationAgent")
        self.prompt = ChatPromptTemplate.from_template(CLARIFICATION_AGENT_PROMPT)
    
    def analyze_query(self, user_input: str, chat_history: list = None) -> Dict[str, Any]:
        """
        Analiza la consulta del usuario y determina si necesita clarificación
        
        Returns:
            {
                "needs_clarification": bool,
                "clarification_questions": list[str] | None,
                "reason": str | None,
                "can_proceed": bool
            }
        """
        try:
            # Construir contexto con historial si existe
            context = user_input
            if chat_history:
                context_parts = []
                for msg in reversed(chat_history[-3:]):  # Últimos 3 mensajes
                    context_parts.append(f"Usuario: {msg['user_message']}")
                    context_parts.append(f"IA: {msg['ai_response']}")
                context_parts.append(f"Usuario: {user_input}")
                context = "\n".join(context_parts)
            
            chain = self.prompt | self.llm
            response = chain.invoke({
                "user_input": user_input,
                "context": context,
                "chat_history_length": len(chat_history) if chat_history else 0
            })
            
            try:
                result = json.loads(response.content.strip())
                
                # Validar estructura de respuesta
                required_fields = ["needs_clarification", "can_proceed"]
                for field in required_fields:
                    if field not in result:
                        result[field] = False
                
                # Asegurar que clarification_questions sea una lista
                if result.get("needs_clarification") and "clarification_questions" not in result:
                    result["clarification_questions"] = ["¿Podrías ser más específico sobre tu consulta?"]
                
                return result
                
            except json.JSONDecodeError:
                print(f"Error parsing clarification response: {response.content}")
                return {
                    "needs_clarification": False,
                    "clarification_questions": None,
                    "reason": "Error parsing response",
                    "can_proceed": True
                }
                
        except Exception as e:
            return {
                "needs_clarification": False,
                "clarification_questions": None,
                "reason": f"Error in clarification agent: {str(e)}",
                "can_proceed": True
            }
    
    def generate_followup_response(self, clarification_questions: list) -> str:
        """Genera una respuesta amigable con las preguntas de clarificación"""
        if not clarification_questions:
            return "¿Podrías ser más específico sobre tu consulta?"
        
        if len(clarification_questions) == 1:
            return f"Para ayudarte mejor, necesito aclarar algo: {clarification_questions[0]}"
        
        response = "Para darte la mejor respuesta, necesito aclarar algunos puntos:\n\n"
        for i, question in enumerate(clarification_questions, 1):
            response += f"{i}. {question}\n"
        
        response += "\n¿Podrías responder estas preguntas para que pueda ayudarte mejor?"
        return response 