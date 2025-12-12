# Stage 37: Remove Redis Dependency

**Date:** 2025-12-12
**Focus:** Remove Redis dependency and use in-memory storage for rate limiting to achieve "plug-and-play" deployment.

## 1. Problem Description

When deploying to school VM, the system sometimes fails to load databases (courses, skills) due to Redis issues. Users must manually run `redis-cli FLUSHALL` to recover.

**Root Cause:** Flask-Limiter uses Redis for rate limiting storage. If Redis has corrupted data or connection issues, the entire Flask app fails to initialize, blocking all subsequent service loading.

## 2. Current Architecture

```
Redis (docker) ←── Flask-Limiter (rate limiting counters)
                   └── "200 per day", "50 per hour" per IP
```

**Redis stores only:**
- Rate limiting counters (e.g., `LIMITER:192.168.1.100:/chat:2025-12-12 → 15`)
- Auto-expires after time window (1 hour / 1 day)
- Total size: ~30KB for 100 concurrent users

**Redis does NOT store:**
- Course data
- Skills data
- User sessions
- Configuration

## 3. Solution: Remove Redis, Use Memory Storage

For single-instance VM deployment, in-memory storage is sufficient and eliminates Redis-related failures.

### Changes Required

#### A. Modify `web/flask_api.py`

```python
# Before (lines 37-51):
redis_url = os.getenv("REDIS_URL")
storage_uri = redis_url if redis_url else "memory://"

# After:
# Force memory storage - no Redis dependency for single-instance deployment
storage_uri = "memory://"
```

#### B. Modify `docker-compose.prod.yml`

Remove Redis service and related configuration:

```yaml
# REMOVE this entire service block:
redis:
  image: redis:7.2-alpine
  container_name: vr-redis
  ...

# REMOVE from vr-recommender service:
environment:
  - REDIS_URL=redis://redis:6379/0  # DELETE this line
depends_on:
  - redis  # DELETE this line

# REMOVE from volumes:
redis_data:  # DELETE this line
```

#### C. Modify `requirements.txt`

```
# Optional: Remove redis package if not used elsewhere
# redis>=4.0.0  # Can be removed
```

## 4. Files to Modify

| File | Changes |
|------|---------|
| `web/flask_api.py` | Force `storage_uri = "memory://"` |
| `docker-compose.prod.yml` | Remove redis service, redis_data volume, REDIS_URL env |
| `requirements.txt` | (Optional) Remove redis package |

## 5. Trade-offs

| Aspect | With Redis | With Memory |
|--------|-----------|-------------|
| Rate limit persistence | Survives restart | Resets on restart |
| Multi-instance support | ✅ Shared state | ❌ Per-instance |
| Complexity | Higher | Lower |
| Failure points | More | Fewer |
| For school VM | Overkill | Perfect fit |

**Note:** Rate limit reset on restart has minimal impact - users just get fresh quotas.

## 6. Verification Steps

1. Remove Redis from docker-compose and rebuild:
   ```bash
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. Verify no Redis dependency:
   ```bash
   docker ps  # Should NOT show vr-redis
   ```

3. Check Flask startup logs:
   ```bash
   docker logs vr-recommender | grep "Rate Limiter"
   # Should show: Rate Limiter Storage: memory://
   ```

4. Test rate limiting still works:
   - Access `/chat` endpoint multiple times
   - After 10 requests/minute, should get 429 Too Many Requests

5. Test restart recovery:
   ```bash
   docker-compose -f docker-compose.prod.yml restart vr-recommender
   # System should start cleanly without any FLUSHALL needed
   ```

## 7. Risk Assessment

**Very Low Risk:**
- Only affects rate limiting storage location
- No business logic changes
- No data migration needed
- Simplifies deployment

**Status:** COMPLETED
