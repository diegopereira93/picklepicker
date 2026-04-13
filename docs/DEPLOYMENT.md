# Deployment — PickleIQ

Deployment architecture, procedures, and configuration.

## Architecture

| Component | Platform | Region |
|-----------|----------|--------|
| Backend API | Railway | US East |
| Frontend | Vercel | Edge (global) |
| Database | Supabase | US East (pgvector) |
| Scrapers | GitHub Actions | Scheduled |

## Deploy Targets

### Backend — Railway

- **Runtime:** Python 3.12 on Railway container
- **Entry:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **URL:** `https://pickleiq-api.up.railway.app`
- **Health:** `GET /health` returns `{"status": "healthy"}`

### Frontend — Vercel

- **Framework:** Next.js 14 App Router
- **Build:** `npm run build` in `frontend/`
- **URL:** `https://pickleiq.com`
- **Config:** `vercel.json` (root) for security headers and rewrites

### Database — Supabase

- **Engine:** PostgreSQL 15 with pgvector extension
- **Connection:** Via `DATABASE_URL` env var
- **Schema:** Managed in `pipeline/db/schema.sql`
- **Migrations:** Apply manually via `psql` or Supabase dashboard

### Scrapers — GitHub Actions

- **Trigger:** Scheduled (cron) and manual
- **Workflow:** `.github/workflows/scraper.yml`
- **Output:** Price snapshots appended to database

## Environment Variables

### Backend (Railway)

| Variable | Description | Source |
|----------|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection string | Supabase |
| `GROQ_API_KEY` | Groq LLM API (chat streaming) | groq.com |
| `JINA_API_KEY` | Jina AI embeddings (primary) | jina.ai |
| `HUGGINGFACE_API_KEY` | HF embeddings (fallback) | huggingface.co |
| `FIRECRAWL_API_KEY` | Web scraping API | firecrawl.dev |
| `ADMIN_SECRET` | Admin endpoint Bearer token | Self-generated |
| `TELEGRAM_BOT_TOKEN` | Error alerting bot | @BotFather |
| `TELEGRAM_CHAT_ID` | Alert destination chat | Telegram |

### Frontend (Vercel)

| Variable | Description | Source |
|----------|-------------|--------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk public key | clerk.com |
| `CLERK_SECRET_KEY` | Clerk server key | clerk.com |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Railway |

## Deployment Process

### Automatic (Recommended)

Pushing to `main` branch triggers:
1. **Test workflow** — `.github/workflows/test.yml` runs all tests
2. **Deploy workflow** — `.github/workflows/deploy.yml` deploys to Railway + Vercel

```bash
git push origin main
```

### Manual Backend Deploy

<!-- VERIFY: Railway CLI commands may differ based on project config -->

```bash
# Install Railway CLI
npm i -g @railway/cli

# Link and deploy
railway link
railway up
```

### Manual Frontend Deploy

```bash
cd frontend
vercel --prod
```

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy.yml` | Push to main | Deploy backend + frontend |
| `test.yml` | Pull request | Run test suites |
| `scraper.yml` | Cron (daily) | Run all scrapers |
| `lighthouse.yml` | Cron (weekly) | Performance audit |
| `price-alerts.yml` | Cron (hourly) | Check price drops |
| `nps-survey.yml` | Cron (monthly) | Send NPS surveys |

## Security

### Headers (vercel.json)

Security headers applied via `vercel.json`:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy` configured

### Admin Endpoints

Protected via Bearer token (`ADMIN_SECRET` env var):
- `GET /api/v1/admin/paddles`
- `GET /api/v1/admin/stats`

### Database

- Connection string uses SSL in production
- Parameterized queries only (no SQL injection)
- No ORM — direct psycopg with async connection pooling

## Monitoring

### Health Check

```bash
curl https://pickleiq-api.up.railway.app/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-12T20:00:00+00:00",
  "version": "2.2.0"
}
```

### Error Alerting

Backend errors trigger Telegram notifications via `middleware/alerts.py`:
- Rate limited to 1 alert per error type per 60 seconds
- Includes stack trace and request context
- Configured via `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

### Logging

Backend uses structlog with JSON output:
- Structured fields: `timestamp`, `level`, `event`, `error`
- Configured in `app/logging_config.py`

## Rollback

### Backend (Railway)

<!-- VERIFY: Railway rollback procedure -->

```bash
railway rollback    # Rollback to previous deployment
```

Or via Railway dashboard → Deployments → Redeploy previous.

### Frontend (Vercel)

```bash
vercel rollback https://pickleiq.com
```

Or via Vercel dashboard → Deployments → Promote previous.

### Database

No automatic rollback. Schema changes require manual SQL migration.

## Local Production Simulation

```bash
# Build frontend
cd frontend && npm run build && npm start

# Run backend in production mode
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Use local DB
docker compose up -d
```

## Troubleshooting Deployments

### Backend won't start on Railway

1. Check `DATABASE_URL` is set and points to Supabase
2. Check `GROQ_API_KEY` is valid
3. View logs: `railway logs`

### Frontend build fails on Vercel

1. Check `npm run build` passes locally
2. Verify all env vars are set in Vercel dashboard
3. Check build logs in Vercel dashboard

### Database migration issues

1. Connect to Supabase via dashboard SQL editor
2. Apply schema from `pipeline/db/schema.sql`
3. Verify pgvector extension: `SELECT * FROM pg_extension WHERE extname = 'vector';`

### Scrapers not running

1. Check GitHub Actions tab for failed runs
2. Verify `FIRECRAWL_API_KEY` in repository secrets
3. Check `DATABASE_URL` in repository secrets
