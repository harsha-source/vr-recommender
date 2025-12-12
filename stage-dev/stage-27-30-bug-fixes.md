# Stages 27-30: Bug Fixes for Data Management System

**Date:** 2025-12-11
**Focus:** Fix critical bugs in Admin Data Management: MongoDB sync, API key configuration, Job Console status, and data overwrite issues.

---

## Stage 27: Fix MongoDB Sync for Course/VRApp Dataclass Objects

### Problem
When updating courses or VR apps, MongoDB sync failed because the fetchers return `Course` and `VRApp` dataclass instances, but the repository's `bulk_upsert()` method expects dictionaries with `.get()` and `.copy()` methods.

### Root Cause
```python
# Before: Passing dataclass objects directly
count = CoursesRepository().bulk_upsert(courses)  # courses are Course objects
```

The `Course` and `VRApp` dataclasses don't have `.get()` or `.copy()` methods that the repository expects.

### Solution
Convert dataclass objects to dicts before passing to repository:

```python
# After: Convert to dicts first
course_dicts = [c.to_dict() if hasattr(c, 'to_dict') else c for c in courses]
count = CoursesRepository().bulk_upsert(course_dicts)
```

### Files Modified
| File | Changes |
|------|---------|
| `src/data_manager.py` | Convert Course/VRApp objects to dicts before `bulk_upsert()` |

### Commit
`220c7bb` - Stage 27: Fix MongoDB sync for Course/VRApp dataclass objects

---

## Stage 28: Fix SkillExtractor API Key Configuration

### Problem
Skill extraction jobs failed with `401 Unauthorized` errors because `SkillExtractor` had a hardcoded invalid OpenRouter API key.

### Root Cause
```python
# Before: Hardcoded invalid API key
api_key = os.getenv(
    "OPENROUTER_API_KEY",
    "sk-or-v1-19d9956040439b25..."  # Invalid hardcoded key
)
```

### Solution
Integrate with `ConfigManager` to get API key from database or environment:

```python
# After: Use ConfigManager for API key
def __init__(self, api_key: str = None, model: str = None):
    if not api_key:
        try:
            from src.config_manager import ConfigManager
            config = ConfigManager()
            api_key = config.openrouter_api_key
            model = model or config.openrouter_model
        except Exception:
            pass

    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OpenRouter API key not configured...")
```

### Files Modified
| File | Changes |
|------|---------|
| `skill_extraction/src/skill_extraction/extractor.py` | Remove hardcoded key, add ConfigManager integration, update default model to `google/gemini-2.0-flash-001` |

### Commit
`d530b83` - Stage 28: Fix SkillExtractor to use ConfigManager for API key

---

## Stage 29: Fix Job Console Stuck on "STARTING" Status

### Problem
Job Console in Admin Data Management always showed "STARTING" status and never progressed, even though jobs were actually running successfully.

### Root Cause
Gunicorn was configured with `workers=4`, meaning each worker had its own `JobManager` instance with separate in-memory state:

```
Worker A: Starts job → job_manager.current_job = {...}
Worker B: Status poll → job_manager.current_job = None  ← Different instance!
Worker C: Status poll → job_manager.current_job = None
Worker D: Status poll → job_manager.current_job = None
```

Additionally, rate limiting was blocking the 2-second status polling, causing 429 errors.

### Solution

**Part A: Single Worker for State Consistency**
```python
# web/gunicorn_config.py
workers = 1      # Single worker maintains job state
threads = 8      # Increased threads to compensate
```

**Part B: Exempt Admin Endpoints from Rate Limiting**
```python
# web/flask_api.py
@app.route("/api/admin/data/status", methods=["GET"])
@limiter.exempt  # Admin endpoints already protected by login_required
@login_required
def data_status():
    ...
```

### Files Modified
| File | Changes |
|------|---------|
| `web/flask_api.py` | Add `@limiter.exempt` to all admin API endpoints |
| `web/gunicorn_config.py` | Set `workers=1`, increase `threads=8` |

### Commit
`48c5ab8` - Stage 29: Fix Job Console stuck on STARTING status

---

## Stage 30: Fix Course Data Overwrite Bug

### Problem
Running "Test Run (Limit 5)" course update caused "Total Courses" to show only 5 instead of preserving the existing 455 courses.

### Root Cause

**Issue 1:** `get_data_stats()` was reading counts from JSON files, which got overwritten with only the new data.

**Issue 2:** `save_courses()` and `save_apps()` used overwrite mode (`'w'`) instead of merging with existing data.

### Solution

**Part A: Use MongoDB as Source of Truth for Counts**
```python
# Before: JSON file counts (easily overwritten)
stats["courses"] = self._get_file_info("courses.json")

# After: MongoDB counts (accurate)
stats["courses"] = {
    "exists": True,  # Required for frontend status indicator
    "count": CoursesRepository().count(),
    "last_updated": courses_file.get("last_updated"),
    "source": "mongodb"
}
```

**Part B: Merge Data Instead of Overwrite**
```python
def save_courses(self, courses: List[Course], path: str, merge: bool = True):
    new_courses_dict = {course.course_id: course.to_dict() for course in courses}

    if merge and os.path.exists(path):
        with open(path, 'r') as f:
            existing_data = json.load(f)
        existing_dict = {c.get('course_id'): c for c in existing_data}

        # Merge: new courses override existing by ID
        merged_dict = {**existing_dict, **new_courses_dict}
        merged_courses = list(merged_dict.values())
    else:
        merged_courses = list(new_courses_dict.values())

    with open(path, 'w') as f:
        json.dump(merged_courses, f, indent=2)
```

**Part C: Add `exists` Field for Frontend Status Indicators**
The frontend checks for `exists` field to determine status dot color (green/red).

### Files Modified
| File | Changes |
|------|---------|
| `src/data_manager.py` | Use MongoDB counts, add `exists` field for frontend |
| `data_collection/src/data_collection/course_fetcher_improved.py` | Add `merge=True` parameter to `save_courses()` |
| `data_collection/src/data_collection/vr_app_fetcher_improved.py` | Add `merge=True` parameter to `save_apps()` |

### Commits
- `0579c76` - Stage 30: Fix course data overwrite bug
- `c831782` - Stage 30 fix: Add exists field for frontend status indicators

---

## Summary Table

| Stage | Issue | Fix | Risk |
|-------|-------|-----|------|
| 27 | MongoDB sync fails for dataclass objects | Convert to dicts before bulk_upsert | Low |
| 28 | SkillExtractor 401 errors | Use ConfigManager for API key | Low |
| 29 | Job Console stuck on STARTING | Single Gunicorn worker + exempt rate limiting | Medium |
| 30 | Course data gets overwritten | Merge data + use MongoDB counts | Medium |

## Verification

After all fixes:
1. Course Update works and syncs to MongoDB
2. Skill Extraction uses configured API key
3. Job Console shows real-time progress (STARTING → RUNNING → COMPLETED)
4. "Test Run (Limit 5)" merges with existing data instead of overwriting

**Status:** COMPLETED
