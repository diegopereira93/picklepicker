# PickleIQ — Requirements

## Scope: v1.0 (MVP → Beta Launch)

---

## Table Stakes (must-have for any release)

- [ ] Plataforma web responsiva acessível via browser (sem app nativo)
- [ ] HTTPS em todas as rotas
- [ ] Chaves de API via environment variables (nunca hardcoded)
- [ ] FTC disclosure acima do primeiro link de afiliado em cada página (não apenas no footer)
- [ ] Consentimento de cookies + política de privacidade (GDPR/CCPA básico)
- [ ] Rate limiting na API pública
- [ ] CI/CD via GitHub Actions

---

## Phase 1 — Foundation & Data Infrastructure

### R1.1 — Ambiente de Desenvolvimento
- Docker Compose com PostgreSQL 16 (Redis adicionado na Fase 3 quando cache for necessário)
- Monorepo estruturado: `backend/` (Python/FastAPI) + `frontend/` (Next.js) + `pipeline/` (scripts Python + GH Actions)
- `.env.example` documentando todas as variáveis necessárias

### R1.2 — Schema PostgreSQL
Tabelas obrigatórias:
- `paddles` — catálogo master de raquetes (nome, SKU fabricante, brand, imagens, specs técnicas)
- `retailers` — varejistas configurados (nome, URL base, tipo de integração)
- `price_snapshots` — append-only: `(paddle_id, retailer_id, price_brl, currency, in_stock, scraped_at, source_raw JSONB)`
- `latest_prices` — materialized view com `DISTINCT ON (paddle_id, retailer_id)` sobre `price_snapshots`
- `paddle_specs` — specs técnicas: swingweight, twistweight, weight_oz, grip_size, core_thickness_mm, face_material
- `paddle_embeddings` — embedding vector(1536), updated_at
- `review_queue` — itens flagrados para revisão manual: id, type, paddle_id, related_paddle_id, data JSONB, status, created_at
- `users`, `price_alerts` (estrutura base para Fase 5)

### R1.3 — Crawler Brazil Pickleball Store (Proof of Concept)
- Firecrawl `/extract` com JSON schema para: nome, preço em BRL, disponibilidade, imagem, URL, specs técnicas
- Retry automático com exponential backoff (3 tentativas)
- Alerta via Telegram bot em falha persistente (após 3 retries) — não e-mail
- Dados salvos em `price_snapshots` com `currency=BRL` e `source_raw` preservado
- Testar parser manualmente antes de automatizar no GH Actions

### R1.4 — Mercado Livre Afiliados Integration
- Busca de raquetes via ML API (categoria Esportes e Fitness)
- Extração: item_id, título, preço em BRL, disponibilidade, imagem, URL com tag de afiliado ML
- Programa formal existente: Mercado Livre Afiliados (aprovação imediata, sem gate de vendas)
- Salvar em `price_snapshots` com `currency=BRL`
- **Amazon PA-API → backlog pós-lançamento** (requer 3 vendas qualificadas para ativar)

> **Varejistas internacionais (PickleballCentral, Fromuth, Johnkew):** usados apenas para enriquecimento de specs técnicas (swingweight, twistweight, etc.) via scraping periódico + match por nome de modelo. Não são varejistas de preço para o usuário BR.

---

## Phase 2 — Full Data Pipeline

### R2.1 — Expansão de Crawlers (mercado BR)
- Crawlers para Drop Shot Brasil e expansão Mercado Livre via Firecrawl `/extract`
- Frequência: a cada 24h via GitHub Actions schedule
- Cobertura mínima: 500 raquetes indexadas antes do lançamento
- Crawlers de specs internacionais (PickleballCentral, Johnkew): job separado, sem salvar preços — apenas atualizar `paddle_specs`
- **Match de specs internacionais:** normalizar `(brand, model_name)` → lowercase + strip pontuação → match exato; fallback RapidFuzz threshold ≥ 0.85; sem match → fila de revisão manual (não atualizar automaticamente)

### R2.2 — Normalização & Deduplicação
- Estratégia 3-tier de deduplicação de SKU:
  1. Match por SKU do fabricante (quando disponível no HTML)
  2. Hash de título normalizado
  3. Fuzzy matching com RapidFuzz (threshold ≥ 0.85)
- Fila de revisão manual para matches abaixo do threshold
- `variant_label` capturado por snapshot (não normalizado na Fase 1)

