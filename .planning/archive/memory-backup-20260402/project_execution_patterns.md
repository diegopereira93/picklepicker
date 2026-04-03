---
name: GSD Execution Patterns — Validated 2026-03-27 to 2026-03-28
description: Confirmed execution patterns across Phases 3, 4, 5 — Wave 1 Checkpoint, parallel sub-plans, /ship workflow
type: project
---

## Wave 1 Checkpoint Mode — Validated Pattern

**Validation Date:** 2026-03-27 (Phase 2 → Phase 3)

Pattern confirmed effective across Phase 2 and Phase 3 execution:
- Execute Wave 1 to completion, pause for user verification
- User reviews WAVE-1-CHECKPOINT.md summary
- User approves continuation → execute Waves 2-N with `/gsd:execute-phase --auto`
- Prevents context explosion, enables feedback loops, allows decision points

**Benefits realized:**
- Wave 1 eval gate (Phase 3) showed critical decision point: Groq vs Claude → Groq selected based on 4.0 threshold
- Checkpoint allowed user to adjust course before waves 2-5 implementation
- Clear stopping point if issues emerge; no revert needed on full phase
- Parallel execution within waves maintained (02-01 + 02-02, Wave 1 tests in parallel)

**Pattern applies to:** Multi-plan phases (3+ plans, 2+ waves). Phase 3 used, Phase 4 did not need (single wave per sub-plan), Phase 5 used planning verification (not execution checkpoint).

---

## Parallel Sub-Plan Execution — Validated Pattern

**Validation Date:** 2026-03-27 (Phase 4)

Phase 4 executed 5 sub-plans (04-01 through 04-05) in parallel when dependencies allowed:
- Sub-plans with no cross-dependencies: executed in parallel
- Sub-plans with sequential dependency: coordinated via shared VERIFICATION.md checks
- Each sub-plan: independent test suite, independent PR commit
- Integration verified via: full test suite run + production build check

**Results:**
- Execution time: ~90 min total (would be 5×20=100 min if sequential)
- Parallel efficiency: ~11% savings; worth it for code organization
- Integration risk: Mitigated by final build + full test suite (61 tests)
- Build failures: Caught and auto-fixed (3 issues fixed in aab970f commit)

**Pattern applies to:** Multi-sub-plan phases where sub-plans have independent scope (UI components, API routes, test suites). Phase 4 validated; applicable to Phase 6+.

---

## /ship Fully Automated Workflow — Validated Pattern

**Validation Date:** 2026-03-27 (Post-Phase 2, 3, 4, 5 execution)

Workflow: `npm run build` → tests pass → `/ship` → version bump + CHANGELOG + PR creation

**Automation confirmed:**
1. Version bump auto-decided:
   - PATCH: 50-7171 lines (automatic, no prompt)
   - MINOR/MAJOR: Prompts user (not used in recent phases — all PATCH)
2. CHANGELOG auto-generated from diff (git-based)
3. TODOS.md auto-updated (completed items marked with version)
4. PR created with comprehensive body:
   - Test coverage summary
   - Review findings
   - Verification results
   - Link to shipped code
5. No interactive prompts mid-workflow

**Benefits:**
- Consistent commit message format across all phases
- CHANGELOG always in sync with merged code
- Version tracking automatic (no manual SemVer mistakes)
- Pre-landing review catches issues before PR (e.g., Phase 4 integration fixes caught in review)

**Pattern applies to:** End of phase execution. Confirmed working for Phases 2, 3, 4, 5.

---

## Planning Blocker Detection — New Pattern

**Discovery Date:** 2026-03-28 (Phase 5 verification)

Before executing large phases (4+ plans), run plan verification to catch:
1. **Wave dependency serialization issues** — Phase 5 Plan 02 incorrectly depended on Plan 01, forcing unnecessary Wave 2
2. **Missing test artifacts** — Phase 5 VALIDATION.md missing; Wave 0 test files listed but not created
3. **Version control anti-patterns** — Phase 5 Plan 01 listed .env.local (secrets) instead of .env.example

**Process:**
- gsd-plan-checker verifies wave structure before execution
- Blocks execution if critical dependencies wrong
- Surface for user decision: fix before running or proceed as-is
- Phase 5: Fixed both blockers pre-execution, improved efficiency and clarity

**Benefits:**
- Catches architectural issues before 10-14 hour phase execution
- Reduces iteration loops mid-phase
- Forces clarity on test infrastructure upfront

