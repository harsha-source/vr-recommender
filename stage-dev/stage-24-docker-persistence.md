# Stage 24: Docker Data Persistence Fix

**Date:** 2025-12-11
**Focus:** Fix data persistence issue causing databases to not load after Docker restart.

## 1. Problem Diagnosis

After Docker restart, only Neo4j data was preserved. ChromaDB vector index was lost every time, causing the chatbot to return "nothing found" for all queries.

### Root Cause Analysis

| Database | Volume Config | Persistence | Status |
|----------|--------------|-------------|--------|
| **Neo4j** | `neo4j_data:/data` | Yes | Working |
| **Redis** | `redis_data:/data` | Yes (no AOF) | Partial |
| **ChromaDB** | **None** | **No** | **Broken** |
| **MongoDB** | N/A | Cloud (Atlas) | Working |

**Core Issue:** ChromaDB had no Docker Volume mapping. Every container restart wiped the vector index.

### Data Flow Before Fix

```
JSON Data → Neo4j (persisted) → ChromaDB (NOT persisted)
                                      ↓
                               Container restart
                                      ↓
                               ChromaDB = Empty
                                      ↓
                               RAG search returns 0 results
```

## 2. Changes Made

### `docker-compose.prod.yml`

**Added ChromaDB volume and Redis AOF persistence:**

```yaml
services:
  redis:
    image: redis:7.2-alpine
    command: redis-server --appendonly yes --appendfsync everysec  # NEW
    volumes:
      - redis_data:/data

  vr-recommender:
    volumes:
      - chroma_data:/app/vector_store/data/chroma  # NEW

volumes:
  redis_data:
  neo4j_data:
  chroma_data:  # NEW
```

### `web/flask_api.py`

**Added startup auto-recovery for ChromaDB:**

```python
def _ensure_chromadb_initialized():
    """
    Startup check: If ChromaDB is empty, automatically rebuild from skills.json.
    This ensures the system recovers gracefully after Docker restarts.
    """
    try:
        from vector_store.src.vector_store.indexer import VectorIndexer

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chroma_path = os.path.join(base_dir, "vector_store", "data", "chroma")
        skills_path = os.path.join(base_dir, "data_collection", "data", "skills.json")

        indexer = VectorIndexer(persist_dir=chroma_path)
        stats = indexer.get_stats()
        total_skills = stats.get('total_skills', 0)

        if total_skills == 0:
            if os.path.exists(skills_path):
                print("[Startup] ChromaDB empty, rebuilding from skills.json...")
                indexer.build_index(skills_path, clear_existing=False)
                new_stats = indexer.get_stats()
                print(f"[Startup] ChromaDB rebuilt: {new_stats.get('total_skills', 0)} skills indexed")
            else:
                print(f"[Startup] ChromaDB empty and skills.json not found")
        else:
            print(f"[Startup] ChromaDB ready: {total_skills} skills indexed")
    except Exception as e:
        print(f"[Startup] ChromaDB check failed: {e}")

# Run before service initialization
_ensure_chromadb_initialized()
```

## 3. Expected Behavior After Fix

### Startup Logs (Normal)
```
[Startup] ✓ ChromaDB ready: 1847 skills indexed
✓ RAG VR Recommender ready!
✓ Conversation Agent ready!
```

### Startup Logs (Auto-Recovery)
```
[Startup] ⚠ ChromaDB empty, rebuilding from skills.json...
[Startup] ✓ ChromaDB rebuilt: 1847 skills indexed
✓ RAG VR Recommender ready!
✓ Conversation Agent ready!
```

## 4. Verification Commands

```bash
# 1. Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build vr-recommender

# 2. Check logs for ChromaDB status
docker logs vr-recommender 2>&1 | grep -E "Startup|ChromaDB"

# 3. Test search
printf '{"message": "find VR apps for data science"}' | \
  curl -s -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" -d @- | jq

# 4. Restart and re-test (verify persistence)
docker-compose -f docker-compose.prod.yml restart vr-recommender
sleep 10
printf '{"message": "machine learning apps"}' | \
  curl -s -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" -d @- | jq
```

## 5. Files Modified

| File | Action | Description |
|------|--------|-------------|
| `docker-compose.prod.yml` | MODIFIED | Added `chroma_data` volume + Redis AOF |
| `web/flask_api.py` | MODIFIED | Added `_ensure_chromadb_initialized()` |
| `stage-dev/stage-24-docker-persistence.md` | CREATED | This documentation |

## 6. Conclusion

The fix implements a two-layer protection:

1. **Primary:** Docker volume persists ChromaDB data across restarts
2. **Fallback:** Startup auto-recovery rebuilds from skills.json if empty

This ensures the VR Recommender chatbot works reliably in production, surviving both planned restarts and unexpected container recreations.

**Status:** COMPLETE
