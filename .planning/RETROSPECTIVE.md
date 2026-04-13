# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.2.0 — Launch Readiness: Testes & Correções Críticas

**Shipped:** 2026-04-13
**Phases:** 4 (24-27) | **Plans:** 4 | **Commits:** 26 | **Timeline:** 1 day

### What Was Built
- Pipeline test suite restored (38 failures → 146+ passing, mock updates for scrape-based crawlers)
- Frontend test suite stabilized (179/179 Vitest passing after quiz widget rewrites)
- Playwright E2E test suite created from scratch (23 tests, 5 spec files)
- Backend deprecation fixes (datetime.utcnow → datetime.now(timezone.utc))
- Project documentation generated (7 canonical docs, 2,108 lines)
- Developer onboarding improved (backend/.env.example created)

### What Worked
- **Parallel agent execution** — Multiple explore/deep/oracle agents ran simultaneously, cutting total time
- **Oracle verification gates** — 3 independent Oracle sessions caught issues (E2E selectors, missing .env.example) before final delivery
- **Fix mocks, not crawlers** — Correct decision to update test mocks instead of reverting production crawler code
- **Direct execution for simple phases** — Phases 22, 23, 26, 27 executed directly in ultrawork loop without formal GSD planning overhead

### What Was Inefficient
- **gsd-doc-writer agents timed out** — 3 of 3 gsd-doc-writer agents got stuck (55min timeouts on large codebase). Fell back to writing category agents, then manual generation. Should have started with `writing` category agents.
- **GSD metadata drift** — Phases executed directly during ultrawork got SUMMARY.md files but no PLAN.md files, causing GSD tooling to show them as "pending" when they were actually complete
- **Oracle test count inaccuracy** — Oracle reported 134 backend tests (ran pytest without venv); actual count was 198. Must verify Oracle claims independently.
- **Debugging quiz test encoding** — 5+ commits debugging quiz test failures (cedilla encoding, button text matching). Could have been resolved faster with earlier codebase inspection.

### Patterns Established
- **Scrape-based crawlers** — Crawlers now use `app.scrape()` returning markdown, not `app.extract()` returning structured data. All pipeline tests must mock scrape-based patterns.
- **Playwright E2E** — E2E tests use selective CSS selectors with `role="radio"` for quiz options. Vitest config excludes `e2e/` directory.
- **Manual docs fallback** — For large codebases, documentation generation works better with `writing` category agents or inline generation than with specialized gsd-doc-writer agents.

### Key Lessons
1. **Verify Oracle output independently** — Oracle ran pytest without backend venv activated, reported wrong test counts. Always cross-check critical numbers.
2. **Large codebase docs = manual work** — gsd-doc-writer agents struggle with repos >20 files. Use `writing` category or inline generation instead.
3. **Match test mocks to current production code** — When crawlers change API surface (extract→scrape), tests must be updated simultaneously, not deferred.
4. ** ultrawork + GSD metadata gap** — Direct execution bypasses GSD planning, creating metadata gaps. Acceptable for time-critical execution, but requires manual cleanup in ROADMAP/STATE.

### Cost Observations
- **Agent mix:** ~60% Sisyphus-Junior (implementation), ~25% Oracle (verification), ~15% explore/librarian (research)
- **Oracle sessions:** 5 total (3 verified, 1 rejected with valid findings, 1 re-verification)
- **Notable:** The 3 cancelled gsd-doc-writer agents consumed ~2.75h of agent time with no usable output. Switching to manual generation for the remaining 4 docs was the right call.
- **Documentation:** 4 of 7 docs written inline (GETTING-STARTED, DEVELOPMENT, TESTING, DEPLOYMENT), 3 by agents (README, ARCHITECTURE, CONFIGURATION partial)

---

## Cross-Milestone Trends

| Milestone | Phases | Timeline | Agents Used | Key Pattern |
|-----------|--------|----------|-------------|-------------|
| v2.2.0 | 4 | 1 day | Oracle ×5, Sisyphus-Junior ×7, explore ×3 | Ultrawork direct execution + Oracle verification |
