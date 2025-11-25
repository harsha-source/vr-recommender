# Stage 8: Dashboard Data Management

## 🎯 Objective
Enhance the Admin Dashboard with a dedicated **Data Management** interface. This allows administrators to monitor the status of the data pipeline and trigger updates for Courses and VR Applications directly from the UI, removing the need to run CLI scripts.

## 🏗 Architecture Changes

### 1. Backend: Data Management Service (`src/data_manager.py`)
We will create a unified service to wrap the existing `data_collection` scripts.
*   **Refactoring Requirement**: The existing scripts (`run_fetch_all_courses.py`, `test_improved_vr.py`) are CLI-focused. We will refactor the core fetcher classes to be importable and callable by this new service without `sys.exit()` or hardcoded prints blocking the thread.
*   **Async Execution**: Data collection is slow (web scraping). We will use Python's `threading` or `concurrent.futures` to run these tasks in the background so the UI doesn't freeze.
*   **Status Tracking**: We need a way to track "Job Status" (e.g., `IDLE`, `RUNNING`, `COMPLETED`, `FAILED`) and progress logs.

### 2. Backend: New API Endpoints
*   `GET /api/admin/data/status`: Returns current status of data files (last modified time, item counts) and any running jobs.
*   `POST /api/admin/data/update/courses`: Triggers a background job to update course data.
    *   Params: `mode` (e.g., "all", "department"), `limit` (optional).
*   `POST /api/admin/data/update/apps`: Triggers a background job to update VR apps.
    *   Params: `mode` (e.g., "curated", "search", "all").

### 3. Frontend: Data Management Page (`admin_data.html`)
A new page accessible via the Dashboard sidebar/nav.
*   **Data Status Cards**: Show "Courses" (Count: 232, Last Updated: 2h ago) and "VR Apps" (Count: 77, Last Updated: 5h ago).
*   **Control Panel**:
    *   **Update Courses**: Button group to "Update All", "Update Specific Dept".
    *   **Update VR Apps**: Button to "Refresh App List".
*   **Live Console**: A scrolling text area showing the logs from the background job (e.g., "Fetching URL...", "Found 5 new courses...").

---

## 📅 Implementation Plan

### Step 1: Backend Refactoring & Service Layer
- [ ] **Refactor Fetchers**: Ensure `CMUCourseFetcherImproved` and `VRAppFetcherImproved` return data cleanly instead of just writing to files, or at least expose a clean entry point.
- [ ] **Create `src/data_manager.py`**:
    - Implement `JobManager` class to handle background threads.
    - Implement `get_data_stats()` to read JSON file metadata.

### Step 2: API Implementation (`flask_api.py`)
- [ ] Register `/api/admin/data/*` endpoints.
- [ ] Connect endpoints to `data_manager`.
- [ ] Implement a simple in-memory log buffer so the frontend can poll for progress updates.

### Step 3: Frontend Development
- [ ] Create `admin_data.html` (inheriting style from `admin_dashboard.html`).
- [ ] Add Navigation links between "Logs" and "Data" pages.
- [ ] Implement JS logic to:
    - Poll status.
    - Trigger updates via POST.
    - Poll for log updates when a job is running.

### Step 4: Testing
- [ ] **Mock Testing**: Initially test with a "mock" fetcher that just sleeps for 5 seconds and logs fake progress (to avoid spamming CMU/Firecrawl APIs during dev).
- [ ] **Integration Test**: Run a real (but limited) update (e.g., limit courses to 5) to verify end-to-end flow.

---

## 📊 Data Flow (Update Process)

1.  **Admin** clicks "Update Courses" -> `POST /api/admin/data/update/courses`.
2.  **Flask** checks if a job is already running. If not, starts a **Background Thread**.
3.  **Background Thread**:
    - Calls `CMUCourseFetcherImproved.fetch_courses()`.
    - Writes progress logs to a shared `JobStatus` object.
    - On completion, saves `courses.json` and updates the Knowledge Graph (Stage 3 script).
4.  **Frontend** polls `GET /api/admin/data/status` every 2s.
    - Receives `{"status": "RUNNING", "logs": ["Fetched 10...", "Fetched 20..."]}`.
    - Updates the "Live Console" in the UI.
5.  **Completion**:
    - Thread finishes. Status becomes `COMPLETED`.
    - Frontend shows "Update Successful" and refreshes the "Last Updated" timestamp.

## ⚠️ Risks & Mitigations
-   **Timeout**: Web requests can take minutes. **Mitigation**: Strictly use background threads; API returns `202 Accepted` immediately.
-   **API Limits**: Firecrawl/Tavily have rate limits. **Mitigation**: Admin UI should show a warning or estimated cost. Add a "Dry Run" or "Limit" option.
