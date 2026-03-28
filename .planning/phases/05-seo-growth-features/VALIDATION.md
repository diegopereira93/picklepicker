# Phase 5: SEO & Growth Features - Test Architecture & Validation

**Created:** 2026-03-28
**Purpose:** Define test strategy, verify Nyquist compliance, map requirements to test coverage

---

## Test Architecture Overview

Phase 05 requires comprehensive validation across four requirement areas:
- **R5.1**: SEO metadata and structured data (product pages)
- **R5.2**: Authentication and session management (Clerk integration)
- **R5.3**: Price history visualization and alerts (Recharts, data accuracy)
- **R5.4**: Email delivery and compliance (Resend, FTC disclosure)

### Test Framework Stack

| Layer | Framework | Config | Command | Scope |
|-------|-----------|--------|---------|-------|
| Frontend Unit | Vitest + Testing Library | `vitest.config.ts` | `npm run test` | Component rendering, hooks, mocks |
| Frontend Integration | Vitest + MSW | `vitest.config.ts` | `npm run test:integration` | API calls, state management, navigation |
| Backend Unit | pytest | `pyproject.toml` | `pytest tests/ -k "unit" -q` | FastAPI endpoints, business logic, SQL |
| End-to-End | Playwright | `playwright.config.ts` | `npm run test:e2e` | Full user flows (Clerk login, price alert creation) |
| Coverage Gate | pytest-cov | `pyproject.toml` | `pytest --cov=backend --cov-fail-under=80` | Minimum 80% code coverage |

---

## Wave 0: Test Scaffolding

**Goal:** Create empty test files with proper structure before implementation waves execute. Enables TDD Red→Green→Refactor.

### Test Files (7 required, 8 optional E2E)

#### Frontend Tests

| File | Requirement | Purpose | Lines |
|------|-------------|---------|-------|
| `frontend/__tests__/product-metadata.test.ts` | R5.1 | Verify `generateMetadata()` returns title, description, OG image, canonical URL | 40 |
| `frontend/__tests__/product-schema.test.ts` | R5.1 | Verify Schema.org/Product JSON-LD renders without hydration mismatch, all fields present | 50 |
| `frontend/__tests__/clerk-auth.test.ts` | R5.2 | Verify `auth()` returns userId for authenticated users, null for anon, type safety | 35 |
| `frontend/__tests__/price-chart.test.tsx` | R5.3 | Verify Recharts chart renders with SSR: false, no hydration errors, tooltip functions | 45 |

#### Backend Tests

| File | Requirement | Purpose | Lines |
|------|-------------|---------|-------|
| `backend/tests/test_price_alerts.py` | R5.2 | Verify POST /price-alerts requires auth (401 if anon), creates alert, returns correct schema | 60 |
| `backend/tests/test_price_history.py` | R5.3 | Verify GET /paddles/{id}/price-history?days=90 returns 90-day data, percentile calc correct | 70 |
| `backend/tests/test_resend_email.py` | R5.4 | Verify email sends with List-Unsubscribe header, template renders correctly, no failures | 50 |

#### Optional E2E Tests (Wave 2+)

| File | Requirement | Purpose | Notes |
|------|-------------|---------|-------|
| `e2e/clerk-login-flow.spec.ts` | R5.2 | Anon user → Clerk <SignIn /> → authenticated session persists | Playwright, manual approval |
| `e2e/price-alert-creation.spec.ts` | R5.2 | User sets price alert, receives email when threshold breached | Requires Resend sandbox |
| `e2e/product-seo.spec.ts` | R5.1 | Navigate to /paddles/[brand]/[slug], verify OG tags in HTML, no 404s | Playwright |
| `e2e/price-history-chart.spec.ts` | R5.3 | Chart loads, hover shows tooltip, no console errors | Playwright |
| `e2e/affiliate-disclosure.spec.ts` | R5.4 | Product page displays FTC disclosure above first affiliate link | Visual regression |

---

## Requirement → Test Mapping

### R5.1: SEO Metadata & Structured Data

**Truth:** Product pages are indexable by search engines with dynamic metadata per product.

**Test Coverage:**

```
✓ product-metadata.test.ts
  ├─ generateMetadata() returns title: `${brand} ${model} - PickleIQ`
  ├─ OG image set to paddle.image_url
  ├─ OG description from paddle.description
  ├─ Canonical URL correct
  └─ Robots: index, follow

✓ product-schema.test.ts
  ├─ ld+json renders as <script type="application/ld+json">
  ├─ @type: Product, name, brand fields present
  ├─ offers.priceCurrency: BRL
  ├─ aggregateRating fields present
  ├─ No hydration mismatch (client/server match)
  └─ Valid JSON serialization

✓ E2E: product-seo.spec.ts (Wave 2+)
  ├─ Navigate /paddles/selkirk/amped
  ├─ Verify page title in <head>
  ├─ Verify <meta property="og:image"> present
  └─ No 404 errors
```

