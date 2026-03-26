# PickleIQ — Roadmap

**Projeto:** PickleIQ — Plataforma de Inteligência de Dados & IA para Pickleball
**Versão:** 1.0 (MVP → Beta)
**Granularidade:** Standard
**Modo:** YOLO | Paralelo | Research habilitado | Plan Check habilitado

---

## Milestone 1: MVP → Beta Launch

**Objetivo:** Plataforma completa em produção com o máximo de raquetes cobertas pelos crawlers ativos, agente de IA funcional e links de afiliado ativos.

**Critério de conclusão:** 50 usuários beta usando a plataforma, affiliate links gerando cliques, NPS ≥ 50 após 30 dias de beta.

---

### Phase 1 — Foundation & Data Infrastructure
**Goal:** Ambiente de desenvolvimento configurado e primeiro crawler funcional salvando dados no PostgreSQL.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 1.1 | Monorepo setup: estrutura `backend/` + `frontend/` + `pipeline/`, Docker Compose (PostgreSQL), `.env.example` + **provisionar Supabase** (pgvector nativo, staging desde Phase 1) | P0 |
| 1.2 | Schema PostgreSQL: tabelas `paddles`, `retailers`, `price_snapshots`, `paddle_specs`, `paddle_embeddings`, `review_queue`, `users`, `price_alerts` + materialized view `latest_prices` | P0 |
| 1.3 | Crawler Brazil Pickleball Store via Firecrawl `/extract` com retry (3x backoff), alerta Telegram em falha persistente e persistência no banco | P0 |
| 1.4 | Mercado Livre Afiliados integration: busca de raquetes via ML API, extração de dados (ASIN/item_id, preço, disponibilidade, URL com tag de afiliado), salvar em `price_snapshots` | P1 |

**Dependências:** Nenhuma (fase inicial)
**Entregáveis:** Dev environment funcional, schema criado, ≥ 50 raquetes dos varejistas BR (+ Mercado Livre) indexadas

> **Nota sobre varejistas internacionais:** Sites como PickleballCentral, Fromuth Pickleball, Johnkew e PickleballEffect são usados exclusivamente para **enriquecimento de specs técnicas** (swingweight, twistweight, etc.) — não como varejistas de preço. O mercado-alvo é brasileiro.

---

### Phase 2 — Full Data Pipeline
**Goal:** Pipeline completo cobrindo todos os varejistas BR, com deduplicação, spec enrichment e embeddings pgvector.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 2.1 | Crawlers Drop Shot Brasil + Mercado Livre (expansão) via Firecrawl `/extract` | P0 |
| 2.2 | Normalização + deduplicação SKU 3-tier (SKU fabricante → title hash → RapidFuzz) + fila de revisão manual | P0 |
| 2.3 | GitHub Actions schedule (cron 24h): orquestração de todos os crawlers, retry com exponential backoff, alerta Telegram em falha persistente + **provisionar Railway** (API staging) | P0 |
| 2.4 | pgvector embeddings: extensão `vector` no Supabase, embeddings `text-embedding-3-small` (200-400 tokens/doc), índice HNSW, re-embedding assíncrono via flag `needs_reembed` + job noturno | P1 |
| 2.5 | FastAPI endpoints: `GET /paddles`, `GET /paddles/{id}`, `GET /paddles/{id}/prices`, `GET /paddles/{id}/latest-prices`, `GET /health` | P0 |

**Dependências:** Phase 1 completa
**Entregáveis:** Catálogo indexado (máximo de raquetes cobertas pelos varejistas ativos), API funcional, pgvector populado, pipeline rodando 24h

---

### Phase 3 — RAG Agent & AI Core
**Goal:** Agente conversacional recomendando raquetes com latência < 3s, com observabilidade via Langfuse.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 3.1 | Estrutura do agente RAG: **eval gate de modelo** (10 queries PT-BR, score ≥ 4.0/5.0 → OSS via Groq; < 4.0 → Claude Sonnet) + busca pgvector + geração de recomendação | P0 |
| 3.2 | Sistema de prompt: tradução de métricas (swingweight, twistweight, core, face) + regras de affiliate URL + uso de perfil vindo do quiz de onboarding | P0 |
| 3.3 | Endpoint `POST /chat` com streaming SSE, filtros SQL + pgvector, top-3 recomendações | P0 |
| 3.4 | Otimização de latência: cache de queries frequentes (Redis adicionado aqui), budget P95 < 3s (pgvector < 50ms + context assembly < 100ms + LLM < 2.5s) | P1 |
| 3.5 | Langfuse: traces de LLM, dashboard de latência/tokens/custo, alertas de P95 > 3s | P1 |

**Dependências:** Phase 2 completa (pgvector populado + API rodando)
**Entregáveis:** Agente funcional P95 < 3s, modelo escolhido via eval gate, traces no Langfuse, testes de qualidade de recomendação

---

