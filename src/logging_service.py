import uuid
import time
from typing import Dict, Any, Optional
from .database import Database

class InteractionLogger:
    """Service to handle interaction logging to the database."""
    
    def __init__(self):
        self.db = Database()
        
    def log_interaction(self, 
                        user_id: str, 
                        query: str, 
                        response: str, 
                        intent: str = "unknown",
                        recommended_apps: list = None,
                        metadata: Dict[str, Any] = None,
                        session_id: Optional[str] = None):
        """
        Log a chat interaction.
        
        Args:
            user_id: Unique identifier for the user
            query: The user's message
            response: The system's response text
            intent: Detected intent (e.g., 'recommendation', 'greeting')
            recommended_apps: List of recommended app objects (optional)
            metadata: Additional data like latency, source (optional)
            session_id: Session identifier (optional)
        """
        try:
            self.db.log_interaction(
                user_id=user_id,
                session_id=session_id,
                query_text=query,
                intent=intent,
                response_text=response,
                recommended_apps=recommended_apps,
                metadata=metadata
            )
            print(f"📝 Logged interaction for user {user_id[:8]}...")
        except Exception as e:
            print(f"❌ Failed to log interaction: {e}")

    def get_admin_logs(self, limit: int = 50, offset: int = 0, user_id: str = None):
        """Get logs for admin dashboard."""
        return self.db.get_logs(limit, offset, user_id)

    def get_admin_stats(self):
        """Get system stats."""
        return self.db.get_stats()
