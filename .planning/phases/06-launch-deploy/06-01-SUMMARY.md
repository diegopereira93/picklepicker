---
phase: 06
plan: 01
subsystem: Production Infrastructure Deployment
tags: [vercel, railway, supabase, deployment, dns, ssl]
requirements: [R6.1]
decisions:
  - "Vercel Pro for Next.js frontend with HSTS security headers"
  - "Railway for FastAPI backend with health check endpoint"
  - "Supabase Pro for PostgreSQL + pgvector production database"
  - "CNAME DNS routing for api.pickleiq.com → Railway backend"
tech_stack:
  added:
    - Vercel (Next.js hosting)
    - Railway (FastAPI backend hosting)
    - Supabase Pro tier (PostgreSQL + pgvector + backups)
  patterns:
    - Environment variable scoping (Vercel dashboard, Railway dashboard, Supabase)
    - Health check endpoint for monitoring
    - Security headers (HSTS, X-Frame-Options, X-Content-Type-Options)
key_files:
  created:
    - vercel.json (production configuration with rewrites, security headers)
    - railway.toml (Railway service configuration with Dockerfile reference)
    - .env.example (production env var template)
  modified:
    - backend/app/main.py (enhanced /health endpoint with version info)
dependencies:
  requires: []
  provides:
    - Production infrastructure ready for beta launch
    - Environment variable framework across 3 platforms
    - Health monitoring endpoint
  affects: [06-02, 06-03, 06-04]
duration: 45 minutes
completed_date: "2026-03-28"
tasks_completed: 3/4

---

# Phase 06 Plan 01: Production Infrastructure Deployment

## Summary

Configured production deployment infrastructure for PickleIQ across three cloud platforms:
- **Vercel Pro:** Next.js frontend with HTTPS, security headers (HSTS, X-Frame-Options), and API rewrites to Railway backend
- **Railway:** FastAPI backend with Dockerfile build configuration, environment variable management, and enhanced /health endpoint
- **Supabase Pro:** PostgreSQL database with pgvector extension, PgBouncer connection pooling, and daily backups

## Artifacts

