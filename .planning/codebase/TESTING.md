# Testing Patterns

**Analysis Date:** 2026-04-20

## Testing Frameworks

### Backend (Python)

**Framework:** pytest + pytest-asyncio

**Config:** `backend/pyproject.toml`
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Version:** pytest-asyncio >= 0.21.0

**Frontend (TypeScript)**

**Framework:** Vitest (jsdom environment)

**Config:** `frontend/vitest.config.ts`
```typescript
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts'],
    exclude: ['**/e2e/**', '**/node_modules/**', '**/dist/**'],
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
})
```

---

## Running Tests

### Makefile Commands

**All tests:**
```bash
make test                     # Backend + frontend
```

**Backend only:**
```bash
make test-backend             # pytest -v
make test-backend-cov         # pytest with HTML coverage report
```

**Frontend only:**
```bash
make test-frontend            # vitest run
```

**E2E / Scraper tests:**
```bash
make test-e2e               # Requires DB running (starts it automatically)
```

### Direct Commands

**Backend:**
```bash
cd backend && . venv/bin/activate && PYTHONPATH=$(PWD) python3 -m pytest -v
```

**Frontend:**
```bash
cd frontend && npm run test           # vitest run
cd frontend && npm run test:watch     # vitest (watch mode)
```

---

## Test File Organization

### Backend Tests

**Location:** `backend/tests/`

**Naming:** `test_*.py`

```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_paddles_endpoints.py
├── test_agent.py
├── test_chat_endpoint.py
├── test_price_alerts.py
├── test_cache.py
└── ... (23 test files total)
```

### Frontend Tests

**Location:** `frontend/src/tests/`

**Naming:** `*.test.ts` or `*.test.tsx`

```
frontend/src/tests/
├── setup.ts                 # Test setup (imports jest-dom)
├── unit/
│   ├── product-card.test.ts
│   ├── quiz.test.ts
│   ├── catalog-components.test.tsx
│   └── ... (14 test files)
├── api.test.ts
├── blog-metadata.test.tsx
├── ftc-disclosure.test.tsx
└── price-history-chart.test.tsx
```

### Pipeline Tests

**Location:** `pipeline/tests/`

```
pipeline/tests/
├── test_utils.py
├── test_dropshot_brasil_scraper.py
├── test_mercado_livre_scraper.py
├── test_embeddings.py
└── ...
```

---

## Test Structure Patterns

### Backend Test Example

```python
"""Tests for paddles API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_paddles__200():
    """Test GET /paddles returns 200 with proper schema."""
    response = client.get("/api/v1/paddles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)

def test_get_paddles__limit_max():
    """Test /paddles limit cannot exceed 100."""
    response = client.get("/api/v1/paddles?limit=150")
    assert response.status_code == 422  # Validation error
```

### Frontend Test Example

```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { InlinePaddleCard } from '@/components/chat/inline-paddle-card'

vi.mock('@/lib/api', () => ({ fetchPaddle: vi.fn().mockResolvedValue(null) }))

const SAMPLE_PADDLE = {
  paddle_id: 42,
  name: 'ProKing Elite 500',
  brand: 'ProKing',
  price_min_brl: 599.9,
  affiliate_url: 'https://example.com/buy/proking-elite-500',
  similarity_score: 0.92,
}

describe('InlinePaddleCard', () => {
  it('renders paddle name', () => {
    render(React.createElement(InlinePaddleCard, SAMPLE_PADDLE))
    expect(screen.getByText('ProKing Elite 500')).toBeDefined()
  })

  it('renders affiliate link', () => {
    render(React.createElement(InlinePaddleCard, SAMPLE_PADDLE))
    const link = screen.getByRole('link', { name: /ver ofertas/i })
    expect(link).toBeDefined()
    expect(link.getAttribute('href')).toBe('https://example.com/buy/proking-elite-500')
  })
})
```

---

## Test Fixtures & Mocks

### Backend Fixtures (`backend/tests/conftest.py`)

