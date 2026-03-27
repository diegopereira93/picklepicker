---
phase: 03-rag-agent-ai-core
plan: all
type: execute
wave: 1-5
depends_on: [02]
files_modified:
  - backend/app/agents/eval_gate.py
  - backend/app/agents/rag_agent.py
  - backend/app/prompts.py
  - backend/app/api/chat.py
  - backend/app/observability.py
  - backend/app/cache.py
  - backend/app/main.py
  - backend/tests/test_eval_gate.py
  - backend/tests/test_agent.py
  - backend/tests/test_chat_endpoint.py
  - pipeline/db/schema-updates.sql
autonomous: true
requirements: [R3.1, R3.2, R3.3, R3.4]
user_setup:
  - service: openai
    why: "GPT-4o mini for eval gate, streaming chat completions"
    env_vars:
      - name: OPENAI_API_KEY
        source: "OpenAI Platform → API keys"
  - service: groq
    why: "Fallback LLM if eval gate score ≥ 4.0 (optional, evaluated in Wave 1)"
    env_vars:
      - name: GROQ_API_KEY
        source: "Groq Console → API keys (if Groq selected post-eval)"
  - service: langfuse
    why: "LLM observability — trace latency, tokens, cost"
    env_vars:
      - name: LANGFUSE_PUBLIC_KEY
        source: "Langfuse Dashboard → Settings → API keys"
      - name: LANGFUSE_SECRET_KEY
        source: "Langfuse Dashboard → Settings → API keys"
  - service: redis
    why: "Query result caching (TTL 3600s, latency budget P95 < 3s)"
    env_vars:
      - name: REDIS_URL
        source: "Railway or local Redis (redis://localhost:6379)"

must_haves:
  truths:
    - "Eval gate executes on 10 Portuguese queries, scores model candidates, documents selection"
    - "POST /chat endpoint streams SSE with top-3 paddle recommendations in < 3s (P95)"
    - "Metric translation (swingweight/twistweight/core/face) renders in simple Portuguese"
    - "Degraded mode activates on LLM timeout (>8s), returns top-3 by price via SSE"
    - "Langfuse traces record latency, token counts, and cost per query"

  artifacts:
    - path: "backend/app/agents/eval_gate.py"
      provides: "Model evaluation (10 queries, score ≥4.0 → Groq, <4.0 → Claude Sonnet)"
      exports: ["EvalResult", "run_eval_gate()"]
    - path: "backend/app/agents/rag_agent.py"
      provides: "RAG search + recommendation generation against pgvector"
      exports: ["RecommendationResult", "RAGAgent"]
    - path: "backend/app/prompts.py"
      provides: "System prompt + metric translation rules (PT-BR)"
      exports: ["SYSTEM_PROMPT", "translate_metrics()"]
    - path: "backend/app/api/chat.py"
      provides: "POST /chat with SSE streaming, filtering, top-3 logic"
      exports: ["chat_stream()"]
    - path: "backend/app/cache.py"
      provides: "Redis wrapper for query caching (3600s TTL)"
      exports: ["get_cached()", "set_cached()"]
    - path: "backend/app/observability.py"
      provides: "Langfuse integration — traces and latency budgets"
      exports: ["log_trace()", "LangfuseHandler"]
    - path: "backend/tests/test_eval_gate.py"
      provides: "LLM eval tests (10 queries, scoring logic)"
      min_tests: 5
    - path: "backend/tests/test_agent.py"
      provides: "RAG agent unit tests (search, filtering, degradation)"
      min_tests: 6
    - path: "backend/tests/test_chat_endpoint.py"
      provides: "E2E chat endpoint tests (SSE streaming, latency)"
      min_tests: 4

  key_links:
    - from: "backend/app/api/chat.py"
      to: "backend/app/agents/rag_agent.py"
      via: "fetch RAG recommendations from pgvector"
      pattern: "RAGAgent.search.*pgvector"
    - from: "backend/app/agents/rag_agent.py"
      to: "backend/app/api/paddles.py"
      via: "retrieve paddle specs + affiliate URLs"
      pattern: "db_fetch.*paddles"
    - from: "backend/app/api/chat.py"
      to: "backend/app/cache.py"
      via: "check Redis for query results (3600s TTL)"
      pattern: "get_cached.*chat_key"
    - from: "backend/app/api/chat.py"
      to: "backend/app/observability.py"
      via: "log latency and token counts to Langfuse"
      pattern: "log_trace.*latency"
    - from: "backend/app/agents/eval_gate.py"
      to: "OpenAI API"
      via: "evaluate model candidates on 10 PT-BR queries"
      pattern: "client.chat.completions.create"

