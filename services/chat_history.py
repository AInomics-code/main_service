"""
Chat history service using Redis for session management
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config.redis_config import get_redis_client

class ChatHistoryService:
    """Service for managing chat history with Redis"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.session_ttl = 24 * 60 * 60  # 24 hours in seconds
        self.max_messages_per_session = 50  # Maximum messages to keep per session
    
    def create_session(self) -> str:
        """
        Create a new chat session with a random UUID
        Returns the session ID
        """
        session_id = str(uuid.uuid4())
        session_key = f"chat_session:{session_id}"
        
        # Initialize session with metadata
        session_data = {
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "message_count": 0
        }
        
        # Store session metadata
        self.redis_client.hset(session_key, mapping=session_data)
        self.redis_client.expire(session_key, self.session_ttl)
        
        return session_id
    
    def add_message(self, session_id: str, message: str, response: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a message and response to the chat history
        Returns True if successful, False otherwise
        """
        try:
            session_key = f"chat_session:{session_id}"
            messages_key = f"chat_messages:{session_id}"
            
            # Check if session exists
            if not self.redis_client.exists(session_key):
                return False
            
            # Create message entry
            message_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_message": message,
                "ai_response": response,
                "metadata": metadata or {}
            }
            
            # Add message to list (left push to maintain chronological order)
            self.redis_client.lpush(messages_key, json.dumps(message_data))
            
            # Limit the number of messages per session
            self.redis_client.ltrim(messages_key, 0, self.max_messages_per_session - 1)
            
            # Update session metadata
            self.redis_client.hincrby(session_key, "message_count", 1)
            self.redis_client.hset(session_key, "last_activity", datetime.utcnow().isoformat())
            
            # Set TTL for messages
            self.redis_client.expire(messages_key, self.session_ttl)
            
            return True
            
        except Exception as e:
            print(f"Error adding message to session {session_id}: {e}")
            return False
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """
        Get chat history for a session
        Returns list of messages (most recent first)
        """
        try:
            session_key = f"chat_session:{session_id}"
            messages_key = f"chat_messages:{session_id}"
            
            # Check if session exists
            if not self.redis_client.exists(session_key):
                return []
            
            # Get messages (most recent first due to LPUSH)
            messages = self.redis_client.lrange(messages_key, 0, limit - 1)
            
            # Parse JSON messages
            history = []
            for msg in messages:
                try:
                    history.append(json.loads(msg))
                except json.JSONDecodeError:
                    continue
            
            return history
            
        except Exception as e:
            print(f"Error getting history for session {session_id}: {e}")
            return []
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists
        """
        try:
            session_key = f"chat_session:{session_id}"
            return self.redis_client.exists(session_key) > 0
        except Exception as e:
            print(f"Error checking session {session_id}: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get session metadata
        """
        try:
            session_key = f"chat_session:{session_id}"
            
            if not self.redis_client.exists(session_key):
                return None
            
            session_data = self.redis_client.hgetall(session_key)
            return session_data
            
        except Exception as e:
            print(f"Error getting session info for {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages
        """
        try:
            session_key = f"chat_session:{session_id}"
            messages_key = f"chat_messages:{session_id}"
            
            # Delete both session metadata and messages
            self.redis_client.delete(session_key, messages_key)
            return True
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (Redis handles this automatically with TTL)
        Returns number of sessions cleaned up
        """
        try:
            # This is mostly informational since Redis handles TTL automatically
            # We could implement manual cleanup if needed
            return 0
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0

# Global instance
chat_history_service = ChatHistoryService() 