### Phase 4 — Frontend: Chat & Product UI
**Goal:** Interface web completa com chat de IA, comparador de raquetes e tracking de afiliados.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 4.1 | Next.js 14 scaffolding: App Router + Tailwind + shadcn/ui + layout base (sem auth — anônimo-first) | P0 |
| 4.2 | Quiz de onboarding (3 steps: nível → estilo → orçamento) + Chat widget via Route Handler proxy (Next.js → FastAPI) + Vercel AI SDK `useChat` + cards de produto inline | P0 |
| 4.3 | Página de comparação: search/autocomplete, tabela side-by-side, RadarChart (Recharts, `ssr: false`) | P0 |
| 4.4 | Tracking de afiliados: `fetch` com `keepalive: true`, Edge Route Handler, logs server-side | P1 |
| 4.5 | Admin Panel: `/admin/queue` (duplicatas, specs não-matched, anomalias de preço — ação obrigatória) + `/admin/catalog` (CRUD de paddles, ajuste fino livre) — protegido por `ADMIN_SECRET` env var | P1 |

**Dependências:** Phase 3 completa (endpoint `/chat` funcional)
**Entregáveis:** Frontend deployado no Vercel (preview), chat funcional com recomendações, comparador operacional

---

### Phase 5 — SEO & Growth Features
**Goal:** Páginas SSR/SEO indexáveis, alertas de preço funcionais e histórico de preços visível.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 5.1 | Páginas de produto SSR: `generateMetadata()`, Schema.org/Product JSON-LD, slug `/paddles/[brand]/[model]`, ISR para listings | P0 |
| 5.2 | Auth + Price alerts: Clerk v5 com `clerkMiddleware()` + favoritar produto + preço-alvo, worker GH Actions 24h, e-mail Resend + React Email | P1 |
| 5.3 | Histórico de preços: gráfico de linha 90/180 dias, indicador "Bom momento para comprar" (≤ P20) | P1 |
| 5.4 | Pillar page SEO: "Best Pickleball Paddles for Beginners" + FTC disclosure em todas as páginas com afiliados | P0 |

**Dependências:** Phase 4 completa (frontend base funcionando)
**Entregáveis:** Páginas indexáveis pelo Google, price alerts enviando e-mails, gráfico de histórico visível

---

### Phase 6 — Launch & Deploy
**Goal:** Plataforma em produção, CI/CD configurado, beta com 50 usuários iniciado.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 6.1 | Infraestrutura produção: promover Supabase (provisionado em Phase 1) e Railway (Phase 2) para produção + variáveis de env via painéis | P0 |
| 6.2 | CI/CD GitHub Actions: lint + testes em PR, cobertura ≥ 80% no pipeline Python, deploy automático main → Vercel | P0 |
| 6.3 | Observabilidade produção: logs estruturados, alertas de falha de scraping, Langfuse produção, health checks | P0 |
| 6.4 | Beta launch: deploy com dados reais (máximo de raquetes disponíveis), onboarding de 50 usuários, coleta de NPS | P0 |

**Dependências:** Phases 1-5 completas
**Entregáveis:** Produção estável, beta ativo, NPS baseline coletado

---

## Backlog (Milestone 2+)

| ID | Feature | Fase Origem PRD |
|----|---------|----------------|
| B1 | Expansão de catálogo: bolas, redes, calçados, vestuário | Fase 4 PRD |
| B2 | Analytics avançado: tendências de mercado e preferências de consumidores | Fase 4 PRD |
| B3 | Painel B2B para fabricantes e varejistas (modelo pago) | Fase 4 PRD |
| B4 | Contribuições da comunidade com moderação de specs técnicas | Risco PRD |
| B5 | Histórico de preços 180+ dias com análise de tendência | US-06 PRD |
| B6 | Integração com mais varejistas (expansão além dos 4 iniciais) | Escalabilidade |

---

## Timeline Estimada

| Fase | Duração Estimada | Acumulado |
|------|-----------------|-----------|
| Phase 1 | 2 semanas | Semana 2 |
| Phase 2 | 3 semanas | Semana 5 |
| Phase 3 | 2 semanas | Semana 7 |
| Phase 4 | 2 semanas | Semana 9 |
| Phase 5 | 2 semanas | Semana 11 |
| Phase 6 | 1 semana | Semana 12 |

**Beta launch estimado: Semana 12 (mês 3 de desenvolvimento)**

---

## KPIs de Sucesso

| Métrica | Meta | Verificar em |
|---------|------|-------------|
| Raquetes indexadas | Máximo dos varejistas ativos | Fim Phase 2 |
| Freshness de preços | Atualização a cada 24h | Fim Phase 2 |
| Latência agente IA (P95) | < 3s | Fim Phase 3 |
| Usuários beta | 50 | Fim Phase 6 |
| MAU (mês 3 pós-launch) | 500 | 3 meses após Phase 6 |
| Taxa de conversão afiliado | ≥ 3% clique→compra | 60 dias pós-launch |
| NPS | ≥ 50 | 90 dias pós-launch |
| MRR | USD 1.000 | Mês 9 |
