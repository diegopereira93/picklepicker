# Phase 21 — Price Alerts CRUD Endpoint

## Overview

Implemented POST and GET endpoints for price alerts functionality in PickleIQ's FastAPI backend. The `price_alerts` table already existed in the database schema, so this phase focused on API layer implementation.

## Implementation

### 1. Pydantic Schemas (`backend/app/schemas.py`)

Added two new Pydantic models:

- **`PriceAlertCreate`**: Request schema for creating a price alert
  - `user_id`: int (required)
  - `paddle_id`: int (required)
  - `target_price_brl`: float (required)

- **`PriceAlertResponse`**: Response schema for a price alert
  - `id`: int
  - `user_id`: int
  - `paddle_id`: int
  - `target_price_brl`: float
  - `is_active`: bool
  - `created_at`: Optional[datetime]

### 2. API Endpoint (`backend/app/api/price_alerts.py`)

Created new FastAPI router with two endpoints:

#### POST `/api/v1/price-alerts`
- Creates a new price alert
- Checks for duplicate alerts (same `user_id` + `paddle_id` with `is_active=true`)
- Returns `409 Conflict` if duplicate exists
- Returns `201 Created` with the new alert on success
- Uses parameterized queries with psycopg for SQL injection prevention

#### GET `/api/v1/price-alerts`
- Lists all price alerts for a specific user
- Requires `user_id` query parameter
- Returns alerts ordered by `created_at DESC`
- Returns empty array if no alerts found

### 3. Router Registration (`backend/app/main.py`)

- Imported `price_alerts_router` from `app.api.price_alerts`
- Registered router at `/api/v1` prefix
- Maintains consistent routing pattern with other endpoints

### 4. Tests (`backend/tests/test_price_alerts.py`)

Created comprehensive test suite with 5 test cases:

1. **`test_create_price_alert__201`**: Verifies successful alert creation returns 201
2. **`test_create_price_alert__missing_fields__422`**: Validates required fields
3. **`test_create_price_alert__duplicate__409`**: Confirms duplicate detection
4. **`test_list_price_alerts__200`**: Verifies alert listing works
5. **`test_list_price_alerts__missing_user_id__422`**: Validates required query param

Used custom mock fixture to simulate database behavior:
- Tracks duplicate existence state
- Handles sequential `fetchone()` calls (duplicate check + INSERT RETURNING)
- Resets state between tests

## Verification

### Backend Tests
- All 5 new price alerts tests: **PASSED** ✅
- Total backend tests: 187 passed, 11 failed
- Note: 11 pre-existing failures in unrelated tests (affiliate_clicks, chat, e2e) - not caused by this implementation

### Frontend Tests
- All 179 frontend tests: **PASSED** ✅
- No regression from backend changes

### API Contract
```
POST /api/v1/price-alerts
Request: {"user_id": 1, "paddle_id": 1, "target_price_brl": 500.0}
Response (201): {"id": 1, "user_id": 1, "paddle_id": 1, "target_price_brl": 500.0, "is_active": true, "created_at": "2026-04-12T00:00:00Z"}

GET /api/v1/price-alerts?user_id=1
Response (200): [{"id": 1, "user_id": 1, "paddle_id": 1, "target_price_brl": 500.0, "is_active": true, "created_at": "2026-04-12T00:00:00Z"}]

POST /api/v1/price-alerts (duplicate)
Response (409): {"detail": "Price alert already exists for this user and paddle"}
```

## Files Changed

1. `backend/app/schemas.py` — Added `PriceAlertCreate` and `PriceAlertResponse` schemas
2. `backend/app/api/price_alerts.py` — New file with POST and GET endpoints
3. `backend/app/main.py` — Registered `price_alerts_router`
4. `backend/tests/test_price_alerts.py` — New test file with 5 test cases

## Design Decisions

1. **Duplicate Detection Logic**: Checked at API level before INSERT for better error handling. Could alternatively use UNIQUE constraint with `user_id`, `paddle_id`, and `is_active` at DB level.
2. **No ORM**: Used raw psycopg with parameterized queries, following existing project conventions.
3. **Response Schema**: Returns all fields including `is_active` (currently always true) for future extensibility.

## Next Steps

Phase 22 will implement affiliate click tracking persistence (database + endpoint).
