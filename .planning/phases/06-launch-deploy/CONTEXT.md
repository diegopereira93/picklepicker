# Phase 6: Launch & Deploy — Context & Requirements

## Phase Goal
Plataforma em produção, CI/CD configurado, beta com 50 usuários iniciado.

## Depends On
Phase 5 (MVP core features, search, Redis cache, Langfuse setup)

## Requirements Summary

### R6.1 — Infraestrutura de Produção
- **Frontend**: Vercel (hobby → pro as needed)
- **Backend API**: Railway
- **Database**: Supabase (recommended) or Railway with custom Dockerfile
  - PostgreSQL + pgvector
  - Environment variables via Vercel + Railway/Supabase panels (never in repo)
  - Domínio configurado

### R6.2 — CI/CD GitHub Actions
- Lint + tests on PR
- Coverage ≥ 80% for Python pipeline
- Automatic deploy: main → Vercel + preview PRs

### R6.3 — Observabilidade & Alertas
- Structured JSON logs
- Telegram alerts for scraping issues
- Langfuse production instance
- Health checks

### R6.4 — Beta Launch
- Deploy to production with ≥ 200 rackets indexed (500 is aspirational)
- Closed beta: 50 selected players
- NPS collection after 30 days (target ≥ 50)
- Affiliate links active with FTC disclosure

## Success Criteria
1. ✓ Supabase + Railway production with all env vars configured
2. ✓ CI/CD: lint + tests on PR, coverage ≥ 80% Python, auto-deploy main → Vercel
3. ✓ Observability: JSON logs, Telegram alerts, Langfuse production, health checks
4. ✓ Beta live: ≥ 200 rackets, 50 users onboarded, NPS baseline collected

## Current Project State
- **Phases 1-5**: Complete (MVP ready)
- **Tech Stack**: Next.js, FastAPI, PostgreSQL, Groq LLM, Langfuse, Redis
- **Production Services**: Vercel (frontend), Railway (backend candidate)
- **Database**: Supabase ready for production
