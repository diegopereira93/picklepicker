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
- Docker Compose com PostgreSQL 16 + Redis
- Monorepo estruturado: `backend/` (Python/FastAPI) + `frontend/` (Next.js) + `pipeline/` (Prefect)
- `.env.example` documentando todas as variáveis necessárias

### R1.2 — Schema PostgreSQL
Tabelas obrigatórias:
- `products` — catálogo master de raquetes (nome, SKU fabricante, brand, imagens, specs técnicas)
- `retailers` — varejistas configurados (nome, URL base, tipo de integração)
- `price_snapshots` — append-only: `(product_id, retailer_id, price, currency, in_stock, variant_label, scraped_at, source_raw JSONB)`
- `latest_prices` — materialized view com `DISTINCT ON (product_id, retailer_id)` sobre `price_snapshots`
- `paddle_specs` — specs técnicas: swingweight, twistweight, weight_oz, grip_size, core_thickness_mm, face_material
- `users`, `price_alerts` (estrutura base para Fase 5)

### R1.3 — Crawler PickleballCentral (Proof of Concept)
- Firecrawl `/extract` com JSON schema para: nome, preço, disponibilidade, imagem, URL, specs técnicas
- Retry automático com exponential backoff (3 tentativas)
- Alerta por e-mail em falha persistente (após 3 retries)
- Dados salvos em `price_snapshots` com `source_raw` preservado

### R1.4 — Amazon PA-API Integration
- **Não usar Firecrawl para Amazon** — usar Amazon Product Advertising API v5
- Busca por keyword "pickleball paddle" na categoria Sports
- Extração: ASIN, título, preço, disponibilidade, imagem, URL com tag de afiliado
- Nota: requer 3 vendas qualificadas para ativar a PA-API; usar dados mockados no desenvolvimento

---

## Phase 2 — Full Data Pipeline

### R2.1 — Expansão de Crawlers
- Crawlers para Fromuth Pickleball e JustPaddles via Firecrawl `/extract`
- Frequência: a cada 24h via Prefect cron schedule
- Cobertura mínima: 500 raquetes indexadas antes do lançamento

### R2.2 — Normalização & Deduplicação
- Estratégia 3-tier de deduplicação de SKU:
  1. Match por SKU do fabricante (quando disponível no HTML)
  2. Hash de título normalizado
  3. Fuzzy matching com RapidFuzz (threshold ≥ 0.85)
- Fila de revisão manual para matches abaixo do threshold
- `variant_label` capturado por snapshot (não normalizado na Fase 1)

### R2.3 — Pipeline de Embeddings (Pinecone)
- Um documento por raquete: texto narrativo de 200-400 tokens (specs + descrição + tradução de métricas)
- Metadata no Pinecone: `product_id`, `brand`, `price_min`, `price_max`, `in_stock`, `skill_level`, `play_style`
- Embeddings gerados com `text-embedding-3-small` (OpenAI)
- Re-embedding automático quando specs ou preço mudam significativamente (±10%)
- Índice separado (namespace) para cache de perfis de usuário

### R2.4 — FastAPI Endpoints
- `GET /products` — listagem com filtros (brand, price_range, skill_level, in_stock)
- `GET /products/{id}` — detalhes + specs + última versão de métricas traduzidas
- `GET /products/{id}/prices` — histórico de preços por varejista
- `GET /products/{id}/latest-prices` — preços atuais de todos os varejistas
- Health check endpoint para monitoring

---

## Phase 3 — RAG Agent & AI Core

### R3.1 — Arquitetura do Agente (sem LangChain/LlamaIndex)
- Raw SDK: Pinecone SDK + Anthropic SDK direto
- **Fase de extração de perfil:** Claude Haiku (turns 1-3) — coletar nível, estilo, orçamento, preferências físicas
- **Fase de recomendação:** Claude Sonnet — busca semântica + geração de resposta

### R3.2 — Chat Pipeline
- Endpoint FastAPI: `POST /chat` com streaming via Server-Sent Events
- Máximo 3 recomendações por consulta, ordenadas por custo-benefício
- Filtros de metadata aplicados antes do reranking (in_stock, price_range, skill_level)
- URLs de afiliados passadas do Pinecone metadata explicitamente (proibido construir URLs no LLM)

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
- Streaming com `client.messages.stream()` → time-to-first-token < 800ms
- Cache Pinecone para queries frequentes (namespace separado) → hits < 200ms
- Meta P95: resposta completa < 3s
- Langfuse para traces de LLM (latência, tokens, custo por query)