---

<objective>
Build a conversational RAG agent recommending pickleball paddles in Portuguese, with <3s P95 latency, LLM model selection via eval gate, and observability via Langfuse.

**Purpose:**
Phase 3 transforms Phase 2's paddle catalog + embeddings into an intelligent recommendation system. The agent:
1. Evaluates multiple LLM candidates (Groq vs Claude Sonnet) on 10 Portuguese queries to select the best performer
2. Streams recommendations via SSE with top-3 paddles, filtering by user profile (skill level, budget)
3. Translates technical specs (swingweight, twistweight, core material) into conversational Portuguese
4. Falls back gracefully if LLM latency exceeds 8s budget (returns top-3 by price)
5. Traces every query to Langfuse for observability

**Output:**
- Working POST /chat endpoint with SSE streaming
- Eval gate documentation showing model selection rationale
- Redis cache reducing redundant LLM calls
- Langfuse dashboard showing P95 latency < 3s
- 15+ passing tests covering eval, search, streaming, and degradation
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/02-full-data-pipeline/PHASE-2-COMPLETE.md
@.planning/phases/02-full-data-pipeline/02-05-SUMMARY.md

## Phase 2 Handoff

Phase 2 provides (verified ✅):
- **pgvector index** on paddle_embeddings with HNSW search
- **5 FastAPI endpoints** (GET /paddles, /paddles/{id}, /prices, /latest-prices, /health)
- **Pydantic schemas** (PaddleResponse, SpecsResponse, PriceSnapshot, etc.)
- **PostgreSQL** with paddle, paddle_specs, price_snapshots, latest_prices tables
- **Router pattern** established in backend/app/api/paddles.py

## Phase 2 API Contract (to be used in Phase 3)

```python
# backend/app/api/paddles.py exports:
async def list_paddles(
    brand: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    in_stock: bool = True,
    limit: int = 50,
    offset: int = 0
) -> PaddleListResponse

async def get_paddle_detail(paddle_id: int) -> PaddleResponse
# Returns: {id, name, brand, specs, price_min_brl, created_at}

async def get_paddle_prices(paddle_id: int) -> PriceHistoryResponse
# Returns: {paddle_id, paddle_name, prices: [{retailer_name, price_brl, in_stock, scraped_at}]}
```

## Research Decisions from Phase 1 (BINDING)

1. **No LangChain/LlamaIndex** — Raw SDK for control + latency
2. **Raw pgvector search** — HNSW index for cosine similarity (no ORM)
3. **Streaming via Vercel AI SDK** (`streamText`) in Phase 4; Phase 3 uses raw SSE
4. **Langfuse for observability** — Latency traces, token counts, cost per query
5. **Groq for cost if ≥ 4.0 score, Claude Sonnet fallback** — Eval gate determines selection
6. **Portuguese narratives** — Metric translation must use Portuguese metric names

## Tech Stack (Phase 3)

**LLM Runtime:**
- OpenAI (for eval gate + primary) — `openai` library
- Groq (conditional fallback) — `groq` library
- Claude Sonnet (fallback if Groq <4.0) — `anthropic` library

**Observability:**
- Langfuse v3 — `langfuse` library for trace logging

**Caching:**
- Redis — `redis` library (async: `aioredis` or `redis[asyncio]`)

**Async Runtime:**
- `asyncio` — stdlib, already in use
- `pytest-asyncio` — for testing

</context>

<tasks>

## WAVE 1: Model Eval Gate + Agent Skeleton (Checkpoint After)

<task type="auto">
  <name>Task 1.1: Implement LLM Eval Gate (10 Portuguese Queries)</name>
  <files>backend/app/agents/eval_gate.py, backend/tests/test_eval_gate.py</files>
  <action>
Create eval gate that:

