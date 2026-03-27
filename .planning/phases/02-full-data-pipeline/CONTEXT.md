# Phase 2: Full Data Pipeline

## Goal
Pipeline completo cobrindo todos os varejistas BR, com deduplicação, spec enrichment e embeddings pgvector.

## Requirements
- R2.1: Crawlers Drop Shot Brasil + Mercado Livre expansão
- R2.2: Deduplicação SKU 3-tier com fila de revisão
- R2.3: GitHub Actions schedule 24h
- R2.4: pgvector embeddings com re-embedding assíncrono
- R2.5: FastAPI endpoints

## Success Criteria (what must be TRUE)
1. Crawlers Drop Shot Brasil + expansão Mercado Livre rodando via GH Actions schedule 24h
2. Deduplicação SKU 3-tier funcionando com fila de revisão manual para matches abaixo do threshold
3. pgvector embeddings populados (text-embedding-3-small, índice HNSW) com re-embedding assíncrono
4. FastAPI com todos os 5 endpoints GET /paddles funcionando + GET /health
5. Railway provisionado para API staging

## Known Decisions (from Memory)
- Use text-embedding-3-small for embeddings
- RapidFuzz threshold: ≥ 0.85 for dedup
- Async re-embedding via needs_reembed flag
- FastAPI endpoints: GET /paddles, GET /paddles/{id}, GET /paddles/{id}/prices, GET /paddles/{id}/latest-prices, GET /health
- Telegram alerts for crawler failures (after 3 retries)
- GitHub Actions for orchestration (not Prefect)
- Railway for API staging (not Phase 6)

## Proposed Plans (5 total)
1. 02-01: Crawlers Drop Shot Brasil + Mercado Livre expansão
2. 02-02: Normalização + deduplicação SKU 3-tier + fila de revisão
3. 02-03: GitHub Actions schedule + Railway provisioning
4. 02-04: pgvector embeddings + re-embedding assíncrono
5. 02-05: FastAPI endpoints

## Architectural Context
- Monorepo structure: backend/ (FastAPI) + frontend/ (Next.js) + pipeline/ (crawlers)
- PostgreSQL with pgvector extension (via Supabase)
- Firecrawl for web scraping
- Redis cache TBD (Phase 3)
