# Phase 21: Price Alerts CRUD

**Status:** Planning phase
**Milestone:** v1.7.0 — Backend API for Frontend Redesign
**Dependencies:** Phase 20 complete
**Created:** 2026-04-07

## Goal

Create database table and POST endpoint for price alerts modal. Users can subscribe to price drop notifications.

## Requirements (from ROADMAP.md)

| # | Requirement | Description |
|---|-------------|-------------|
| PRICE-01 | price_alerts table | Add `id`, `paddle_id`, `target_price`, `email`, `created_at`, `notified_at` |
| PRICE-02 | POST /price-alerts | Create endpoint with validation |
| PRICE-03 | Pydantic schemas | PriceAlertCreate, PriceAlertResponse |
| PRICE-04 | Tests | Valid, invalid email, non-existent paddle, duplicate handling |

## Success Criteria

1. `POST /price-alerts` creates alert and returns 201
2. Duplicate alerts return 409 Conflict
3. Worker can query: `SELECT * FROM price_alerts WHERE notified_at IS NULL`
4. All tests pass (backend)

## Commit Strategy

4 atomic commits:
1. `feat(phase21): add price_alerts table to schema`
2. `feat(phase21): add PriceAlertCreate and PriceAlertResponse schemas`
3. `feat(phase21): add POST /price-alerts endpoint`
4. `test(phase21): add price-alerts endpoint tests`

## TDD Approach

| Phase | Test → Implementation |
|-------|----------------------|
| Red | Test expects 201 → run (fails) |
| Green | Implement endpoint → run (passes) |
| Refactor | Add 409 duplicate test → implement duplicate check |