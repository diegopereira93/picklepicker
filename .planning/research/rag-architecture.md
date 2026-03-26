# RAG Architecture Research: PickleIQ Recommendation Platform

**Domain:** RAG for product recommendation chatbots
**Researched:** 2026-03-26
**Overall Confidence:** MEDIUM (based on training data through August 2025; WebSearch unavailable)

---

## 1. FastAPI + Pinecone + Claude: Best Practices

**Confidence: MEDIUM**

### Recommended Pattern: Two-Phase Chat Pipeline

```
User message → Profile collector → Query builder → Pinecone retrieval → Claude synthesis → Streaming response
```

**FastAPI structure:**
- Use a single `/chat` POST endpoint with `StreamingResponse` for < 3s perceived latency.
- Maintain conversation state server-side with a short-lived Redis session keyed by `session_id` (passed as cookie or header). Do NOT embed full history in every request body.
- Separate the pipeline into two explicit phases:
  1. **Profile collection** (turns 1–3): Extract `skill_level`, `play_style`, `budget` from user messages using Claude with a structured extraction prompt. Store in session.
  2. **Recommendation** (trigger when profile is complete): Build Pinecone query from profile, retrieve candidates, synthesize final answer.

**Pinecone client setup:**
- Use `pinecone-client` v3+ (namespace-based indexes). One index, two namespaces: `paddles` and `cache`.
- Use `pinecone.Index.query()` with `top_k=10`, then rerank to 3 in the LLM step — do not ask Pinecone to return only 3, since reranking on specs happens at Claude level.
- Always pass `include_metadata=True` to get structured fields back without a separate DB fetch.

**Claude integration:**
- Use `claude-3-5-sonnet` for the synthesis step (best cost/quality ratio for structured output).
- Use `claude-3-haiku` for profile extraction turns (fast, cheap for short structured tasks).
- Call `client.messages.stream()` for the final recommendation response to enable SSE streaming.

---

## 2. Embedding Strategy: What to Embed and Chunking

**Confidence: HIGH**

### What to Embed

Do NOT embed raw spec tables. Embed a **narrative product document** that combines both semantic and semi-structured content.

**Recommended document template per paddle:**

```
[Brand] [Model] — [Category tagline]

Feel: [grip feel, control description from manufacturer or synthesized]
Power: [power level description]
Spin: [surface texture, spin potential]
Maneuverability: [weight, balance point in natural language]
Ideal player: [skill level, play style this suits]
Budget tier: [budget / mid-range / premium]

Specs: Weight [X]g, Core thickness [Xmm], Face material [X], Grip length [X]in
Price: $[X]
```

**Rationale:** Models like `text-embedding-3-small` (OpenAI) or Voyage AI's `voyage-large-2` encode semantic meaning. Embedding "ideal for control-oriented players" retrieves better than embedding `"control_score": 8.2`. Structured numbers in the text act as anchors without polluting the semantic space.

**Chunking strategy:**
- **One document = one paddle.** Do NOT chunk paddle documents further. Each paddle is ~200–400 tokens — well within embedding context limits.
- Embed at upsert time (not at query time). Re-embed when product data changes.
- Store the full structured record in Pinecone metadata (price, stock_status, affiliate_url, brand, weight_grams, etc.). This avoids a secondary DB lookup.

**Embedding model recommendation:**
- `text-embedding-3-small` (OpenAI) — 1536 dims, cheap, well-supported. Use if OpenAI is already in the stack.
- `voyage-large-2-instruct` (Voyage AI) — superior retrieval quality, especially for product domains. Recommended if embedding quality is a priority.
- Do NOT use Pinecone's built-in hosted embeddings for this use case — they add latency and reduce control.

---

## 3. Combining Structured Data with Vector Search Results

**Confidence: HIGH**

### Pattern: Metadata-Enriched Context Block

After Pinecone returns `top_k` results, construct a structured context block for Claude:

```python
def build_context(matches: list[dict], user_profile: dict) -> str:
    blocks = []
    for m in matches:
        meta = m["metadata"]
        blocks.append(f"""
PADDLE: {meta['brand']} {meta['model']}
Price: ${meta['price_usd']} | In stock: {meta['in_stock']}
Weight: {meta['weight_grams']}g | Core: {meta['core_thickness_mm']}mm
Affiliate URL: {meta['affiliate_url']}
Semantic score: {m['score']:.3f}

Description: {meta['narrative_description']}
""")
    profile_block = f"""
USER PROFILE:
Skill: {user_profile['skill_level']}
Play style: {user_profile['play_style']}
Budget: ${user_profile['budget_max']}
"""
    return profile_block + "\n---\n".join(blocks)
```