**Automated Commands:**
```bash
# Unit: metadata
npm run test -- --grep="product-metadata"

# Unit: structured data
npm run test -- --grep="product-schema"

# E2E: full page (Wave 2+)
npm run test:e2e -- e2e/product-seo.spec.ts
```

---

### R5.2: Authentication & Session Management

**Truth:** Authenticated users see price alerts; anonymous users see 401 on alert creation.

**Test Coverage:**

```
✓ clerk-auth.test.ts
  ├─ auth() mock returns userId for authenticated users
  ├─ auth() mock returns { userId: null } for anonymous
  ├─ useAuth() hook type-safe with Clerk SDK
  └─ Middleware guards /admin routes

✓ backend: test_price_alerts.py
  ├─ POST /price-alerts missing Authorization → 401
  ├─ POST /price-alerts with valid JWT → 201, creates alert
  ├─ Alert schema: user_id, paddle_id, price_target, active
  ├─ GET /price-alerts/:id only returns alerts for authenticated user
  └─ DELETE removes alert from authenticated user only

✓ E2E: clerk-login-flow.spec.ts (Wave 2+)
  ├─ Anon user visits /
  ├─ Click "Save Profile" → <SignIn /> modal
  ├─ Sign up with email + password
  ├─ Post-signup, auth() returns userId
  ├─ Chat history preserved (migrated from localStorage)
  └─ <UserButton /> shows signed-in state
```

**Automated Commands:**
```bash
# Frontend auth mocks
npm run test -- --grep="clerk-auth"

# Backend auth enforcement
pytest tests/test_price_alerts.py -xvs

# E2E login (Wave 2+)
npm run test:e2e -- e2e/clerk-login-flow.spec.ts
```

---

### R5.3: Price History & Visualization

**Truth:** Users see 90-day price history with percentile indicator.

**Test Coverage:**

```
✓ backend: test_price_history.py
  ├─ GET /paddles/{id}/price-history?days=90 returns correct data
  ├─ Percentile 20 calculation: finds lowest 20% of prices
  ├─ Data sorted by date (ascending)
  ├─ Handles missing data gracefully (returns available range)
  └─ Performance: < 200ms for 180 snapshots

✓ frontend: price-chart.test.tsx
  ├─ Chart renders with dynamic(..., { ssr: false })
  ├─ Tooltip displays on hover (no SSR errors)
  ├─ Line chart shows BRL currency format
  ├─ Legend visible and accessible
  └─ Responsive layout (mobile, tablet, desktop)

✓ E2E: price-history-chart.spec.ts (Wave 2+)
  ├─ Navigate to product detail page
  ├─ Chart loads and renders
  ├─ Hover tooltip appears with date + price
  ├─ No console errors
  └─ Percentile indicator visible
```

**Automated Commands:**
```bash
# Backend price history
pytest tests/test_price_history.py -xvs

# Frontend Recharts integration
npm run test -- --grep="price-chart"

# E2E visualization (Wave 2+)
npm run test:e2e -- e2e/price-history-chart.spec.ts
```

---

### R5.4: Email & Compliance

**Truth:** Users receive price alert emails with proper unsubscribe mechanism and FTC disclosure.

**Test Coverage:**

```
✓ backend: test_resend_email.py
  ├─ Email sends via Resend (mocked in tests)
  ├─ Subject: "Alerta de preço: {paddle_name}"
  ├─ List-Unsubscribe header present (RFC 8058)
  ├─ Unsubscribe link in email body
  ├─ React Email template renders without errors
  └─ No exceptions during send

✓ frontend: product page
  ├─ FTC disclosure visible above first affiliate link
  ├─ Disclosure text: "Affiliate Link" or badge
  ├─ High contrast for readability
  ├─ Mobile-accessible (not hidden on small screens)
  └─ No alignment with product description (per FTC rules)

✓ E2E: affiliate-disclosure.spec.ts (Wave 2+)
  ├─ Navigate to product detail page
  ├─ Screenshot product section
  ├─ Verify disclosure badge/text above first link
  ├─ Visual regression: compare against approved baseline
  └─ Accessibility: screen reader finds disclosure
```

