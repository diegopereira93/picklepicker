# Phase 32: Production Cache & Backend Auth - Research

**Researched:** 2026-04-22
**Domain:** Redis caching + Clerk JWT authentication
**Confidence:** HIGH

## Summary

Phase 32 addresses two critical production issues: (1) the `RedisCache` class uses a Python dict which doesn't share across Railway instances, and (2) all backend endpoints are publicly accessible without authentication.

The solution involves integrating the `redis[hiredis]>=5.0` package with async Redis using `SETEX` for proper TTL, and creating a Clerk JWT verification middleware using FastAPI's dependency injection pattern. The research found that `redis[hiredis] v5.12.1` is current and the `fastapi-clerk-auth` library provides a well-tested solution for Clerk JWKS validation. The project already has Clerk configured on the frontend side, so the backend can leverage the same Clerk authentication infrastructure.

**Primary recommendation:** Use `redis[hiredis]>=5.0` for async Redis with in-memory fallback, and create a custom auth dependency using Clerk JWKS validation rather than relying on `fastapi-clerk-auth` to maintain full control over the authentication flow.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Caching | API/Backend | — | Redis runs as external service, FastAPI manages cache logic |
| JWT verification | API/Backend | — | Clerk JWKS validation happens server-side |
| Protected endpoints | API/Backend | — | Endpoints enforce auth via FastAPI dependencies |

## Standard Stack

### Core Dependencies

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `redis[hiredis]` | ≥5.0 | Async Redis client with hiredis parser | Industry-standard Python Redis client, async support, faster parsing |
| `PyJWT` | ≥2.8.0 | JWT decoding and verification | Required for manual Clerk JWKS validation |
| `cryptography` | Any | RSA key handling for JWKS | Required by PyJWT for RS256 verification |

### Installation

```bash
# Add to backend/pyproject.toml
redis[hiredis]>=5.0
PyJWT>=2.8.0
cryptography>=41.0.0
requests>=2.31.0  # For Clerk JWKS fetching
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `redis[hiredis]>=5.0` | `aioredis` (deprecated) | aioredis merged into redis-py v4.2+, use redis directly |
| Custom Clerk auth | `fastapi-clerk-auth` | Library adds abstraction, custom provides full control; both use same JWKS validation |

## Architecture Patterns

### System Architecture Diagram

```
                                    ┌─────────────────────┐
                                    │  Railway Backend   │
                                    │  (FastAPI app)     │
                                    └────────┬──────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
                ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                │  Redis Pod  │    │    Clerk    │    │  PostgreSQL │
                │ (cache.db) │    │   (auth)   │    │   (data)    │
                └──────────────┘    └──────────────┘    └────��─────────┘
                    
Data Flow:
1. Request → FastAPI endpoint
2. If protected → Auth middleware validates Bearer token
3. Auth middleware fetches Clerk JWKS, verifies signature, extracts claims
4. If cache eligible → Redis SETEX with TTL (or fallback to memory)
5. Response with clerk_id in request.state
```

### Recommended Project Structure

```
backend/app/
├── cache.py              # RedisCache class with SETEX + memory fallback
├── middleware/
│   └── auth.py        # Clerk JWT verification dependency
├── api/
│   ├── price_alerts.py   # Add Depends(require_clerk_auth)
│   ├── affiliate_clicks.py  # Public - no auth
│   └── users.py          # Add Depends(require_clerk_auth)
└── main.py              # Register middleware + REDIS_URL env
```

### Pattern 1: Redis Cache with TTL + Fallback

**What:** Cache class that uses real Redis when `REDIS_URL` is set, falls back to in-memory dict for development

**When to use:** Need distributed caching across multiple backend instances

**Example:**
```python
# Source: Context7 + redis-py documentation
import redis.asyncio as redis
from typing import Optional, Dict, Any

