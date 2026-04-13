<!-- generated-by: gsd-doc-writer -->
# Configuration

Guia de configuração para o PickleIQ — todas as variáveis de ambiente, opções de config file, e valores padrão.

## Environment Variables

### Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string. Local: `postgresql://pickleiq:changeme@localhost:5432/pickleiq`. Production (Supabase): `postgresql://postgres:[password]@db.[region].supabase.co:5432/postgres?pool_size=10&max_overflow=20&sslmode=require` |
| `POSTGRES_HOST` | No | `localhost` | PostgreSQL host (used by local Docker setup) |
| `POSTGRES_PORT` | No | `5432` | PostgreSQL port |
| `POSTGRES_DB` | No | `pickleiq` | Database name |
| `POSTGRES_USER` | No | `pickleiq` | Database user |
| `POSTGRES_PASSWORD` | No | `changeme` | Database password |

### Supabase (Production)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | No (prod) | — | Supabase project URL: `https://[project].supabase.co` |
| `SUPABASE_ANON_KEY` | No (prod) | — | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | No (prod) | — | Supabase service role key (server-side only) |
| `SUPABASE_DATABASE_URL` | No (prod) | — | Supabase managed PostgreSQL connection string |

### LLM & Observability

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | — | Groq API key for chat LLM (`gsk_...` prefix). Used by the RAG agent for streaming responses |
| `LANGFUSE_SECRET_KEY` | No | — | Langfuse secret key for observability (`sk-lf-...` prefix) |
| `LANGFUSE_PUBLIC_KEY` | No | — | Langfuse public key |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` | Langfuse server URL |

### Embeddings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JINA_API_KEY` | Yes | — | Jina AI API key for embeddings (`jina_...` prefix). Primary embedding provider |
| `HUGGINGFACE_API_KEY` | No | — | Hugging Face API key (`hf_...` prefix). Fallback when Jina fails |
| `GEMINI_API_KEY` | No | — | Google Gemini API key. Optional, not currently used in main pipeline |
| `EMBEDDING_PROVIDER` | No | `auto` | Embedding provider selection: `auto` (Jina first, HF fallback), `jina`, `hf`, `gemini` |

### Scrapers & Crawlers

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FIRECRAWL_API_KEY` | Yes | — | Firecrawl API key (`fc-...` prefix). Used by all crawlers (Brazil Store, Dropshot Brasil, Mercado Livre) |
| `ML_AFFILIATE_TAG` | No | — | Mercado Livre affiliate tag for tracking affiliate links |
| `ML_API_BATCH_SIZE` | No | `50` | Batch size for Mercado Livre API calls |
| `ML_API_MAX_PAGES` | No | `10` | Maximum pages to scrape per Mercado Livre run |
| `FIRECRAWL_TIMEOUT_SEC` | No | `30` | Timeout for Firecrawl scraping requests |

### Telegram Alerts

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | No | — | Telegram bot token for error alerting (`[0-9]+:[A-Za-z0-9_-]+` format) |
| `TELEGRAM_CHAT_ID` | No | — | Telegram chat ID for error alert destination |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_FASTAPI_URL` | Yes | — | Backend API URL. Local: `http://localhost:8000`. Staging (Railway auto-domain): `https://api.railway.app`. Production: `https://api.pickleiq.com` |
| `NEXT_PUBLIC_LANGFUSE_KEY` | No | — | Langfuse public key for frontend observability (`pk-...` prefix) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | No | — | Clerk publishable key for authentication (Phase 5+) |
| `CLERK_SECRET_KEY` | No | — | Clerk secret key (server-side) |

### Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | Runtime environment: `development`, `staging`, `production` |
| `CORS_ORIGINS` | No | `http://localhost:3000,https://pickleiq.com` | Comma-separated list of allowed CORS origins |
| `ADMIN_SECRET` | No | — | Bearer token for admin endpoints. Must be set for production |
| `RAILWAY_GIT_COMMIT_SHA` | Auto | — | Set automatically by Railway deployment. Used as version identifier in health checks |
| `PORT` | Auto | `8000` | Port the backend server listens on (Railway sets this) |
| `PICKLEIQ_ENV` | No | — | Optional environment label for logging (e.g., `production`, `staging`) |

