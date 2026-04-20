# External Integrations

**Analysis Date:** 2026-04-20

## AI/ML Services

**LLM Provider (Chat):**
- Groq - Chat/RAG LLM inference
  - API Key: `GROQ_API_KEY`
  - Model: Mixtral 8x7B (via Groq)
  - Usage: Real-time chat responses, streaming SSE

**Embedding Provider:**
- Jina AI - Text embeddings for semantic search (primary)
  - API Key: `JINA_API_KEY`
  - Model: jina-embeddings-v2-base
  - Dimensions: 768
  - Fallback: Hugging Face API (`HUGGINGFACE_API_KEY`)

## Data Storage

**Database:**
- PostgreSQL 16 with pgvector extension
- Connection: `DATABASE_URL` environment variable
- Local: `postgresql://pickleiq:changeme@localhost:5432/pickleiq`
- Production: Supabase (`postgresql://postgres:[password]@db.[region].supabase.co:5432/postgres?sslmode=require`)
- ORM: Raw psycopg (no ORM, direct SQL)
- Connection pooling: psycopg async pool

**Vector Storage:**
- Same PostgreSQL with pgvector
- Table: `paddle_embeddings` with `vector(768)` column

## Authentication

**Frontend Auth:**
- Clerk - Next.js authentication
  - Publishable Key: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - Secret Key: `CLERK_SECRET_KEY`
  - Config: `frontend/src/middleware.ts`

**Admin Auth:**
- Bearer token via `ADMIN_SECRET` env var
- Protects `/admin/*` endpoints

## Web Scraping

**Primary Scraper:**
- Firecrawl - Structured web extraction
  - API Key: `FIRECRAWL_API_KEY`
  - Used for: Brazil Store, Dropshot Brasil retailers

**Shopify Integration:**
- Native JSON API (httpx)
- Used for: JOOLA Brasil (direct Shopify store API)

## Notifications

**Telegram Alerts:**
- python-telegram-bot
- Bot Token: `TELEGRAM_BOT_TOKEN`
- Chat ID: `TELEGRAM_CHAT_ID`
- Usage: Error alerting, price alerts, monitoring

**Email:**
- Resend - Transactional email
  - API Key: `RESEND_API_KEY`
  - Usage: NPS surveys, notifications

## External APIs Consumed

**Retailer APIs:**
- Brazil Store - Product listings via Firecrawl
- Dropshot Brasil - Product listings via Firecrawl
- JOOLA Brasil - Shopify JSON API (`api.joola.com.br`)

**Affiliate:**
- Mercado Livre Afiliados - Affiliate link tracking
  - Tag: `ML_AFFILIATE_TAG`

## Deployment Services

**Backend Hosting:**
- Railway
  - Dockerfile: `Dockerfile.railway`
  - Auto-generated domain: `https://[project]-[env]-[random].railway.app`
  - Port: 8000

**Frontend Hosting:**
- Vercel
  - Next.js deployment
  - Custom domain: `pickleiq.com` (production)

**Database Hosting:**
- Supabase
  - PostgreSQL with pgvector
  - Connection pooling enabled

## Environment Variables

### Required (`backend/.env.example`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `GROQ_API_KEY` | Groq LLM API key | `gsk_...` |
| `JINA_API_KEY` | Jina AI embeddings API key | `jina-...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `EMBEDDING_PROVIDER` | Embedding service | `jina` |
| `HUGGINGFACE_API_KEY` | Fallback embeddings | - |
| `FIRECRAWL_API_KEY` | Web scraping | - |
| `GEMINI_API_KEY` | Alternative LLM | - |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk auth | - |
| `CLERK_SECRET_KEY` | Clerk auth | - |
| `RESEND_API_KEY` | Email service | - |
| `TELEGRAM_BOT_TOKEN` | Telegram alerts | - |
| `TELEGRAM_CHAT_ID` | Telegram chat | - |
| `ADMIN_SECRET` | Admin Bearer token | - |

### Frontend (`frontend/.env.example`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_FASTAPI_URL` | Backend API URL |
| `ADMIN_SECRET` | Admin authentication |

### Root (`.env.example`)

| Variable | Description |
|----------|-------------|
| `POSTGRES_*` | Database config |
| `SUPABASE_*` | Supabase config |
| `FIRECRAWL_API_KEY` | Scraping |
| `ML_AFFILIATE_TAG` | Affiliate tracking |
| `TELEGRAM_*` | Alerts |
| `GROQ_API_KEY` | LLM |
| `LANGFUSE_SECRET_KEY` | Observability |

## Webhooks

**Internal:**
- `/webhook/affiliate` - Affiliate click tracking (stub)
- `/webhook/price-alert` - Price alert notifications (planned)

**External (incoming):**
- None currently configured

## Observability

**Langfuse - LLM Observability:**
- Secret Key: `LANGFUSE_SECRET_KEY`
- Public Key: `NEXT_PUBLIC_LANGFUSE_KEY`
- Usage: LLM call tracing, metrics

**Structured Logging:**
- structlog (Python)
- Configured in `backend/app/logging_config.py`

## CI/CD Pipelines

GitHub Actions workflows:
- `test.yml` - Backend and frontend tests
- `deploy.yml` - Railway + Vercel deployment
- `scraper.yml` - Scheduled data pipeline runs
- `lighthouse.yml` - Performance auditing
- `price-alerts-check.yml` - Price monitoring
- `validate-production.yml` - Production smoke tests
- `nps-survey.yml` - User feedback collection

---

*Integration audit: 2026-04-20*