class RedisCache:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
        self._memory_cache: Dict[str, Any] = {}
        self._memory_ttl: Dict[str, float] = {}  # Track TTL for memory fallback
    
    async def _get_client(self) -> Optional[redis.Redis]:
        """Lazy Redis client initialization."""
        if self._redis is None and self.redis_url:
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis
    
    async def get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached value by key."""
        client = await self._get_client()
        if client:
            value = await client.get(key)
            return json.loads(value) if value else None
        # Memory fallback
        if key in self._memory_cache:
            # Check TTL expiry for memory
            if key in self._memory_ttl:
                import time
                if time.time() > self._memory_ttl[key]:
                    del self._memory_cache[key]
                    del self._memory_ttl[key]
                    return None
            return self._memory_cache[key]
        return None
    
    async def set_cached(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> None:
        """Store value with TTL."""
        client = await self._get_client()
        import json
        if client:
            await client.setex(key, ttl, json.dumps(value))
        else:
            # Memory fallback
            import time
            self._memory_cache[key] = value
            self._memory_ttl[key] = time.time() + ttl
```

### Pattern 2: Clerk JWT Verification Dependency

**What:** FastAPI dependency that validates Clerk JWT tokens via JWKS

**When to use:** Protect endpoints that require authenticated users

**Example:**
```python
# Source: Clerk documentation + fastapi-clerk-middleware pattern
import requests
import jwt
from jwt import algorithms as jwt_algorithms
from fastapi import Depends, HTTPException, status, Request
from typing import Optional

CLERK_JWKS_URL = "https://{your-clerk-frontend}.clerk.accounts.dev/.well-known/jwks.json"
CLERK_ISSUER = "https://{your-clerk-frontend}.clerk.accounts.dev"

class ClerkAuthState:
    def __init__(self, clerk_id: str, email: Optional[str] = None, payload: dict = None):
        self.clerk_id = clerk_id
        self.email = email
        self.payload = payload or {}

async def get_clerk_jwks(jwks_url: str) -> dict:
    """Fetch and cache JWKS (implement caching for production)."""
    response = requests.get(jwks_url, timeout=10)
    response.raise_for_status()
    return response.json()

async def verify_clerk_token(token: str, jwks_url: str) -> ClerkAuthState:
    """Verify Clerk JWT token."""
    try:
        # Get unverified header to find key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # Fetch JWKS
        jwks = await get_clerk_jwks(jwks_url)
        
        # Find matching key
        public_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                public_key = jwt_algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not public_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
            }
        )
        
        clerk_id = payload.get("sub")
        if not clerk_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims"
            )
        
        return ClerkAuthState(
            clerk_id=clerk_id,
            email=payload.get("email"),
            payload=payload
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

async def require_clerk_auth(request: Request) -> ClerkAuthState:
    """FastAPI dependency for protected routes."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme"
        )
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    jwks_url = os.getenv(
        "CLERK_JWKS_URL",
        "https://your-app.clerk.accounts.dev/.well-known/jwks.json"
    )
    
    return await verify_clerk_token(token, jwks_url)
```

### Pattern 3: Protected Endpoint Integration

**What:** Using `Depends()` in FastAPI routes

**When to use:** Protect specific endpoints while keeping others public

**Example:**
```python
from fastapi import Depends, APIRouter

router = APIRouter()

# Protected endpoint (requires Clerk auth)
@router.post("/price-alerts")
async def create_price_alert(
    alert: PriceAlertCreate,
    auth: ClerkAuthState = Depends(require_clerk_auth)
):
    """Create price alert - requires authentication."""
    # Use auth.clerk_id as user identifier
    return await create_alert(user_id=auth.clerk_id, alert=alert)

# Public endpoint (no auth required)
@router.post("/affiliate-clicks")
async def log_click(click: AffiliateClickCreate):
    """Log affiliate click - public endpoint."""
    return await log_affiliate_click(click)

# Protected user endpoint
@router.get("/users/{clerk_id}")
async def get_user(
    clerk_id: str,
    auth: ClerkAuthState = Depends(require_clerk_auth)
):
    # Users can only access their own data
    if auth.clerk_id != clerk_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_user_data(clerk_id)
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|------------|-------------|-----|
| Redis connection | Custom socket code | `redis[hiredis]` | Connection pooling, reconnection, error handling already handled |
| JWT verification | Build from scratch | `PyJWT` + JWKS | Clerk uses RS256, proper signature verification complex |
| JWKS fetching | ad-hoc HTTP calls | `requests` + caching | JWKS should be cached to avoid per-request network calls |

**Key insight:** The `redis[hiredis]` package already includes the hiredis C parser for 10x faster parsing. Use async Redis with `await` to maintain non-blocking behavior in FastAPI.

## Runtime State Inventory