1. **Evaluation Logic** (`backend/app/agents/eval_gate.py`)
   - Define 10 Portuguese queries that test paddle recommendation quality:
     ```python
     EVAL_QUERIES = [
       "Sou iniciante, orçamento até R$ 500. Qual raquete?",
       "Prefiro raquete mais pesada, melhor controle. Sugestões?",
       ...
     ]
     ```
   - Create `EvalResult` Pydantic model: {model_name, avg_score, explanation, timestamp}
   - Implement `run_eval_gate()` async function:
     - For each query: call OpenAI GPT-4o mini with same system prompt used in chat
     - After each response: have a evaluator prompt score quality 1-5 (relevance, Portuguese clarity, specificity)
     - Average scores across 10 queries
     - **Selection logic:** if avg_score ≥ 4.0 → return "groq" candidate; if < 4.0 → return "claude-sonnet"
     - Log decision to `backend/data/eval_results.json` (for documentation)
   - Cost tracking: log OpenAI tokens/cost per eval query

2. **Test Coverage** (`backend/tests/test_eval_gate.py`)
   - `test_eval_gate__returns_result()` — Verify EvalResult structure
   - `test_eval_gate__scores_between_1_5()` — Each query score in valid range
   - `test_eval_gate__10_queries_evaluated()` — All 10 queries processed
   - `test_eval_gate__selection_logic_groq()` — Avg ≥4.0 → "groq"
   - `test_eval_gate__selection_logic_sonnet()` — Avg <4.0 → "claude-sonnet"

**Per R3.1:** Eval gate executed, model selected, result documented in eval_results.json
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_eval_gate.py -v --tb=short</automated>
  </verify>
  <done>
- EvalResult dataclass with {model_name, avg_score, explanation, timestamp}
- run_eval_gate() function executes 10 PT-BR queries, scores each 1-5, averages, selects model
- eval_results.json created with winning model and rationale
- 5 test cases passing
  </done>
</task>

<task type="auto">
  <name>Task 1.2: RAG Agent Skeleton — pgvector Search + Top-3 Logic</name>
  <files>backend/app/agents/rag_agent.py, backend/tests/test_agent.py</files>
  <action>
Create `RAGAgent` class that performs semantic search + filtering:

1. **Agent Class** (`backend/app/agents/rag_agent.py`)
   - Define `RecommendationResult` Pydantic model:
     ```python
     class RecommendationResult(BaseModel):
       paddle_id: int
       name: str
       brand: str
       reasoning: str  # Why recommended for user
       price_min_brl: float
       affiliate_url: str
     ```
   - Create `RAGAgent` class with methods:
     ```python
     class RAGAgent:
       async def __init__(db_pool, model_name: str)

       async def search_by_profile(
         skill_level: str,  # "beginner", "intermediate", "advanced"
         budget_brl: float,
         style: Optional[str] = None  # e.g., "control", "power"
       ) -> List[RecommendationResult]:
           # 1. Translate profile to search query ("iniciante, controle, até R$ 500")
           # 2. Embed query using Phase 2's OpenAI embedding
           # 3. pgvector similarity search (top-10)
           # 4. Filter by budget_brl and in_stock
           # 5. Return top-3 with reasoning
           # Each recommendation includes affiliate URL from price_snapshots
     ```
   - **Filtering Rules:**
     - Price constraint: `latest_price ≤ budget_brl`
     - Stock constraint: `in_stock = true` (from latest_prices materialized view)
     - Relevance ranking: Cosine similarity score + price proximity to budget
   - **Degraded Mode Function:**
     ```python
     async def get_top_by_price(budget_brl: float, limit: int = 3) -> List[RecommendationResult]:
         # Simple price-based fallback (no embedding search)
         # Returns top-3 by (budget_brl - actual_price), highest first
     ```

2. **Test Coverage** (`backend/tests/test_agent.py`)
   - `test_rag_search__returns_3_paddles()` — Top-3 always returned
   - `test_rag_search__respects_budget()` — No paddle > budget_brl
   - `test_rag_search__in_stock_constraint()` — Only in_stock=true
   - `test_rag_search__includes_affiliate_url()` — Affiliate URLs present
   - `test_degraded_mode__returns_by_price()` — Fallback uses price ranking
   - `test_recommendation_result__schema_valid()` — RecommendationResult validates

**Per R3.1 & R3.2:** Agent can fetch top-3 via pgvector, has fallback for degraded mode
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_agent.py -v --tb=short</automated>
  </verify>
  <done>