### R2.3 — GitHub Actions Schedule (substitui Prefect)
- Workflow `.github/workflows/scrape.yml` com `schedule: cron('0 6 * * *')` (6h BRT)
- Jobs separados por varejista: `scrape-brazil-pickleball`, `scrape-franklin-br`, `scrape-head-br`, `scrape-joola-br`, `scrape-mercadolivre`, `enrich-specs`
- Retry: 3 tentativas com exponential backoff via `retry` action ou lógica Python nativa
- Falha persistente (3 retries): send email via GitHub Actions + Resend API
- Logs estruturados enviados para Railway (stdout JSON)
- **Migrar para Prefect apenas se:** jobs exceederem 6h runtime ou dependências complexas entre varejistas surgirem

### R2.4 — Pipeline de Embeddings (pgvector)
- Ativar extensão `vector` no PostgreSQL (Supabase tem nativo; Railway requer Dockerfile customizado)
- Um documento por raquete: texto narrativo de 200-400 tokens (specs + descrição + tradução de métricas)
- Coluna `embedding vector(1536)` na tabela `paddle_embeddings` (separada de `products` para performance)
- Índice HNSW: `CREATE INDEX ON paddle_embeddings USING hnsw (embedding vector_cosine_ops)`
- Embeddings gerados com `text-embedding-3-small` (OpenAI)
- Re-embedding assíncrono: trigger PostgreSQL em UPDATE de `paddle_specs` marca `needs_reembed = true` (não chama API imediatamente). Job GH Actions roda 1x/dia após o crawler: `SELECT WHERE needs_reembed=true` → batch OpenAI → reset flag. Evita 500 API calls síncronas em batch updates.
- Threshold mínimo de similaridade: 0.65 (abaixo disso: avisar o agente no contexto)

### R2.5 — FastAPI Endpoints
- `GET /paddles` — listagem com filtros (brand, price_range, skill_level, in_stock)
- `GET /paddles/{id}` — detalhes + specs + última versão de métricas traduzidas
- `GET /paddles/{id}/prices` — histórico de preços por varejista
- `GET /paddles/{id}/latest-prices` — preços atuais de todos os varejistas
- `GET /health` — health check para monitoring

---

## Phase 3 — RAG Agent & AI Core

### R3.1 — Arquitetura do Agente (sem LangChain/LlamaIndex)
- Raw SDK: pgvector (psycopg3) + SDK do modelo escolhido via eval gate
- **Sem extração de perfil conversacional** — perfil chega pré-preenchido do quiz de onboarding (nível, estilo, orçamento)
- **Eval gate de modelo (obrigatório antes de codar o agente):**
  - 10 queries representativas em PT-BR cobrindo: iniciante/intermediário/avançado × control/power/balanced × R$400-1200
  - Score humano 1-5 em: clareza da explicação, precisão técnica, tom em português, uso correto de analogias
  - Média ≥ 4.0 → usar modelo OSS (Llama 3.3 70B via Groq API, $0.59/MTok)
  - Média < 4.0 → Claude Sonnet (qualidade garantida, custo maior)
  - Documentar resultado do eval em `backend/evals/model-selection-{date}.md`
- **Fluxo único de recomendação:** perfil do quiz → busca pgvector → geração de resposta com modelo escolhido

### R3.2 — Chat Pipeline
- Endpoint FastAPI: `POST /chat` com streaming via Server-Sent Events
- Input obrigatório: `{ session_id, messages, profile: { level, style, budget_max } }` (perfil vindo do quiz)
- Máximo 3 recomendações por consulta, ordenadas por custo-benefício
- Filtros SQL aplicados antes da busca vetorial (in_stock=true, price_usd ≤ budget_max, skill_level match)
- Busca pgvector: cosine similarity, threshold 0.65, top-5 candidatos → reranking → top-3 resposta
- URLs de afiliados construídas server-side e passadas no contexto (proibido construir URLs no LLM)
- **Degraded mode contract:** se LLM não responder em 8s → SSE event `{type:"degraded", paddles:[...top-3 por preço]}`. Copy frontend: "Não consegui gerar uma explicação completa, mas aqui estão as melhores opções:" — inclui affiliate links (receita não interrompida). Nenhum indicador de qualidade reduzida visível ao usuário.

### R3.3 — Prompt Engineering — Tradução de Métricas
Sistema de mapeamento obrigatório:
- Swingweight < 100 → "Raquete ágil — ideal para reações rápidas na rede"
- Swingweight > 120 → "Mais potência — ideal para fundo de quadra"
- Twistweight < 6 → "Exige precisão — para jogadores experientes"
- Twistweight > 7 → "Sweet spot ampliado — perdoa erros de posicionamento"
- Core 13mm → "Resposta viva e potência — para jogadores agressivos"
- Core 16mm → "Mais controle e absorção — indicado para iniciantes"
- Face carbono T700 → "Durabilidade premium com spin consistente"
- Face fibra de vidro → "Toque suave e forgiving — ótimo para iniciantes"