> This section not applicable - Phase 32 is a greenfield implementation, not a rename/refactor/migration phase.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — new implementation | N/A |
| Live service config | None — new configuration | Add REDIS_URL and CLERK_JWKS_URL to Railway env vars |
| OS-registered state | None | N/A |
| Secrets/env vars | REDIS_URL, CLERK_JWKS_URL | Configure in Railway dashboard |
| Build artifacts | None | N/A |

**Nothing found in category:** All runtime state is new configuration, not existing runtime that needs migration.

## Common Pitfalls

### Pitfall 1: Redis Connection Failure in Production
**What goes wrong:** Redis pod unavailable causes 500 errors across all endpoints
**Why it happens:** No fallback when Redis is unavailable
**How to avoid:** Implement in-memory fallback in RedisCache class
**Warning signs:** `ConnectionError` or `TimeoutError` from Redis client

### Pitfall 2: JWKS Fetch on Every Request
**What goes slow:** Per-request JWKS fetching adds 50-200ms latency
**Why it happens:** No caching of JWKS keys
**How to avoid:** Cache JWKS with 1-hour TTL, refresh on verification failure
**Warning signs:** High latency on authenticated endpoints

### Pitfall 3: Invalid Token Without Clear Error
**What goes wrong:** Generic 401 responses don't indicate if token is missing vs invalid vs expired
**Why it happens:** Catching all exceptions together
**How to avoid:** Specific error messages for each failure case
**Warning signs:** All auth failures return same message

### Pitfall 4: CORS Blocks Clerk Service Calls
**What goes wrong:** Backend CORS doesn't allow Clerk JWKS endpoint
**Why it happens:** Overly restrictive CORS configuration
**How to avoid:** CORS is for browser requests, Clerk JWKS is server-to-server - not affected

## Code Examples

### Cache with Proper TTL (redis-py async)

```python
# Source: redis-py documentation + Context7
import json
import redis.asyncio as redis
from typing import Optional

class RedisCache:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
    
    async def _ensure_client(self) -> Optional[redis.Redis]:
        if self._redis is None and self.redis_url:
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis
    
    async def get_cached(self, key: str) -> Optional[dict]:
        client = await self._ensure_client()
        if client:
            value = await client.get(key)
            return json.loads(value) if value else None
        return self._memory_cache.get(key)
    
    async def set_cached(self, key: str, value: dict, ttl: int = 3600) -> None:
        client = await self._ensure_client()
        if client:
            await client.setex(key, ttl, json.dumps(value))
        else:
            self._memory_cache[key] = value
```

### Clerk JWT Verification

```python
# Source: Clerk documentation + Stack Overflow patterns
import jwt
from jwt import algorithms as RSAAlgorithm
import requests
from fastapi import HTTPException, status
import os

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "https://your-app.clerk.accounts.dev")

async def verify_token(token: str) -> dict:
    # Get unverified header for key ID
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    
    # Fetch JWKS
    jwks_response = requests.get(CLERK_JWKS_URL, timeout=10)
    jwks = jwks_response.json()
    
    # Find matching public key
    public_key = None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            public_key = RSAAlgorithm.RSAAlgorithm.from_jwk(key)
            break
    
    if not public_key:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Verify token
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=CLERK_ISSUER,
        options={"verify_exp": True, "verify_iss": True}
    )
    
    return {"clerk_id": payload.get("sub"), "email": payload.get("email")}
```

### FastAPI Protected Endpoint

```python
# Source: FastAPI documentation
from fastapi import Depends, HTTPException, status

async def require_auth(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header[7:]
    return await verify_token(token)

@router.post("/price-alerts")
async def create_alert(
    alert: PriceAlertCreate,
    auth: dict = Depends(require_auth)
):
    # auth contains clerk_id from token
    return await create_alert_for_user(auth["clerk_id"], alert)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Memory-only cache | Redis with SETEX | Phase 32 | Shared cache across Railway instances |
| No authentication | Clerk JWKS validation | Phase 32 | Protected user endpoints |
| Hardcoded Clerk frontend | Environment-based JWKS URL | Phase 32 | Dev/prod configuration |

**Deprecated/outdated:**
- `RedisCache` dict-based implementation — no TTL, no sharing across instances
- `aioredis` package — merged into `redis-py` v4.2+, use `redis[hiredis]`
- All endpoints public — security risk, Phase 32 adds proper auth

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Clerk JWKS URL follows pattern `https://*.clerk.accounts.dev/.well-known/jwks.json` | Auth Middleware | JWKS URL format changed by Clerk — configure via env var |
| A2 | Frontend uses Clerk for authentication | Project Context | If not, auth middleware needs different provider |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions

