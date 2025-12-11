# Stage 32: Fix Course Update to Support Multiple Semesters

**Date:** 2025-12-11
**Status:** COMPLETED
**Focus:** Fix course data uniqueness to use `course_id + semester` as composite key

---

## 1. Problem Description

When updating courses for a new semester (e.g., Spring 2026), the system would **overwrite existing courses** instead of adding new entries.

### Observed Behavior:
- Database had 455 courses (Fall 2025 data)
- Added 5 courses for Spring 2026
- Total stayed at 455 (should be 460)
- MongoDB `bulk_upsert` was updating existing records

### Root Cause:
The unique key for courses was only `course_id` (e.g., "08-200"), ignoring the semester. This meant:
- "08-200" in Fall 2025 → stored as `_id: "08-200"`
- "08-200" in Spring 2026 → **overwrote** the same record

---

## 2. Solution: Composite Unique Key

Use `course_id + semester` as the unique identifier:
- "08-200" in Fall 2025 → `_id: "08-200_f25"`
- "08-200" in Spring 2026 → `_id: "08-200_s26"` (new record!)

---

## 3. Files Modified

| File | Changes |
|------|---------|
| `data_collection/src/models.py` | Add `semester` field to Course dataclass |
| `data_collection/src/data_collection/course_fetcher_improved.py` | Pass semester to Course constructor; use composite key in `save_courses` |
| `src/db/repositories/courses_repo.py` | Use `course_id_semester` as MongoDB `_id` in `bulk_upsert` |

---

## 4. Code Changes

### Part A: Course Model (`data_collection/src/models.py`)

```python
@dataclass
class Course:
    course_id: str
    title: str
    department: str
    description: str
    units: int
    prerequisites: List[str]
    learning_outcomes: List[str]
    semester: str = ""  # NEW: "s26", "f25" - semester code for uniqueness
```

### Part B: Course Fetcher (`course_fetcher_improved.py`)

**1. Pass semester to Course constructor:**
```python
return Course(
    course_id=course_code,
    title=title,
    ...
    semester=semester  # NEW
)
```

**2. Use composite key in `save_courses`:**
```python
def make_key(course_dict):
    cid = course_dict.get('course_id', '')
    sem = course_dict.get('semester', '')
    return f"{cid}_{sem}" if sem else cid

new_courses_dict = {make_key(course.to_dict()): course.to_dict() for course in courses}
```

### Part C: MongoDB Repository (`courses_repo.py`)

```python
def bulk_upsert(self, courses: List[Dict]) -> int:
    for course in courses:
        course_id = course.get('course_id')
        semester = course.get('semester', '')

        # Use composite key as MongoDB _id
        unique_id = f"{course_id}_{semester}" if semester else course_id

        course_copy['_id'] = unique_id
        course_copy['course_id'] = course_id  # Keep original for queries

        operations.append(UpdateOne(
            {"_id": unique_id},
            {"$set": update_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        ))
```

---

## 5. Verification

### Test Performed:
1. Initial state: **455 courses** (existing data)
2. Selected: School of Computer Science + Spring 2026 (s26) + Limit 5
3. Clicked Update

### Result:
- Job Console: "Synced 5 courses to MongoDB"
- **Total Courses: 460** (455 + 5 = 460) ✓

### Screenshot:
![Stage 32 Fix Verified](../screenshots/stage32-fix-course-count-460.png)

---

## 6. Data Structure After Fix

### MongoDB Document Example:
```json
{
  "_id": "08-200_s26",
  "course_id": "08-200",
  "title": "Course 08-200",
  "department": "School of Computer Science",
  "semester": "s26",
  "description": "...",
  "units": 12,
  "created_at": "2025-12-11T14:50:14Z",
  "updated_at": "2025-12-11T14:50:14Z"
}
```

### JSON File Key:
```
"08-200_s26": { ... }
"08-200_f25": { ... }
```

---

## 7. Commit

```
fea33fe Stage 32: Fix course update to add new semester courses instead of overwriting
```

**Files changed:** 3
**Insertions:** +40
**Deletions:** -21
