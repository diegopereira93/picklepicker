# Phase 3 — Wave 1 Checkpoint

**Phase:** 03-rag-agent-ai-core (RAG Agent & AI Core)
**Wave:** 1 (Model Eval Gate + Agent Skeleton)
**Status:** PENDING EXECUTION
**Checkpoint Gate:** BLOCKING (must approve before Waves 2-5)

---

## Wave 1 Deliverables (Pre-Checkpoint)

After executing Wave 1 tasks (1.1, 1.2), verify the following:

### Task 1.1: Model Eval Gate

**Files Created:**
- [ ] `backend/app/agents/eval_gate.py` — Script running 10 Portuguese queries against both Groq + Claude Sonnet
- [ ] `backend/data/eval_results.json` — JSON with structure:
  ```json
  {
    "eval_date": "2026-03-27T...",
    "queries": [ { "id": 1, "pt_query": "...", "groq_score": 4.5, "claude_score": 4.3 }, ... ],
    "groq_avg": 4.25,
    "claude_avg": 4.15,
    "selected_model": "groq",
    "reasoning": "Groq avg score 4.25 >= 4.0 threshold"
  }
  ```

**Quality Checks:**
- [ ] 10 queries cover skill_level (iniciante/intermediário/avançado) × style (controle/potência/equilibrado) × budget (R$400/700/1200)
- [ ] Score rubric applied consistently (clarity, technical accuracy, Portuguese tone, analogies)
- [ ] Average score ≥4.0 → Groq selected (cost-effective)
- [ ] Average score <4.0 → Claude Sonnet selected (quality guaranteed)
- [ ] Human reviewer confirms rubric application (spot-check 2-3 queries manually)

**Expected Test Results:**
```
test_eval_gate.py::test_loads_10_queries ✓
test_eval_gate.py::test_scores_in_range_1_to_5 ✓
test_eval_gate.py::test_avg_score_calculated_correctly ✓
test_eval_gate.py::test_groq_selected_when_avg_gte_4_0 ✓
test_eval_gate.py::test_claude_fallback_when_avg_lt_4_0 ✓
─────────────────────────────────────────────────────
5/5 tests passing
```

---

### Task 1.2: RAG Agent Skeleton

**Files Created:**
- [ ] `backend/app/agents/rag_agent.py` — Core agent logic:
  - `search_paddles(profile, query_embedding)` — pgvector search with filters
  - `filter_by_profile(results, profile)` — SQL filters on (skill_level, budget_brl, in_stock)
  - `build_affiliate_urls(paddles)` — Server-side URL construction (never by LLM)
  - `apply_reranking(candidates)` — Top-5 → top-3 via scoring

**Quality Checks:**
- [ ] SQL filters correctly applied:
  - `WHERE in_stock = true`
  - `WHERE price_brl <= profile.budget_max`
  - `WHERE skill_level = ANY(profile.applicable_levels)`
- [ ] pgvector search uses cosine similarity (vector_cosine_ops)
- [ ] Similarity threshold 0.65 enforced (candidates below threshold flagged)
- [ ] Affiliate URLs contain required parameters: paddle_id, retailer, session_id
- [ ] No user-visible URLs leaked from LLM (all URLs from backend)

**Expected Test Results:**
```
test_rag_agent.py::test_search_paddles_cosine_similarity ✓
test_rag_agent.py::test_filter_by_skill_level ✓
test_rag_agent.py::test_filter_by_budget_excludes_expensive ✓
test_rag_agent.py::test_filter_by_in_stock ✓
test_rag_agent.py::test_build_affiliate_urls_server_side ✓
test_rag_agent.py::test_apply_reranking_top_3 ✓
─────────────────────────────────────────────────────
6/6 tests passing
```

---

## Checkpoint Gate Criteria

✅ **All 11 tests passing** (5 eval_gate + 6 rag_agent)

✅ **eval_results.json created** with:
- Model selected (Groq OR Claude Sonnet)
- Avg score documented
- Queries + scores visible for review

✅ **rag_agent.py verified** to:
- Filter on skill_level, budget_brl, in_stock
- Search via pgvector cosine similarity
- Build affiliate URLs server-side
- Apply reranking to top-3

✅ **No integration with LLM yet** (Wave 1 is skeleton only)

---

## Decision Points at Checkpoint

### Decision 1: Model Selection
**If:** eval_results.json shows Groq avg ≥4.0
**Then:** Use Groq API (`model="mixtral-8x7b-32768"`)
**Else:** Use Claude Sonnet (`model="claude-3-5-sonnet-20241022"`)

**Owner:** Human reviewer (Diego)

### Decision 2: Proceed to Waves 2-5?
**Condition:** 11/11 tests pass + model selection documented
**Action:** Approve → proceed to Wave 2 (Prompt Engineering)

---

## Rollback Criteria

Rollback Wave 1 if:
1. ❌ Any test failing after legitimate rework
2. ❌ eval_results.json inconsistent (scores not in 1-5 range, queries not representative)
3. ❌ rag_agent.py missing required filters (e.g., in_stock not checked)

**Rollback action:** Re-run Wave 1 tasks with corrections, re-test.

---

## Next Steps (Post-Checkpoint Approval)

Once checkpoint approved:

```bash
# Proceed to Waves 2-5
/gsd:execute-phase 03-rag-agent-ai-core --wave 2-5
```

Wave 2 will integrate the eval gate + LLM selection into the chat endpoint.

---

## Approval Checklist

- [ ] eval_results.json reviewed (model selection reasonable)
- [ ] 11/11 tests passing in CI/CD
- [ ] rag_agent.py filters verified (manual code review)
- [ ] No hardcoded URLs or LLM calls in Wave 1
- [ ] Ready to proceed to Wave 2

**Approver:** Diego
**Date Approved:** [pending execution]
