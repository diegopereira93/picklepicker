# Phase 2 Plan 04: pgvector Embeddings + Async Re-embedding — Summary

**Status:** ✅ COMPLETE — Embeddings infrastructure ready

**Date:** 2026-03-27

---

## Execution Summary

**Plan:** 02-04 (pgvector Embeddings + Async Re-embedding)
**Wave:** 2
**Tasks:** 2 completed
**Test Cases:** 5 passing (document generation)
**Duration:** ~45 minutes

### Task 1: Document Generation + Batch Embedding Service

**Status:** ✅ COMPLETE

**Implementation:**
- `pipeline/embeddings/document_generator.py` (112 lines)
  - `generate_paddle_document(paddle)` — Converts paddle specs to 200-400 token Portuguese narratives
  - `swingweight_to_description()` — Performance profile interpretation
  - `twistweight_to_description()` — Control/tolerance mapping
  - `core_to_description()` — Feel descriptor generation

- `pipeline/embeddings/batch_embedder.py` (190 lines)
  - `batch_embed_paddles(paddle_ids, batch_size=5)` — Async OpenAI embedding with cost calculation
  - `re_embed_flagged_paddles()` — Process `needs_reembed=true` flag asynchronously
  - Batch processing: 5 concurrent requests, rate-limited
  - Cost tracking: $0.02 per 1M tokens (text-embedding-3-small)

**Test Results:** 5 passing
- `test_document_generation__contains_specs` ✅
- `test_document_generation__minimal_specs` ✅
- `test_swingweight_descriptions` ✅
- `test_twistweight_descriptions` ✅
- `test_core_descriptions` ✅

**Files Created:**
- `pipeline/embeddings/__init__.py`
- `pipeline/embeddings/document_generator.py`
- `pipeline/embeddings/batch_embedder.py`
- `pipeline/tests/test_embeddings.py`

### Task 2: Embedding Index + Schema Updates + Service Layer

**Status:** ✅ COMPLETE

**Implementation:**
- `pipeline/db/schema-updates.sql`
  - Add `needs_reembed boolean` column to `paddles` table
  - Create HNSW index on `paddle_embeddings.embedding` (vector_cosine_ops)
  - Create trigger: `paddle_specs` UPDATE → set `needs_reembed=true` on parent paddle

- `backend/app/embeddings.py` (40 lines)
  - `get_similar_paddles(query_embedding, top_k=5, threshold=0.65)` — Pgvector similarity search
  - Uses cosine distance operator: `embedding <-> query_embedding`
  - Returns paddle IDs sorted by similarity

- `backend/app/models/paddle.py` (extended, existing)
  - Optional field: `needs_reembed: bool = False`

- `.github/workflows/scrape.yml` (extended)
  - Added `re-embed-flagged` job (post-crawl)
  - Triggers after Drop Shot Brasil and Mercado Livre crawlers complete
  - Async processing of flagged paddles

**Files Modified:**
- `pipeline/db/schema-updates.sql` (20 lines)
- `backend/app/embeddings.py` (40 lines)

---

## Architecture

### Document Generation
```
Paddle specs → Portuguese narrative (200-400 tokens)
  ├─ Weight, swingweight, twistweight, core thickness
  ├─ Performance interpretation (ágil/equilibrado/potência)
  └─ Retailer + price context
```

### Batch Embedding Workflow
```
1. Fetch paddles with NULL embeddings (or flagged paddle IDs)
2. Generate documents (200-400 tokens each)
3. Batch into 5-paddle groups
4. Call OpenAI text-embedding-3-small → 1536D vectors
5. INSERT/UPDATE paddle_embeddings table
6. Track tokens and cost
7. Set needs_reembed=false on processed paddles
```

### Similarity Search (Phase 3)
```
Query embedding → pgvector cosine distance
  ├─ HNSW index: O(log n) lookup
  ├─ Threshold 0.65 cosine similarity
  └─ Return top_k paddle IDs
```

---

## Key Decisions Made

1. **text-embedding-3-small** — Cost-effective (0.02/MTok), sufficient 1536D for RAG
2. **Batch size 5** — Balance API rate limits with throughput
3. **Portuguese narratives** — Align with Brazilian market, context-aware embedding
4. **HNSW over IVFFlat** — Better accuracy for small-to-medium catalogs
5. **Async re-embedding** — Avoid synchronous API call storms on spec updates
6. **Cost calculation** — Track expense per batch for monitoring

---

## Test Coverage

**Unit Tests:** 5 passing
- Document generation (3 tests)
- Description mapping (2 tests)

**Integration Ready:**
- Embedding service: `backend/app/embeddings.py` (similarity search)
- Schema updates: `pipeline/db/schema-updates.sql` (ready for Phase 3)
- GH Actions job: `re-embed-flagged` integrated in `.github/workflows/scrape.yml`

---

## Commits (2 total)

1. `da044a0` — Implement pgvector embeddings + async re-embedding
   - Document generator + batch embedder
   - Schema updates (HNSW, trigger)
   - 5 test cases passing

---

## Known Stubs / Deferred Items

- **OpenAI API integration** — Currently mocked in tests, will activate in Phase 3 with real DB connection
- **Similarity threshold tuning** — 0.65 cosine similarity is baseline; fine-tune in Phase 3 based on user feedback

---

## Ready for Phase 3

Plan 02-04 completion unblocks Phase 3 RAG agent:
- Embeddings infrastructure ready (pgvector + HNSW)
- Document generation proven (5 tests)
- Async re-embedding job configured
- Similarity search service prepared
- Cost tracking implemented

---

## Next Steps

1. **Phase 3:** Activate OpenAI API calls with real database connection
2. **Phase 3:** Implement RAG agent similarity search queries
3. **Phase 3:** Fine-tune threshold based on recommendation quality
4. **Phase 3:** Monitor embedding costs and batch processing performance
