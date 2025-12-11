"""Chat session management - MongoDB implementation."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.db.repositories.sessions_repo import ChatSessionsRepository

class ChatSession:
    """Chat session management."""

    def __init__(self, session_id: str, user_id: str = "anonymous"):
        """
        Initialize a chat session.

        Args:
            session_id: Unique session identifier
            user_id: User identifier
        """
        self.session_id = session_id
        self.user_id = user_id
        self.repo = ChatSessionsRepository()
        self._load_or_create()

    def _load_or_create(self):
        """Load session from DB or create if new."""
        # This ensures the session document exists
        self.repo.get_or_create(self.session_id, self.user_id)
        
    def add_message(self, role: str, content: str):
        """
        Add a message to the session.

        Args:
            role: Message role (e.g., 'user', 'assistant')
            content: Message content
        """
        self.repo.add_message(self.session_id, role, content)

    def get_context(self, last_n: int = 5) -> str:
        """
        Get recent messages as context string.

        Args:
            last_n: Number of recent messages to include

        Returns:
            Formatted context string
        """
        messages = self.repo.get_messages(self.session_id, limit=last_n)
        # Messages from repo are dicts, need to format them
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    def get_messages(self, limit: int = 20) -> List[Dict]:
        """Get raw messages list."""
        return self.repo.get_messages(self.session_id, limit=limit)

    def should_trigger_recommendation(self, message: str) -> bool:
        """
        Check if message should trigger VR app recommendation.

        Args:
            message: User message

        Returns:
            True if recommendation should be triggered
        """
        triggers = [
            "recommend", "suggest", "find", "vr app", "application",
            "应用", "推荐", "learn", "study", "want to", "looking for",
            "help me", "what should", "how to"
        ]
        return any(t in message.lower() for t in triggers)

    def clear_history(self):
        """Clear session history (Not implemented for persistent DB)."""
        # In a persistent DB, we typically don't delete history unless requested.
        # For now, we can just mark it ended or do nothing.
        pass

    def get_message_count(self) -> int:
        """Get total number of messages in session."""
        doc = self.repo.collection.find_one({"_id": self.session_id}, {"message_count": 1})
        return doc.get("message_count", 0) if doc else 0

    def get_messages_for_llm(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get messages formatted for OpenAI API.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        messages = self.get_messages(limit=limit)
        llm_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Only include user and assistant messages with content
            if role in ["user", "assistant"] and content:
                llm_messages.append({"role": role, "content": content})
        return llm_messages

    def set_last_recommended_apps(self, apps: List[Dict[str, Any]]):
        """
        Store the last recommended apps for follow-up queries.

        Args:
            apps: List of app dicts to store
        """
        self.repo.update_metadata(
            self.session_id,
            {"last_recommended_apps": apps[:5]}  # Store top 5
        )

    def get_last_recommended_apps(self) -> List[Dict[str, Any]]:
        """
        Get the last recommended apps from session.

        Returns:
            List of app dicts or empty list
        """
        doc = self.repo.collection.find_one(
            {"_id": self.session_id},
            {"last_recommended_apps": 1}
        )
        return doc.get("last_recommended_apps", []) if doc else []

    def add_tool_interaction(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_result: Dict[str, Any]
    ):
        """
        Log a tool interaction for debugging/analytics.

        Args:
            tool_name: Name of the tool called
            tool_args: Arguments passed to the tool
            tool_result: Result returned by the tool
        """
        self.repo.add_tool_call(
            self.session_id,
            tool_name,
            tool_args,
            tool_result
        )