### Price Alerts (Workers)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RESEND_API_KEY` | No | — | Resend API key for sending price alert emails |

## Config File Format

No config files beyond environment variables — the project uses raw `psycopg` with raw SQL and FastAPI with direct `os.environ` / `os.getenv` calls. There is no YAML/TOML/JSON config file consumed at runtime.

`railway.toml` at the project root is a Railway deployment manifest (not a runtime config):

```toml
[build]
builder = "dockerfile"
dockerfile = "backend/Dockerfile"

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"

[env]
ENVIRONMENT = "production"
```

## Required vs Optional Settings

### Required (application will fail to start without these)

| Variable | Fail condition |
|----------|---------------|
| `DATABASE_URL` | If absent, backend `psycopg_pool.AsyncConnectionPool` raises `KeyError` on startup |
| `GROQ_API_KEY` | If absent, chat endpoint returns 500 on first request (checked at request time, not startup) |
| `JINA_API_KEY` | If absent, embedding generation fails (checked at request time) |
| `FIRECRAWL_API_KEY` | If absent, crawlers fail immediately (not called during normal app startup) |
| `NEXT_PUBLIC_FASTAPI_URL` | If absent, frontend API client points to nowhere — all requests fail |

### Optional (application starts and runs with defaults or empty strings)

| Variable | Default when absent |
|----------|-------------------|
| `HUGGINGFACE_API_KEY` | Embedding fallback disabled — Jina-only mode |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Telegram alerting silently skipped |
| `LANGFUSE_SECRET_KEY` | Observability disabled, no traces emitted |
| `ENVIRONMENT` | `"development"` — verbose logging, detailed error messages |
| `CORS_ORIGINS` | `http://localhost:3000,https://pickleiq.com` |
| `EMBEDDING_PROVIDER` | `"auto"` — Jina first, HF fallback |

## Defaults

Core defaults as defined in source code:

| Variable | Default | Location |
|----------|---------|----------|
| `POSTGRES_HOST` | `localhost` | `docker-compose.yml` |
| `POSTGRES_PORT` | `5432` | `docker-compose.yml` |
| `POSTGRES_DB` | `pickleiq` | `docker-compose.yml` |
| `POSTGRES_USER` | `pickleiq` | `docker-compose.yml` |
| `POSTGRES_PASSWORD` | `changeme` | `docker-compose.yml` + `.env.example` |
| `ENVIRONMENT` | `development` | `backend/app/main.py:28` |
| `CORS_ORIGINS` | `http://localhost:3000,https://pickleiq.com` | `backend/app/main.py:47` |
| `EMBEDDING_PROVIDER` | `auto` | `backend/app/services/embedding.py:50` |
| `ML_API_BATCH_SIZE` | `50` | `.env.example` |
| `ML_API_MAX_PAGES` | `10` | `.env.example` |
| `FIRECRAWL_TIMEOUT_SEC` | `30` | `.env.example` |
| `PORT` | `8000` | Railway default |

## Per-Environment Overrides

### Development (`ENVIRONMENT=development`)

- Uses local PostgreSQL via Docker Compose (`localhost:5432`)
- `CORS_ORIGINS` defaults to `http://localhost:3000`
- Verbose structlog logging
- Error responses include full stack traces

### Staging (Railway)

- Railway auto-generates a domain: `https://[project]-[env]-[random].railway.app`
- `NEXT_PUBLIC_FASTAPI_URL` = Railway auto-domain (auto-injected by Railway)
- `ENVIRONMENT` = `production` (set by Railway via `railway.toml`)
- `RAILWAY_GIT_COMMIT_SHA` = Git commit SHA (auto-injected by Railway)

### Production (Supabase + Railway + Vercel)

- `DATABASE_URL` = Supabase managed PostgreSQL (`db.[region].supabase.co`)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` = Supabase project credentials
- `NEXT_PUBLIC_FASTAPI_URL` = `https://api.pickleiq.com` <!-- VERIFY: Production API domain - not confirmed from repo -->
- `ADMIN_SECRET` = must be set in Railway environment variables
- `ENVIRONMENT` = `production`
- CORS restricted to production origins only