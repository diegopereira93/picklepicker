# Testing — PickleIQ

Testing infrastructure, conventions, and how to run/write tests.

## Test Suites Overview

| Suite | Framework | Location | Count | Runner |
|-------|-----------|----------|-------|--------|
| Backend | pytest-asyncio | `backend/tests/` | 198 | `make test-backend` |
| Frontend | Vitest + jsdom | `frontend/src/tests/` | 179 | `make test-frontend` |
| E2E | Playwright | `frontend/e2e/` | 23 | `npx playwright test` |
| Pipeline | pytest-asyncio | `pipeline/tests/` | 153 | `pipeline/.venv/bin/pytest` |

## Quick Start

```bash
# Run everything
make test

# Individual suites
make test-backend          # pytest (backend)
make test-frontend         # vitest (frontend)
cd frontend && npx playwright test  # E2E
```

## Backend Tests

### Setup

- Framework: pytest-asyncio with `asyncio_mode = "auto"`
- DB mocking: Autouse fixture in `backend/tests/conftest.py` replaces `get_connection()` with mock
- Coverage threshold: 80%
- No real database or API keys needed

### Running

```bash
make test-backend              # Quick run
make test-backend-cov          # With HTML coverage report
backend/venv/bin/python -m pytest tests/test_paddles.py -v   # Single file
```

### Writing Backend Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_my_endpoint(client):
    response = await client.post("/api/v1/my-resource", json={"field": "value"})
    assert response.status_code == 201
    data = response.json()
    assert data["field"] == "value"
```

Key patterns:
- Use the `client` fixture from conftest (AsyncClient with mocked DB)
- Mock external APIs (Groq, Jina) with `patch`
- Use `AsyncMock` for async functions
- Test files match source: `api/paddles.py` → `tests/test_paddles.py`

### Known Failures

Two tests fail without real API keys:
- `test_chat_stream__recommendation_has_affiliate_url` — needs Jina/HF/Groq keys
- `test_e2e_chat_flow__happy_path` — needs Jina/HF/Groq keys

These are pre-existing and do not block development.

## Frontend Tests

### Setup

- Framework: Vitest with jsdom environment
- Setup file: `frontend/src/tests/setup.ts`
- Config: `frontend/vitest.config.ts` (excludes `e2e/` directory)

### Running

```bash
make test-frontend                          # All tests
cd frontend && npx vitest run test/my-test   # Single file
cd frontend && npx vitest watch              # Watch mode
```

### Writing Frontend Tests

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import MyComponent from './my-component'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

Key patterns:
- Use `@testing-library/react` for component tests
- Mock `next/navigation` with `vi.mock('next/navigation')`
- Mock Clerk auth with `useAuth` mock
- Test files live alongside source or in `src/tests/`

## E2E Tests

### Setup

- Framework: Playwright
- Config: `frontend/playwright.config.ts`
- Starts dev server automatically via `webServer` config
- Chromium only (no Firefox/WebKit)

### Running

```bash
cd frontend && npx playwright test           # All E2E tests
cd frontend && npx playwright test --ui      # Interactive UI
cd frontend && npx playwright test e2e/home  # Single spec
```

### Writing E2E Tests

```typescript
import { test, expect } from '@playwright/test'

test.describe('My Page', () => {
  test('loads with 200 status', async ({ page }) => {
    const response = await page.goto('/my-page')
    expect(response!.status()).toBe(200)
  })

  test('renders content', async ({ page }) => {
    await page.goto('/my-page')
    await expect(page.getByRole('heading')).toBeVisible({ timeout: 5000 })
  })
})
```

Key conventions:
- Tests verify page **loads**, not full functionality
- No API mocking — let the app handle failures naturally
- Use `getByRole()` for selectors (accessible queries)
- Use `page.waitForLoadState('networkidle')` before asserting content
- Keep timeouts reasonable (5-10s for content, 30s for navigation)

### E2E Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `e2e/home.spec.ts` | 4 | Landing page, hero, CTA links |
| `e2e/catalog.spec.ts` | 4 | Catalog load, filters, API failure |
| `e2e/chat.spec.ts` | 4 | Chat load, quiz prompt, navigation |
| `e2e/quiz.spec.ts` | 4 | Quiz load, options, progress |
| `e2e/navigation.spec.ts` | 7 | Route status, navigation, 404 |

## Pipeline Tests

### Setup

- Framework: pytest-asyncio
- DB mocking: Mock connections in `pipeline/tests/conftest.py`
- HTTP mocking: Mock Firecrawl API responses

### Running

```bash
pipeline/.venv/bin/python -m pytest pipeline/tests/ -q
```

### Known Issues

- 2 embedding placeholder tests require a running DB — skip with `-k "not embedding"`
- 2 retry tests hang due to real tenacity backoff waits — skip with `-k "not rate_limit_backoff and not retry_3_times"`

### Writing Pipeline Tests

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_crawler_extracts_products():
    mock_scrape = AsyncMock(return_value="# Markdown with product data...")
    with patch("crawlers.my_store.app.scrape", mock_scrape):
        result = await crawl_products()
        assert len(result) > 0
        assert result[0]["price_brl"] > 0
```

Key patterns:
- Mock `app.scrape()` (not `app.extract()` — crawlers migrated to scrape-based markdown parsing)
- Mock DB connections for save operations
- Test price parsing with Brazilian format: `R$1.299,90` (no space after R$)
- Verify `call_count` matches expected (2 per product: SELECT + INSERT)

## CI/CD Integration

Tests run automatically on:
- **PRs** — `.github/workflows/test.yml`
- **Push to main** — `.github/workflows/deploy.yml`
- **Scheduled** — scraping pipeline, lighthouse audits

### Coverage

```bash
make test-backend-cov    # Generates htmlcov/
```

Open `backend/htmlcov/index.html` for the coverage report.