### R3.4 — Performance & Observabilidade
- Streaming → time-to-first-token < 800ms
- Budget de latência: pgvector < 50ms + context assembly < 100ms + LLM streaming < 2.5s + overhead < 350ms ≈ P95 < 3s
- Redis adicionado aqui (primeira necessidade concreta): cache de queries pgvector frequentes → hits < 200ms. TTL = 3600s. Invalidar `redis.delete_pattern('pgvector:*')` ao final de cada crawler run bem-sucedido.
- Langfuse para traces de LLM (latência, tokens, custo por query)
- Degraded mode: se LLM não responder em 8s → retornar paddles sem narrativa com `type: "degraded"`

---

## Phase 4 — Frontend: Chat & Product UI

### R4.1 — Scaffolding Next.js 14
- App Router + Tailwind CSS + shadcn/ui
- **Sem auth (anônimo-first)** — Clerk adicionado na Fase 5 quando price alerts exigirem
- Edge runtime para rotas de AI chat e click tracking
- Node runtime para rotas de acesso a banco

### R4.2 — Quiz de Onboarding + Chat Widget
**Quiz de onboarding (pré-chat):**
- 3 steps sequenciais antes de abrir o chat: (1) Nível de jogo → (2) Estilo → (3) Orçamento máximo em R$
- UI com cards/botões grandes (não inputs de texto livre)
- Perfil salvo em `localStorage` com chave `pickleiq:profile:{uid}` (persiste entre sessões sem login). UUID anônimo gerado via `crypto.randomUUID()` no primeiro acesso e salvo em localStorage.
- Usuário pode editar o perfil a qualquer momento sem reiniciar o chat

**Chat Widget:**
- Next.js Route Handler (`/api/chat`) como proxy: recebe `useChat` → chama FastAPI → transforma SSE FastAPI para Vercel AI SDK data stream format (`0:"token"`, `2:[paddles]`, `d:{}`)
- `useChat` hook com `api: "/api/chat"` + `body: { profile }` passando o perfil do quiz
- Route Handler no Edge com `maxDuration = 30`. Propagar AbortSignal: `fetch(FASTAPI_URL, { signal: request.signal })` — cancela a chamada FastAPI quando o browser cancela (evita tokens desperdiçados).
- Cards de produto inline na resposta: imagem, nome, bullets de métricas traduzidas, menor preço em R$, botão de compra com link de afiliado
- Indicador de estoque: 🟢 in-stock / 🟡 poucas unidades / 🔴 out-of-stock

### R4.3 — Página de Comparação
- Seleção de 2-3 raquetes via search/autocomplete
- Tabela side-by-side: specs técnicas + tradução em linguagem simples
- Gráfico radar: Potência, Controle, Manobrabilidade, Sweet Spot, Custo-Benefício
- Recharts `RadarChart` com `dynamic(() => import(...), { ssr: false })`
- Menor preço e link de compra por raquete

### R4.5 — Admin Panel

**Backend (criado em Phase 2, junto com a dedup logic):**
- `GET /admin/queue` — lista itens flagrados (tipo: `duplicate` | `spec_unmatched` | `price_anomaly`), ordenados por prioridade
- `PATCH /admin/queue/{id}/resolve` — resolve um item: `{ action: "merge" | "reject" | "manual", data?: {...} }`
- `GET /admin/paddles` + `PATCH /admin/paddles/{id}` — CRUD do catálogo
- Todos os endpoints protegidos por middleware `Authorization: Bearer $ADMIN_SECRET`

**Frontend (`/admin` no Next.js — Phase 4.5):**
- `/admin/queue` — Review Queue: itens automáticos aguardando decisão humana
  - Card por item: o que foi detectado, sugestão automática, botões de ação
  - Filtro por tipo (duplicata / spec / preço)
- `/admin/catalog` — Catálogo completo de paddles: busca, edição inline de specs, visualização de preços por varejista
- Acesso via `ADMIN_SECRET` no header (sem Clerk — simples e seguro para uso solo)

**Tabela `review_queue` (adicionar ao schema Phase 1.2):**
```sql
review_queue: id, type (duplicate|spec_unmatched|price_anomaly),
              paddle_id, related_paddle_id, data JSONB,
              status (pending|resolved|dismissed),
              resolved_at, resolved_by, created_at
```

### R4.4 — Tracking de Afiliados
- `fetch` com `keepalive: true` no click — obrigatório para capturar navegações
- Log server-side via Edge Route Handler: `(user_id?, paddle_id, retailer, timestamp, utm_params)`
- Parâmetros UTM preservados nos links de afiliado

