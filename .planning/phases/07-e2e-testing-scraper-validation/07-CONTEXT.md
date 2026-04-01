# v1.1 Milestone Context

**Version:** 1.1
**Status:** Planning
**Start Date:** 2026-03-29
**Goal:** Validate production-readiness of scraper suite and firecrawl integration through comprehensive end-to-end testing

---

## Why v1.1 Exists

v1.0 shipped 2026-03-28 with 6 production phases complete. Phase 2 (Full Data Pipeline) implemented 3 scrapers:
- **Brazil Pickleball Store** — Firecrawl `/extract` with retry/backoff
- **Drop Shot Brasil** — Additional BR retailer via Firecrawl
- **Mercado Livre** — ML API search + affiliate integration

**Risk:** Scrapers not validated against real retailers under load. Firecrawl integration needs local E2E validation before scaling to production cron schedule.

**v1.1 Phase 1** de-risks this by validating all scrapers locally with:
- Real retailer connectivity (staging mode where possible)
- Firecrawl `/extract` behavior and error handling
- Data integrity and deduplication quality
- Performance under concurrent requests

---

## Phase 1: E2E Testing & Scraper Validation

**Goal:** Validate all 3 scrapers (Brazil Store, Drop Shot Brasil, Mercado Livre) + Firecrawl integration work correctly locally with staging/test data.

**Success Criteria** (what must be TRUE):
1. E2E test suite covers all 3 scrapers with ≥ 80% code path coverage
2. Each scraper tested against real retailer URL (or staging mock) with schema validation
3. Firecrawl `/extract` error modes documented and handled (timeout, rate limit, parse failure)
4. Data integrity verified: schema compliance, dedup matching, affiliate URL formatting
5. Performance validated: crawl times < 30s per retailer, no memory leaks

**Constraints:**
- Work locally without CI/CD (tests run via `pytest`, `pytest-e2e`, or shell script)
- No production data touched
- Can mock external APIs (Firecrawl) if needed for deterministic testing
- Must document retry/backoff behavior

**Why this scope:**
- Phases 1-6 shipped with minimal E2E coverage of scrapers
- Production cron schedule (Phase 2, plan 02-03) will depend on scraper reliability
- Local validation gates before GitHub Actions CI/CD rollout

---

## Dependencies & Constraints

**Depends on:** v1.0 complete (all phases shipped, infrastructure stable)

**Blockers to resolve:**
- [ ] Drop Shot Brasil scraper current state (modified but unreviewed)
- [ ] Local test environment setup for staging/mock data

**Out of scope v1.1:**
- Scaling scrapers to production cron
- Optimizing crawl latency beyond 30s baseline
- Supporting additional retailers (Phase 2 expansion)
- Database migrations or schema changes

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Scraper coverage | ≥ 80% of code paths | pytest --cov output |
| Test suite size | ≥ 12 test cases | Test file line count |
| Data quality | 100% schema compliance | Schema validation in test assertions |
| Performance | <30s per retailer | Test execution time |
| Documentation | All error modes covered | README or docstrings in test files |

---

## Next Steps

1. **Plan Phase 1** → Create detailed plans for E2E test infrastructure
2. **Execute plans** → Implement test suite, fixtures, and validation logic
3. **Verify** → All tests passing, coverage ≥ 80%, documentation complete
4. **Ship** → PR to `master`, code review, merge
5. **Move to Phase 2** → Plan next v1.1 work (scaling, optimization, new retailers)