**Key rules:**
- Always include `in_stock` and `price_usd` directly — Claude must filter out-of-budget or OOS items before recommending.
- Include `affiliate_url` in the context block; instruct Claude to include it verbatim in responses (do not hallucinate URLs).
- Pass semantic score to Claude so it can weigh relevance vs. structured fit. Example system prompt addition: "Prefer paddles with higher semantic scores unless budget or stock constraints eliminate them."
- Cap context at ~2000 tokens for the candidates block to stay well inside Claude's context and keep latency low.

---

## 4. Prompt Engineering: Specs to User-Friendly Language

**Confidence: HIGH**

### System Prompt Architecture

Use a two-layer system prompt:

**Layer 1 — Persona and tone:**
```
You are PickleIQ, a friendly pickleball gear advisor. You explain equipment in plain language,
relating technical specs to how they feel and perform on the court. Never use raw numbers
without explaining what they mean to the player.
```

**Layer 2 — Translation table (inject as part of system prompt):**
```
When describing paddles, translate specs using these guidelines:
- Weight < 7.5oz → "nimble, easy to maneuver at the net"
- Weight > 8.2oz → "powerful baseline drives, more arm fatigue over time"
- Core thickness 14–16mm → "soft, controlled feel, good for dinking"
- Core thickness < 13mm → "snappy, powerful, less dwell time"
- Elongated shape → "extended reach, suits singles play"
- Standard shape → "balanced for doubles, easier to control"
- Rough surface texture → "heavy topspin potential"
- Swingweight > 115 → "more stability on off-center hits, suits aggressive players"
- Swingweight 95–115 → "versatile, suits intermediate and up"
```

**Recommendation output format instruction (in system prompt):**
```
Always recommend exactly 1–3 paddles. For each:
1. Name the paddle and price
2. One sentence on why it fits this player specifically
3. One sentence translating the key differentiating spec into court feel
4. Affiliate link as a plain URL on its own line
Never recommend out-of-stock items or items over the user's stated budget.
```

**Confidence: HIGH** — This pattern (translation table in system prompt) is well-established in product domain LLM deployments and does not require fine-tuning.

---

## 5. Latency Optimization: Achieving < 3s Response

**Confidence: HIGH**

### Primary Strategy: Streaming

Use SSE (Server-Sent Events) via FastAPI `StreamingResponse` + `anthropic` SDK's `client.messages.stream()`. Perceived latency drops to time-to-first-token (~400–800ms for claude-3-5-sonnet), well under 3s.

```python
from fastapi.responses import StreamingResponse
from anthropic import Anthropic

client = Anthropic()

async def stream_recommendation(context: str, messages: list) -> StreamingResponse:
    async def generator():
        with client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(generator(), media_type="text/event-stream")
```

### Secondary Strategy: Semantic Query Caching

Cache Pinecone query results for semantically similar user profiles using a lightweight cache index in Pinecone itself (or Redis with vector similarity).

**Pattern:**
1. At recommendation trigger, embed the normalized user profile string: `"intermediate control-player $150"`.
2. Query a `cache` namespace in Pinecone with `top_k=1`. If score > 0.97, return cached recommendation directly (< 200ms).
3. On cache miss, run full pipeline, then upsert result to cache namespace.
4. TTL: re-embed and invalidate cache entries when product stock/price changes.

**Additional optimizations:**
- Pre-warm Pinecone index (keep connection pool alive, not per-request).
- Embed user profile query in parallel with Claude extraction response (async gather).
- Use `max_tokens=600` cap on Claude output — recommendation responses don't need to be long.
- Pinecone query with `top_k=10` is typically < 100ms for indexes under 100K vectors.

**Expected latency breakdown:**
| Step | Latency |
|------|---------|
| Profile extraction (Haiku) | 300–600ms |
| Profile embed + Pinecone query | 80–150ms |
| Cache lookup | 20–50ms |
| Claude synthesis TTFT (streaming) | 400–800ms |
| **Total to first token** | **~800ms–1.6s** |

---

## 6. LangChain vs LlamaIndex vs Raw SDK

**Confidence: MEDIUM**

### Recommendation: Raw SDK + Pinecone client directly

**For PickleIQ specifically, do NOT use LangChain or LlamaIndex.** Here is why:

| Factor | LangChain | LlamaIndex | Raw SDK |
|--------|-----------|------------|---------|
| Abstraction overhead | HIGH | MEDIUM | NONE |
| Debugging transparency | Poor (chain internals hidden) | Medium | Full |
| Latency overhead | 50–200ms extra | 30–100ms extra | 0ms |
| Pinecone integration | Good but abstracted | Good | Direct |
| Bundle size / dependency footprint | Very heavy | Medium | Minimal |
| Required for this use case | No | No | Yes |
| Learning curve for custom behavior | High (fighting abstractions) | Medium | Low |