---

## Phase 5 — SEO & Growth Features

### R5.1 — Páginas de Produto (SSR/SEO)
- Server Components + `generateMetadata()` por produto
- `<script type="application/ld+json">` com Schema.org/Product (name, offers, aggregateRating)
- Product detail pages: SSR (sempre fresh)
- Listing pages: ISR com `revalidate: 3600`
- URL slug: `/paddles/[brand]/[model-slug]`

### R5.2 — Auth (Clerk) + Price Alerts
- **Clerk v5 introduzido aqui** com `clerkMiddleware()` — primeira necessidade concreta de auth
- Usuário favorita produto + define preço-alvo (requer login)
- Histórico de conversas e perfil salvo persistentemente pós-login (upgrade do sessionStorage anônimo)
- Worker Prefect verifica `latest_prices` vs `price_alerts` a cada 24h
- E-mail transacional via Resend (free tier: 3K/mês) com React Email
- Unsubscribe link em todos os e-mails (compliance)

### R5.3 — Histórico de Preços
- Gráfico de linha: variação de preço 90/180 dias por produto + varejista
- Indicador: "Bom momento para comprar" quando preço ≤ percentil 20 dos últimos 90 dias
- Dados servidos por `GET /paddles/{id}/price-history?days=90`

### R5.4 — Blog / Conteúdo SEO
- Páginas estáticas de review por produto (SSG + ISR)
- Pillar page prioritária: "Best Pickleball Paddles for Beginners"
- FTC disclosure obrigatória: bloco visível acima do primeiro link de afiliado

---

## Phase 6 — Launch & Deploy

### R6.1 — Infraestrutura de Produção
- Frontend: Vercel (plano hobby → pro conforme necessidade)
- Backend API: Railway
- PostgreSQL + pgvector: **Supabase recomendado** (pgvector nativo, tier gratuito suficiente para MVP, sem Dockerfile customizado) — Railway como alternativa com Dockerfile customizado
- Variáveis de ambiente via painel Vercel + Railway/Supabase (nunca em repositório)

### R6.2 — CI/CD
- GitHub Actions: lint + testes em cada PR
- Cobertura de testes ≥ 80% no pipeline Python
- Deploy automático para Vercel on merge to main
- Preview deployments para cada PR no Vercel

### R6.3 — Observabilidade & Alertas
- Logs estruturados (JSON) no backend
- Alerta de falha de scraping: Telegram bot após 3 retries consecutivos falhando (não e-mail)
- Langfuse dashboard configurado para produção
- Health check endpoint monitorado

### R6.4 — Beta Launch
- Deploy completo em produção com o máximo de raquetes cobertas pelos crawlers ativos (meta orientativa: ≥ 200; 500 é aspiracional — ir com o que os varejistas tiverem)
- Beta fechado: 50 jogadores selecionados
- Coleta de NPS após 30 dias (meta ≥ 50)
- Affiliate links ativos com FTC disclosure em todas as páginas relevantes

---

## Out of Scope (v1.0)

- App mobile nativo (iOS/Android)
- Análise de vídeo / biomecânica
- Marketplace de equipamentos usados
- Coaching ou conteúdo de treinamento
- Integração com wearables ou sensores
- Expansão para outros esportes (tênis, padel)
- Painel B2B para fabricantes/varejistas
- Contribuições da comunidade com moderação de specs

---

## Testing Strategy (definida em /plan-eng-review 2026-03-26)

### Stack
| Camada | Framework | Uso |
|--------|-----------|-----|
| Backend Python | pytest + pytest-asyncio + HTTPX TestClient | Pipeline, FastAPI endpoints, workers |
| Frontend TS | Vitest + Testing Library | Componentes React, Route Handler logic |
| E2E | Playwright + MSW (CI) / Docker real (staging) | Fluxos críticos ponta-a-ponta |
| LLM Evals | Claude-as-judge (5 critérios, rubrica fixa) | Eval gate Phase 3.1, regressão de prompts |

### Cobertura mínima (CI gate em R6.2)
- Python pipeline: ≥ 80% (pytest-cov)
- FastAPI endpoints: 100% happy path + auth errors
- Frontend crítico (Route Handler SSE transform, Quiz): 100%
- E2E: 3 fluxos críticos (ver abaixo)

### Testes obrigatórios por módulo

**Phase 1 — Crawler**
- `pipeline/tests/test_brazil_store_crawler.py`
  - Happy path: Firecrawl /extract → salva em price_snapshots
  - Retry: 3 tentativas com backoff crescente (mock 5xx)
  - Persistent failure: após 3 retries → Telegram alert disparado
  - Partial data: preço ausente, imagem ausente → comportamento definido

