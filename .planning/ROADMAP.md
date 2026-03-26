# PickleIQ — Roadmap

**Projeto:** PickleIQ — Plataforma de Inteligência de Dados & IA para Pickleball
**Versão:** 1.0 (MVP → Beta)
**Granularidade:** Standard
**Modo:** YOLO | Paralelo | Research habilitado | Plan Check habilitado

---

## Milestone 1: MVP → Beta Launch

**Objetivo:** Plataforma completa em produção com ≥ 500 raquetes indexadas, agente de IA funcional e links de afiliado ativos.

**Critério de conclusão:** 50 usuários beta usando a plataforma, affiliate links gerando cliques, NPS ≥ 50 após 30 dias de beta.

---

### Phase 1 — Foundation & Data Infrastructure
**Goal:** Ambiente de desenvolvimento configurado e primeiro crawler funcional salvando dados no PostgreSQL.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 1.1 | Monorepo setup: estrutura `backend/` + `frontend/` + `pipeline/`, Docker Compose (PostgreSQL + Redis), `.env.example` | P0 |
| 1.2 | Schema PostgreSQL: tabelas `products`, `retailers`, `price_snapshots`, `paddle_specs`, `users`, `price_alerts` + materialized view `latest_prices` | P0 |
| 1.3 | Crawler PickleballCentral via Firecrawl `/extract` com retry, alertas de falha e persistência no banco | P0 |
| 1.4 | Amazon PA-API integration: busca por keyword, extração de dados, salvar em `price_snapshots` | P1 |

**Dependências:** Nenhuma (fase inicial)
**Entregáveis:** Dev environment funcional, schema criado, ≥ 50 raquetes da PickleballCentral + Amazon indexadas

---

### Phase 2 — Full Data Pipeline
**Goal:** Pipeline completo cobrindo todos os varejistas, com deduplicação e embeddings no Pinecone.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 2.1 | Crawlers Fromuth Pickleball + JustPaddles via Firecrawl `/extract` | P0 |
| 2.2 | Normalização + deduplicação SKU 3-tier (SKU fabricante → title hash → RapidFuzz) + fila de revisão manual | P0 |
| 2.3 | Pipeline Prefect: schedule 24h, orchestração de todos os crawlers, retry com exponential backoff | P0 |
| 2.4 | Pinecone setup: índice de raquetes (narrativo, 200-400 tokens/doc) + embeddings `text-embedding-3-small` | P1 |
| 2.5 | FastAPI endpoints: `GET /products`, `GET /products/{id}`, `GET /products/{id}/prices`, `GET /products/{id}/latest-prices` | P0 |

**Dependências:** Phase 1 completa
**Entregáveis:** ≥ 500 raquetes indexadas, API funcional, Pinecone populado, pipeline rodando 24h

---

### Phase 3 — RAG Agent & AI Core
**Goal:** Agente conversacional recomendando raquetes com latência < 3s, com observabilidade via Langfuse.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 3.1 | Estrutura do agente RAG: extração de perfil com Haiku (turns 1-3) + recomendação com Sonnet | P0 |
| 3.2 | Sistema de prompt: tradução de métricas (swingweight, twistweight, core, face) + regras de affiliate URL | P0 |
| 3.3 | Endpoint `POST /chat` com streaming SSE, filtros de metadata Pinecone, top-3 recomendações | P0 |
| 3.4 | Cache de perfis de usuário no Pinecone (namespace separado) + otimização de latência | P1 |
| 3.5 | Langfuse: traces de LLM, dashboard de latência/tokens/custo, alertas de P95 > 3s | P1 |

**Dependências:** Phase 2 completa (Pinecone populado + API rodando)
**Entregáveis:** Agente funcional P95 < 3s, traces no Langfuse, testes de qualidade de recomendação

---

### Phase 4 — Frontend: Chat & Product UI
**Goal:** Interface web completa com chat de IA, comparador de raquetes e tracking de afiliados.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 4.1 | Next.js 14 scaffolding: App Router + Tailwind + shadcn/ui + Clerk v5 + layout base | P0 |
| 4.2 | Chat widget: Vercel AI SDK `streamText` + `useChat`, Edge runtime, onboarding conversacional + cards de produto inline | P0 |
| 4.3 | Página de comparação: search/autocomplete, tabela side-by-side, RadarChart (Recharts, `ssr: false`) | P0 |
| 4.4 | Tracking de afiliados: `fetch` com `keepalive: true`, Edge Route Handler, logs server-side | P1 |

**Dependências:** Phase 3 completa (endpoint `/chat` funcional)
**Entregáveis:** Frontend deployado no Vercel (preview), chat funcional com recomendações, comparador operacional

---

### Phase 5 — SEO & Growth Features
**Goal:** Páginas SSR/SEO indexáveis, alertas de preço funcionais e histórico de preços visível.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 5.1 | Páginas de produto SSR: `generateMetadata()`, Schema.org/Product JSON-LD, slug `/paddles/[brand]/[model]`, ISR para listings | P0 |
| 5.2 | Price alerts: favoritar produto + preço-alvo (Clerk auth), worker Prefect 24h, e-mail Resend + React Email | P1 |
| 5.3 | Histórico de preços: gráfico de linha 90/180 dias, indicador "Bom momento para comprar" (≤ P20) | P1 |
| 5.4 | Pillar page SEO: "Best Pickleball Paddles for Beginners" + FTC disclosure em todas as páginas com afiliados | P0 |

**Dependências:** Phase 4 completa (frontend base funcionando)
**Entregáveis:** Páginas indexáveis pelo Google, price alerts enviando e-mails, gráfico de histórico visível

---

### Phase 6 — Launch & Deploy
**Goal:** Plataforma em produção, CI/CD configurado, beta com 50 usuários iniciado.

| Plan | Descrição | Prioridade |
|------|-----------|-----------|
| 6.1 | Infraestrutura produção: Vercel (frontend) + Railway (API + PostgreSQL) + Pinecone managed + variáveis de env | P0 |
| 6.2 | CI/CD GitHub Actions: lint + testes em PR, cobertura ≥ 80% no pipeline Python, deploy automático main → Vercel | P0 |
| 6.3 | Observabilidade produção: logs estruturados, alertas de falha de scraping, Langfuse produção, health checks | P0 |
| 6.4 | Beta launch: deploy com dados reais (≥ 500 raquetes), onboarding de 50 usuários, coleta de NPS | P0 |

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
| Raquetes indexadas | ≥ 500 | Fim Phase 2 |
| Freshness de preços | Atualização a cada 24h | Fim Phase 2 |
| Latência agente IA (P95) | < 3s | Fim Phase 3 |
| Usuários beta | 50 | Fim Phase 6 |
| MAU (mês 3 pós-launch) | 500 | 3 meses após Phase 6 |
| Taxa de conversão afiliado | ≥ 3% clique→compra | 60 dias pós-launch |
| NPS | ≥ 50 | 90 dias pós-launch |
| MRR | USD 1.000 | Mês 9 |
