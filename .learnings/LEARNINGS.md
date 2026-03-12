# Learnings

## [LRN-20260312-001] performance_monitoring

**Logged**: 2026-03-12T05:00:00Z
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
Added performance monitoring middleware and enhanced health check endpoint to Welcome-Link API.

### Details
- Added `RequestTimingMiddleware` to track request processing time
- Added `X-Process-Time-Ms` header to all responses for debugging
- Enhanced `/api/health` endpoint with system metrics (CPU, memory, disk)
- Added database health check with SQLite connection test
- Slow requests (>500ms) are logged with warning level
- Version bump to 2.7.2

### Implementation
```python
# Request Timing Middleware
class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        if process_time > 500:
            logger.warning(f"⚠️ Slow request: {request.method} {request.url.path}")
        return response

# Enhanced Health Check with psutil
@api_router.get("/health")
def health_check():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    # ... returns detailed metrics
```

### Metadata
- Source: user_request
- Related Files: welcome-backend/backend/server.py
- Tags: performance, monitoring, backend, health-check
- Pattern-Key: backend.performance_monitoring

---

## [LRN-20260312-002] git_workflow

**Logged**: 2026-03-12T05:00:00Z
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
Always check git status before making changes and commit with descriptive messages.

### Details
When making improvements:
1. Check `git status --short` to see current state
2. Check `git log --oneline -10` to see recent commits
3. Make changes incrementally
4. Use `git add -A && git diff --cached --stat` to review before commit
5. Write clear commit messages with feature prefix

### Suggested Action
Follow this workflow for all code changes.

### Metadata
- Source: best_practice
- Tags: git, workflow, commits
- Pattern-Key: workflow.git_commit

---