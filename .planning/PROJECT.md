# PickleIQ — Plataforma de Inteligência de Dados & IA para Pickleball

## O que estamos construindo

PickleIQ é uma plataforma web que combina monitoramento automatizado de preços de mercado com um agente de IA conversacional para ajudar jogadores de pickleball a escolherem raquetes. A plataforma usa scraping via Firecrawl para coletar preços e especificações técnicas de varejistas brasileiros em tempo real, e um agente RAG (Retrieval-Augmented Generation) para traduzir métricas técnicas em linguagem simples e recomendar produtos personalizados.

## Por que existe

O mercado de pickleball cresceu no Brasil e os compradores enfrentam dois problemas: (1) métricas técnicas incompreensíveis como swingweight e twistweight, e (2) preços fragmentados entre varejistas sem visibilidade centralizada. A PickleIQ resolve ambos e monetiza via comissões de afiliados de 10-40% por venda. Fundador tem parceiro treinador profissional que valida o conceito e quer distribuir para alunos.

## Para quem é

- **Iniciante entusiasmado (35-55 anos):** Quer recomendação personalizada em linguagem simples sem precisar entender jargões técnicos
- **Jogador intermediário analítico (28-45 anos):** Quer comparativo técnico com preço em tempo real de múltiplas fontes
- **Gift buyer:** Descreve o perfil do presenteado e orçamento, recebe sugestão direta com link de compra

## Stack Tecnológico

| Camada | Tecnologia | Decisão |
|---|---|---|
| Scraping | Firecrawl API `/extract` | — |
| Pipeline Orchestration | GitHub Actions (cron) | Prefect descartado — zero infra extra |
| Banco Relacional | PostgreSQL via Supabase | Native pgvector, free tier, sem Dockerfile custom |
| Banco Vetorial | pgvector (extensão Supabase) | Pinecone descartado — 500 raquetes não justificam serviço separado |
| LLM | Claude Sonnet via Anthropic API | Eval gate OSS em Phase 3.1 |
| Embeddings | OpenAI text-embedding-3-small | 200-400 tokens/doc, índice HNSW |
| Backend | Python + FastAPI | — |
| Frontend | Next.js 14 (App Router) + Tailwind + shadcn/ui | — |
| Auth | Clerk v5 | Deferido para Phase 5 — anônimo-first até lá |
| Cache | Redis | Adicionado apenas Phase 3 (pgvector query cache) |
| Hospedagem Backend | Railway | Provisionado Phase 2 |
| Hospedagem Frontend | Vercel | — |
| Observabilidade LLM | Langfuse | — |
| Afiliados | Mercado Livre Afiliados (primário) | Amazon PA-API deferido pós-launch |
| Alertas Crawler | Telegram bot | Após 3 retries Firecrawl |
| Streaming Chat | SSE via Route Handler proxy | Next.js → FastAPI; useChat não wired diretamente |

## Varejistas

**Preço (BR):** Brazil Pickleball Store, Franklin Pickleball Brasil, Head Brasil, JOOLA Brasil, Drop Shot Brasil, Mercado Livre

**Spec enrichment apenas (internacionais):** PickleballCentral, Fromuth Pickleball, Johnkew — não são varejistas de preço para o mercado BR

## O que "done" parece

**MVP (beta):**
- Máximo de raquetes indexadas dos varejistas BR ativos com preços atualizados a cada 24h
- Chat conversacional que recomenda raquetes com justificativa personalizada em < 3s (P95)
- Cards de produto com menor preço atual + link de afiliado
- Comparador side-by-side com gráfico radar
- Deploy em produção (Vercel + Railway + Supabase)

**Métricas de sucesso:**
- 500 MAU no mês 3 pós-lançamento
- Taxa de conversão ≥ 3% (clique → compra)
- NPS ≥ 50 após 90 dias
- MRR USD 1.000 no mês 9

## Decisões Chave (pós /plan-eng-review)

