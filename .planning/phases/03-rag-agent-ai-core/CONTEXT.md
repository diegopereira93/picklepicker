# Phase 3 Planning Context

**Phase:** 03-rag-agent-ai-core
**Status:** PLAN CREATED & VERIFIED
**Date:** 2026-03-27
**Planning Approach:** Wave 1 Checkpoint Mode (default for multi-plan phases)

---

## Phase 3 Goal

Deliver a functional **RAG Agent** that:
1. Recommends top-3 paddles via **conversational Portuguese AI**
2. Uses **pgvector semantic search** with user profile filtering (skill level, budget, stock)
3. Meets **latency SLA: P95 < 3s**, time-to-first-token < 800ms
4. Handles **model quality via eval gate** (Groq OSS ≥4.0 score, fallback Claude Sonnet)
5. Provides **observability:** Langfuse traces + degraded mode fallback

---

## Requirements Mapping

| Requirement | Wave | Task | Success Criterion |
|-------------|------|------|-------------------|
| R3.1 — Eval gate (10 PT-BR queries → model selection) | 1 | 1.1 | Avg score ≥4.0 → Groq, else Claude Sonnet |
| R3.2 — POST /chat SSE streaming with top-3 recommendations | 3 | 3.1 | SSE events (recommendations, reasoning, done) emitted |
| R3.3 — Metric translation (swingweight/twistweight → Portuguese) | 2 | 2.1 | translate_metrics() tested on 5+ spec combinations |
| R3.4 — Latency < 3s, Redis cache, Langfuse, degraded mode | 4,5 | 4.1, 4.2, 5.1, 3.1 | P95 measured <3s, cache hits <200ms, degraded triggers @8s |

---

## Wave Breakdown

### Wave 1: Model Eval Gate + Agent Skeleton (CHECKPOINT)

**Focus:** Determine which LLM to use (Groq vs Claude Sonnet) based on quality eval.

**Deliverables:**
- `backend/app/agents/eval_gate.py` — Runs 10 Portuguese queries, scores 1-5, selects model
- `backend/app/agents/rag_agent.py` — Basic RAG search: pgvector + SQL filters + affiliate URL population
- `backend/data/eval_results.json` — Documented eval outcome (queries, scores, selected model)

**Tests:** 11 (eval_gate: 5, agent: 6)

**Checkpoint Gate:** Human approval required:
- [ ] eval_results.json shows avg score ≥4.0 OR <4.0 with Claude Sonnet selected
- [ ] rag_agent.py filters on (skill_level, budget_brl, in_stock)
- [ ] Affiliate URLs constructed server-side, not by LLM
- [ ] All 11 tests passing

---

### Wave 2: Prompt Engineering + Portuguese Metric Translation

**Focus:** Build Portuguese system prompt + metric translation function.

**Deliverables:**
- `backend/app/prompts/system.md` — System prompt in Portuguese (conversational, accurate specs)
- `backend/app/agents/metrics.py` — Function `translate_metrics()` converting swingweight/twistweight → plain language
- `backend/app/agents/metric_mappings.json` — Swingweight ranges, twistweight ranges, core thickness, face materials → Portuguese explanations

**Tests:** 5 (metric translation, Portuguese validation)

**Success:** Metric translation produces consistent, idiomatic Portuguese (validated manually or via LLM-as-judge).

---

### Wave 3: POST /chat SSE Endpoint + Filtering

**Focus:** Implement FastAPI endpoint returning Server-Sent Events with recommendations.

**Deliverables:**
- `backend/app/api/chat.py` — POST /chat endpoint:
  - Input: `{ session_id, messages, profile: { level, style, budget_max } }`
  - Filters: `in_stock=true, price_brl ≤ budget_max, skill_level match`
  - pgvector search: cosine similarity, threshold 0.65, top-5 candidates
  - Output: SSE stream with events `{ type: "recommendations" | "reasoning" | "done" }`

**Deliverables (cont.):**
- `backend/app/agents/rag_agent.py` — Enhanced with `filter_and_rank()` + reranking logic
- Degraded mode: If LLM timeout > 8s, return SSE `{ type: "degraded", paddles: [top-3 by price] }`

**Tests:** 4 (SSE format, events, filtering, degradation)

**Success:** Streaming response arrives in <3s P95, degraded mode activates on timeout.

---

### Wave 4: Redis Caching + Latency Budget Tracking

**Focus:** Reduce redundant pgvector calls, track P95 latency.

