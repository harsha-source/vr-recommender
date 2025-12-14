"""Conversational Agent with Tool-Calling for VR App Recommendations.

This module implements a conversational agent that uses OpenRouter's function calling
capabilities to intelligently decide when to search for VR apps.
"""

import json
from typing import List, Dict, Any, Optional

from openai import OpenAI

from src.config_manager import ConfigManager
from src.chat.session import ChatSession
from src.rag.service import RAGService
from .tools import AVAILABLE_TOOLS, SYSTEM_PROMPT


class ConversationAgent:
    """Conversational agent with tool-calling capabilities."""

    def __init__(self):
        """Initialize the conversation agent."""
        self.config = ConfigManager()
        self.client = OpenAI(
            api_key=self.config.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = self.config.openrouter_model
        self.rag_service = RAGService()

    def process_message(
        self,
        session_id: str,
        user_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Args:
            session_id: Unique session identifier
            user_id: User identifier
            message: User message text

        Returns:
            Dict containing response text and metadata
        """
        # 1. Load/create session
        session = ChatSession(session_id, user_id)

        # 2. Add user message to history
        session.add_message("user", message)

        # 3. Get conversation history for context
        history = session.get_messages(limit=10)

        # 4. Build messages array for LLM
        messages = self._build_messages(history)

        # 5. Call LLM with tools
        try:
            response = self._call_llm_with_tools(messages)
        except Exception as e:
            print(f"[Agent] LLM call error: {e}")
            # Fallback to simple response
            return self._fallback_response(message, session)

        # 6. Handle response (may include tool calls)
        result = self._handle_response(response, messages, session)

        # 7. Save assistant response to session
        session.add_message("assistant", result["response"])

        return result

    def _build_messages(self, history: List[Dict]) -> List[Dict]:
        """
        Build OpenAI-format messages array from session history.

        Args:
            history: List of message dicts from session

        Returns:
            List of OpenAI-format message dicts
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Skip tool-related messages in history for now
            # (They don't need to be re-sent to the LLM)
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

        return messages

    def _call_llm_with_tools(self, messages: List[Dict]):
        """
        Call the LLM with tools parameter.

        Args:
            messages: List of message dicts

        Returns:
            OpenAI ChatCompletion response
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=AVAILABLE_TOOLS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1024
        )

    def _handle_response(
        self,
        response,
        messages: List[Dict],
        session: ChatSession
    ) -> Dict[str, Any]:
        """
        Handle LLM response, executing tools if needed.

        Args:
            response: OpenAI ChatCompletion response
            messages: Current messages list
            session: Chat session for storing tool interactions

        Returns:
            Dict with response text and metadata
        """
        choice = response.choices[0]
        message = choice.message

        # No tool call - return text directly
        if not message.tool_calls:
            return {
                "response": message.content or "I'm here to help with VR app recommendations.",
                "tool_used": None,
                "apps": []
            }

        # Execute tool calls
        tool_results = []
        apps_found = []

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"[Agent] Executing tool: {tool_name} with args: {tool_args}")

            if tool_name == "search_vr_apps":
                result = self._search_vr_apps(tool_args.get("query", ""))
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "result": result
                })
                apps_found = result.get("apps", [])
            else:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "result": {"error": f"Unknown tool: {tool_name}"}
                })

        # Append assistant message with tool calls
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        # Append tool results
        for tr in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tr["tool_call_id"],
                "content": json.dumps(tr["result"], ensure_ascii=False)
            })

        # Call LLM again with tool results to get final response
        try:
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            response_text = final_response.choices[0].message.content
        except Exception as e:
            print(f"[Agent] Final LLM call error: {e}")
            # Fallback: format apps directly
            response_text = self._format_apps_fallback(apps_found)

        return {
            "response": response_text or "I found some VR apps for you.",
            "tool_used": "search_vr_apps",
            "apps": apps_found
        }

    def _search_vr_apps(self, query: str) -> Dict[str, Any]:
        """
        Execute VR app search via RAG service.

        Args:
            query: Search query string

        Returns:
            Dict with apps list and metadata
        """
        if not query:
            return {"apps": [], "error": "Empty query"}

        try:
            result = self.rag_service.recommend(query, top_k=8)

            apps = []
            for app in result.apps:
                apps.append({
                    "name": app.name,
                    "category": app.category,
                    "score": round(app.score * 100),  # Convert to percentage
                    "matched_skills": app.matched_skills,
                    "reasoning": app.reasoning,
                    "retrieval_source": app.retrieval_source
                })

            return {
                "apps": apps,
                "query_understanding": result.query_understanding,
                "total_matches": result.total_matches
            }

        except Exception as e:
            print(f"[Agent] RAG search error: {e}")
            return {"apps": [], "error": str(e)}

    def _format_apps_fallback(self, apps: List[Dict]) -> str:
        """
        Format apps as markdown when LLM fails.

        Args:
            apps: List of app dicts

        Returns:
            Formatted markdown string
        """
        if not apps:
            return "I couldn't find specific VR apps matching your query. Could you try describing what you want to learn in different words?"

        lines = ["Here are VR apps that match your interests:\n"]

        for app in apps[:5]:
            score = app.get("score", 0)
            lines.append(f"- **{app['name']}** ({app['category']}) - {score}% match")
            if app.get("reasoning"):
                lines.append(f"  _{app['reasoning']}_")

        lines.append("\nWould you like more details about any of these apps?")
        return "\n".join(lines)

    def _fallback_response(
        self,
        message: str,
        session: ChatSession
    ) -> Dict[str, Any]:
        """
        Generate a fallback response when LLM fails.

        Args:
            message: Original user message
            session: Chat session

        Returns:
            Dict with response text
        """
        msg_lower = message.lower()

        # Simple intent detection fallback
        if any(g in msg_lower for g in ["hi", "hello", "hey"]):
            response = "Hello! I'm your VR app recommender. What would you like to learn?"
        elif any(t in msg_lower for t in ["thank", "thanks"]):
            response = "You're welcome! Let me know if you need more recommendations."
        elif any(h in msg_lower for h in ["help", "what can"]):
            response = "I can help you find VR apps for Meta Quest that support your learning goals. Just tell me what you want to learn!"
        else:
            # Try to do a search anyway
            result = self._search_vr_apps(message)
            if result.get("apps"):
                response = self._format_apps_fallback(result["apps"])
                session.add_message("assistant", response)
                return {"response": response, "tool_used": "search_vr_apps", "apps": result["apps"]}
            else:
                response = "I'm having trouble processing your request. Could you try rephrasing what you'd like to learn?"

        session.add_message("assistant", response)
        return {"response": response, "tool_used": None, "apps": []}

    def reload_rag(self):
        """Reload RAG service after graph rebuild."""
        if self.rag_service:
            print("[Agent] Reloading RAG service...")
            self.rag_service.reload()
            print("[Agent] RAG service reloaded successfully")

    def close(self):
        """Close service connections."""
        if self.rag_service:
            self.rag_service.close()