**Why raw SDK wins here:**
- The pipeline is simple and well-defined: extract profile → embed → query Pinecone → call Claude. This is ~150 lines of Python, not a complex multi-hop RAG that needs LangChain's agent orchestration.
- LangChain's `ConversationalRetrievalChain` adds latency and makes streaming harder to implement correctly.
- LlamaIndex's `QueryEngine` is more justified if you have 10+ data sources or complex routing — not needed here.
- Both frameworks update frequently and introduce breaking changes; raw SDK gives you stable, predictable code.

**Use LlamaIndex IF:** The scope expands to include rule-based hybrid retrieval (BM25 + vector), multi-index routing, or a knowledge graph over paddle relationships.

**Use LangChain IF:** The scope expands to include complex multi-step agents (e.g., web search + RAG + calculator) or you need LangSmith observability tooling specifically.

**Dependency list for raw SDK approach:**
```
fastapi>=0.111
uvicorn[standard]
anthropic>=0.26
pinecone-client>=3.2
redis>=5.0
python-dotenv
pydantic>=2.0
```

---

## Architecture Diagram

```
Browser / Mobile Client
        |
        | SSE stream
        v
FastAPI /chat endpoint
        |
   [Session store - Redis]
        |
   ┌────┴────────────────────────────┐
   │  Phase 1: Profile Collection    │
   │  Claude Haiku (extraction)      │
   │  → structured {skill, style,    │
   │    budget} stored in Redis      │
   └────┬────────────────────────────┘
        │ (profile complete)
   ┌────┴────────────────────────────┐
   │  Phase 2: Recommendation        │
   │  1. Embed profile query         │
   │     (Voyage / OpenAI embed API) │
   │  2. Check cache namespace       │
   │  3. Query paddles namespace     │
   │  4. Build context block         │
   │  5. Stream via Claude Sonnet    │
   └─────────────────────────────────┘
        |
   Pinecone Index
   ├── namespace: paddles (product vectors + metadata)
   └── namespace: cache  (profile hash → recommendation)
```

---

## Critical Pitfalls

### 1. Hallucinated Affiliate URLs
**Risk:** Claude generates plausible-looking but wrong URLs.
**Prevention:** Pass exact `affiliate_url` from Pinecone metadata in context. Add to system prompt: "Only use affiliate URLs provided in the PADDLE data blocks. Never construct or guess URLs."

### 2. Out-of-Stock Recommendations
**Risk:** Pinecone returns semantically relevant paddles that are OOS or over budget.
**Prevention:** Include `in_stock` and `price_usd` in metadata AND in context block. Add hard filter instruction in system prompt. Optionally, use Pinecone metadata filters at query time: `filter={"in_stock": True, "price_usd": {"$lte": budget}}`.

### 3. Embedding Stale Product Data
**Risk:** Price/stock changes don't propagate to Pinecone, so Claude sees outdated info.
**Prevention:** Store price/stock ONLY in metadata (not the embedded text). Update metadata-only upserts on price/stock changes without re-embedding the whole document. Re-embed only when description or specs change.

### 4. Cold Start Latency on First Request
**Risk:** Pinecone connection initialization adds 500ms+ on first request.
**Prevention:** Initialize `pinecone.Index` at FastAPI startup (`@app.on_event("startup")`), not inside the request handler.

### 5. Context Window Overflow
**Risk:** 10 paddle documents + full conversation history overflows Claude's efficient context.
**Prevention:** Summarize conversation history after profile collection (replace multi-turn with single structured profile block). Cap candidate context at 2000 tokens.

---

## Phase-Specific Research Flags

| Phase Topic | Needs Deeper Research | Reason |
|-------------|----------------------|--------|
| Pinecone metadata filtering | LOW — well documented | Simple key/value filter syntax |
| Voyage AI embedding quality vs OpenAI for product data | MEDIUM | Benchmark with real paddle data needed |
| Redis session TTL strategy | LOW | Standard pattern |
| SSE implementation in FastAPI | LOW — well documented | Standard async generator pattern |
| Affiliate URL tracking / click attribution | HIGH | Not a RAG problem; needs separate research |
| Paddle data ingestion pipeline | MEDIUM | Depends on data source (scraping vs manual) |

---

## Sources

- Anthropic API docs (streaming, model selection): https://docs.anthropic.com/en/api/messages-streaming
- Pinecone metadata filtering docs: https://docs.pinecone.io/guides/data/filter-with-metadata
- Voyage AI embedding models: https://docs.voyageai.com/docs/embeddings
- FastAPI StreamingResponse docs: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- OpenAI text-embedding-3-small: https://platform.openai.com/docs/guides/embeddings

**Note:** WebSearch was unavailable during this research session. All findings are based on training data (cutoff August 2025). Confidence levels reflect this. Recommend validating embedding model choice (Voyage vs OpenAI) and LangChain/LlamaIndex current state with a live search before implementation.