- **pgvector no Supabase** — não Pinecone. 500 raquetes não justificam serviço vetorial separado
- **Anônimo-first até Phase 4** — Clerk auth deferido para Phase 5; price alerts exigem auth
- **GitHub Actions** — não Prefect. Migrar só se jobs > 6h ou DAG complexo
- **Entidade: `paddles`** — tabela principal, endpoints `/api/paddles/`
- **Sem Redis em Phase 1/2** — adicionar Phase 3 quando cache pgvector for concreto
- **Route Handler proxy** — Next.js Route Handler chama FastAPI internamente e transforma SSE; `useChat` não conecta direto no FastAPI (formato incompatível)
- **Sem switch Haiku/Sonnet** — eval gate OSS (Groq/Llama 3.3 70B) em Phase 3.1
- **Spec enrichment matching** — normalize `(brand, model_name)`, RapidFuzz fallback ≥ 0.85; sem match → `review_queue` (type: spec_unmatched)
- **Pre-chat quiz** — 3 steps (nível → estilo → orçamento) antes do chat, sessionStorage, vai ao RAG context (Phase 4.2)
- **Admin Panel** — `/admin/queue` (review obrigatório) + `/admin/catalog` (CRUD livre), protegido por `ADMIN_SECRET`
- **Infra timing** — Supabase Phase 1, Railway Phase 2 (não Phase 6)
- **Mercado Livre Afiliados** — blocker pré-code: aprovação ainda pendente (2026-03-26)
- **Meta raquetes** — sem número fixo; ir com o que os varejistas tiverem
- **Stack de testes** — pytest + HTTPX + Vitest + Playwright + MSW (CI) / Docker (staging)

## Restrições

- Frontend responsivo via browser (sem app mobile nativo)
- Fora de escopo v1: análise de vídeo, marketplace de usados, coaching, wearables, outros esportes, painel B2B
- Anti-bot: proxies rotativos via Firecrawl
- CI/CD via GitHub Actions; cobertura de testes ≥ 80% no pipeline Python

## Contexto de Negócio

Receita via comissões de afiliados (10-40% por venda). Distribuição primária via parceiro treinador → alunos (WhatsApp groups). SEO como canal secundário (maturação 6-12 meses, começa Phase 5). URLs de afiliado geradas server-side — LLM nunca constrói URLs diretamente.

## Current State — v1.3 In Progress

**Phase 13 Complete:** 2026-04-02

Hybrid Modern Sports Tech design system implemented:

