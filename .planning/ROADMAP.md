# Roadmap: PickleIQ

## Overview

Plataforma de inteligência de dados e IA para o mercado brasileiro de pickleball. Pipeline de scraping de preços BR → catálogo com pgvector embeddings → agente RAG conversacional → frontend Next.js com quiz de onboarding, comparador e links de afiliado ativos. Beta com 50 usuários em 12 semanas.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Foundation & Data Infrastructure** - Dev environment + schema + primeiro crawler + Mercado Livre integration
- [ ] **Phase 2: Full Data Pipeline** - Crawlers BR completos, deduplicação SKU, embeddings pgvector, FastAPI endpoints
- [ ] **Phase 3: RAG Agent & AI Core** - Agente conversacional PT-BR com eval gate de modelo, streaming SSE, latência P95 < 3s
- [ ] **Phase 4: Frontend Chat & Product UI** - Next.js 14 com quiz onboarding, chat widget, comparador de raquetes e admin panel
- [ ] **Phase 5: SEO & Growth Features** - Páginas SSR indexáveis, price alerts com Clerk + Resend, histórico de preços
- [ ] **Phase 6: Launch & Deploy** - Produção estável, CI/CD, observabilidade, beta 50 usuários

## Phase Details

### Phase 1: Foundation & Data Infrastructure
**Goal**: Ambiente de desenvolvimento configurado e primeiro crawler funcional salvando dados no PostgreSQL.
**Depends on**: Nothing (first phase)
**Requirements**: R1.1, R1.2, R1.3, R1.4
**Success Criteria** (what must be TRUE):
  1. Docker Compose sobe PostgreSQL com schema completo aplicado (todas as 8 tabelas + materialized view)
  2. Supabase provisionado (staging) com pgvector nativo disponível
  3. Crawler Brazil Pickleball Store extrai raquetes via Firecrawl, salva em price_snapshots com retry + alerta Telegram
  4. Mercado Livre Afiliados indexa raquetes com tag de afiliado ativa em price_snapshots
  5. ≥ 50 raquetes indexadas no total entre varejistas BR + Mercado Livre
**Plans**: 4 plans

Plans:
- [x] 01-01: Monorepo setup (backend/ + frontend/ + pipeline/), Docker Compose PostgreSQL, .env.example, provisionar Supabase staging
- [x] 01-02: Schema PostgreSQL — tabelas paddles, retailers, price_snapshots, latest_prices, paddle_specs, paddle_embeddings, review_queue, users, price_alerts
- [ ] 01-03: Crawler Brazil Pickleball Store via Firecrawl /extract com retry 3x backoff, alerta Telegram em falha persistente
- [ ] 01-04: Mercado Livre Afiliados integration — busca via ML API, extração item_id/preço/URL afiliado, salvar em price_snapshots

### Phase 2: Full Data Pipeline
**Goal**: Pipeline completo cobrindo todos os varejistas BR, com deduplicação, spec enrichment e embeddings pgvector.
**Depends on**: Phase 1
**Requirements**: R2.1, R2.2, R2.3, R2.4, R2.5
**Success Criteria** (what must be TRUE):
  1. Crawlers Drop Shot Brasil + expansão Mercado Livre rodando via GH Actions schedule 24h
  2. Deduplicação SKU 3-tier funcionando com fila de revisão manual para matches abaixo do threshold
  3. pgvector embeddings populados (text-embedding-3-small, índice HNSW) com re-embedding assíncrono
  4. FastAPI com todos os 5 endpoints GET /paddles funcionando + GET /health
  5. Railway provisionado para API staging
**Plans**: 5 plans