**Phase 2 — Spec Enrichment & Dedup**
- `pipeline/tests/test_spec_matcher.py`
  - Exact match: normaliza (brand, model) → atualiza paddle_specs
  - Fuzzy ≥ 0.85: aceito (casos calibrados: score 0.85 e 0.86)
  - Fuzzy 0.84: rejeitado → review_queue (type: spec_unmatched)
  - Score < 0.50: rejeitado, sem confusão com match
- `backend/tests/test_admin_endpoints.py`
  - GET /admin/queue: 200 com ADMIN_SECRET, 401 sem token
  - GET /admin/queue?type=duplicate: filtra corretamente
  - PATCH /admin/queue/{id}/resolve: status → resolved/dismissed no DB

**Phase 3 — RAG Agent**
- `backend/tests/test_chat_handler.py`
  - Filter extraction: parses level/budget/style da mensagem
  - SQL filters: in_stock=true, price_brl ≤ budget, skill_level match
  - pgvector: todos resultados < 0.65 → warning no contexto do agente
  - SSE stream: eventos token / paddles / done emitidos em ordem
  - Degraded mode: mock LLM timeout 8s → response type='degraded' com paddles
  - Affiliate URL: construída server-side, nunca pelo LLM
- `backend/tests/test_redis_cache.py`
  - Cache hit: retorna em <200ms sem chamar pgvector
  - Cache miss: chama pgvector, armazena resultado
- `backend/evals/` (LLM-as-judge)
  - 10 queries PT-BR avaliadas em 5 critérios (acurácia, PT-BR, não alucina, preço em R$, ≤3 paddles)
  - Score ≥ 4.0/5.0 → seleciona OSS (Groq); < 4.0 → Claude Sonnet
  - Resultados em `backend/evals/model-selection-{date}.md`

**Phase 4 — Frontend**
- `frontend/tests/unit/route-handler-proxy.test.ts` (Vitest)
  - SSE FastAPI `{type:token,content:"x"}` → Vercel AI SDK `0:"x"` (formato exato)
  - FastAPI unreachable → 503 (não silent failure)
  - FastAPI timeout → error propagado ao client
- `frontend/tests/unit/quiz.test.ts` (Vitest)
  - 3 steps renderizados sequencialmente
  - Profile salvo em sessionStorage após step 3
  - Edit mid-chat → próximo request inclui perfil atualizado
  - Avanço bloqueado sem seleção
- `frontend/tests/unit/affiliate.test.ts` (Vitest)
  - keepalive fetch dispara no click
  - Edge Handler loga paddle_id, retailer, timestamp
- `frontend/tests/unit/radar-chart.test.ts` (Vitest)
  - RadarChart não crasha em render server-side (ssr: false guard)

**E2E críticos (Playwright)**
- `e2e/full-user-flow.spec.ts` — quiz (3 steps) → chat → product cards → affiliate click
- `e2e/admin-queue.spec.ts` — login ADMIN_SECRET → queue item → resolve → item removido da fila
- `e2e/double-submit.spec.ts` — segundo submit bloqueado enquanto primeiro em andamento

**E2E target:**
- CI: Playwright com MSW interceptando chamadas FastAPI (rápido, zero Docker)
- Staging: Playwright contra FastAPI real em Docker Compose (manual ou scheduled)

---

## Open Questions (verificar antes de iniciar fases específicas)

- [ ] Confirmar detalhes do programa de afiliados da Fromuth (contato direto necessário)
- [ ] Confirmar rede do Selkirk affiliate (Impact Radius vs ShareASale vs direto)
- [ ] Verificar volume atual de keywords via Ahrefs/Semrush antes da Fase 5
- [ ] Confirmar pricing do Firecrawl `/extract` por call para dimensionar o budget de 24h
- [ ] Testar se PickleballCentral e Fromuth expõem SKU do fabricante no HTML
- [ ] Amazon PA-API: confirmar se cobre todos os SKUs do catálogo target
- [ ] **BLOCKER Phase 0:** Confirmar aprovação no Mercado Livre Afiliados antes de iniciar Phase 1. Fallback se rejeitado: links diretos para varejistas BR sem comissão (rastrear clicks via `/go/` mesmo sem afiliados ativos).
- [ ] Mapear SKU count aproximado de cada varejista BR (Brazil Pickleball Store, Franklin BR, Head BR, JOOLA BR, Drop Shot Brasil, Mercado Livre) antes da Phase 2 — validar viabilidade de cobertura do catálogo.
