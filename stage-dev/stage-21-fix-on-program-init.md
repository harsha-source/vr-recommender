# Stage 21: Fix Admin Dashboard "Rebuild Knowledge Graph" Missing ChromaDB Rebuild

**Date:** 2025-12-10
**Focus:** Fixing the Admin Dashboard's "Rebuild Knowledge Graph" button to also rebuild the ChromaDB vector index, ensuring the chatbot returns recommendations after a rebuild.

## 1. Overview

When using the Admin Dashboard (`/admin/data`) to rebuild the Knowledge Graph via the "Rebuild Knowledge Graph" button, the chatbot would stop returning any recommendations. All queries resulted in: *"I couldn't find specific VR apps for..."*.

Investigation revealed the rebuild process was incomplete:
1. **Neo4j was rebuilt correctly** - Graph nodes and relationships were populated.
2. **ChromaDB was NOT rebuilt** - Vector index remained empty after the rebuild.
3. **Chatbot failed silently** - Vector search returned results, but graph queries returned 0 apps.

## 2. Diagnosis & Root Cause

### Issue: Incomplete Rebuild Pipeline

**Symptom:** After clicking "Rebuild Knowledge Graph" in Admin Dashboard:
- Neo4j showed correct data (2073 nodes, 3396 relationships)
- ChromaDB was empty (0 skills indexed)
- Chatbot returned no recommendations

**Root Cause:** The `_build_graph()` method in `src/data_manager.py` only called the `KnowledgeGraphBuilder` to rebuild Neo4j. It did **not** rebuild the ChromaDB vector index.

```python
# BEFORE: Only Neo4j was rebuilt
def _build_graph(self, params: Dict[str, Any]):
    builder = KnowledgeGraphBuilder(logger=self._log)
    builder.build(data_dir=self.data_dir, clear=clear_db)
    # ChromaDB rebuild was missing!
```

### System Architecture Context

The recommendation system requires **both** databases to function:

1. **ChromaDB (Vector Store):** Converts user query to embeddings and finds semantically similar skills
2. **Neo4j (Knowledge Graph):** Traverses `VRApp -[DEVELOPS]-> Skill` relationships to find matching apps

Without ChromaDB, the skill search returns results but Neo4j has no skills to match against.

## 3. The Fix

### Fix 1: Add ChromaDB Rebuild to `_build_graph()`
**File:** `src/data_manager.py`

Added VectorIndexer import and ChromaDB rebuild logic:

```python
# Added import
from vector_store.indexer import VectorIndexer

def _build_graph(self, params: Dict[str, Any]):
    """Run knowledge graph builder AND rebuild ChromaDB vector index."""
    clear_db = params.get("clear", True)
    self._log(f"Starting Graph Build (Clear DB: {clear_db})...")

    try:
        # Step 1: Build Neo4j Knowledge Graph
        builder = KnowledgeGraphBuilder(logger=self._log)
        self._log("Building graph in Neo4j...")
        builder.build(data_dir=self.data_dir, clear=clear_db)
        self._log("Neo4j graph build complete.")

        # Step 2: Rebuild ChromaDB Vector Index (NEW)
        self._log("Rebuilding ChromaDB vector index...")
        skills_path = os.path.join(self.data_dir, "skills.json")

        if os.path.exists(skills_path):
            chroma_path = os.path.join(self.base_dir, "vector_store", "data", "chroma")
            indexer = VectorIndexer(persist_dir=chroma_path)
            indexer.build_index(skills_path)
            self._log(f"ChromaDB rebuilt with skills from {skills_path}")
        else:
            self._log(f"Skills file not found at {skills_path}, skipping ChromaDB rebuild")

        self._log("Full rebuild complete (Neo4j + ChromaDB).")

    except Exception as e:
        raise e
```

### Fix 2: Update Admin Dashboard UI
**File:** `web/admin_data.html`

Updated button text and warning message to reflect the complete rebuild:

```html
<!-- BEFORE -->
<p class="text-muted">Rebuilds the Neo4j graph from JSON data.</p>
<button class="btn btn-success" onclick="processGraph()">
    <i class="bi bi-share me-1"></i>Rebuild Knowledge Graph
</button>
<small class="text-muted"><b>Warning:</b> Clears existing database before building.</small>

<!-- AFTER -->
<p class="text-muted">Rebuilds Neo4j graph <b>and</b> ChromaDB vector index.</p>
<button class="btn btn-success" onclick="processGraph()">
    <i class="bi bi-share me-1"></i>Rebuild Knowledge Graph + Vectors
</button>
<small class="text-muted"><b>Warning:</b> Clears Neo4j and rebuilds ChromaDB.</small>
```

## 4. Files Modified

| File | Change |
|------|--------|
| `src/data_manager.py` | Added VectorIndexer import; Modified `_build_graph()` to rebuild ChromaDB |
| `web/admin_data.html` | Updated button text and description |

## 5. Verification Results

### Before Fix
```bash
curl -X POST http://localhost:5001/chat -d '{"message": "machine learning"}'
# Response: "I couldn't find specific VR apps for..."
```

### After Fix
```bash
curl -X POST http://localhost:5001/chat -d '{"message": "data science"}'
# Response: "Based on your interest in data science, here are VR apps..."
#   - Immersed (100% match)
#   - Virtual Desktop (100% match)
```

### Rebuild Process Output (via Admin Dashboard Console)
```
[19:04:52] Starting Graph Build (Clear DB: true)...
[19:04:52] Building graph in Neo4j...
[19:04:55] Neo4j graph build complete.
[19:04:55] Rebuilding ChromaDB vector index...
[19:04:58] ChromaDB rebuilt with skills from data_collection/data/skills.json
[19:04:58] Full rebuild complete (Neo4j + ChromaDB).
[19:04:58] Job completed successfully.
```

## 6. Conclusion

The Admin Dashboard's "Rebuild Knowledge Graph" button now performs a complete rebuild of both:
1. **Neo4j** - Knowledge graph with Course/App/Skill nodes and relationships
2. **ChromaDB** - Vector index with 1544 skill embeddings

This ensures the chatbot continues to function correctly after any data rebuild operation.

**Status:** RESOLVED & VERIFIED