```python
@pytest.fixture(autouse=True)
def mock_db_pool():
    """Mock database connection pool for all tests."""
    mock_cursor = AsyncMock()
    mock_cursor.execute = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value={"total": 0})
    mock_cursor.fetchall = AsyncMock(return_value=[])
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    mock_pool = AsyncMock()
    mock_pool.connection = MagicMock(return_value=mock_conn)
    mock_pool.__aenter__ = AsyncMock(return_value=mock_pool)
    mock_pool.__aexit__ = AsyncMock(return_value=None)

    with patch('app.db.get_pool', new_callable=AsyncMock) as mock_get:
        with patch('app.db.close_pool', new_callable=AsyncMock) as mock_close:
            with patch('app.db.get_connection') as mock_get_conn:
                mock_get.return_value = mock_pool
                mock_close.return_value = None
                mock_get_conn.return_value = mock_conn
                yield mock_pool
```

### Pipeline Fixtures (`pipeline/tests/test_utils.py`)

```python
class AsyncMockFirecrawl:
    """Reusable mock for FirecrawlApp usable in E2E scraper tests."""

    def __init__(self):
        self._responses = []
        self._call_count = 0

    def set_extract_response(self, response: dict) -> None:
        self._responses = [response]

    def set_extract_errors(self, errors: list) -> None:
        self._responses = errors

    def extract(self, urls=None, prompt=None, schema=None, **kwargs):
        idx = min(self._call_count, len(self._responses) - 1) if self._responses else 0
        self._call_count += 1

        if not self._responses:
            return {"data": {"products": []}}

        item = self._responses[idx] if idx < len(self._responses) else self._responses[-1]
        if isinstance(item, type) and issubclass(item, Exception):
            raise item("Simulated error")
        if isinstance(item, Exception):
            raise item
        return item
```

### Firecrawl Fixtures

```python
@pytest.fixture
def mock_firecrawl_app():
    """Mock FirecrawlApp instance with extract() and crawl() methods."""
    app = MagicMock()
    app.extract = MagicMock(return_value={
        "data": {
            "products": [
                {
                    "name": "Selkirk Vanguard Power Air",
                    "price_brl": 1299.90,
                    "in_stock": True,
                    "image_url": "https://example.com/img.jpg",
                    "product_url": "https://brazilpickleballstore.com.br/product/1",
                    "brand": "Selkirk",
                    "specs": {"weight_oz": 8.4, "core_thickness_mm": 16},
                }
            ]
        }
    })
    return app
```

---

## Test Types

### Unit Tests

**Scope:** Individual functions, classes, API endpoints

**Backend:** `test_paddles_endpoints.py`, `test_agent.py`
**Frontend:** `test_product-card.test.ts`, `test_quiz.test.ts`

### Integration Tests

**Scope:** Multiple components working together

**Backend:** API endpoint tests with mocked DB
**Frontend:** Component rendering tests

### E2E / Scraper Tests

**Location:** `pipeline/tests/`

**Requirements:** Real database running

**Command:** `make test-e2e`

**Coverage:** Live scraping tests against staging config

```bash
cd pipeline && \
    . .venv/bin/activate && \
    python test_e2e_scraper.py
```

---

## Test Coverage

### Backend

**Tool:** pytest-cov

**Threshold:** 80% (per CONTRIBUTING.md)

**Report location:** `backend/htmlcov/index.html`

**Command:**
```bash
make test-backend-cov
# Output: backend/htmlcov/index.html
```

### Frontend

**No enforced coverage threshold found.** Tests run via Vitest.

---

## CI/CD Testing

### GitHub Actions

**Workflow:** `.github/workflows/test.yml`

**Runs on:** Every PR

**Steps:**
1. Install dependencies
2. Run ruff (linting)
3. Run pytest (backend tests)
4. Run vitest (frontend tests)
5. Check coverage threshold (80%)

**Merge requirements:**
- All status checks passing
- Minimum 80% code coverage

---

## Anti-Patterns (Per AGENTS.md)

- **No specific test patterns beyond basic mocks**
- **Eval gate is mock** - `eval_gate.py` returns hardcoded scores arrays (not testing real LLMs)
- **Pre-existing Jina/HF API 401 failures** - 2 test failures in backend

---

*Testing analysis: 2026-04-20*