- RecommendationResult Pydantic model with {paddle_id, name, brand, reasoning, price_min_brl, affiliate_url}
- RAGAgent class with search_by_profile() returning top-3 with budget/stock filters
- get_top_by_price() degraded mode fallback
- Affiliate URLs populated from latest_prices join
- 6 test cases passing (search, budget constraint, stock constraint, fallback)
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
- Eval gate runs 10 PT-BR queries, scores model candidates, selects winner
- RAG agent skeleton fetches top-3 recommendations with budget/stock filtering
- Degraded mode fallback to price-based ranking
- Both modules fully tested (11 passing tests)
  </what-built>
  <how-to-verify>
1. Check `backend/data/eval_results.json` exists with model selection + rationale
2. Run: `pytest backend/tests/test_eval_gate.py backend/tests/test_agent.py -v`
3. Verify test count ≥ 11, all passing
4. Spot-check: Read eval_gate.py line ~50: verify score averaging logic (sum / 10)
5. Spot-check: Read rag_agent.py line ~80: verify budget filtering in search_by_profile()
  </how-to-verify>
  <resume-signal>Type "approved" once all 11 tests pass and eval_results.json is documented</resume-signal>
</task>

## WAVE 2: Prompt Engineering + Metric Translation

<task type="auto">
  <name>Task 2.1: Prompt System + Portuguese Metric Translation</name>
  <files>backend/app/prompts.py, backend/tests/test_prompts.py</files>
  <action>
Create `prompts.py` with system prompt and metric translation:

1. **System Prompt** (`backend/app/prompts.py`)
   ```python
   SYSTEM_PROMPT = """
   Você é um especialista em raquetes de pickleball brasileiro.
   Recomende as 3 melhores raquetes com base no perfil do usuário.

   Para cada recomendação:
   - Nome e marca da raquete
   - 2-3 razões por que é perfeita para o usuário
   - Preço em BRL e onde comprar (link de afiliado)

   Seja conciso, conversacional e em português brasileiro.
   """
   ```

2. **Metric Translation Function**
   - Create `translate_metrics(specs: SpecsResponse) -> Dict[str, str]`
   - Translate technical metrics to simple Portuguese:
     ```python
     # Input: SpecsResponse {swingweight: 115, twistweight: 7.2, weight_oz: 8.3, core: "polypropylene", face: "fiberglass"}
     # Output:
     {
       "peso_balanceado": "Média (115 pontos) — bom controle + potência",
       "torcao": "Baixa (7.2) — menos vibração, mais precisão",
       "peso_total": "236g — confortável para longas sessões",
       "nucleoInterno": "Polipropileno — toque macio, absorção de impacto",
       "facePrincipal": "Fibra de vidro — durabilidade alta"
     }
     ```
   - Handle missing specs gracefully (return "Dado não disponível")
   - Units: Convert oz→g, keep swingweight/twistweight as-is with explanation

3. **Test Coverage** (`backend/tests/test_prompts.py`)
   - `test_translate_metrics__all_fields_present()` — All 5 metrics translated
   - `test_translate_metrics__missing_spec()` — Handles NULL gracefully
   - `test_translate_metrics__output_portuguese()` — All output text is PT-BR
   - `test_system_prompt__contains_portuguese()` — System prompt is Portuguese
   - `test_metric_ranges__explanation_matches()` — Swingweight explanation matches value

**Per R3.3:** Metric translation system working in Portuguese with clear explanations
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_prompts.py -v --tb=short</automated>
  </verify>
  <done>
- SYSTEM_PROMPT constant defined (conversational, Portuguese, 3-reason format)
- translate_metrics() function converts specs to plain-language Portuguese dict
- Handles missing specs (returns "não disponível")
- Unit conversions (oz→g) correct
- 5 test cases passing (all fields, missing, Portuguese validation)
  </done>
</task>

## WAVE 3: POST /chat Endpoint + SSE Streaming

<task type="auto">
  <name>Task 3.1: POST /chat SSE Endpoint with Filtering + Top-3</name>
  <files>backend/app/api/chat.py, backend/tests/test_chat_endpoint.py, backend/app/main.py</files>
  <action>
Create streaming chat endpoint:

