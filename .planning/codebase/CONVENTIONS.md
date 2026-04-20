# Coding Conventions

**Analysis Date:** 2026-04-20

## Python (Backend)

### Linting & Formatting

**Tool:** ruff (linting) + black (formatting)

**Check commands:**
```bash
cd backend
ruff check app/
# Auto-fix: ruff check app/ --fix
# Format: black app/
```

**Note:** No `.prettierrc` for Python - ruff handles both linting and formatting.

### Type Hints

**Pattern:** Full type hints required for function parameters and return types.

```python
async def _get_similar_paddle_ids(paddle_id: int, top_k: int = 5, threshold: float = 0.2) -> list[int]:
    """Get similar paddle IDs based on vector embeddings."""
    # ...
    return [r[0] for r in results]
```

**Optional types:**
```python
from typing import Optional

def _sanitize_image_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
```

### Docstrings

**Style:** Google-style with triple quotes.

```python
"""Paddles API endpoints."""

async def list_paddles(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
):
    """List all paddles with optional filters."""
    # ...
```

### Import Organization

**Order (per file):**
1. Standard library
2. Third-party packages
3. Local application imports

```python
import hashlib
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from psycopg.rows import dict_row
from app.schemas import (
    PaddleResponse,
    PaddleListResponse,
    PriceHistoryResponse,
)
from app.db import get_connection
from app.cache import RedisCache
```

### Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Functions | snake_case | `_sanitize_image_url`, `_get_paddle_details` |
| Private functions | leading underscore | `_get_similar_paddle_ids` |
| Constants | UPPER_SNAKE_CASE | `_BROKEN_URL_MARKERS`, `_cache` |
| Classes | PascalCase | `PaddleResponse`, `PriceHistoryResponse`, `SpecsResponse` |
| Variables | snake_case | `paddle_ids`, `where_clauses` |
| Async functions | prefix with `async_` or use `async def` | `async def get_paddle(paddle_id: int)` |

### Error Handling

**HTTP Exceptions:**
```python
from fastapi import HTTPException, status

if not paddle:
    raise HTTPException(status_code=404, detail="Paddle not found")
```

**Global Exception Handler:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled.exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

### Response Schemas (Pydantic)

**Location:** `backend/app/schemas.py`

```python
from pydantic import BaseModel

class SpecsResponse(BaseModel):
    """Paddle specifications response model."""
    swingweight: Optional[float] = None
    twistweight: Optional[float] = None
    weight_oz: Optional[float] = None
    grip_size: Optional[str] = None
    core_thickness_mm: Optional[float] = None
    face_material: Optional[str] = None

    model_config = {"from_attributes": True}
```

### API Router Pattern

**Location:** `backend/app/api/*.py`

```python
from fastapi import APIRouter

router = APIRouter(prefix="/paddles", tags=["paddles"])

@router.get("", response_model=PaddleListResponse, status_code=status.HTTP_200_OK)
async def list_paddles(...):
    """List all paddles with optional filters."""
    # ...
```

### Logging

**Library:** structlog

```python
import structlog
logger = structlog.get_logger()

logger.info("http.request", request_id=request_id, method=request.method, path=request.url.path)
logger.warning(f"No embedding found for paddle {paddle_id}")
logger.error("unhandled.exception", error=str(exc), path=request.url.path)
```

---

## TypeScript (Frontend)

### Linting & Formatting

**Tool:** ESLint (Next.js preset)

**Config file:** `frontend/.eslintrc.json`
```json
{
  "extends": ["next/core-web-vitals", "next/typescript"]
}
```

**Check command:**
```bash
cd frontend
npm run lint
```

**Note:** No Prettier configuration found in project.

### TypeScript Configuration

**Config file:** `frontend/tsconfig.json`

**Path aliases:**
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### React Component Patterns

**File naming:** PascalCase for components, kebab-case for utilities

