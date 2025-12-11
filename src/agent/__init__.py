"""Agent module for conversational VR app recommendations.

This module provides a tool-calling agent architecture that intelligently
decides when to trigger VR app retrieval based on conversation context.
"""

from .agent import ConversationAgent

__all__ = ["ConversationAgent"]
