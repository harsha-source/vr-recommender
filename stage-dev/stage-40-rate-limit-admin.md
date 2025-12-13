# Stage 40: Dynamic Rate Limit Configuration Admin Page

**Date:** 2025-12-12
**Focus:** Add admin dashboard page for hot-reload rate limit configuration.

## 1. Overview

Added a new admin dashboard page that allows administrators to configure rate limits dynamically. Changes take effect **immediately** without restarting Docker/Flask - a true "hot plugin" approach.

## 2. Technical Implementation

### Hot-Reload Mechanism

Flask-Limiter supports **callable functions** for rate limits in decorators. Instead of static strings, we use functions that read from ConfigManager on every request:

```python
# Before (static - requires restart):
@limiter.limit("10 per minute")

# After (dynamic - hot-reload):
def get_chat_limit():
    if config_manager:
        return config_manager.chat_rate_limit
    return "10 per minute"

@limiter.limit(get_chat_limit)
```

### Limitation

Flask-Limiter's `default_limits` parameter in the Limiter constructor does NOT support callables - only endpoint-specific decorators do. Therefore:
- **Hot-Reload Capable**: Chat (`/chat`) and Login (`/api/auth/login`) endpoints
- **Requires Restart**: Default global limits (200/day, 50/hour)

## 3. Configurable Rate Limits

| Key | Default | Endpoint | Hot-Reload |
|-----|---------|----------|------------|
| `RATE_LIMIT_CHAT` | 10 per minute | `/chat` | Yes |
| `RATE_LIMIT_LOGIN` | 5 per minute | `/api/auth/login` | Yes |
| Default Daily | 200 per day | All endpoints | No (restart required) |
| Default Hourly | 50 per hour | All endpoints | No (restart required) |

## 4. Files Modified

| File | Action |
|------|--------|
| `web/admin_ratelimits.html` | **CREATED** - New admin page |
| `web/flask_api.py` | **MODIFIED** - Dynamic limit functions, API endpoints |
| `src/config_manager.py` | **MODIFIED** - Rate limit property getters |
| `web/admin_dashboard.html` | **MODIFIED** - Added nav link |
| `web/admin_data.html` | **MODIFIED** - Added nav link |
| `web/admin_config.html` | **MODIFIED** - Added nav link |

## 5. New API Endpoints

### GET /api/admin/ratelimits
Returns current rate limit configuration.

**Response:**
```json
{
  "RATE_LIMIT_CHAT": {
    "value": "10 per minute",
    "label": "Chat Endpoint Limit",
    "description": "Maximum chat requests per minute (protects LLM API costs)",
    "default": "10 per minute"
  },
  "RATE_LIMIT_LOGIN": {
    "value": "5 per minute",
    "label": "Login Endpoint Limit",
    "description": "Maximum login attempts per minute (prevents brute force)",
    "default": "5 per minute"
  }
}
```

### POST /api/admin/ratelimits
Update rate limits. Changes effective immediately.

**Request:**
```json
{
  "RATE_LIMIT_CHAT": "5 per minute",
  "RATE_LIMIT_LOGIN": "10 per minute"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Rate limits updated. Changes are effective immediately.",
  "updated": ["RATE_LIMIT_CHAT", "RATE_LIMIT_LOGIN"]
}
```

**Validation:**
- Format must match pattern: `N per minute/hour/day/second/month/year`
- Invalid formats return 400 error with details

## 6. Admin UI Features

### Rate Limits Page (`/admin/ratelimits`)

- **Hot Reload Enabled** banner (green) - explains changes are immediate
- **Format Info** banner (blue) - shows valid format patterns
- **Default Limits** banner (gray) - notes static limits require restart
- **Endpoint-Specific Limits** card with:
  - Chat Endpoint input (`/chat`)
  - Login Endpoint input (`/api/auth/login`)
- **Reset** button - reloads current values from server
- **Save Changes** button - saves to MongoDB, effective immediately

### Navigation

"Rate Limits" link added to navbar in all admin pages:
- `/admin` (Logs & Stats)
- `/admin/data` (Data Management)
- `/admin/config` (System Config)
- `/admin/ratelimits` (Rate Limits) - NEW

## 7. Testing Verification

### Hot-Reload Test Performed:
1. Set chat limit to `5 per minute` via admin UI
2. Sent 6 rapid requests to `/chat`
3. Request 6 returned: `"You've exceeded the limit of 5 per 1 minute"`
4. Reset to `10 per minute` via admin UI (no restart needed)
5. New limit effective immediately

### Test Commands:
```bash
# Send rapid requests to test rate limit
for i in 1 2 3 4 5 6; do
  curl -X POST http://localhost:5001/chat \
    -H 'Content-Type: application/json' \
    -d '{"message": "test"}'
done
```

## 8. Code Changes Summary

### config_manager.py
Added rate limit property getters:
```python
@property
def chat_rate_limit(self) -> str:
    return self.get("RATE_LIMIT_CHAT", "10 per minute")

@property
def login_rate_limit(self) -> str:
    return self.get("RATE_LIMIT_LOGIN", "5 per minute")
```

### flask_api.py
1. Added dynamic limit getter functions (before Limiter initialization)
2. Changed `@limiter.limit("10 per minute")` to `@limiter.limit(get_chat_limit)`
3. Added `RATE_LIMIT_KEYS` dictionary for validation
4. Added GET/POST `/api/admin/ratelimits` endpoints
5. Added `/admin/ratelimits` page route

## 9. Persistence

Rate limits are stored in MongoDB via ConfigManager:
- Collection: `system_config`
- Keys: `rate_limit_chat`, `rate_limit_login` (lowercase)
- Persists across Docker restarts

**Status:** COMPLETED