| Pattern | Example |
|---------|---------|
| Components | `InlinePaddleCard.tsx`, `LandingClient.tsx` |
| Pages | `page.tsx`, `layout.tsx` |
| Utils | `api.ts`, `types.ts`, `security.ts` |

### Component Definition

**Functional components with TypeScript:**
```typescript
import { Metadata } from 'next'
import { LandingClient } from '@/components/home/landing-client'

export const metadata: Metadata = {
  title: 'PickleIQ — Encontre a Raquete Perfeita com IA',
  description: 'Plataforma de inteligência para pickleball...',
}

export default function Home() {
  return <LandingClient />
}
```

### Import Organization

```typescript
import { Metadata } from 'next'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { InlinePaddleCard } from '@/components/chat/inline-paddle-card'
import { fetchPaddle } from '@/lib/api'
```

### Constants & Config

**Pattern:** Uppercase constants in separate files or at module top

```typescript
const SAMPLE_PADDLE = {
  paddle_id: 42,
  name: 'ProKing Elite 500',
  brand: 'ProKing',
  price_min_brl: 599.9,
  affiliate_url: 'https://example.com/buy/proking-elite-500',
  similarity_score: 0.92,
}
```

---

## Git Conventions

### Branch Naming

**Pattern:** `<type>/<description>`

| Type | Example |
|------|---------|
| Feature | `feature/your-feature` |
| Fix | `fix/bug-description` |

**From CONTRIBUTING.md:**
```bash
git checkout -b feature/your-feature master
```

### Commit Messages

**Pattern:** Conventional commits (type: description)

```bash
git commit -m "feat: description of changes"
git commit -m "fix: resolve paddle listing issue"
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Adding tests

### PR Flow

1. Create branch from `master`
2. Make changes and commit
3. Push to remote
4. Open PR - CI runs automatically
5. After approval, merge to `main`

---

## Configuration Patterns

### Environment Variables

**Backend:** `backend/.env` (never committed - in `.gitignore`)

**Required:**
- `DATABASE_URL` - PostgreSQL connection
- `GROQ_API_KEY` - LLM API key
- `ADMIN_SECRET` - Admin endpoint authentication

**Frontend:** Vercel dashboard or `.env.local`

### Database

**Pattern:** Raw psycopg (no ORM)

```python
from app.db import get_connection

async with get_connection() as conn:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(query, params)
        results = await cur.fetchall()
```

---

## API Conventions

### URL Patterns

| Pattern | Example |
|---------|---------|
| Collection | `/api/v1/paddles` |
| Single resource | `/api/v1/paddles/{id}` |
| Nested | `/api/v1/paddles/{id}/prices` |
| Similar | `/api/v1/paddles/{id}/similar` |

### Request/Response

- Query parameters for filtering/pagination
- Pydantic models for request validation
- JSON response format

**Pagination:**
```python
limit: int = Query(50, ge=1, le=100, description="Pagination limit")
offset: int = Query(0, ge=0, description="Pagination offset")
```

### Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 404 | Not found |
| 422 | Validation error |
| 500 | Internal server error |

---

## Documentation Conventions

### Inline Comments

**When to comment:**
- Complex business logic
- Non-obvious workarounds
- TODO items for future work

**Style:** Clear, concise, in English or Portuguese (project is PT-BR market)

### Module Docstrings

**Location:** Top of every module

```python
"""Paddles API endpoints."""
```

### README Structure

**Per CONTRIBUTING.md:**
- Setup instructions
- Environment configuration
- Development commands
- Testing instructions
- CI/CD pipeline info

---

## Anti-Patterns (Per AGENTS.md)

- **No .editorconfig or .pre-commit-config** - No formatting consistency enforcement
- **No ORM** - Raw SQL with parameterized queries (safe but requires careful review)
- **No LangChain** - Direct API calls to Groq (intentional simpler stack)

---

*Convention analysis: 2026-04-20*
