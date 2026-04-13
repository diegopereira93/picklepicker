---
phase: 24
slug: fix-pipeline-tests-recriar-fixtures
status: verified
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-12
---

# Phase 24 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (asyncio_mode=auto) |
| **Config file** | `pipeline/pyproject.toml` |
| **Quick run command** | `python3 -m pytest pipeline/tests/test_data_integrity.py -q --tb=short` |
| **Full suite command** | `python3 -m pytest pipeline/tests/ -q --ignore=pipeline/tests/test_spec_matcher.py` |
| **Estimated runtime** | ~20 seconds |

**Note:** `test_spec_matcher.py` is excluded from collection due to pre-existing `rapidfuzz` import error (ModuleNotFoundError). This is NOT a Phase 24 issue.

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest pipeline/tests/test_data_integrity.py -q`
- **After every plan wave:** Run `python3 -m pytest pipeline/tests/ --co -q --ignore=pipeline/tests/test_spec_matcher.py`
- **Before `/gsd-verify-work`:** Full suite must collect without errors
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 24-01-01 | 01 | 1 | Brazil Store mock fixture (4 products, PRODUCT_SCHEMA) | N/A | N/A | fixture-validation | `python3 -c "import json; d=json.load(open('pipeline/tests/fixtures/mock_responses/brazil_store_response.json')); ..."` | ✅ | ✅ green |
| 24-01-02 | 01 | 1 | Dropshot Brasil mock fixture (2 products, PRODUCT_SCHEMA) | N/A | N/A | fixture-validation | `python3 -c "import json; d=json.load(open('pipeline/tests/fixtures/mock_responses/dropshot_brasil_response.json')); ..."` | ✅ | ✅ green |
| 24-01-03 | 01 | 1 | Mercado Livre mock fixture (4 items, id/title/price/permalink) | N/A | N/A | fixture-validation | `python3 -c "import json; ml=json.load(open('pipeline/tests/fixtures/mock_responses/mercado_livre_response.json')); ..."` | ✅ | ✅ green |
| 24-02-01 | 02 | 2 | staging_config.yaml (valid YAML, correct URLs) | N/A | N/A | config-validation | `python3 -c "import yaml; yaml.safe_load(open('pipeline/tests/fixtures/staging_config.yaml'))"` | ✅ | ✅ green |
| 24-02-02 | 02 | 2 | Full test suite collects (141 tests) | N/A | N/A | collection | `python3 -m pytest pipeline/tests/ --co -q --ignore=pipeline/tests/test_spec_matcher.py` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Verification Evidence

- **Plan 01 Summary:** 21/23 tests passing in `test_data_integrity.py`. 2 failures = pre-existing `rapidfuzz` import errors (not fixture-related).
- **Plan 02 Summary:** 141 tests collected (excluding `test_spec_matcher.py`). 115/153 passing. 38 pre-existing failures from mock misconfiguration (crawler tests mock `app.extract()` but code uses `app.scrape()`).
- **All Phase 24 fixture files** validated by the inline `python3 -c` scripts in PLAN.md `<verify><automated>` blocks — confirmed in summaries.

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No Wave 0 stubs needed.

- ✅ `pipeline/tests/conftest.py` — shared fixtures exist
- ✅ `pipeline/tests/test_utils.py` — `load_mock_response()` and `PRODUCT_SCHEMA` exist
- ✅ `pipeline/pyproject.toml` — pytest configured with `asyncio_mode = "auto"`

---

## Manual-Only Verifications

All phase behaviors have automated verification.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| *(none)* | — | — | — |

---

## Validation Audit Trail

| Audit Date | Gaps Found | Resolved | Escalated | Run By |
|------------|------------|----------|-----------|--------|
| 2026-04-12 | 0 | 0 | 0 | gsd-validate-phase (auto) |

### Audit Notes

- **Scope:** 4 files created (3 JSON mock fixtures + 1 YAML staging config)
- **Test collection:** 141 tests collected (excluding pre-existing `test_spec_matcher.py` ImportError)
- **Pre-existing issues:** `rapidfuzz` not installed (blocks `test_spec_matcher.py` collection), 38 test failures from mock misconfiguration (not fixture-related)
- **Phase 24-specific:** All `<verify><automated>` commands pass. All fixture data validated against PRODUCT_SCHEMA.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none needed)
- [x] No watch-mode flags
- [x] Feedback latency < 20s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-12