1. **Chat Endpoint** (`backend/app/api/chat.py`)
   ```python
   @app.post("/chat")
   async def chat_stream(
     message: str,
     skill_level: str,      # "beginner", "intermediate", "advanced"
     budget_brl: float,
     style: Optional[str] = None
   ) -> StreamingResponse:
   ```

   - **Request validation:**
     - skill_level must be in ["beginner", "intermediate", "advanced"]
     - budget_brl > 0
     - message non-empty

   - **Response:** Server-Sent Events (text/event-stream)
     ```
     event: recommendations
     data: {"paddles": [...top 3 recommendations...]}

     event: reasoning
     data: {"text": "...streaming LLM response..."}

     event: done
     data: {"tokens": 145, "latency_ms": 1250, "model": "claude-sonnet"}
     ```

   - **Flow (per task action below):**
     1. Validate input
     2. Check Redis cache for same (message, skill_level, budget_brl) → return if hit (TTL 3600s)
     3. Fetch top-3 paddles via RAGAgent.search_by_profile()
     4. Send "recommendations" SSE event with paddles + affiliate URLs
     5. Stream LLM response for reasoning (using selected model from eval gate)
     6. On LLM timeout (>8s): trigger degraded_mode → send "degraded" event + top-3 by price
     7. Log trace to Langfuse with latency, tokens
     8. Cache result to Redis (3600s TTL)
     9. Send "done" event with metadata

   - **Timeout Handling:**
     ```python
     try:
       response = await asyncio.wait_for(
         llm_client.chat.completions.create(...),
         timeout=8.0
       )
     except asyncio.TimeoutError:
       # Degraded mode: return top-3 by price
       yield "event: degraded\ndata: {...}\n\n"
       return
     ```

2. **Router Integration** (`backend/app/main.py`)
   - Import: `from backend.app.api.chat import router as chat_router`
   - Include: `app.include_router(chat_router)`

3. **Test Coverage** (`backend/tests/test_chat_endpoint.py`)
   - `test_chat_stream__returns_sse()` — Response is text/event-stream
   - `test_chat_stream__includes_recommendations()` — "recommendations" event present
   - `test_chat_stream__includes_reasoning()` — "reasoning" event with LLM text
   - `test_chat_stream__degraded_mode_on_timeout()` — On 8s timeout, send "degraded" event

**Per R3.2 & R3.4:** Chat endpoint streams top-3 with SSE, degrades gracefully on timeout
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_chat_endpoint.py -v --tb=short</automated>
  </verify>
  <done>
- POST /chat endpoint accepts {message, skill_level, budget_brl, style}
- Returns Server-Sent Events stream with "recommendations", "reasoning", "done" events
- Degraded mode triggers on LLM timeout (>8s) → returns top-3 by price
- 4 test cases passing (SSE format, events present, degradation)
  </done>
</task>

## WAVE 4: Redis Caching + Latency Budget

<task type="auto">
  <name>Task 4.1: Redis Cache Layer (3600s TTL, Query Deduplication)</name>
  <files>backend/app/cache.py, backend/tests/test_cache.py</files>
  <action>
Create Redis caching for chat queries:

1. **Cache Module** (`backend/app/cache.py`)
   ```python
   class RedisCache:
     def __init__(self, redis_url: str):
       self.client = aioredis.from_url(redis_url, decode_responses=True)

     async def get_cached(key: str) -> Optional[Dict]:
       # key format: f"chat:{message}:{skill_level}:{budget_brl}"
       # Return parsed JSON or None

     async def set_cached(key: str, value: Dict, ttl: int = 3600):
       # Store JSON-serialized value with TTL
   ```

2. **Integration into POST /chat**
   - Before LLM call: `cached = await cache.get_cached(chat_key)`
   - If hit: stream cached result directly, skip LLM
   - After LLM: `await cache.set_cached(chat_key, result, ttl=3600)`
   - Cache key: `f"chat:v1:{hashlib.md5(f'{message}:{skill_level}:{budget_brl}'.encode()).hexdigest()}"`

3. **Test Coverage** (`backend/tests/test_cache.py`)
   - `test_cache_get__hit()` — Retrieve cached value
   - `test_cache_set__stores_json()` — Store and retrieve JSON
   - `test_cache_ttl__expires_after_3600s()` — Mock Redis expiry
   - `test_cache_key__deterministic()` — Same inputs → same key

**Per R3.4:** Cache reduces redundant LLM calls, helping meet P95 < 3s latency target
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_cache.py -v --tb=short</automated>
  </verify>
  <done>