Plans:
- [ ] 02-01: Crawlers Drop Shot Brasil + Mercado Livre expansão via Firecrawl /extract
- [ ] 02-02: Normalização + deduplicação SKU 3-tier (SKU fabricante → title hash → RapidFuzz ≥ 0.85) + fila de revisão manual
- [ ] 02-03: GitHub Actions schedule (cron 24h) — orquestração crawlers, retry exponential backoff, alerta Telegram + provisionar Railway
- [ ] 02-04: pgvector embeddings — extensão vector Supabase, text-embedding-3-small, índice HNSW, re-embedding assíncrono via needs_reembed flag
- [ ] 02-05: FastAPI endpoints — GET /paddles, GET /paddles/{id}, GET /paddles/{id}/prices, GET /paddles/{id}/latest-prices, GET /health

### Phase 3: RAG Agent & AI Core
**Goal**: Agente conversacional recomendando raquetes com latência < 3s, com observabilidade via Langfuse.
**Depends on**: Phase 2
**Requirements**: R3.1, R3.2, R3.3, R3.4
**Success Criteria** (what must be TRUE):
  1. Eval gate executado: 10 queries PT-BR avaliadas, modelo selecionado (OSS Groq se ≥ 4.0, Claude Sonnet se < 4.0), resultado documentado
  2. POST /chat com streaming SSE retorna top-3 recomendações em P95 < 3s
  3. Sistema de prompt traduz swingweight/twistweight/core/face para linguagem simples PT-BR
  4. Degraded mode: se LLM timeout em 8s → SSE event type:degraded com top-3 por preço
  5. Langfuse traces de latência, tokens e custo por query
**Plans**: 5 plans

Plans:
- [ ] 03-01: Estrutura agente RAG — eval gate modelo (10 queries PT-BR, score ≥ 4.0 → Groq, < 4.0 → Claude Sonnet) + busca pgvector
- [ ] 03-02: Sistema de prompt — tradução de métricas (swingweight/twistweight/core/face) + regras affiliate URL + perfil do quiz
- [ ] 03-03: Endpoint POST /chat com streaming SSE, filtros SQL + pgvector, top-3 recomendações
- [ ] 03-04: Otimização latência — Redis cache queries frequentes (TTL 3600s), budget P95 < 3s, degraded mode 8s timeout
- [ ] 03-05: Langfuse — traces LLM, dashboard latência/tokens/custo, alertas P95 > 3s

### Phase 4: Frontend Chat & Product UI
**Goal**: Interface web completa com chat de IA, comparador de raquetes e tracking de afiliados.
**Depends on**: Phase 3
**Requirements**: R4.1, R4.2, R4.3, R4.4, R4.5
**Success Criteria** (what must be TRUE):
  1. Next.js 14 App Router deployado no Vercel (preview) com Tailwind + shadcn/ui
  2. Quiz onboarding 3 steps (nível → estilo → orçamento) → chat widget funcional com produto cards inline
  3. Comparador de raquetes com search/autocomplete, tabela side-by-side e RadarChart
  4. Affiliate click tracking com keepalive fetch + Edge Route Handler logging
  5. Admin panel /admin/queue + /admin/catalog protegido por ADMIN_SECRET
**Plans**: 5 plans

Plans:
- [ ] 04-01: Next.js 14 scaffolding — App Router + Tailwind + shadcn/ui + layout base (anônimo-first, sem auth)
- [ ] 04-02: Quiz onboarding (3 steps) + Chat widget (Route Handler proxy → FastAPI, useChat, SSE transform, product cards inline)
- [ ] 04-03: Página de comparação — search/autocomplete, tabela side-by-side, RadarChart Recharts (ssr: false)
- [ ] 04-04: Tracking de afiliados — fetch keepalive, Edge Route Handler logging, UTM params preservados
- [ ] 04-05: Admin Panel — /admin/queue (review queue) + /admin/catalog (CRUD paddles) protegido por ADMIN_SECRET