**Pattern applies to:** All phases 3+. Recommend running `/gsd:plan-phase --verify` or `/gsd:validate-phase` for multi-plan phases.

---

## Decision Point Pattern — Validated in Phase 3

**Validation Date:** 2026-03-27

**Pattern:** Wave 1 eval gate serves as decision checkpoint.

Phase 3 Wave 1 eval gate: Tested Groq (Llama 3.3 70B) vs Claude Sonnet on 10 PT-BR pickleball queries.
- **Result:** Groq scored ≥4.0 on all queries (selected)
- **Implication:** Waves 2-5 optimized for Groq (streaming, token counting, cost tracking)
- **Decision:** User could have pivoted to Claude Sonnet (slower, different token counts) but Groq met threshold

**Benefit:** Defers expensive decision (LLM choice) until data from Wave 1 eval available. Prevents implementing entire phase on wrong model.

**Pattern applies to:** Phases with model/infrastructure choices. Phase 3 only so far, but recommend for Phase 6 if deployment strategy needs testing (Vercel vs Railway vs self-hosted).

---

## Integration Fix Pattern — Phase 4 Auto-Fixes

**Discovery Date:** 2026-03-27 (Post Phase 4 execution)

During production build, 3 issues were caught and auto-fixed:
1. Unused `UIPartLike` interface → removed
2. Type inference on `id` variable → explicit `string` annotation
3. `msg.content` property doesn't exist on `UIMessage` → removed fallback

**Root cause:** TSConfig `strict: true` caught issues missed by local eslint. Production build more strict than dev.

**Prevention:** Run `npm run build` before `/ship` (part of standard workflow). All 3 issues auto-fixed in single aab970f commit.

**Lesson:** Integration builds catch issues that unit tests miss. Recommend running build + full test suite before /ship on complex phases.

---

## Blocker Recovery Pattern — Phase 5 Planning

**Date:** 2026-03-27 to 2026-03-28

Phase 5 verification (gsd-plan-checker) identified 2 blockers:
1. **Wave serialization:** Plan 02 incorrectly depended on Plan 01 → Fixed by editing depends_on
2. **Missing VALIDATION.md:** Plans assumed test files existed → Confirmed tests exist, documented in VALIDATION.md

**Recovery process:**
- Blocker identified in plan verification (before execution started)
- User educated on issue + fix
- Plans edited and reverified
- Execution proceeded without delays

**Time saved:** 30-60 min (avoided re-planning mid-execution) + prevented test failures

**Pattern applies to:** All plan-phase workflows. gsd-plan-checker → identify blockers → fix plans → execute is faster than execute → debug → replan.

---

## Summary of Validated Patterns (as of 2026-03-28)

| Pattern | Validated In | Status | Confidence |
|---------|--------------|--------|------------|
| Wave 1 Checkpoint Mode | Phase 2, Phase 3 | ✅ Effective | High — used successfully for large phases |
| Parallel Sub-Plan Execution | Phase 4 | ✅ Effective | Medium — 5 sub-plans executed, integration verified |
| /ship Fully Automated | Phase 2, 3, 4, 5 | ✅ Effective | High — consistent across all phases |
| Plan Blocker Detection | Phase 5 | ✅ Effective | Medium — caught 2 blockers pre-execution |
| Wave 1 Decision Point | Phase 3 | ✅ Effective | Medium — Groq eval gate deferred LLM choice |
| Integration Build Catch | Phase 4 | ✅ Effective | Medium — 3 issues caught + fixed |
| Blocker Recovery | Phase 5 | ✅ Effective | Medium — prevented mid-execution delays |

---

## Recommended Workflow for Phase 6+

1. **Plan phase:** `/gsd:plan-phase N --auto` → generates PLAN.md + CONTEXT.md
2. **Verify plan:** `/gsd:validate-phase N` → gsd-plan-checker runs, identifies blockers
3. **Fix blockers:** Edit PLAN.md, re-run validation until green
4. **Execute Wave 1:** `/gsd:execute-phase N` (if multi-wave) or `/gsd:execute-phase N --auto` (if single wave)
5. **Review checkpoint:** (if Wave 1 Checkpoint Mode) → user reads WAVE-1-CHECKPOINT.md
6. **Continue execution:** `/gsd:execute-phase N --auto` → run remaining waves
7. **Ship phase:** `/ship` → fully automated PR creation, version bump, CHANGELOG
8. **Build verification:** Production build clean before PR landing

**Total time for 5-plan phase:** ~10-15 hours (Phases 3-5 benchmarks)