- RedisCache class with get_cached() and set_cached() methods
- TTL set to 3600s (1 hour)
- Cache key deterministic (MD5 hash of message + profile)
- 4 test cases passing (hit, store, expiry, key determinism)
  </done>
</task>

<task type="auto">
  <name>Task 4.2: Latency Monitoring + P95 Budget Enforcement</name>
  <files>backend/app/observability.py, backend/tests/test_observability.py, backend/app/main.py</files>
  <action>
Add latency tracking and P95 < 3s monitoring:

1. **Observability Module** (`backend/app/observability.py`)
   ```python
   class LatencyTracker:
     def __init__(self):
       self.latencies_ms = deque(maxlen=1000)  # Keep last 1000 queries

     async def record(latency_ms: float):
       self.latencies_ms.append(latency_ms)

     def p95_latency_ms(self) -> float:
       sorted_latencies = sorted(self.latencies_ms)
       return sorted_latencies[int(0.95 * len(sorted_latencies))]

     async def check_budget(self, latency_ms: float) -> bool:
       # Returns True if latency < 3000ms
       return latency_ms < 3000

   async def log_trace(
     query_id: str,
     latency_ms: float,
     input_tokens: int,
     output_tokens: int,
     model: str,
     cache_hit: bool
   ):
       # Log to Langfuse (see Wave 5)
       pass
   ```

2. **Middleware Integration** (`backend/app/main.py`)
   - Add `LatencyTracker` instance to FastAPI app state
   - Create middleware that wraps every request:
     ```python
     @app.middleware("http")
     async def track_latency(request, call_next):
       start = time.time()
       response = await call_next(request)
       latency_ms = (time.time() - start) * 1000
       await app.state.latency_tracker.record(latency_ms)
       response.headers["X-Latency-Ms"] = str(latency_ms)
       return response
     ```

3. **Test Coverage** (`backend/tests/test_observability.py`)
   - `test_latency_tracker__records_value()` — Value stored
   - `test_latency_tracker__p95_calculation()` — Correct P95 percentile
   - `test_budget_check__under_3s()` — Returns True for <3000ms
   - `test_budget_check__over_3s()` — Returns False for ≥3000ms

**Per R3.4:** Latency tracking and P95 budget enforcement in place
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_observability.py -v --tb=short</automated>
  </verify>
  <done>
- LatencyTracker class with record() and p95_latency_ms() methods
- Tracks last 1000 queries in deque
- P95 calculation correct (95th percentile)
- Middleware adds latency tracking to all requests
- 4 test cases passing (recording, P95, budget checks)
  </done>
</task>

## WAVE 5: Langfuse Observability + Production Ready

<task type="auto">
  <name>Task 5.1: Langfuse Integration — Traces, Cost, Dashboards</name>
  <files>backend/app/observability.py (extended), backend/tests/test_langfuse.py, backend/app/main.py</files>
  <action>
Wire Langfuse v3 for LLM observability:

1. **Langfuse Client Setup** (`backend/app/observability.py`)
   ```python
   from langfuse import Langfuse

   class LangfuseHandler:
     def __init__(self, public_key: str, secret_key: str):
       self.client = Langfuse(
         public_key=public_key,
         secret_key=secret_key,
         # Batch size 100, flush every 10s
       )

     async def log_chat_trace(
       query_id: str,
       user_profile: Dict,       # {skill_level, budget_brl, style}
       model_used: str,          # "groq" or "claude-sonnet"
       input_text: str,
       output_text: str,
       input_tokens: int,
       output_tokens: int,
       latency_ms: float,
       cache_hit: bool,
       degraded_mode: bool
     ):
       trace = self.client.trace(
         name="chat_recommendation",
         input={"query": input_text, "profile": user_profile},
         output={"response": output_text, "paddles": ...},
         metadata={
           "model": model_used,
           "cache_hit": cache_hit,
           "degraded": degraded_mode,
           "latency_ms": latency_ms,
           "phase": "phase-3"
         },
         tags=["chat", "rag", "paddle-recommendation"]
       )

       # Log token counts as separate span
       trace.span(
         name="llm_completion",
         input={"tokens_in": input_tokens},
         output={"tokens_out": output_tokens},
         model=model_used,
         usage={
           "input": input_tokens,
           "output": output_tokens,
           "unit": "tokens"
         }
       )

       return trace
   ```

