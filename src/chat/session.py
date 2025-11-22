"""Chat session management for VR recommender.

Manages user chat sessions, including history and context.
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class ChatSession:
    """Chat session management."""

    def __init__(self, session_id: str, storage_dir: str = "chat_logs"):
        """
        Initialize a chat session.

        Args:
            session_id: Unique session identifier
            storage_dir: Directory to store session logs
        """
        self.session_id = session_id
        self.storage_dir = storage_dir
        self.storage_path = f"{storage_dir}/{session_id}.json"
        self.history: List[Dict] = []

        os.makedirs(storage_dir, exist_ok=True)
        self._load()

    def _load(self):
        """Load session history from disk."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.history = json.load(f)

    def save(self):
        """Save session history to disk."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_message(self, role: str, content: str):
        """
        Add a message to the session.

        Args:
            role: Message role (e.g., 'user', 'assistant')
            content: Message content
        """
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save()

    def get_context(self, last_n: int = 5) -> str:
        """
        Get recent messages as context.

        Args:
            last_n: Number of recent messages to include

        Returns:
            Formatted context string
        """
        recent = self.history[-last_n:] if len(self.history) > last_n else self.history
        return "\n".join([f"{m['role']}: {m['content']}" for m in recent])

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
        """Clear session history."""
        self.history = []
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)

    def get_message_count(self) -> int:
        """Get total number of messages in session."""
        return len(self.history)