**Deliverables:**
- `backend/app/cache.py` — Redis client:
  - Deterministic key: MD5(profile_hash + query)
  - Get/set with 3600s TTL
  - Graceful degradation if Redis unavailable
- `backend/app/middleware/latency.py` — Middleware tracking P95 latency:
  - pgvector time, context assembly time, LLM time, overhead time
  - Log to stdout + Langfuse (Wave 5)

**Tests:** 8 (cache get/set, TTL, key determinism, P95 calculation, budget enforcement)

**Success:** Cache hits return in <200ms, P95 latency <3s over 100 requests.

---

### Wave 5: Langfuse Observability + Production Readiness

**Focus:** Complete observability + final checks before execution.

**Deliverables:**
- `backend/app/observability.py` — Langfuse integration:
  - Log traces: model, tokens, cost, cache_hit, degraded_mode flags, latency
  - Startup/shutdown hooks for batch flush
- `backend/tests/test_production.py` — Production readiness checks:
  - All env vars present (OPENAI_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, REDIS_URL)
  - DB accessible, pgvector index present
  - Concurrent request handling (10 simultaneous chats)

**Tests:** 10 (Langfuse metadata, token logging, flush, E2E happy path, degraded mode, production checks)

**Success:** Langfuse dashboard shows traces, 80%+ code coverage, ready for staging deployment.

---

## Dependencies & Blockers

### Phase 2 Dependencies (All Complete ✓)
- pgvector index (HNSW) on `paddle_embeddings`
- FastAPI framework + Pydantic models
- PostgreSQL schemas + embeddings populated
- GET /paddles endpoints functional

### External Services (User Setup Required)
- [ ] OpenAI API key (eval gate + chat completions)
- [ ] Langfuse public/secret keys (observability)
- [ ] Redis (optional but recommended; graceful degradation if unavailable)
- [ ] Groq API key (only if eval score ≥4.0)

### Internal Dependencies
- Wave 1 checkpoint must pass before Waves 2-5 proceed
- Waves 2-3 independent (can run in parallel if desired)
- Wave 4 depends on Wave 3 completion
- Wave 5 depends on Wave 4 completion

---

## Risk Mitigation

| Risk | Mitigation | Verification |
|------|-----------|--------------|
| Model selection wrong (eval gate score miscalibrated) | Eval 10 representative PT-BR queries, threshold at 4.0 (exact rubric in Wave 1) | eval_results.json reviewed by human |
| LLM latency exceeds 3s | Timeout at 8s + degraded mode fallback + Redis cache (3600s TTL) + P95 tracking via middleware | latency.py tests + Wave 4 benchmark |
| Missing paddle specs → confusing recommendations | translate_metrics() handles NULL specs gracefully ("não disponível") | metrics.py unit tests + manual PT-BR review |
| Redis unavailable → performance degrades | Cache degrades to fresh pgvector call (always works, just slower) | cache.py resilience tests |
| Langfuse API down → chat blocks | Async batch flush, non-blocking error logging (chat continues even if Langfuse fails) | observability.py tests + production check |

---

## Success Metrics

- ✅ Model selected (Groq OR Claude Sonnet documented in eval_results.json)
- ✅ Chat endpoint streaming (SSE format verified)
- ✅ Latency budget met (P95 <3s over 100 requests)
- ✅ Metric translation accurate (5+ spec combos, Portuguese validation)
- ✅ Degraded mode working (8s LLM timeout → fallback to top-3)
- ✅ Observability complete (Langfuse traces logged)
- ✅ 38+ tests passing (80%+ code coverage)

---

## Execution Path

1. **Start Wave 1:** `/gsd:execute-phase 03-rag-agent-ai-core`
2. **Wave 1 Checkpoint:** After 11 tests pass, pause for human approval
3. **Continue Waves 2-5:** `/gsd:execute-phase 03-rag-agent-ai-core --wave 2-5`

---

## Notes

- **Prompt Language:** All system prompts in Portuguese (PT-BR standard for BR market)
- **Model Selection:** Groq API ($0.59/MTok) preferred if quality sufficient; Claude Sonnet fallback
- **Cache TTL:** 3600s chosen to match 24h crawler cycle (cleared on new data)
- **Affiliate URLs:** Constructed server-side in rag_agent.py, never by LLM (compliance)
- **Degraded Mode:** Activated at 8s timeout; returns top-3 by price without LLM explanation (revenue-positive fallback)