### Phase 5: SEO & Growth Features
**Goal**: Páginas SSR/SEO indexáveis, alertas de preço funcionais e histórico de preços visível.
**Depends on**: Phase 4
**Requirements**: R5.1, R5.2, R5.3, R5.4
**Success Criteria** (what must be TRUE):
  1. Páginas de produto com generateMetadata() + Schema.org JSON-LD indexadas pelo Google
  2. Clerk v5 auth + price alerts enviando e-mails via Resend após worker GH Actions 24h
  3. Gráfico de histórico de preços 90/180 dias com indicador "Bom momento para comprar" (≤ P20)
  4. Pillar page "Best Pickleball Paddles for Beginners" com FTC disclosure acima do primeiro link
**Plans**: 4 plans

Plans:
- [ ] 05-01: Páginas produto SSR — generateMetadata(), Schema.org/Product JSON-LD, slug /paddles/[brand]/[model], ISR listings
- [ ] 05-02: Auth Clerk v5 + price alerts — clerkMiddleware(), favoritar produto, worker GH Actions 24h, e-mail Resend + React Email
- [ ] 05-03: Histórico de preços — gráfico linha 90/180 dias, indicador "Bom momento para comprar" (≤ P20 últimos 90 dias)
- [ ] 05-04: Pillar page SEO — "Best Pickleball Paddles for Beginners" + FTC disclosure obrigatória em todas as páginas com afiliados

### Phase 6: Launch & Deploy
**Goal**: Plataforma em produção, CI/CD configurado, beta com 50 usuários iniciado.
**Depends on**: Phase 5
**Requirements**: R6.1, R6.2, R6.3, R6.4
**Success Criteria** (what must be TRUE):
  1. Supabase + Railway promovidos para produção com todas as env vars configuradas
  2. CI/CD GitHub Actions: lint + testes em PR, cobertura ≥ 80% pipeline Python, deploy automático main → Vercel
  3. Observabilidade: logs estruturados JSON, alertas Telegram, Langfuse produção, health checks
  4. Beta ativo: ≥ 200 raquetes indexadas, 50 usuários onboarded, NPS baseline coletado após 30 dias
**Plans**: 4 plans

Plans:
- [ ] 06-01: Infraestrutura produção — Supabase + Railway pro, variáveis env via painéis, domínio configurado
- [ ] 06-02: CI/CD GitHub Actions — lint + testes PR, cobertura ≥ 80% Python, deploy automático main → Vercel + preview PRs
- [ ] 06-03: Observabilidade produção — logs estruturados, alertas Telegram scraping, Langfuse produção, health checks
- [ ] 06-04: Beta launch — deploy dados reais, onboarding 50 usuários beta, coleta NPS após 30 dias

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Data Infrastructure | 2/4 | In Progress|  |
| 2. Full Data Pipeline | 0/5 | Not started | - |
| 3. RAG Agent & AI Core | 0/5 | Not started | - |
| 4. Frontend Chat & Product UI | 0/5 | Not started | - |
| 5. SEO & Growth Features | 0/4 | Not started | - |
| 6. Launch & Deploy | 0/4 | Not started | - |

---

## KPIs de Sucesso

| Métrica | Meta | Verificar em |
|---------|------|-------------|
| Raquetes indexadas | ≥ 200 (meta: 500) | Fim Phase 2 |
| Freshness de preços | Atualização a cada 24h | Fim Phase 2 |
| Latência agente IA (P95) | < 3s | Fim Phase 3 |
| Usuários beta | 50 | Fim Phase 6 |
| NPS | ≥ 50 | 90 dias após Phase 6 |
| Taxa conversão afiliado | ≥ 3% clique→compra | 60 dias pós-launch |

## Backlog (Milestone 2+)

- B1: Expansão catálogo — bolas, redes, calçados, vestuário
- B2: Analytics avançado — tendências mercado e preferências consumidores
- B3: Painel B2B para fabricantes e varejistas (modelo pago)
- B4: Contribuições comunidade com moderação de specs técnicas
- B5: Histórico preços 180+ dias com análise de tendência
- B6: Integração com mais varejistas (expansão além dos iniciais)
- B7: Amazon PA-API (requer 3 vendas qualificadas para ativar)
