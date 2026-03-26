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

## Current Milestone: v1.0 — MVP → Beta Launch

**Goal:** Plataforma completa em produção com crawlers BR ativos, agente de IA funcional e links de afiliado gerando cliques.

**Target features:**
- Foundation: monorepo + PostgreSQL/pgvector + Supabase + crawler BR + Mercado Livre Afiliados
- Full data pipeline: todos os varejistas BR, dedup, embeddings, GitHub Actions schedule, Railway
- RAG agent: eval gate OSS + streaming SSE + prompt engineering + Redis + Langfuse
- Frontend: Next.js 14 anônimo-first + quiz + Route Handler proxy + Admin Panel
- SEO + Clerk auth + alertas de preço (Resend) + histórico de preços
- Deploy prod + CI/CD + 50-user beta

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-03-26*