2. **POST /chat Integration**
   - After LLM response: call `await langfuse_handler.log_chat_trace(...)`
   - Include cache_hit flag
   - Include degraded_mode flag if fallback used
   - Flush on graceful shutdown

3. **FastAPI Startup/Shutdown** (`backend/app/main.py`)
   ```python
   @app.on_event("startup")
   async def startup():
     app.state.langfuse = LangfuseHandler(
       public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
       secret_key=os.getenv("LANGFUSE_SECRET_KEY")
     )

   @app.on_event("shutdown")
   async def shutdown():
     await app.state.langfuse.client.flush()
   ```

4. **Test Coverage** (`backend/tests/test_langfuse.py`)
   - `test_langfuse_trace__includes_metadata()` — Model, cache_hit, degraded flags present
   - `test_langfuse_trace__logs_token_counts()` — Token span created
   - `test_langfuse_flush__on_shutdown()` — Client flushed gracefully
   - `test_langfuse_dashboard_query()` — Can query traces from Langfuse API

**Per R3.4:** Langfuse traces latency, tokens, cost, cache hits, and degradation mode
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_langfuse.py -v --tb=short</automated>
  </verify>
  <done>
- LangfuseHandler class with log_chat_trace() method
- Traces include model, cache_hit, degraded_mode, latency_ms, token counts
- Token counts logged as separate span with unit="tokens"
- FastAPI startup/shutdown hooks wire Langfuse client
- 4 test cases passing (metadata, tokens, flush, dashboard query)
  </done>
</task>

<task type="auto">
  <name>Task 5.2: End-to-End Testing + Production Checklist</name>
  <files>backend/tests/test_e2e_chat.py, backend/tests/test_production_readiness.py</files>
  <action>
Create comprehensive E2E and production readiness tests:

1. **E2E Chat Test** (`backend/tests/test_e2e_chat.py`)
   ```python
   # Full flow: eval gate → agent → cache → LLM → Langfuse
   async def test_e2e_chat_flow():
     # 1. Run eval gate (or load cached result)
     # 2. Call POST /chat with valid profile
     # 3. Parse SSE events: recommendations, reasoning, done
     # 4. Verify top-3 paddles respect budget + stock
     # 5. Verify latency < 3s (P95)
     # 6. Verify Langfuse trace created
     # 7. Call same chat again, verify cache hit (latency <500ms)

   async def test_degraded_mode_e2e():
     # Mock LLM timeout, verify "degraded" event + fallback top-3
   ```

2. **Production Readiness Test** (`backend/tests/test_production_readiness.py`)
   ```python
   async def test_all_env_vars_present():
     # Check OPENAI_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, REDIS_URL

   async def test_db_pool_connection():
     # Verify PostgreSQL connection pool opens/closes properly

   async def test_error_handling__malformed_input():
     # Invalid skill_level, negative budget → 422 responses

   async def test_concurrent_requests():
     # 10 concurrent /chat requests, all complete < 3s (P95)
   ```

3. **Coverage Goals**
   - E2E: 2 tests (happy path, degraded mode)
   - Production: 4 tests (env vars, DB, validation, concurrency)
   - Total: 6 new tests

**Per R3.4:** Production readiness validated, E2E flow proven
  </action>
  <verify>
    <automated>cd backend && python -m pytest tests/test_e2e_chat.py tests/test_production_readiness.py -v --tb=short</automated>
  </verify>
  <done>
- E2E test covering eval gate → chat → cache → Langfuse flow
- E2E test for degraded mode (8s timeout → fallback)
- Production readiness tests: env vars, DB pool, input validation, concurrency
- All 6 tests passing
- Test coverage >= 80% for Phase 3 backend code
  </done>
</task>

</tasks>

<verification>

## Phase 3 Success Checklist

After all 5 waves complete:

1. **Eval Gate (Wave 1)**
   - [ ] `backend/data/eval_results.json` exists with model selection + rationale
   - [ ] Selected model: either "groq" or "claude-sonnet" (based on 10-query avg score)
   - [ ] Test count: eval_gate (5) + agent (6) = 11 tests passing

2. **Chat Endpoint (Wave 3)**
   - [ ] POST /chat accepts {message, skill_level, budget_brl, style}
   - [ ] Returns text/event-stream with "recommendations", "reasoning", "done" events
   - [ ] Top-3 paddles include affiliate_url
   - [ ] Degraded mode activates on 8s timeout