**Design System (HY-01–HY-12):**
- **Typography:** Google Fonts CDN (Instrument Sans, Inter, JetBrains Mono), CSS font variables
- **Color System:** Lime (#84CC16) for primary actions, Green (#76b900) for data elements
- **Components:** Button variants with lime borders, card components with hy-* classes
- **Navigation:** Logo with lime "IQ" accent, responsive header/footer
- **Class Migration:** Complete nv-* → hy-* migration, CSS aliases for backwards compatibility

**Key Deliverables:**
- 12 requirements (HY-01 through HY-12) verified
- 8 plans completed (4 original + 4 gap closure)
- Design system documented in DESIGN.md v2.0

---

### v1.2 — Core Web Vitals Optimization

**Shipped:** 2026-04-01

Milestone v1.2 complete. Production performance and accessibility compliance achieved:

**Performance:**
- **Image Optimization (11.1):** All images migrated to next/Image with responsive sizes, priority loading for hero images, automatic WebP/AVIF via Next.js
- **Font & Script Optimization (11.2):** Font loading optimized with display swap and adjustFontFallback, third-party scripts audited and documented
- **Layout Stability (11.3):** Skeleton placeholders with Suspense for async content, min-height containers prevent CLS, no layout shifts during font loading

**Monitoring & Accessibility:**
- **RUM & A11Y (11.4):** Vercel Speed Insights integrated with dynamic import (zero initial load), Lighthouse CI with strict budgets (LCP < 2500ms, CLS < 0.1), bundle analyzer with 150KB performance budget, WCAG 2.1 AA compliance with focus indicators and useAnnouncer hook

**Key Deliverables:**
- LCP, INP, CLS, TTFB targets defined and tracked via Vercel Speed Insights
- Lighthouse CI enforcing performance budgets in build pipeline
- WCAG 2.1 AA compliance audit passed
- 4 plans, 12 tasks completed

**Archived:** See `.planning/milestones/v1.2-ROADMAP.md`

## Previous Milestones

### v1.1 — Scraper Validation & E2E Testing

**Shipped:** 2026-04-01

Milestone v1.1 complete. Added 3 new phases:
- **Phase 07:** E2E Testing & Scraper Validation — 101 tests added, 94% coverage on Mercado Livre, Firecrawl error handling documented, data integrity verified ✓
- **Phase 08:** Navigation UX Fixes — Fixed /compare 404, removed Chat IA standalone nav, mobile nav gaps closed, enriched paddle data populated ✓
- **Phase 09:** Image Extraction — Two-phase Brazil Store crawler extracting real product images from individual pages, 6% → 80% real image coverage ✓

**Key Deliverables:**
- Comprehensive E2E test suite covering all 3 scrapers with mocked Firecrawl
- Fixed navigation gaps (broken links, quiz gate enforcement)
- Real product images replacing Unsplash placeholders
- 10 additional SUMMARY files, 38 total tasks across v1.1

**Archived:** See `.planning/milestones/v1.1-ROADMAP.md` and `.planning/MILESTONES.md`

### v1.0 — MVP

**Shipped:** 2026-03-28

All 6 phases complete. MVP delivered:
- **Phase 1:** Foundation & Data Infrastructure — Monorepo, PostgreSQL, Firecrawl crawler, Mercado Livre afiliados ✓
- **Phase 2:** Full Data Pipeline — Crawlers BR (Brazil Pickleball, Drop Shot), dedup, pgvector embeddings, Railway ✓
- **Phase 3:** RAG Agent & AI Core — Eval gate (Groq selected), streaming SSE, Redis cache, Langfuse observability ✓
- **Phase 4:** Frontend Chat & Product UI — Next.js 14, 3-step quiz, chat widget, comparator, affiliate tracking, admin panel ✓
- **Phase 5:** SEO & Growth Features — SSR product pages, Clerk auth, price alerts, Resend emails, price history ✓
- **Phase 6:** Launch & Deploy — Vercel + Railway + Supabase in production, CI/CD, beta launch ✓

**Key Deliverables:**
- 500+ paddle catalog with real-time pricing from 6 BR retailers
- Conversational RAG agent with <3s latency (P95)
- Next.js web app with quiz onboarding, chat, comparison, admin panel
- Full E2E deployment with observability (Langfuse)
- 28 test summaries across 20 plans — 100% phase completion

**Archived:** See `.planning/milestones/v1.0-ROADMAP.md`

## Next Milestone: v1.3

Phase 13 (Hybrid UI Redesign) complete. Ready for next phase planning or milestone completion.
Run `/gsd:progress` to see status, or `/gsd:complete-milestone` to finalize v1.3.

## Evolução

Este documento evolui nas transições de fase e limites de milestone.

*Última atualização: 2026-04-01 — v1.2 Core Web Vitals Optimization shipped*

**Após cada transição de fase** (via `/gsd:transition`):
1. Requisitos invalidados? → Mover para Out of Scope com razão
2. Requisitos validados? → Mover para Validados com referência de fase
3. Novos requisitos emergiram? → Adicionar a Ativos
4. Decisões para registrar? → Adicionar a Decisões Chave
5. "O que Isso É" ainda preciso? → Atualizar se divergiu

**Após cada milestone** (via `/gsd:complete-milestone`):
1. Revisão completa de todas as seções
2. Verificação de Valor Central — ainda a prioridade certa?
3. Auditoria Out of Scope — razões ainda válidas?
4. Atualizar Context com estado atual

---

*Last updated: 2026-04-02
