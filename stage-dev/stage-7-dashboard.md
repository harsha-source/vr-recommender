# Stage 7: Admin Dashboard & Database Logging

## 🎯 Objective
Create a web-based **Admin Dashboard** to visualize user interactions, monitor system performance, and analyze user needs. This stage transitions the system from ephemeral file-based logging to a structured **relational database**, enabling multi-user tracking and historical data analysis.

## 🏗 Architecture Changes

### 1. Database Layer (The "Lightweight" DB)
We will implement **SQLite** as the persistence layer.
*   **Why SQLite?** It is serverless, zero-configuration, standard in the Python ecosystem, and extremely lightweight while supporting complex SQL queries for analytics. It is easily upgradeable to PostgreSQL or MySQL later if scaling requires it.
*   **Schema (`interaction_logs`):**
    *   `id`: Primary Key (Auto-increment)
    *   `user_id`: UUID (Persistent for specific browsers/users)
    *   `session_id`: UUID (Unique per chat session)
    *   `timestamp`: DateTime
    *   `query_text`: The raw user input
    *   `detected_intent`: (e.g., "course_lookup", "skill_search", "chitchat")
    *   `response_content`: The text response sent to the user
    *   `recommended_apps`: JSON string (List of apps returned)
    *   `latency_ms`: Processing time

### 2. Backend Updates (`flask_api.py` & `src/logging`)
*   **User Identification:** Implement a simple cookie-based mechanism to assign and track `user_id` across requests.
*   **DB Logger Module:** Create a unified `InteractionLogger` class to handle asynchronous writing to the database.
*   **Admin API Endpoints:**
    *   `GET /api/admin/stats`: Aggregate metrics (total queries, top intents, unique users).
    *   `GET /api/admin/logs`: Paginated list of detailed chat logs.

### 3. Frontend Dashboard (`dashboard.html`)
A standalone HTML/JS page (using Vue.js or vanilla JS + Bootstrap) to consume the Admin API.
*   **Features:**
    *   **Live Log Table:** Showing Timestamp, User ID, Query, and Result.
    *   **Detail View:** Click a row to see the full JSON response and reasoning.
    *   **Filters:** Filter by User ID or Date.

---

## 📅 Implementation Plan

### Step 1: Database Infrastructure
- [ ] Create `src/database.py`: Handle SQLite connection and table creation.
- [ ] Define the SQL schema for `interaction_logs`.
- [ ] Create `src/logging/db_logger.py`: A service to insert log entries safely.

### Step 2: Backend Integration
- [ ] Modify `flask_api.py` to generate/read `user_id` from cookies.
- [ ] Integrate `InteractionLogger` into the `/chat` endpoint.
- [ ] Ensure every request (POST) is recorded in the DB.

### Step 3: Admin API Development
- [ ] Implement `GET /api/admin/logs` (with pagination parameters).
- [ ] Implement `GET /api/admin/stats` (basic counts).
- [ ] Add basic authentication (optional/simple token) to protect these endpoints.

### Step 4: Dashboard Frontend
- [ ] Create `admin_dashboard.html` in the root directory.
- [ ] Implement data fetching from `/api/admin/logs`.
- [ ] Design a clean UI table to display:
    - User Hash (shortened ID)
    - Query
    - Response Summary
    - Time
- [ ] Add "Refresh" capability.

### Step 5: Testing & Verification
- [ ] **Simulate Multi-user Traffic:** Use a script to send requests with different User IDs.
- [ ] **Verify Data Persistence:** Restart the server and ensure logs remain.
- [ ] **UI Test:** Confirm the dashboard accurately reflects the DB content.

---

## 📊 Data Flow

1.  **User** sends message -> `POST /chat`
2.  **Flask** extracts `user_id` (or assigns new one).
3.  **RAG System** processes query -> Returns Response.
4.  **Logger** captures `{User, Query, Response, Time}` -> **SQLite DB**.
5.  **Admin** opens `admin_dashboard.html` -> `GET /api/admin/logs`.
6.  **Flask** reads **SQLite DB** -> Returns JSON list.
7.  **Dashboard** renders the table.