---

## Phase 4 — Frontend: Chat & Product UI

### R4.1 — Scaffolding Next.js 14
- App Router + Tailwind CSS + shadcn/ui
- Clerk v5 com `clerkMiddleware()` (não `authMiddleware` deprecado)
- Edge runtime para rotas de AI chat e click tracking
- Node runtime para rotas de alertas e acesso a banco

### R4.2 — Chat Widget (AI Recommendation)
- Vercel AI SDK `streamText` + `useChat` hook
- Route Handler no Edge com `maxDuration = 30`
- Onboarding conversacional: nível → estilo → orçamento → preferências físicas
- Cards de produto inline na resposta do chat: imagem, nome, bullets de métricas traduzidas, menor preço atual, botão de compra com link de afiliado
- Indicador de estoque: 🟢 in-stock / 🟡 poucas unidades / 🔴 out-of-stock

### R4.3 — Página de Comparação
- Seleção de 2-3 raquetes via search/autocomplete
- Tabela side-by-side: specs técnicas + tradução em linguagem simples
- Gráfico radar: Potência, Controle, Manobrabilidade, Sweet Spot, Custo-Benefício
- Recharts `RadarChart` com `dynamic(() => import(...), { ssr: false })`
- Menor preço e link de compra por raquete

### R4.4 — Tracking de Afiliados
- `fetch` com `keepalive: true` no click — obrigatório para capturar navegações
- Log server-side via Edge Route Handler: `(user_id?, product_id, retailer, timestamp, utm_params)`
- Parâmetros UTM preservados nos links de afiliado

---

## Phase 5 — SEO & Growth Features

### R5.1 — Páginas de Produto (SSR/SEO)
- Server Components + `generateMetadata()` por produto
- `<script type="application/ld+json">` com Schema.org/Product (name, offers, aggregateRating)
- Product detail pages: SSR (sempre fresh)
- Listing pages: ISR com `revalidate: 3600`
- URL slug: `/paddles/[brand]/[model-slug]`

### R5.2 — Price Alerts
- Usuário favorita produto + define preço-alvo (requer autenticação Clerk)
- Worker Prefect verifica `latest_prices` vs `price_alerts` a cada 24h
- E-mail transacional via Resend (free tier: 3K/mês) com React Email
- Unsubscribe link em todos os e-mails (compliance)

### R5.3 — Histórico de Preços
- Gráfico de linha: variação de preço 90/180 dias por produto + varejista
- Indicador: "Bom momento para comprar" quando preço ≤ percentil 20 dos últimos 90 dias
- Dados servidos por `GET /products/{id}/price-history?days=90`

### R5.4 — Blog / Conteúdo SEO
- Páginas estáticas de review por produto (SSG + ISR)
- Pillar page prioritária: "Best Pickleball Paddles for Beginners"
- FTC disclosure obrigatória: bloco visível acima do primeiro link de afiliado

---

## Phase 6 — Launch & Deploy

### R6.1 — Infraestrutura de Produção
- Frontend: Vercel (plano hobby → pro conforme necessidade)
- Backend API: Railway
- PostgreSQL: Railway managed ou Supabase
- Pinecone: managed (starter tier)
- Variáveis de ambiente via painel Vercel + Railway (nunca em repositório)

### R6.2 — CI/CD
- GitHub Actions: lint + testes em cada PR
- Cobertura de testes ≥ 80% no pipeline Python
- Deploy automático para Vercel on merge to main
- Preview deployments para cada PR no Vercel

### R6.3 — Observabilidade & Alertas
- Logs estruturados (JSON) no backend
- Alerta de falha de scraping: e-mail após 3 retries consecutivos falhando
- Langfuse dashboard configurado para produção
- Health check endpoint monitorado

### R6.4 — Beta Launch
- Deploy completo em produção com dados reais (≥ 500 raquetes)
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

## Open Questions (verificar antes de iniciar fases específicas)

- [ ] Confirmar detalhes do programa de afiliados da Fromuth (contato direto necessário)
- [ ] Confirmar rede do Selkirk affiliate (Impact Radius vs ShareASale vs direto)
- [ ] Verificar volume atual de keywords via Ahrefs/Semrush antes da Fase 5
- [ ] Confirmar pricing do Firecrawl `/extract` por call para dimensionar o budget de 24h
- [ ] Testar se PickleballCentral e Fromuth expõem SKU do fabricante no HTML
- [ ] Amazon PA-API: confirmar se cobre todos os SKUs do catálogo target
