# Stage 26: Fix Missing Docker Dependencies

**Date:** 2025-12-11
**Focus:** Add missing `firecrawl-py` and `tavily-python` dependencies to Docker container.

## 1. Problem Description

When running Course Update or VR App Update jobs from Admin Data Management page, the jobs fail with:
```
Error: 'NoneType' object has no attribute 'scrape'
No course codes found
```

## 2. Root Cause Analysis

The main `requirements.txt` (used by Docker) is missing data collection dependencies:

| Dependency | Purpose | Location |
|------------|---------|----------|
| `firecrawl-py` | Scrape CMU course catalog pages | `data_collection/requirements.txt` only |
| `tavily-python` | Search and fetch VR applications | `data_collection/requirements.txt` only |

### Current State

```
requirements.txt (Docker uses this)     data_collection/requirements.txt
────────────────────────────────────    ────────────────────────────────
pymongo[srv]==4.15.4                    firecrawl-py>=0.0.1
openai==2.0.1                           tavily-python>=0.3.0
requests==2.32.5                        ...
beautifulsoup4==4.14.2
Flask==3.0.3
... (NO firecrawl-py or tavily-python)
```

## 3. Solution

### Fix: Add missing dependencies to `requirements.txt`

Add the following to `requirements.txt`:
```
# Data collection APIs
firecrawl-py>=0.0.1
tavily-python>=0.3.0
```

## 4. Files to Modify

| File | Changes |
|------|---------|
| `requirements.txt` | Add `firecrawl-py>=0.0.1` and `tavily-python>=0.3.0` |

## 5. Verification Steps

1. Rebuild Docker container:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build vr-recommender
   ```

2. Verify dependencies installed:
   ```bash
   docker exec vr-recommender pip list | grep -E "firecrawl|tavily"
   ```

3. Test Course Update:
   - Go to Admin Data Management page
   - Click "Update" with Test Run (Limit 5)
   - Verify Job Console shows actual course extraction (not errors)

4. Test VR App Update:
   - Click "Refresh All Apps"
   - Verify apps are fetched successfully

## 6. Expected Results

After fix:
- Course Update: Should fetch courses from CMU catalog
- VR App Update: Should search and return VR applications
- No more `'NoneType' object has no attribute 'scrape'` errors

## 7. Risk Assessment

**Low Risk:**
- Only adding dependencies, not changing code
- Dependencies are already tested in `data_collection` module
- Docker rebuild required but no data migration needed

**Status:** PLANNED