1. **What's the exact Clerk frontend domain?**
   - What we know: Frontend uses Clerk (from `CLERK_PUBLISHABLE_KEY` in environment)
   - What's unclear: The exact `{your-app}.clerk.accounts.dev` domain
   - Recommendation: Use environment variable `CLERK_JWKS_URL` to configure per environment

2. **Should affiliate clicks be public or protected?**
   - What we know: ROADMAP says "Affiliate clicks remain public (legitimate for anonymous users)"
   - What's unclear: Same as ROADMAP — keep public
   - Recommendation: Keep `POST /affiliate-clicks` public per ROADMAP

3. **Where should Redis run in production?**
   - What we know: Railway can provision Redis via "Add service" → "Redis"
   - What's unclear: Whether to use Railway Redis or external service (Upstash, etc.)
   - Recommendation: Use Railway Redis for simplicity, switch to Upstash if Railway Redis unavailable

## Environment Availability

> Step 2.6: SKIPPED — no external dependencies identified beyond adding Redis.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Redis | Caching (production) | ✗ | — | Local dev uses in-memory fallback |
| Clerk | Authentication | ✓ (frontend) | — | Backend uses Clerk JWKS (server-to-server) |

**Missing dependencies with no fallback:**
- Redis in local development — addressed via in-memory fallback

**Missing dependencies with fallback:**
- None — all have clear fallback strategies

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest-asyncio |
| Config file | `backend/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/test_cache.py tests/test_auth_middleware.py -x` |
| Full suite command | `cd backend && pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| B1 | Redis cache set/get with TTL | unit | `pytest tests/test_cache.py::test_cache_set_get_with_redis -x` | ✅ test_cache.py exists |
| B1 | Fallback to memory when Redis unavailable | unit | `pytest tests/test_cache.py::test_cache_fallback_to_memory -x` | ✅ test_cache.py exists |
| B2 | Auth middleware rejects invalid tokens | unit | `pytest tests/test_auth_middleware.py::test_auth_invalid_token -x` | ❌ New file needed |
| B2 | Protected endpoints return 401 without token | unit | `pytest tests/test_auth_middleware.py::test_protected_endpoint_no_token -x` | ❌ New file needed |
| B2 | Public endpoints work without auth | unit | `pytest tests/test_auth_middleware.py::test_public_endpoint_without_auth -x` | ❌ New file needed |

### Sampling Rate

- **Per task commit:** `pytest tests/test_cache.py tests/test_auth_middleware.py -x`
- **Per wave merge:** Full backend test suite
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [x] `tests/test_cache.py` — exists, needs updates for Redis
- [ ] `tests/test_auth_middleware.py` — NEW, covers B2 authentication
- [ ] Redis fixture in `tests/conftest.py` — for mocking or test containers

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Clerk JWT (Bearer token) |
| V3 Session Management | yes | JWT expiry verification |
| V4 Access Control | yes | FastAPI dependency: users can only access own data |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Replay attacks | Tampering | JWT includes expiration (`exp` claim), verify with PyJWT |
| JWKS poisoning | Tampering | Validate token `iss` claim matches expected issuer |
| Redis injection | Tampering | Use parameterized key names, never user input as keys directly |

## Sources

### Primary (HIGH confidence)

- [redis-py documentation](https://github.com/redis/redis-py) - SETEX, async client
- [Clerk FastAPI example](https://github.com/clerk/fastapi-example) - Official Clerk + FastAPI integration
- [FastAPI dependency injection](https://fastapi.tiangolo.com/tutorial/dependencies/) - `Depends()` pattern

### Secondary (MEDIUM confidence)

- [fastapi-clerk-middleware](https://github.com/OSSMafia/fastapi-clerk-middleware) - Alternative library approach
- [Stack Overflow: Clerk JWT](https://stackoverflow.com/questions/76671472/clerk-jwt-authentication) - Manual verification pattern

### Tertiary (LOW confidence)

- PyPI `fastapi-clerk-auth` package - Not verified in this session, reference only

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - redis-py is well-documented, Clerk has official FastAPI example
- Architecture: HIGH - Redis + JWT patterns are standard
- Pitfalls: MEDIUM - Identified common issues but some are theoretical

**Research date:** 2026-04-22
**Valid until:** 90 days (Redis and Clerk APIs are stable)