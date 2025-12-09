# Stage 20: Post-Frontend Reorganization Retrieval & Graph Fixes

**Date:** 2025-11-27
**Focus:** Fixing critical Knowledge Graph build failures and RAG retrieval issues caused by the recent frontend directory restructuring and Docker deployment environment.

## 1. Overview

After moving all frontend and API components into a `web/` subdirectory (Stage 19 Refactor), the system appeared healthy (`/health` returns 200) but failed to return any recommendations. All user queries resulted in: *"I couldn't find specific VR apps for..."*.

Investigation revealed a cascade of failures:
1.  **Knowledge Graph was empty** (0 nodes).
2.  **Vector Index was empty** (0 embeddings) in the running container.
3.  **Data Pipeline crashed** silently during the build phase.

This stage documents the diagnosis and resolution of these critical infrastructure issues.

## 2. Diagnosis & Root Causes

### Issue A: Knowledge Graph Build Failure
*   **Symptom:** Neo4j database contained 0 nodes and 0 relationships.
*   **Root Cause 1 (Imports):** The refactoring moved `flask_api.py` but left `knowledge_graph` scripts in place. When running `build_graph.py` from the project root, absolute imports within the `knowledge_graph` module (`from knowledge_graph.connection import ...`) broke due to path resolution shifts in the execution context.
*   **Root Cause 2 (Data Types):** When switching to MongoDB as the data source (Stage 16), the data flowing into the Neo4j builder contained MongoDB `ObjectId` objects. The Neo4j Python driver **cannot serialize** `ObjectId`, causing the build script to crash with `ValueError: Values of type <class 'bson.objectid.ObjectId'> are not supported`.

### Issue B: Silent Vector Retrieval Failure (The "Empty Index" Bug)
*   **Symptom:** `SkillSearchService` returned 0 results for any query, even common terms like "Python".
*   **Root Cause:** The `RAGRetriever` initialized `SkillSearchService` using a **relative path**: `vector_store/data/chroma`.
    *   In **Development**, we ran from the project root, so this path was valid.
    *   In **Production (Docker)**, we updated `Dockerfile.prod` to run Gunicorn with `--chdir web`. This changed the Current Working Directory (CWD) to `/app/web`.
    *   The service looked for the index at `/app/web/vector_store/data/chroma` (which didn't exist).
    *   **Critical Failure:** ChromaDB's default behavior is to **silently create a new, empty database** if the path doesn't exist, rather than raising an error. This masked the configuration error.

### Issue C: Startup Race Condition
*   **Symptom:** Even after fixing the graph, the first few queries might return no results if the app started faster than the graph populated.
*   **Root Cause:** The `RAGRetriever` loads a cache of "Active Skills" (skills connected to apps) only **once** at startup (`__init__`). If Neo4j is empty or initializing during this split-second, the cache is empty `[]`, breaking the "Semantic Bridge" logic which relies on this list to find fallback matches.

## 3. The Fixes

### Fix 1: Robust Knowledge Graph Builder
**File:** `knowledge_graph/src/knowledge_graph/builder.py`

1.  **Relative Imports:** Switched to relative imports to make the module robust to execution context.
    ```python
    # Before
    from knowledge_graph.connection import Neo4jConnection
    # After
    from .connection import Neo4jConnection
    ```

2.  **Data Sanitation:** Implemented a sanitation layer to scrub incompatible types before Neo4j insertion.
    ```python
    def _sanitize_data(self, data_list):
        """Convert ObjectId to string for Neo4j compatibility."""
        sanitized = []
        for item in data_list:
            new_item = item.copy()
            if '_id' in new_item:
                new_item['_id'] = str(new_item['_id'])
            sanitized.append(new_item)
        return sanitized
    ```

### Fix 2: Absolute Path Resolution for Vector Store
**File:** `src/rag/retriever.py`

Changed the `persist_dir` calculation to rely on the **file's location** rather than the process's CWD. This ensures the path is always correct regardless of where the app is launched from (Root, `web/`, or Docker).

```python
# Before: Relied on CWD
self.skill_search = SkillSearchService(persist_dir="vector_store/data/chroma")

# After: Absolute path relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.abspath(os.path.join(current_dir, "../../vector_store/data/chroma"))
self.skill_search = SkillSearchService(persist_dir=persist_dir)
```

### Fix 3: Auto-Healing "Active Skills" Cache
**File:** `src/rag/retriever.py`

Added logic to check if the cache is empty during retrieval and attempt a refresh. This solves the race condition where the app starts before the graph is ready.

```python
def retrieve(self, query: str, top_k: int = 8):
    # Auto-refresh if empty (handles cold start / race condition)
    if not self.active_skills:
        print("[RAG] Active skills cache empty. Refreshing...")
        self.active_skills = self._get_active_skills()
    
    # ... proceed with retrieval ...
```

## 4. Verification Results

After applying these fixes and rebuilding the Docker containers:

### 1. Knowledge Graph Status
The build script ran successfully, populating Neo4j:
*   **Nodes:** 2,073 (452 Courses, 77 Apps, 1544 Skills)
*   **Relationships:** 3,396

### 2. Chatbot Retrieval Test
*   **Query:** "Artificial Intelligence"
*   **Result:**
    *   **Skill Search:** Successfully found "Artificial Intelligence", "Machine Learning" in vector store.
    *   **Graph Query:** Matched app **"InMind"** (100% Match).
    *   **Response:** *"Based on your interest in Artificial Intelligence, here are VR apps..."*

*   **Query:** "I want to learn collaboration skills"
*   **Result:**
    *   **Skill Search:** Matched "Collaboration", "Remote Collaboration Tools".
    *   **Graph Query:** Matched **"Mozilla Hubs"**, **"Horizon Workrooms"**.
    *   **Response:** Correctly recommended productivity tools.

## 5. Conclusion
The system is now fully stable in the production Docker environment. The structural fragility introduced by the folder reorganization has been resolved by implementing absolute pathing and strict data sanitation. The self-healing cache ensures resilience against startup timing issues.

**Status:** ✅ RESOLVED & VERIFIED