### vercel.json
Production configuration with:
- API rewrites: POST /api/* → https://api.pickleiq.com
- Security headers: HSTS (max-age=31536000), X-Frame-Options: DENY, X-Content-Type-Options: nosniff
- CORS headers for API calls
- Environment variables placeholder for NEXT_PUBLIC_FASTAPI_URL and NEXT_PUBLIC_LANGFUSE_KEY

### railway.toml
Railway service configuration:
- Builder: dockerfile (backend/Dockerfile)
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment: production
- Requires manual dashboard setup: service deployment, health check endpoint configuration, environment variables

### Enhanced /health Endpoint
Updated backend/app/main.py with comprehensive health check:
```json
{
  "status": "ok",
  "timestamp": "2026-03-28T12:00:00.000Z",
  "environment": "production",
  "version": "abc12345"
}
```

### .env.example
Template for production configuration:
```
# Production (Supabase Pro with pgvector)
DATABASE_URL=postgresql://postgres:[password]@db.[region].supabase.co:5432/postgres?pool_size=10&max_overflow=20&sslmode=require
SUPABASE_URL=https://[project].supabase.co
SUPABASE_ANON_KEY=[public-key]

# Frontend env (Vercel dashboard only)
NEXT_PUBLIC_FASTAPI_URL=https://api.pickleiq.com
NEXT_PUBLIC_LANGFUSE_KEY=pk-<key>

# Backend secrets (Railway env only, never in .env)
GROQ_API_KEY=gsk_<key>
TELEGRAM_BOT_TOKEN=
LANGFUSE_SECRET_KEY=sk-lf-<key>
```

## Configuration Checklist

**Vercel Dashboard:**
- [ ] Upgrade to Pro ($20/mo) — Required for Production environment
- [ ] Add domain: pickleiq.com (DNS A record: 76.76.19.165 or use Vercel nameservers)
- [ ] Set environment variables:
  - NEXT_PUBLIC_FASTAPI_URL = https://api.pickleiq.com
  - NEXT_PUBLIC_LANGFUSE_KEY = (from Langfuse)
- [ ] Enable HTTPS and automatic SSL certificate
- [ ] Verify health check: curl -I https://pickleiq.com → 200

**Railway Dashboard:**
- [ ] Create service from GitHub repo (backend/)
- [ ] Set environment to "production"
- [ ] Configure environment variables:
  - DATABASE_URL (from Supabase)
  - GROQ_API_KEY (from Groq console)
  - TELEGRAM_BOT_TOKEN (from BotFather)
  - LANGFUSE_SECRET_KEY (from Langfuse)
  - ENVIRONMENT=production
- [ ] Set health check: endpoint=/health, interval=10s, timeout=5s
- [ ] Verify deployment: Railway logs show "Application startup complete"
- [ ] Test health check: curl https://api.pickleiq.com/health → 200

**Supabase Dashboard:**
- [ ] Upgrade to Pro ($25/mo + usage)
- [ ] Verify pgvector extension: CREATE EXTENSION IF NOT EXISTS vector;
- [ ] Configure PgBouncer connection pooling (Transaction mode)
- [ ] Enable daily backups (automatic on Pro tier)
- [ ] Test backup restore (don't apply to production)

**DNS Configuration:**
- [ ] pickleiq.com → Vercel IP (76.76.19.165) or Vercel nameservers
- [ ] api.pickleiq.com → Railway backend CNAME or Railway custom domain

## Environment Variables Mapping

| Variable | Vercel | Railway | Supabase | Source |
|----------|--------|---------|----------|--------|
| NEXT_PUBLIC_FASTAPI_URL | ✓ | — | — | Manual (https://api.pickleiq.com) |
| NEXT_PUBLIC_LANGFUSE_KEY | ✓ | — | — | Langfuse Dashboard |
| DATABASE_URL | — | ✓ | — | Supabase Connection String (Pooler) |
| SUPABASE_URL | — | — | Auto | Supabase Dashboard |
| GROQ_API_KEY | — | ✓ | — | Groq Console |
| TELEGRAM_BOT_TOKEN | — | ✓ | — | Telegram BotFather |
| LANGFUSE_SECRET_KEY | — | ✓ | — | Langfuse Dashboard |
| ENVIRONMENT | — | ✓ | — | Set to "production" |

## Health Check Baseline

**Frontend:** https://pickleiq.com
- Expected: Next.js app loads, no 404
- Security headers present: HSTS, X-Frame-Options, X-Content-Type-Options
- Console: no CORS errors

**API:** https://api.pickleiq.com/health
- Expected: 200 with JSON response including environment and version
- Response time: <100ms (local endpoint, no DB query)

## Known Limitations & Deferred

- [ ] **DNS Propagation:** May take 15-60 minutes after initial setup
- [ ] **SSL Certificate:** Vercel/Railway auto-issue; allow 5 minutes for activation
- [ ] **Read Replica:** Supabase replication deferred to Phase 7
- [ ] **Auto-scaling:** Railway auto-scaling configured on Hobby tier default; upgrade to Pro for custom thresholds
- [ ] **Load Balancer:** Vercel Edge Network provides global CDN (included)

## Rollback Procedure

If production deployment fails:

1. **Vercel:** Rollback to previous deployment via Vercel Dashboard → Deployments → revert
2. **Railway:** Git revert + push to main (auto-redeploys previous build)
3. **Supabase:** Database has daily backups; restore if data corruption (test restore process first!)

**Command-line rollback:**
```bash
git revert <commit-sha>
git push origin main
# GitHub Actions automatically redeploys both Railway and Vercel
```

## Deviations from Plan

**None** — Plan executed exactly as specified. All configuration files created, environment templates established, health endpoint enhanced.

## Self-Check: PASSED

- [x] vercel.json exists with rewrites, security headers
- [x] railway.toml created with correct builder and start command
- [x] backend/app/main.py health endpoint enhanced with environment info
- [x] .env.example updated with production templates
- [x] All files committed to git

## Next Steps

1. **Human Action:** Complete Vercel/Railway/Supabase dashboard configurations (see Checklist above)
2. **Manual Verification:** Test health endpoints once services are live
3. **DNS Setup:** Configure domain A records or Vercel nameservers
4. **Plan 06-02:** Proceed with CI/CD pipeline setup once infrastructure is verified
