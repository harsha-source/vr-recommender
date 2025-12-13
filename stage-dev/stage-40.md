 Stage 40: Dynamic Rate Limit Configuration Admin Page

 Date: 2025-12-12
 Focus: Add admin page for hot-reload rate limit configuration (no restart required).

 1. Overview

 Add a new admin dashboard page that allows administrators to configure rate limits dynamically. Changes take
  effect immediately without restarting Docker/Flask - a true "hot plugin" approach.

 2. Key Technical Insight

 Flask-Limiter supports callable functions for rate limits. Instead of static strings evaluated at import
 time, we use functions that read from ConfigManager on every request:

 # Static (current) - requires restart to change:
 @limiter.limit("10 per minute")

 # Dynamic (new) - hot-reload capable:
 def get_chat_limit():
     return config_manager.get("RATE_LIMIT_CHAT", "10 per minute")

 @limiter.limit(get_chat_limit)

 3. Configurable Rate Limits

 | Key                       | Default       | Description                             |
 |---------------------------|---------------|-----------------------------------------|
 | RATE_LIMIT_DEFAULT_DAILY  | 200 per day   | Global daily limit                      |
 | RATE_LIMIT_DEFAULT_HOURLY | 50 per hour   | Global hourly limit                     |
 | RATE_LIMIT_CHAT           | 10 per minute | Chat endpoint (LLM cost protection)     |
 | RATE_LIMIT_LOGIN          | 5 per minute  | Login endpoint (brute force protection) |

 4. Files to Modify

 | File                      | Action                                              |
 |---------------------------|-----------------------------------------------------|
 | web/admin_ratelimits.html | CREATE - New admin page                             |
 | web/flask_api.py          | MODIFY - Add dynamic limit functions, API endpoints |
 | src/config_manager.py     | MODIFY - Add rate limit property getters            |
 | web/admin_dashboard.html  | MODIFY - Add nav link                               |
 | web/admin_data.html       | MODIFY - Add nav link                               |
 | web/admin_config.html     | MODIFY - Add nav link                               |

 5. Implementation Steps

 Step 1: Extend ConfigManager

 Add rate limit property getters to src/config_manager.py:
 @property
 def chat_rate_limit(self) -> str:
     return self.get("RATE_LIMIT_CHAT", "10 per minute")
 # ... similar for other limits

 Step 2: Add Dynamic Limit Functions to flask_api.py

 def get_chat_limit():
     if config_manager:
         return config_manager.chat_rate_limit
     return "10 per minute"

 Step 3: Replace Static Decorators

 # Change from:
 @limiter.limit("10 per minute")

 # To:
 @limiter.limit(get_chat_limit)

 Step 4: Add API Endpoints

 - GET /api/admin/ratelimits - Fetch current limits
 - POST /api/admin/ratelimits - Update limits (with validation)
 - GET /admin/ratelimits - Serve admin page

 Step 5: Create Admin Page

 New admin_ratelimits.html with:
 - Form inputs for each rate limit
 - Format validation (e.g., "N per minute/hour/day")
 - Success/error toast notifications
 - "Hot Reload Enabled" alert banner

 Step 6: Update Navigation

 Add "Rate Limits" link to navbar in all admin pages.

 6. Validation

 Backend validates rate limit format with regex:
 pattern = r'^\d+\s+per\s+(second|minute|hour|day|month|year)$'

 Valid examples: 10 per minute, 200 per day, 5 per hour

 7. Testing Verification

 1. Page Load: Navigate to /admin/ratelimits, verify form shows current limits
 2. Save Changes: Update chat limit to 5 per minute, verify success toast
 3. Hot Reload Test:
   - Set limit to 2 per minute
   - Send 3 rapid requests → 3rd should return 429
   - Change to 10 per minute (NO RESTART)
   - Send 5 requests → all should succeed
 4. Persistence: Restart Docker, verify limits persist from MongoDB

 8. UI Design

 ┌──────────────────────────────────────────────────────────┐
 │  Heinz VR Admin    [Logs] [Data] [Config] [Rate Limits]  │
 ├──────────────────────────────────────────────────────────┤
 │  ⚡ Hot Reload Enabled: Changes take effect immediately  │
 │                                                          │
 │  ┌─ Default Rate Limits ─────────────────────────────┐  │
 │  │  Daily Limit:   [200 per day    ]                 │  │
 │  │  Hourly Limit:  [50 per hour    ]                 │  │
 │  └───────────────────────────────────────────────────┘  │
 │                                                          │
 │  ┌─ Endpoint-Specific Limits ────────────────────────┐  │
 │  │  Chat /chat:         [10 per minute]              │  │
 │  │  Login /api/auth/login: [5 per minute]            │  │
 │  └───────────────────────────────────────────────────┘  │
 │                                                          │
 │                              [Reset]  [Save Changes]     │
 └──────────────────────────────────────────────────────────┘

 9. Documentation

 Create stage-dev/stage-40-rate-limit-admin.md documenting:
 - Hot-reload mechanism explanation
 - Available configuration options
 - Testing verification steps

 Status: PLANNED