**Automated Commands:**
```bash
# Backend email logic
pytest tests/test_resend_email.py -xvs

# Frontend compliance (manual or pixel-diff)
npm run test:e2e -- e2e/affiliate-disclosure.spec.ts
```

---

## Mocks & Fixtures

### Clerk Mock

```typescript
// frontend/__tests__/setup.ts
import { vi } from 'vitest';

export const mockClerkAuth = {
  userId: 'user_123',
  sessionId: 'sess_456',
  orgId: null,
};

vi.mock('@clerk/nextjs/server', () => ({
  auth: vi.fn(async () => mockClerkAuth),
  clerkMiddleware: vi.fn((cb) => cb),
}));

// Override in individual tests:
// vi.mocked(auth).mockResolvedValueOnce({ userId: null });
```

### Resend Mock

```python
# backend/tests/conftest.py
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_resend():
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {
            'id': 'email_abc123',
            'from': 'alerts@pickleiq.com',
            'to': 'user@example.com',
        }
        yield mock_send
```

### Price Data Fixtures

```python
# backend/tests/fixtures/price_data.py
SAMPLE_PRICES = [
    {'paddle_id': 1, 'date': '2026-03-01', 'price': 599.90},
    {'paddle_id': 1, 'date': '2026-03-08', 'price': 579.90},
    # ... 90 samples ...
]

PERCENTILE_20_PRICE = 489.90  # Expected P20 value
```

### FastAPI Test Client

```python
# backend/tests/conftest.py
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)
```

---

## Execution Plan

### Per-Task Sampling (Wave 1-3)

**Command:** Run after each plan completes
```bash
# Frontend
npm run test -- --watch=false

# Backend
pytest tests/test_price_alerts.py tests/test_price_history.py -q

# Time: ~25s
```

### Per-Wave Merge (before wave gate)

**Command:** Run before merging to staging
```bash
# Full suite with coverage
npm run test && pytest tests/ --cov=backend --cov-fail-under=80

# Time: ~60s
```

### Phase Gate (before /gsd:verify-work)

**Criteria:**
- [ ] All unit tests passing (Vitest + pytest)
- [ ] Backend coverage ≥ 80%
- [ ] E2E tests pass (Playwright, if implemented in Wave 2+)
- [ ] Manual check: Clerk login flow works
- [ ] Manual check: Price alert email received with headers intact
- [ ] Manual check: FTC disclosure visible on product page

---

## Coverage Targets

| Area | Target | Rationale |
|------|--------|-----------|
| Backend critical paths | ≥ 90% | Auth, email, price calc require high fidelity |
| Frontend components | ≥ 70% | UI rendering less critical than business logic |
| E2E smoke tests | 100% | Must-haves (login, alert, email) fully covered |

---

## Known Gaps (as of 2026-03-28)

### Missing Test Files
- [ ] `frontend/__tests__/product-metadata.test.ts` — WAVE 0
- [ ] `frontend/__tests__/product-schema.test.ts` — WAVE 0
- [ ] `frontend/__tests__/clerk-auth.test.ts` — WAVE 0
- [ ] `frontend/__tests__/price-chart.test.tsx` — WAVE 0
- [ ] `backend/tests/test_price_alerts.py` — WAVE 0
- [ ] `backend/tests/test_price_history.py` — WAVE 0
- [ ] `backend/tests/test_resend_email.py` — WAVE 0

### Missing Environment Setup
- [ ] `CLERK_SECRET_KEY` in `.env.local`
- [ ] `RESEND_API_KEY` in `.env.local`
- [ ] Database fixtures: pgvector test data, sample paddles

### Optional (Wave 2+)
- [ ] E2E: Playwright scripts (4 files)
- [ ] Visual regression baselines for affiliate disclosure

---

## Success Criteria

Phase 05 validation complete when:
- [ ] All 7 Wave 0 test files exist with proper structure
- [ ] All unit tests passing: `npm run test && pytest tests/ -q`
- [ ] Coverage ≥ 80% on backend: `pytest --cov-fail-under=80`
- [ ] No hydration mismatches in browser console
- [ ] E2E smoke tests pass (Wave 2+): Clerk login, price alert email
- [ ] FTC disclosure visible on product pages
- [ ] Resend emails sent with List-Unsubscribe header

---

## References

- [Vitest Documentation](https://vitest.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Testing Library Best Practices](https://testing-library.com/docs/)
- [Playwright Testing](https://playwright.dev/docs/intro)
- [RFC 8058: Unsubscribe Header](https://tools.ietf.org/html/rfc8058)
- [FTC Affiliate Disclosure Guide](https://www.ftc.gov/business-guidance/dotcom-disclosures)
