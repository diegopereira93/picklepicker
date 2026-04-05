# Roadmap: PickleIQ

## Milestone v1.5.0 — Core Infrastructure & Production Deploy

**Goal:** Provision production infrastructure, deploy to Railway + Vercel + Supabase, and add resilience for embedding outages.

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 15 | Production Deploy | Provision infra, deploy, health checks, embedding fallback, zero-paddle alert | INFRA-01–05, EMB-01–03, ALERT-01, QA-01–03 | 5 |

### Phase 15: Production Infrastructure

**Goal:** Ship to production with working health checks, embedding fallback, and basic alerting.

**Root causes (from Metis pre-planning analysis):**

1. **No production infra** — Local Docker only. Supabase, Railway, Vercel not provisioned. All deploy targets exist but have never been connected.
2. **Embedding provider fragility** — Jina AI + HuggingFace are external dependencies with no local fallback. `backend/app/services/embedding.py` has dead code `_get_local_model()` (lines 23-34) that's never called. If both APIs fail, RAG is down.
3. **No scraper health monitoring** — Crawlers run via GitHub Actions cron but there's no alert when they return zero results. Price data goes stale silently.
4. **Railway cold starts** — Hobby tier sleeps after 30min inactivity. `/chat` SSE will disconnect during cold start (~15s), causing message duplication.

**Tasks (in execution order):**

#### Wave 1 — Infrastructure Provisioning

| Task | File(s) | Description |
|------|---------|-------------|
| 15.1 | Supabase dashboard, `backend/.env` | Provision Supabase project (sa-east-1 São Paulo for LGPD compliance). Free tier initially. Create `DATABASE_URL` with connection pooler. Verify pgvector extension enabled. |
| 15.2 | `scripts/migrate_to_supabase.py` (new), `pipeline/db/schema.sql` | Create migration script: dump local schema → apply to Supabase. Run `schema-updates.sql` for missing columns. Verify all tables exist. Seed with `populate_paddles.sql`. Run `migrate_real_images.py` for real images. |
| 15.3 | `backend/Dockerfile`, Railway dashboard | Deploy backend to Railway. Configure health check (`/health` endpoint, <5s response). Set env vars via Railway Secrets (not GitHub Secrets). Verify: `curl $RAILWAY_URL/health` → 200. |
| 15.4 | `frontend/vercel.json`, Vercel dashboard | Deploy frontend to Vercel. Configure `NEXT_PUBLIC_API_URL` env var pointing to Railway backend. Verify: homepage loads, /paddles renders, /chat accessible. |

#### Wave 2 — Resilience & Alerting (parallel, after Wave 1)

| Task | File(s) | Description |
|------|---------|-------------|
| 15.5 | `backend/app/services/embedding.py` | Implement embedding fallback chain: Jina AI → HuggingFace → SentenceTransformers (local). Integrate existing dead code `_get_local_model()`. Add dimension validation (384d model must NOT be used — pgvector expects 768d). Use `all-MiniLM-L6-v2` only if dimension matches. Add sticky fallback: once local is active, stay local for 5 minutes before retrying API. |
| 15.6 | `backend/tests/test_embedding_service.py` | Add tests: (a) Jina fails → HuggingFace used, (b) Both APIs fail → local SentenceTransformers used, (c) Dimension validation rejects wrong-size vectors, (d) Sticky fallback timer works, (e) All three providers succeed → Jina preferred. |
| 15.7 | `.github/workflows/scrape.yml` | Add zero-paddle alert step at end of scrape job. Query: `SELECT COUNT(*) FROM price_snapshots WHERE DATE(scraped_at) = CURRENT_DATE AND retailer_id = X`. If 0 for any retailer → Telegram alert via existing middleware. Add "3 consecutive zeros" logic with GitHub Actions cache to avoid false positives from transient network failures. |

#### Wave 3 — Verification & Cold Start Mitigation

| Task | File(s) | Description |
|------|---------|-------------|
| 15.8 | `.github/workflows/keepalive.yml` (new) | Add GitHub Actions cron (every 5 minutes) that `curl`s Railway health endpoint to prevent cold starts. Simple: `curl -sf $RAILWAY_URL/health || echo "unhealthy"`. Runs 24/7. |
| 15.9 | `backend/tests/`, `frontend/src/tests/` | Run full test suite against production: backend 174+ pass, frontend 161+ pass. Verify health endpoint. Verify embedding fallback. Verify scraper alert triggers on zero-paddle condition. |
| 15.10 | All | Production smoke test: (a) Homepage loads, (b) /paddles shows real images or "Foto" fallback, (c) Paddle detail resolves correctly, (d) Quiz completes, (e) /chat returns streaming response. |

**Success criteria:**
1. `curl $PROD_URL/health` returns `{"status":"ok"}` in <2s
2. Homepage loads at production URL with zero console errors
3. `/chat` responds within 5s (no cold start delay)
4. Embedding fallback works when Jina/HuggingFace are unreachable
5. Zero-paddle Telegram alert fires when scraper returns 0 results
6. All existing tests pass with no regressions

---

## Future Milestones (Planned, Not Started)

### v1.5.1 — Monitoring & Resilience

**Goal:** Make production reliable with load testing, eval automation, and enhanced monitoring.

| Task | Description | Priority |
|------|-------------|----------|
| T5 | Load test /chat with k6 (50 concurrent, p95 <2s) | P1 |
| T2 | Eval gate as monthly CI job (real LLM calls, results DB) | P1 |
| Enhanced embedding fallback | Sticky sessions, performance tuning, dimension monitoring | P1 |
| Grafana/scrape dashboard | Scrape success rates, embedding latency, error rates | P2 |
| T7 | Firecrawl self-hosted runbook (document decision, may punt) | P2 |

### v1.5.2 — Legal & Compliance

**Goal:** Unblock public launch with legal sign-off.

| Task | Description | Priority |
|------|-------------|----------|
| T3 | Legal review of BR retailer scraping | P1 (external) |
| LGPD compliance audit | Data residency, privacy policy, cookie consent | P1 (external) |
| Privacy policy + Terms | Legal docs for BR market | P1 (external) |
| Affiliate disclosure | Required by BR consumer law | P1 (external) |

---
*Roadmap created: 2026-04-05*
*Last updated: 2026-04-05 after Metis pre-planning analysis*