3. **Caching & Latency (Wave 4)**
   - [ ] Redis cache with 3600s TTL reduces redundant LLM calls
   - [ ] Latency middleware tracks all requests to deque
   - [ ] P95 latency calculation correct (95th percentile)
   - [ ] Cache + latency tests: 8 tests passing

4. **Observability (Wave 5)**
   - [ ] Langfuse traces created for every chat query
   - [ ] Traces include: model, cache_hit, degraded_mode, latency_ms, token counts
   - [ ] Token counts logged as separate span
   - [ ] Langfuse tests: 4 tests passing

5. **E2E & Production (Wave 5)**
   - [ ] E2E test proves full flow (eval → chat → cache → Langfuse)
   - [ ] E2E test covers degraded mode
   - [ ] Production readiness tests: env vars, DB, validation, concurrency
   - [ ] E2E + production tests: 6 tests passing

6. **Total Test Count**
   - [ ] eval_gate (5) + agent (6) + prompts (5) + chat (4) + cache (4) + observability (4) + langfuse (4) + e2e (6) = **38+ tests passing**

7. **Code Quality**
   - [ ] All code follows Phase 2 patterns (async/await, Pydantic models, TestClient)
   - [ ] No LangChain/LlamaIndex dependencies
   - [ ] No hardcoded secrets (all via environment variables)
   - [ ] Graceful error handling (timeouts, DB disconnects, missing specs)

8. **Documentation**
   - [ ] `backend/data/eval_results.json` documents model selection
   - [ ] Code comments explain eval scoring logic and degraded mode
   - [ ] Chat endpoint SSE event format documented in docstring

</verification>

<success_criteria>

**Phase 3 Complete When:**

✅ **Model Evaluation**
- Eval gate executed on 10 Portuguese queries
- Model selected: Groq (score ≥4.0) or Claude Sonnet (score <4.0)
- Decision documented in eval_results.json

✅ **Chat Pipeline Working**
- POST /chat endpoint streams top-3 recommendations via SSE
- Recommendations include paddle specs, affiliate URLs, pricing
- Streaming latency P95 < 3 seconds (observed via X-Latency-Ms header)
- Metric translation renders in Portuguese (e.g., "peso balanceado", "torcão")

✅ **Degraded Mode Active**
- On LLM timeout (>8s), endpoint sends "degraded" event
- Degraded mode returns top-3 by price (no LLM reasoning)
- Graceful fallback verified in tests

✅ **Cache & Performance**
- Redis cache reduces redundant LLM calls (3600s TTL)
- Repeat queries complete < 500ms (cache hit)
- P95 latency tracked and < 3s (including cache misses)

✅ **Observability Complete**
- Langfuse traces every chat query
- Traces include model, tokens, latency, cache_hit, degraded flags
- Dashboard shows P95 latency < 3s
- Token cost tracked per query

✅ **Test Coverage**
- 38+ passing tests (eval, agent, prompts, chat, cache, observability, langfuse, e2e)
- E2E test covers happy path, degraded mode, cache hit, Langfuse trace
- Production readiness tests (env vars, DB, validation, concurrency)
- Coverage >= 80% for Phase 3 backend code

✅ **No Regressions**
- All Phase 2 endpoints (GET /paddles, /prices) still working
- Phase 2 embeddings still queryable via pgvector
- All Phase 2 tests still passing

**Ready for Phase 4** (Frontend Chat & Product UI)

</success_criteria>

<output>
After completion, create `.planning/phases/03-rag-agent-ai-core/SUMMARY.md` with:

- **Status:** COMPLETE
- **Wave summary:** All 5 waves executed, 38+ tests passing
- **Eval gate result:** Model selected (Groq or Sonnet), score documented
- **Chat latency:** P95 < 3s (observed in last 100 queries)
- **Cache efficiency:** X% of queries served from Redis (3600s TTL)
- **Observability:** Langfuse dashboard active, cost per query tracked
- **Files created:** 15+ (agents, prompts, cache, observability, tests)
- **Key commits:** eval gate, agent skeleton, chat endpoint, caching, langfuse
- **Handoff to Phase 4:** Chat API ready, `/chat` endpoint documented
</output>

