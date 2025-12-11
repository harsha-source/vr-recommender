# Stage 22: Upgrade Chatbot to Tool-Calling Agent Architecture

**Date:** 2025-12-11
**Focus:** Transform the VR Recommender from a keyword search tool into a conversational agent using Tool-Calling (Function Calling) architecture.

## 1. Overview

### Problem
The previous chatbot implementation was essentially a keyword search system:
- Every non-greeting message triggered VR app retrieval
- No conversation context maintained across turns
- Simple regex-based intent detection (greeting/help/recommendation)
- Not a true "chatbot" - more like a retrieval interface

### Solution
Implemented a **Tool-Calling Agent** architecture where:
- The LLM intelligently decides WHEN to search for VR apps
- Conversation history is maintained and used for context
- Greetings, clarifications, and follow-ups are handled conversationally
- Only explicit learning/recommendation requests trigger the RAG pipeline

## 2. Architecture

### Agent Loop Flow

```
User Message
     │
     ▼
┌─────────────────────────┐
│ Load Session + History  │ ← MongoDB ChatSession
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│ LLM with tools param    │ ← OpenRouter API (Gemini 2.0 Flash)
│ tool_choice="auto"      │
└─────────────────────────┘
     │
     ├── No tool_calls → Return text response directly
     │
     └── Has tool_calls → Execute search_vr_apps()
              │
              ▼
         ┌─────────────────┐
         │ RAGService      │
         │ .recommend()    │
         └─────────────────┘
              │
              ▼
         ┌─────────────────┐
         │ Append tool     │
         │ result to msgs  │
         └─────────────────┘
              │
              ▼
         ┌─────────────────┐
         │ LLM again with  │
         │ tool results    │
         └─────────────────┘
              │
              ▼
         Return final response
```

### Tool Definition

```python
SEARCH_VR_APPS_TOOL = {
    "type": "function",
    "function": {
        "name": "search_vr_apps",
        "description": "Search for VR apps that match user's learning goals",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query describing what the user wants to learn"
                }
            },
            "required": ["query"]
        }
    }
}
```

## 3. Files Created

### `src/agent/__init__.py`
Module initialization with ConversationAgent export.

### `src/agent/tools.py`
- `SEARCH_VR_APPS_TOOL`: Tool schema for VR app search
- `AVAILABLE_TOOLS`: List of all available tools
- `SYSTEM_PROMPT`: Agent behavior instructions

### `src/agent/agent.py`
Main `ConversationAgent` class with methods:
- `process_message(session_id, user_id, message)` - Entry point
- `_build_messages(history)` - Build OpenAI-format messages
- `_call_llm_with_tools(messages)` - LLM call with tools parameter
- `_handle_response(response, messages, session)` - Tool execution loop
- `_search_vr_apps(query)` - Execute RAG search
- `_fallback_response(message, session)` - Graceful error handling

## 4. Files Modified

### `src/chat/session.py`
Added methods:
- `get_messages_for_llm(limit)` - Get OpenAI-format messages
- `set_last_recommended_apps(apps)` - Store recommended apps for follow-ups
- `get_last_recommended_apps()` - Retrieve last recommendations
- `add_tool_interaction(tool_name, args, result)` - Log tool calls

### `src/db/repositories/sessions_repo.py`
Added methods:
- `update_metadata(session_id, metadata)` - Update session metadata
- `add_tool_call(session_id, tool_name, args, result)` - Store tool interaction

### `web/flask_api.py`
- Added `ConversationAgent` import and initialization
- Replaced `/chat` endpoint logic to use `conversation_agent.process_message()`
- Updated config reload to include agent reinitialization
- Response now includes `tool_used` field

## 5. Verification Results

### Test Cases

| Input | tool_used | Expected | Result |
|-------|-----------|----------|--------|
| "hi there" | null | Greeting, no search | ✅ PASS |
| "thanks a lot" | null | Acknowledgment, no search | ✅ PASS |
| "what can you do" | null | Explain capabilities | ✅ PASS |
| "I want to learn machine learning" | search_vr_apps | Trigger search | ✅ PASS |
| "recommend VR apps for cybersecurity" | search_vr_apps | Trigger search | ✅ PASS |
| "find VR apps for data visualization" | search_vr_apps | Trigger search | ✅ PASS |

### Sample Responses

**Greeting (No Tool):**
```json
{
    "response": "Hello! How can I help you today?",
    "tool_used": null
}
```

**Search Query (Tool Called):**
```json
{
    "response": "Here are some VR apps that can help with data visualization:\n\n* **GeoGebra AR** (175): Supports interactive data visualization...\n* **Universe Sandbox** (90): Visualize and simulate complex systems...",
    "tool_used": "search_vr_apps"
}
```

## 6. Key Technical Details

### OpenRouter Function Calling
- Model: `google/gemini-2.0-flash-001`
- Supports OpenAI-compatible `tools` parameter
- Uses `tool_choice="auto"` to let LLM decide

### Error Handling
- Fallback to keyword-based responses if LLM fails
- Graceful handling of 401 errors (invalid API key)
- Session continues even if tool call fails

### Context Management
- Last 10 messages included in LLM context
- Tool calls logged in session for debugging
- MongoDB stores complete interaction history

## 7. API Response Format

**Before (Old System):**
```json
{
    "response": "...",
    "type": "success",
    "user_id": "..."
}
```

**After (Agent System):**
```json
{
    "response": "...",
    "type": "success",
    "user_id": "...",
    "tool_used": "search_vr_apps" | null
}
```

## 8. System Prompt

The agent follows these guidelines:
- Be concise and direct
- Use `search_vr_apps` tool ONLY when user wants VR app recommendations
- For greetings, small talk, clarifications - respond without searching
- Present search results clearly with brief explanations

## 9. Conclusion

The chatbot is now a true conversational agent that:
1. **Understands context** - Maintains conversation history
2. **Decides intelligently** - LLM chooses when to trigger retrieval
3. **Handles naturally** - Greetings, thanks, and questions work conversationally
4. **Searches on demand** - RAG pipeline only invoked when appropriate

**Status:** RESOLVED & VERIFIED
