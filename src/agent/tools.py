"""Tool definitions for the conversational agent.

Defines the function calling schemas for VR app search functionality.
"""

# Tool schema for searching VR apps
SEARCH_VR_APPS_TOOL = {
    "type": "function",
    "function": {
        "name": "search_vr_apps",
        "description": (
            "Search for VR applications on Meta Quest that match the user's learning goals, "
            "interests, or skills they want to develop. Use this tool when the user expresses "
            "interest in learning something specific, asks for VR app recommendations, or "
            "mentions topics/skills they want to improve."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The search query describing what the user wants to learn. "
                        "Extract the core learning intent from the conversation. "
                        "Examples: 'machine learning', 'cybersecurity', 'public speaking', 'data analysis'"
                    )
                }
            },
            "required": ["query"]
        }
    }
}

# List of all available tools
AVAILABLE_TOOLS = [SEARCH_VR_APPS_TOOL]

# System prompt for the conversation agent
SYSTEM_PROMPT = """You are a VR app recommender assistant for Heinz College at Carnegie Mellon University.

Your role:
- Help students find VR applications for Meta Quest that support their learning goals
- Have natural, concise conversations
- Use the search_vr_apps tool ONLY when the user wants VR app recommendations

Guidelines:
- Be direct and helpful, avoid unnecessary small talk
- When user mentions learning topics or asks for recommendations, use search_vr_apps
- For greetings, clarifications, or general questions, respond without searching
- After receiving search results, present them clearly with brief explanations
- You can discuss VR technology and learning methods without searching

When to use search_vr_apps:
- "I want to learn cybersecurity" -> search
- "recommend apps for data science" -> search
- "help me find VR apps for Python" -> search
- "looking for VR training tools" -> search

When NOT to use search_vr_apps:
- "Hi" / "Hello" -> greet back
- "Thanks" / "Thank you" -> acknowledge politely
- "What can you do?" -> explain your capabilities
- "Tell me more about [previous app]" -> use context from conversation
- Questions about VR in general -> answer directly

Response style:
- Keep responses concise (2-4 sentences for chat, more for recommendations)
- Use markdown formatting for app lists
- Include match percentages when presenting results
- Offer follow-up assistance"""
