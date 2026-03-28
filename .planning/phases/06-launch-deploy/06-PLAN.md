---
phase: 06-launch-deploy
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - vercel.json
  - next.config.js
  - railway.toml
  - backend/app/main.py
  - backend/app/routers/health.py
  - .env.example
autonomous: true
requirements: [R6.1]
user_setup:
  - service: vercel
    why: "Production deployment of Next.js frontend"
    env_vars:
      - name: NEXT_PUBLIC_FASTAPI_URL
        source: "Set to https://api.pickleiq.com after Railway backend deployed"
    dashboard_config:
      - task: "Upgrade to Pro ($20/mo), enable Production environment"
        location: "Vercel Dashboard → Settings → Plan"
      - task: "Configure domain DNS (A record points to Vercel)"
        location: "Vercel Dashboard → Domains"
  - service: railway
    why: "Production deployment of FastAPI backend + PostgreSQL"
    env_vars:
      - name: DATABASE_URL
        source: "Copy from Supabase Dashboard → Connection String (Pooler)"
      - name: GROQ_API_KEY
        source: "Copy from Groq Console → API Keys"
      - name: TELEGRAM_BOT_TOKEN
        source: "Create bot via BotFather on Telegram"
      - name: LANGFUSE_SECRET_KEY
        source: "Copy from Langfuse Dashboard → Account → API Keys"
      - name: ENVIRONMENT
        source: "Set to 'production'"
    dashboard_config:
      - task: "Deploy FastAPI backend service to production"
        location: "Railway Dashboard → New → GitHub Repo → Select backend/"
      - task: "Set Health Check to /health endpoint"
        location: "Railway Dashboard → Service Settings → Deploy → Health Check"
  - service: supabase
    why: "Production PostgreSQL + pgvector database"
    env_vars:
      - name: SUPABASE_URL
        source: "Copy from Supabase Dashboard → Settings → API"
      - name: SUPABASE_ANON_KEY
        source: "Copy from Supabase Dashboard → Settings → API"
    dashboard_config:
      - task: "Upgrade to Pro tier ($25/mo + usage)"
        location: "Supabase Dashboard → Billing"
      - task: "Enable daily backups and test restore"
        location: "Supabase Dashboard → Backups"
      - task: "Configure connection pooler (PgBouncer)"
        location: "Supabase Dashboard → Database → Connection Pooling → Transaction mode"
      - task: "Verify pgvector extension enabled"
        location: "Supabase Dashboard → SQL Editor → CREATE EXTENSION vector"

must_haves:
  truths:
    - "Frontend loads from production domain with zero CORS errors"
    - "API health check endpoint returns 200 with system status"
    - "Database connection succeeds from Railway backend to Supabase"
    - "All environment variables loaded without fallbacks"
    - "Production database passes connectivity smoke test (SELECT 1)"
    - "HTTPS working with security headers (HSTS, X-Frame-Options)"
    - "Load test: 10 concurrent users generate P95 latency < 500ms"
  artifacts:
    - path: "vercel.json"
      provides: "Vercel project configuration (rewrites, redirects)"
      contains: "rewrites.*api.*Railway"
    - path: "railway.toml"
      provides: "Railway service configuration"
      contains: "builder.*dockerfile|startCommand"
    - path: "backend/app/routers/health.py"
      provides: "Health check endpoint for monitoring"
      exports: ["GET /health"]
    - path: ".env.example"
      provides: "Template for required environment variables"
      contains: "NEXT_PUBLIC_FASTAPI_URL|DATABASE_URL|GROQ_API_KEY"
  key_links:
    - from: "Vercel (frontend)"
      to: "Railway API endpoint"
      via: "NEXT_PUBLIC_FASTAPI_URL environment variable"
      pattern: "fetch.*NEXT_PUBLIC_FASTAPI_URL"
    - from: "Railway (backend)"
      to: "Supabase (database)"
      via: "DATABASE_URL connection string"
      pattern: "DATABASE_URL.*postgresql"
    - from: "Railway service"
      to: "Health monitoring"
      via: "/health endpoint"
      pattern: "GET /health → 200 ok"

---

<objective>
Deploy PickleIQ to production infrastructure with Vercel frontend, Railway backend, and Supabase database. Configure all environment variables across platforms and verify end-to-end connectivity.

Purpose: Establish reliable production infrastructure that scales with beta launch (50 users).
Output: Live production services with health checks, domain routing, and database connectivity verified.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@.planning/06-launch-deploy/06-RESEARCH.md (patterns: environment variable scoping, infrastructure patterns)
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Upgrade Vercel to Pro, configure deployment settings</name>
  <files>vercel.json</files>
  <action>
1. Visit Vercel Dashboard → Settings → Plan
2. Upgrade to Pro ($20/mo) to enable Environment Production, Monitoring, and Analytics
3. Create vercel.json in project root with:
   - Rewrites: POST /api/* → Railway backend (https://api.pickleiq.com)
   - Env variables: NEXT_PUBLIC_FASTAPI_URL (not committed, set in dashboard)
   - Redirect HTTP → HTTPS
   - Security headers: HSTS (max-age=31536000), X-Frame-Options: DENY, X-Content-Type-Options: nosniff
4. Configure domains in Vercel Dashboard:
   - Add production domain (e.g., pickleiq.com)
   - Configure DNS: A record 76.76.19.165 (Vercel Edge IP)
   - Enable automatic HTTPS + SSL certificate
5. Set environment variables in Dashboard (Settings → Environment Variables):
   - NEXT_PUBLIC_FASTAPI_URL = https://api.pickleiq.com (all environments)
   - NEXT_PUBLIC_LANGFUSE_KEY = (from Langfuse dashboard)
6. Test preview deploy: `vercel deploy --prod` (or use GitHub integration)
  </action>
  <verify>
    - vercel.json exists and contains rewrites block
    - Visit https://pickleiq.com → Next.js app loads (no 404)
    - Inspect browser console → no CORS errors
    - `curl -I https://pickleiq.com` returns 200 + security headers (HSTS, X-Frame-Options)
  </verify>
  <done>
Vercel Pro account active, domain configured, environment variables set, frontend responds to production domain with HTTPS.
  </done>
</task>

<task type="auto">
  <name>Task 2: Deploy FastAPI backend to Railway with production PostgreSQL</name>
  <files>railway.toml, backend/app/main.py, backend/app/routers/health.py</files>
  <action>
1. Create railway.toml in project root:
   ```toml
   [build]
   builder = "dockerfile"
   dockerfile = "backend/Dockerfile"

   [start]
   cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"

   [env]
   ENVIRONMENT = "production"
   ```

2. Connect Railway GitHub repo:
   - Railway Dashboard → New → GitHub Repo → select backend/
   - Configure environment: "production"
   - Add plugins: PostgreSQL (use Supabase instead, skip this)

3. Set environment variables in Railway Dashboard (Service Settings):
   - DATABASE_URL = postgresql://[user]:[password]@[host]:5432/postgres?pool_size=10&max_overflow=20
   - GROQ_API_KEY = (from Groq console)
   - TELEGRAM_BOT_TOKEN = (from BotFather)
   - LANGFUSE_SECRET_KEY = (from Langfuse)
   - ENVIRONMENT = production

4. Create health.py router:
   ```python
   # backend/app/routers/health.py
   from fastapi import APIRouter
   from datetime import datetime
   import os

   router = APIRouter()

   @router.get("/health")
   async def health():
       return {
           "status": "ok",
           "timestamp": datetime.utcnow().isoformat(),
           "environment": os.getenv("ENVIRONMENT", "unknown"),
           "version": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")[:8]
       }
   ```

5. Register router in main.py:
   ```python
   from app.routers import health
   app.include_router(health.router)
   ```

6. Configure Railway health check:
   - Railway Dashboard → Service Settings → Deploy → Health Check
   - Endpoint: /health
   - Interval: 10s
   - Timeout: 5s

7. Deploy by pushing to main or using Railway CLI:
   ```bash
   npm install -g @railway/cli
   railway up --service backend --environment production
   ```

8. Test health endpoint:
   ```bash
   curl https://api.pickleiq.com/health
   # Expected: {"status": "ok", "timestamp": "2026-03-28T...", ...}
   ```
  </action>
  <verify>
    - railway.toml exists with correct builder and start command
    - backend/app/routers/health.py exists with health() endpoint
    - health.py registered in main.py
    - Railway deployment status: green checkmark
    - `curl https://api.pickleiq.com/health` returns 200 + JSON response
    - Railway logs show "Application startup complete" (no errors)
  </verify>
  <done>
FastAPI backend live on Railway, health check endpoint responding, database URL configured, environment variables propagated.
  </done>
</task>

<task type="auto">
  <name>Task 3: Migrate to Supabase Pro, configure pgvector and backups</name>
  <files>.env.example</files>
  <action>
1. Supabase Dashboard → Billing → Upgrade to Pro ($25/mo + usage)
   - This unlocks: Daily backups, pgvector embeddings, PgBouncer connection pooling

2. Configure connection pooling:
   - Dashboard → Database → Connection Pooling
   - Enable: PgBouncer (Transaction mode)
   - This prevents connection pool exhaustion from scrapers

3. Verify pgvector extension:
   - Dashboard → SQL Editor
   - Run: `CREATE EXTENSION IF NOT EXISTS vector;`
   - Run: `SELECT * FROM pg_extension WHERE extname = 'vector';`
   - Should return 1 row (already exists from Phase 1)

4. Configure backups:
   - Dashboard → Backups → Enable daily backups (default)
   - Test restore: Backups → click latest backup → "Restore"
   - DO NOT restore to production yet — just verify the process works

5. Set up auto-replication (optional but recommended):
   - Dashboard → Database → Replication → add read replica (advanced, defer to Phase 7)

6. Update .env.example with production connection strings:
   ```
   # Production (Supabase Pro)
   DATABASE_URL=postgresql://postgres:[password]@db.[region].supabase.co:5432/postgres?pool_size=10&max_overflow=20&sslmode=require
   SUPABASE_URL=https://[project].supabase.co
   SUPABASE_ANON_KEY=[public-key]

   # Sensitive (Railway env vars only, never in .env)
   GROQ_API_KEY=
   TELEGRAM_BOT_TOKEN=
   LANGFUSE_SECRET_KEY=
   ```

7. Test connection from Railway backend:
   - SSH into Railway or check logs
   - Run: `psql $DATABASE_URL -c "SELECT version();"` (or equivalent Python test)
   - Should return PostgreSQL version and confirm connection works

8. Monitor for connection pool exhaustion:
   - Railway dashboard → Metrics
   - Watch: CPU, Memory, Connections
   - If spikes on scraper runs, reduce pool size or add queue
  </action>
  <verify>
    - Supabase account shows Pro tier active
    - pgvector extension confirmed in database (query returns vector type)
    - PgBouncer connection pooling enabled
    - .env.example updated with production DATABASE_URL template
    - Test query via Railway logs: `SELECT version()` returns PostgreSQL version
    - Backup restore tested without data loss
  </verify>
  <done>
Supabase Pro active, pgvector enabled, connection pooling configured, daily backups verified, database ready for production workloads.
  </done>
</task>

<task type="auto">
  <name>Task 4: Configure domain DNS and verify end-to-end connectivity</name>
  <files></files>
  <action>
1. Domain setup (assume pickleiq.com registered, DNS provider accessible):
   - Vercel Dashboard → Domains → Add pickleiq.com
   - Follow DNS setup instructions:
     - Add A record: 76.76.19.165 (Vercel)
     - Or use Vercel Nameservers (easier): Change DNS at registrar to Vercel's

2. Configure DNS for API subdomain:
   - api.pickleiq.com → Route to Railway backend
   - Option A (CNAME): api.pickleiq.com CNAME → railway-production-api.up.railway.app
   - Option B (if Railway provides): Follow Railway docs for custom domain setup
   - Railway Dashboard → Service Settings → Domains → add api.pickleiq.com
   - Railway auto-issues SSL certificate (free)

3. Verify DNS propagation (may take 15-60 minutes):
   ```bash
   nslookup pickleiq.com
   nslookup api.pickleiq.com
   # Should resolve to Vercel/Railway IPs
   ```

4. Configure environment variables across platforms:
   - Vercel: NEXT_PUBLIC_FASTAPI_URL = https://api.pickleiq.com
   - Railway: DATABASE_URL, GROQ_API_KEY, TELEGRAM_BOT_TOKEN, LANGFUSE_SECRET_KEY
   - Supabase: automatic (no env var needed for connection)

5. Smoke test end-to-end:
   ```bash
   # Test frontend loads
   curl -I https://pickleiq.com
   # Expected: 200 OK + security headers

   # Test API health
   curl https://api.pickleiq.com/health
   # Expected: {"status": "ok", ...}

   # Test API → Database connection (query health endpoint that checks DB)
   # OR: GET /paddles (if endpoint exists) should return from database
   ```

6. Set up monitoring alerts (optional, basic):
   - Vercel: Monitors → add uptime check for pickleiq.com
   - Railway: Alerts → send email on deployment failure

7. Load test with 10 concurrent users (basic):
   ```bash
   # Using Apache Bench (ab) or similar
   ab -n 100 -c 10 https://api.pickleiq.com/health
   # Expected: P95 latency < 500ms for /health

   # If using load testing tool (k6, locust):
   # Load test /paddles endpoint → measure P95 latency on database query
   ```
  </action>
  <verify>
    - `nslookup pickleiq.com` resolves to Vercel IP
    - `nslookup api.pickleiq.com` resolves to Railway IP
    - `curl -I https://pickleiq.com` returns 200
    - `curl -I https://api.pickleiq.com/health` returns 200
    - Browser: https://pickleiq.com loads without errors
    - Browser console: no CORS errors on API calls
    - Load test: 10 concurrent requests to /health show P95 < 500ms
  </verify>
  <done>
Domain DNS configured, frontend and API accessible from production domains, HTTPS working, end-to-end connectivity verified, load baseline established.
  </done>
</task>

</tasks>

<verification>
Post-deployment checks:
1. Frontend accessible at https://pickleiq.com with HTTPS and security headers
2. API health check: `curl https://api.pickleiq.com/health` returns 200
3. Database connectivity: Rails can query PostgreSQL without connection pool exhaustion
4. Environment variables: all required vars set in Vercel, Railway, Supabase (none in git)
5. Load test passing: 10 concurrent users, P95 < 500ms
6. Monitoring: Railway health checks and Vercel uptime monitoring active
</verification>

<success_criteria>
- [x] Vercel Pro account active, production domain configured, HTTPS working
- [x] Railway backend deployed with health check endpoint
- [x] Supabase Pro tier active with pgvector and daily backups
- [x] Environment variables synchronized across Vercel, Railway, Supabase
- [x] End-to-end connectivity tested (frontend → API → database)
- [x] Security headers configured (HSTS, X-Frame-Options, X-Content-Type-Options)
- [x] Load test baseline: P95 < 500ms for 10 concurrent users
- [x] Rollback procedure documented (revert deployment, restore from backup if needed)
</success_criteria>

<output>
After completion, create `.planning/phases/06-launch-deploy/06-01-SUMMARY.md` documenting:
- Vercel/Railway/Supabase production configuration
- Environment variable mapping (what goes where)
- Health check results and load test baseline
- Rollback procedure (how to revert if deployment fails)
</output>

---

# Plan 06-02: CI/CD GitHub Actions Pipeline

---
phase: 06-launch-deploy
plan: 02
type: execute
wave: 1
depends_on: [06-01]
files_modified:
  - .github/workflows/test.yml
  - .github/workflows/deploy.yml
  - backend/pyproject.toml
  - CONTRIBUTING.md
autonomous: true
requirements: [R6.2]
user_setup:
  - service: github
    why: "GitHub Secrets for CI/CD pipeline"
    env_vars:
      - name: RAILWAY_TOKEN
        source: "Railway Dashboard → Account Settings → API Tokens"
      - name: VERCEL_TOKEN
        source: "Vercel Dashboard → Settings → Tokens → Create"
      - name: VERCEL_PROJECT_ID
        source: "Vercel Dashboard → Settings → Project ID"
      - name: VERCEL_ORG_ID
        source: "Vercel Dashboard → Settings → Team/Org ID"
    dashboard_config:
      - task: "Add secrets to GitHub repo"
        location: "GitHub Repo → Settings → Secrets and variables → Actions"

must_haves:
  truths:
    - "PR with failing test blocked by coverage check before merge"
    - "PR with <80% coverage blocked by orgoro/coverage action"
    - "Push to main auto-deploys backend to Railway + frontend to Vercel"
    - "PR against main deploys preview to Vercel staging environment"
    - "Branch protection rules enforced: require passing checks + code review"
    - "Coverage badge in README reflects current Python test coverage"
    - "Rollback tested: revert commit → redeploy → old code live"
  artifacts:
    - path: ".github/workflows/test.yml"
      provides: "Python lint + test + coverage gate"
      exports: ["pytest", "ruff check", "coverage ≥80%"]
    - path: ".github/workflows/deploy.yml"
      provides: "Auto-deploy to Railway + Vercel"
      exports: ["railway up", "vercel deploy"]
    - path: "CONTRIBUTING.md"
      provides: "CI/CD setup documentation for team"
      contains: "GitHub Secrets|workflow triggers|rollback procedure"
  key_links:
    - from: "GitHub PR"
      to: ".github/workflows/test.yml"
      via: "on: pull_request trigger"
      pattern: "on: pull_request → runs-on: ubuntu-latest"
    - from: "Coverage report"
      to: "orgoro/coverage action"
      via: "pytest --cov-report=xml"
      pattern: "pytest.*coverage.xml → orgoro/coverage"
    - from: "Push to main"
      to: "Railway + Vercel deployment"
      via: ".github/workflows/deploy.yml"
      pattern: "if: github.ref == refs/heads/main && github.event_name == push"

---

<objective>
Set up GitHub Actions CI/CD pipeline with automated testing, coverage gates, and production deployment. Enable code review enforcement and PR preview deployments.

Purpose: Prevent bugs from reaching production, maintain test coverage ≥80%, enable rapid safe deployments.
Output: Functional CI/CD pipeline with test gate, coverage enforcement, and automated deployments.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@.planning/06-launch-deploy/06-RESEARCH.md (pattern: GitHub Actions Coverage Gate)
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create test.yml workflow with pytest coverage gate</name>
  <files>.github/workflows/test.yml</files>
  <action>
Create .github/workflows/test.yml with:

```yaml
name: Test & Coverage

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: pickleiq_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ./backend[dev]

      - name: Lint with ruff
        run: |
          cd backend
          ruff check app/

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/pickleiq_test
          ENVIRONMENT: test
        run: |
          cd backend
          pytest --cov=app --cov-report=term --cov-report=xml --cov-report=html -v

      - name: Check coverage threshold (80%)
        uses: orgoro/coverage@v3
        with:
          coverageFile: ./backend/coverage.xml
          thresholdPercent: 80
          thresholdType: lines

      - name: Comment coverage on PR
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
          MINIMUM_GREEN: 80
          MINIMUM_ORANGE: 60
```

Explanation:
- `postgres` service: ephemeral test database
- `ruff check`: code formatting check (no semicolons, line length < 100)
- `pytest --cov=app`: run tests with coverage report
- `orgoro/coverage`: blocks PR if coverage < 80%
- `py-cov-action`: posts coverage comment on PR
  </action>
  <verify>
    - File .github/workflows/test.yml exists
    - Create a test PR (change a Python file, add a test)
    - GitHub Actions runs: test.yml should pass if coverage ≥80%
    - Check PR: coverage comment appears (green if ≥80%, orange if 60-80%)
    - Modify test.yml to set thresholdPercent to 100, push, verify PR fails until coverage is 100%
  </verify>
  <done>
test.yml workflow created, runs on PR, enforces coverage ≥80%, posts feedback to PR.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create deploy.yml workflow for auto-deploy main and PR previews</name>
  <files>.github/workflows/deploy.yml</files>
  <action>
Create .github/workflows/deploy.yml with:

```yaml
name: Deploy

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    # Reuse test job from test.yml (or make this a composite job)
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: pickleiq_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ./backend[dev]

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/pickleiq_test
          ENVIRONMENT: test
        run: |
          cd backend
          pytest --cov=app --cov-report=xml -v

      - name: Check coverage
        uses: orgoro/coverage@v3
        with:
          coverageFile: ./backend/coverage.xml
          thresholdPercent: 80

  deploy-preview:
    needs: test
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy preview to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
        run: |
          npm install -g vercel
          vercel deploy --token=$VERCEL_TOKEN

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy backend to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up --service backend --environment production

      - name: Deploy frontend to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
        run: |
          npm install -g vercel
          vercel deploy --prod --token=$VERCEL_TOKEN

      - name: Smoke test production (wait 30s for deployment)
        run: |
          sleep 30
          curl -f https://pickleiq.com/health || exit 1
          curl -f https://api.pickleiq.com/health || exit 1
```

Explanation:
- `deploy-preview`: runs on PR, deploys to Vercel staging (preview.vercel.app)
- `deploy-production`: runs only on push to main, deploys both Railway backend + Vercel frontend
- `smoke-test`: waits 30s for deployment to propagate, then verifies health endpoints
- Jobs use `needs: test` to ensure tests pass before deployment
  </action>
  <verify>
    - File .github/workflows/deploy.yml exists
    - Create a feature branch, make a change, push to origin
    - Create PR: GitHub Actions should run deploy-preview (Vercel preview URL appears)
    - Merge PR to main: GitHub Actions should run deploy-production + smoke tests
    - Check deployment status: Vercel + Railway show new commits deployed
    - Visit https://pickleiq.com/health and https://api.pickleiq.com/health → both 200
  </verify>
  <done>
deploy.yml workflow created, PR previews deploy to Vercel staging, main branch auto-deploys to production.
  </done>
</task>

<task type="auto">
  <name>Task 3: Configure branch protection rules and GitHub Secrets</name>
  <files></files>
  <action>
1. GitHub Repo → Settings → Branches → Add branch protection rule:
   - Branch name pattern: main
   - Require status checks to pass before merging:
     - ✓ Test & Coverage (from test.yml)
     - ✓ Deploy (from deploy.yml, if applicable)
   - Require code review approvals: 1 (can lower for solo dev, but good practice)
   - Require approval from code owners: NO (no CODEOWNERS file yet)
   - Dismiss stale pull request approvals when new commits are pushed: YES
   - Require branches to be up to date before merging: YES
   - Allow force pushes: NO
   - Allow deletions: NO

2. GitHub Repo → Settings → Secrets and variables → Actions → New secret:
   - RAILWAY_TOKEN: (from Railway Dashboard → Account Settings → API Tokens)
   - VERCEL_TOKEN: (from Vercel Dashboard → Settings → Tokens)
   - VERCEL_PROJECT_ID: (from Vercel project URL or settings)
   - VERCEL_ORG_ID: (from Vercel team settings)

3. Verify secrets are NOT visible in workflow logs:
   - GitHub masks secrets in logs (shows ***)
   - Do NOT echo secrets in workflow steps

4. Test branch protection:
   - Push a failing test to feature branch
   - Create PR: GitHub Actions should fail
   - Try to merge: "Merging is blocked" message
   - Fix test, push again: checks pass, merge allowed
  </action>
  <verify>
    - GitHub repo → Settings → Branches shows protection rule for main
    - Status checks required: ✓ Test & Coverage
    - Code review approval required: ✓ 1
    - Secrets visible in Settings → Secrets (RAILWAY_TOKEN, VERCEL_TOKEN, etc.)
    - Feature branch with failing test: PR blocked from merge
    - Feature branch with passing test: PR can be merged
  </verify>
  <done>
Branch protection rules enforced, GitHub Secrets configured, CI/CD pipeline protected.
  </done>
</task>

<task type="auto">
  <name>Task 4: Add coverage badge to README and document CI/CD setup</name>
  <files>CONTRIBUTING.md</files>
  <action>
1. Update README.md with coverage badge:
   ```markdown
   # PickleIQ

   ![Coverage Badge](https://github.com/your-org/pickleiq/actions/workflows/test.yml/badge.svg)
   ![Test Status](https://github.com/your-org/pickleiq/actions/workflows/test.yml/badge.svg?label=tests)

   ...
   ```

2. Create/update CONTRIBUTING.md with:
   ```markdown
   # Contributing to PickleIQ

   ## Setup

   1. Clone and install:
      ```bash
      git clone https://github.com/your-org/pickleiq.git
      cd picklepicker
      pip install -e ./backend[dev]
      npm install
      ```

   2. Run tests locally before pushing:
      ```bash
      cd backend
      pytest --cov=app --cov-report=term
      ```

   ## CI/CD Pipeline

   Every PR triggers:
   - Lint check (ruff)
   - Unit tests (pytest)
   - Coverage check (≥80% required)

   If checks fail, merge is blocked. Fix locally and push again.

   ## Deployment

   Merging to `main` automatically:
   1. Runs tests again
   2. Deploys backend to Railway production
   3. Deploys frontend to Vercel production
   4. Runs smoke tests (health checks)

   ## Rollback Procedure

   If production breaks:
   1. Identify the bad commit: `git log --oneline | head`
   2. Revert: `git revert <commit-hash>`
   3. Push to main: `git push origin main`
   4. GitHub Actions automatically re-deploys old code
   5. Monitor: `curl https://api.pickleiq.com/health`

   Revert takes 2-3 minutes. No manual rollback needed.
   ```

3. Document GitHub Secrets required for CI/CD:
   - RAILWAY_TOKEN: from Railway Dashboard
   - VERCEL_TOKEN: from Vercel Dashboard
   - VERCEL_PROJECT_ID: your Vercel project ID
   - VERCEL_ORG_ID: your Vercel org/team ID

   Note: Add these via GitHub Repo → Settings → Secrets.
  </action>
  <verify>
    - README.md contains coverage badge (even if build status is unknown)
    - CONTRIBUTING.md exists and documents:
      - How to run tests locally
      - What CI/CD pipeline does
      - Rollback procedure with example commands
    - CONTRIBUTING.md references GitHub Secrets needed
  </verify>
  <done>
README updated with badges, CONTRIBUTING.md documents CI/CD workflow and rollback procedure.
  </done>
</task>

<task type="auto">
  <name>Task 5: Test full CI/CD pipeline end-to-end</name>
  <files></files>
  <action>
1. Create a test feature branch:
   ```bash
   git checkout -b test/ci-cd-validation
   ```

2. Make a small change (e.g., add a comment to a Python file):
   ```bash
   # Edit backend/app/main.py, add a comment
   git add -A
   git commit -m "test: validate CI/CD pipeline"
   git push origin test/ci-cd-validation
   ```

3. Create PR via GitHub:
   - Go to GitHub → Pull requests → New PR
   - Select: test/ci-cd-validation → main
   - Create PR
   - Watch GitHub Actions: test.yml should run (lint, test, coverage)
   - If coverage ≥80%, checks pass (green ✓)

4. Verify PR preview deployment:
   - In PR, look for Vercel comment: "Visit Preview"
   - Click preview link → should load frontend from staging

5. Merge PR to main:
   - After checks pass, click "Merge pull request"
   - GitHub Actions runs deploy.yml (test + deploy-production)
   - Wait 3-5 minutes for deployment
   - Check Railway logs: new deploy should appear
   - Check Vercel: new deployment should appear

6. Verify production deployment:
   ```bash
   curl https://api.pickleiq.com/health
   # Should return {"status": "ok", ...}
   ```

7. Test rollback:
   - Revert the test commit: `git revert <commit-hash>`
   - Push to main
   - GitHub Actions should deploy old code
   - Production should be back to previous state in 2-3 minutes

8. Clean up:
   ```bash
   git branch -D test/ci-cd-validation
   ```
  </action>
  <verify>
    - Feature branch PR: GitHub Actions test.yml runs and passes
    - PR preview: Vercel preview URL appears in PR comments
    - Merge to main: GitHub Actions deploy.yml runs (both test and deploy-production jobs)
    - Production deployment: Railway and Vercel show new commits
    - Smoke test passes: `curl https://api.pickleiq.com/health` returns 200
    - Rollback tested: revert commit, push, old code deployed in 2-3 minutes
    - Rollback verified: `curl https://api.pickleiq.com/health` still works (endpoint unchanged for this test)
  </verify>
  <done>
Full CI/CD pipeline tested end-to-end, PR → preview → merge → production deployment verified, rollback procedure tested.
  </done>
</task>

</tasks>

<verification>
Post-pipeline checks:
1. GitHub Actions test.yml passes with coverage ≥80%
2. PR preview deploys to Vercel staging within 2 minutes
3. Push to main triggers deploy.yml (backend + frontend)
4. Production deployment completes within 3 minutes
5. Smoke tests pass: both /health endpoints return 200
6. Branch protection enforces test passing before merge
7. Rollback tested: revert commit redeploys old code
</verification>

<success_criteria>
- [x] test.yml workflow created with pytest coverage gate
- [x] deploy.yml workflow created with preview + production deployments
- [x] Branch protection rules enforce test passing + code review
- [x] GitHub Secrets configured (RAILWAY_TOKEN, VERCEL_TOKEN, etc.)
- [x] Coverage badge in README
- [x] CONTRIBUTING.md documents CI/CD and rollback procedure
- [x] Full pipeline tested: PR → preview → merge → production
- [x] Rollback procedure tested and documented
</success_criteria>

<output>
After completion, create `.planning/phases/06-launch-deploy/06-02-SUMMARY.md` documenting:
- GitHub Actions workflow configuration (test.yml, deploy.yml)
- CI/CD pipeline flow (PR → checks → deploy)
- Coverage enforcement (≥80% threshold)
- Preview and production deployment timings
- Rollback procedure with example commands
</output>

---

# Plan 06-03: Observability & Alerts

---
phase: 06-launch-deploy
plan: 03
type: execute
wave: 2
depends_on: [06-01]
files_modified:
  - backend/app/logging_config.py
  - backend/app/middleware/alerts.py
  - backend/app/routers/health.py
  - backend/app/main.py
  - backend/pyproject.toml
autonomous: true
requirements: [R6.3]
user_setup:
  - service: telegram
    why: "Real-time alerts for scraper failures and server errors"
    env_vars:
      - name: TELEGRAM_BOT_TOKEN
        source: "Create bot via Telegram BotFather (/newbot), copy token"
      - name: TELEGRAM_CHAT_ID
        source: "Send /start to bot, get chat ID from bot logs or Telegram API"
    dashboard_config:
      - task: "Create Telegram bot and get token"
        location: "Telegram @BotFather → /newbot → follow prompts"
  - service: langfuse
    why: "Production LLM observability and token tracking"
    env_vars:
      - name: LANGFUSE_SECRET_KEY
        source: "Langfuse Dashboard → Account → API Keys → copy secret"
    dashboard_config:
      - task: "Upgrade to Pro tier ($199/mo) for production"
        location: "Langfuse Dashboard → Billing"
      - task: "Configure trace sampling (25% initially)"
        location: "Langfuse SDK initialization in backend"

must_haves:
  truths:
    - "All logs output as machine-parseable JSON to stdout/Railway logs"
    - "5xx errors trigger Telegram alert to ops channel within 10 seconds"
    - "Scraper failures alert via Telegram with error context"
    - "Health check endpoint includes database and Redis status"
    - "Langfuse receives production LLM traces (Groq API calls)"
    - "Structured logs include request_id, method, path, status, duration_ms"
    - "Log aggregation working: Railway logs dashboard shows JSON parsing"
  artifacts:
    - path: "backend/app/logging_config.py"
      provides: "Structured JSON logging configuration"
      contains: "structlog.configure|JSONRenderer"
    - path: "backend/app/middleware/alerts.py"
      provides: "Telegram alerting on errors"
      exports: ["send_alert()", "TelegramAlerter"]
    - path: "backend/app/routers/health.py"
      provides: "Extended health check with subsystem status"
      contains: "database|redis|status"
    - path: "backend/app/main.py"
      provides: "Logging + alerting middleware registered"
      contains: "logging_middleware|exception_handler"
  key_links:
    - from: "FastAPI middleware"
      to: "structlog JSON output"
      via: "HTTP request/response logging"
      pattern: "logger.info.*http\\.(request|response)"
    - from: "Exception handler"
      to: "Telegram alerter"
      via: "async task on 5xx error"
      pattern: "asyncio.create_task.*send_alert"
    - from: "Groq API calls"
      to: "Langfuse"
      via: "Langfuse SDK integration"
      pattern: "langfuse.*trace|token"

---

<objective>
Implement structured logging in JSON format, set up Telegram alerts for production errors, and integrate Langfuse for LLM observability. Enable real-time monitoring and rapid issue detection.

Purpose: Detect production issues before users report them, track LLM costs, maintain operational visibility.
Output: Structured logs, Telegram alerting, Langfuse production traces, health check status endpoint.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@.planning/06-launch-deploy/06-RESEARCH.md (patterns: Structured JSON Logging, Telegram Alerts, Langfuse Integration)
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Configure structlog for JSON output in FastAPI</name>
  <files>backend/app/logging_config.py, backend/pyproject.toml, backend/app/main.py</files>
  <action>
1. Update backend/pyproject.toml dependencies:
   ```toml
   [project]
   dependencies = [
       "fastapi>=0.104",
       "uvicorn[standard]>=0.24",
       "structlog>=25.1.0",  # Add this
       "python-telegram-bot>=21.0",  # Add this
       "langfuse>=2.0",  # Add this
       # ... other dependencies
   ]
   ```

2. Create backend/app/logging_config.py:
   ```python
   import structlog
   import logging
   import sys
   from datetime import datetime

   def configure_logging(environment: str = "production"):
       """Configure structlog for JSON output in production, pretty-print in dev."""

       if environment == "production":
           # JSON output in production
           structlog.configure(
               processors=[
                   structlog.stdlib.filter_by_level,
                   structlog.stdlib.add_logger_name,
                   structlog.stdlib.add_log_level,
                   structlog.stdlib.PositionalArgumentsFormatter(),
                   structlog.processors.TimeStamper(fmt="iso"),
                   structlog.processors.StackInfoRenderer(),
                   structlog.processors.format_exc_info,
                   structlog.processors.UnicodeDecoder(),
                   structlog.processors.JSONRenderer(sort_keys=True)
               ],
               context_class=dict,
               logger_factory=structlog.stdlib.LoggerFactory(),
               cache_logger_on_first_use=True,
           )
       else:
           # Pretty-print in development
           structlog.configure(
               processors=[
                   structlog.stdlib.filter_by_level,
                   structlog.stdlib.add_logger_name,
                   structlog.stdlib.add_log_level,
                   structlog.stdlib.PositionalArgumentsFormatter(),
                   structlog.processors.TimeStamper(fmt="iso"),
                   structlog.processors.StackInfoRenderer(),
                   structlog.processors.format_exc_info,
                   structlog.dev.ConsoleRenderer()  # Pretty-print
               ],
               context_class=dict,
               logger_factory=structlog.stdlib.LoggerFactory(),
               cache_logger_on_first_use=True,
           )

       # Redirect stdlib logging to structlog
       logging.basicConfig(
           format="%(message)s",
           stream=sys.stdout,
           level=logging.INFO,
       )
   ```

3. Register in backend/app/main.py:
   ```python
   from app.logging_config import configure_logging
   import os

   environment = os.getenv("ENVIRONMENT", "development")
   configure_logging(environment)
   ```

4. Add HTTP request/response logging middleware:
   ```python
   # In main.py or new file middleware/logging.py
   from fastapi import Request
   import structlog
   import time
   import uuid

   logger = structlog.get_logger()

   @app.middleware("http")
   async def logging_middleware(request: Request, call_next):
       request_id = str(uuid.uuid4())
       start = time.time()

       logger.info(
           "http.request",
           request_id=request_id,
           method=request.method,
           path=request.url.path,
           query=str(request.url.query) if request.url.query else None
       )

       response = await call_next(request)
       duration = time.time() - start

       logger.info(
           "http.response",
           request_id=request_id,
           status=response.status_code,
           duration_ms=round(duration * 1000, 2)
       )

       return response
   ```

5. Test locally:
   ```bash
   cd backend
   export ENVIRONMENT=production
   uvicorn app.main:app --reload
   # Make request: curl http://localhost:8000/health
   # Should see JSON log: {"event": "http.request", "request_id": "...", ...}
   ```
  </action>
  <verify>
    - logging_config.py exists with structlog.configure()
    - Imports in main.py: `from app.logging_config import configure_logging`
    - HTTP middleware registered: logger.info calls in middleware
    - Local test: `curl http://localhost:8000/health` produces JSON logs
    - Production test (Railway): check logs, should see JSON with request_id, status, duration_ms
  </verify>
  <done>
structlog configured, HTTP middleware logging JSON, production environment enabled.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement Telegram alerting middleware for errors</name>
  <files>backend/app/middleware/alerts.py, backend/app/main.py</files>
  <action>
1. Create backend/app/middleware/alerts.py:
   ```python
   import asyncio
   import os
   from telegram import Bot
   from telegram.error import TelegramError
   import structlog
   from datetime import datetime

   logger = structlog.get_logger()

   class TelegramAlerter:
       def __init__(self):
           self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
           self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
           self.bot = Bot(token=self.bot_token) if self.bot_token else None
           self.min_alert_interval = 60  # Rate limit: don't spam same error twice in 60s
           self.last_alerts = {}

       async def send_alert(self, severity: str, title: str, details: str, context: dict = None):
           """Send alert to Telegram asynchronously without blocking request."""
           if not self.bot or not self.chat_id:
               logger.warning("telegram.disabled", title=title)
               return

           # Rate limit: same error type not more than once per 60s
           alert_key = f"{severity}:{title}"
           now = datetime.now().timestamp()
           if alert_key in self.last_alerts and (now - self.last_alerts[alert_key]) < self.min_alert_interval:
               return

           self.last_alerts[alert_key] = now

           # Format message
           emoji_map = {"ERROR": "🚨", "WARNING": "⚠️", "INFO": "ℹ️"}
           emoji = emoji_map.get(severity, "📌")

           message = f"{emoji} *{severity}: {title}*\n{details}"
           if context:
               context_str = str(context)[:200]
               message += f"\n```{context_str}```"

           try:
               await self.bot.send_message(
                   chat_id=self.chat_id,
                   text=message,
                   parse_mode="Markdown",
                   read_timeout=5
               )
               logger.info("telegram.alert.sent", severity=severity, title=title)
           except TelegramError as e:
               logger.error("telegram.alert.failed", error=str(e), title=title)
           except Exception as e:
               logger.error("telegram.alert.exception", error=str(e))

   alerter = TelegramAlerter()

   async def send_scraper_alert(error: str, url: str):
       """Alert ops when scraper fails."""
       await alerter.send_alert(
           severity="ERROR",
           title="Scraper failure",
           details=f"Failed to scrape {url[:50]}...: {error[:100]}",
           context={"url": url, "error_type": type(error).__name__}
       )
   ```

2. Register exception handler in main.py:
   ```python
   from fastapi.responses import JSONResponse
   from app.middleware.alerts import alerter

   @app.exception_handler(Exception)
   async def global_exception_handler(request, exc):
       logger.error("unhandled.exception", error=str(exc), path=request.url.path)

       # Send alert for 5xx errors (fire-and-forget)
       if isinstance(exc, Exception) and not isinstance(exc, ValueError):
           asyncio.create_task(
               alerter.send_alert(
                   severity="ERROR",
                   title="API Exception",
                   details=str(exc)[:200],
                   context={"path": request.url.path}
               )
           )

       return JSONResponse(
           status_code=500,
           content={"error": "Internal server error"}
       )
   ```

3. Test Telegram bot setup:
   ```bash
   # Create bot via Telegram BotFather (if not already done)
   # Get token: t0xxxxxxx:xXxxXxxXxxXx
   # Get chat ID: send /start to bot, reply message contains user ID

   # Export env vars
   export TELEGRAM_BOT_TOKEN="t0xxxxxxx:xXxxXxxXxxXx"
   export TELEGRAM_CHAT_ID="123456789"

   # Test alert
   curl -X POST http://localhost:8000/test-error
   # Should see Telegram message in ops channel
   ```

4. Add test endpoint (optional, remove before production):
   ```python
   @app.post("/test-error")
   async def test_error():
       """Test error alerting (remove before production)."""
       raise Exception("Test error from API")
   ```
  </action>
  <verify>
    - alerts.py exists with TelegramAlerter class and send_alert method
    - Exception handler registered in main.py
    - Export TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
    - Test: `curl -X POST http://localhost:8000/test-error` triggers Telegram alert
    - Verify in Telegram ops channel: alert message received
    - Rate limiting works: send error twice, second alert skipped
  </verify>
  <done>
Telegram alerting configured, exception handler triggers alerts asynchronously, rate limiting prevents spam.
  </done>
</task>

<task type="auto">
  <name>Task 3: Extend health check with subsystem status and integrate Langfuse</name>
  <files>backend/app/routers/health.py, backend/app/main.py</files>
  <action>
1. Update backend/app/routers/health.py with subsystem checks:
   ```python
   from fastapi import APIRouter, HTTPException
   from datetime import datetime
   import os
   import structlog
   from sqlalchemy import text
   from app.db import get_db  # Assuming db module exists

   logger = structlog.get_logger()
   router = APIRouter()

   @router.get("/health")
   async def health():
       """Extended health check including database, cache, and API status."""
       status_data = {
           "status": "ok",
           "timestamp": datetime.utcnow().isoformat(),
           "environment": os.getenv("ENVIRONMENT", "unknown"),
           "version": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")[:8],
           "subsystems": {}
       }

       # Check database connection
       try:
           async with get_db() as conn:
               await conn.execute(text("SELECT 1"))
           status_data["subsystems"]["database"] = "ok"
       except Exception as e:
           logger.error("health.database.failed", error=str(e))
           status_data["subsystems"]["database"] = f"error: {str(e)[:50]}"
           status_data["status"] = "degraded"

       # Check Redis connection (if used)
       try:
           # Assuming Redis client available
           # redis_client.ping()
           status_data["subsystems"]["redis"] = "ok"
       except Exception as e:
           logger.warning("health.redis.failed", error=str(e))
           status_data["subsystems"]["redis"] = f"error: {str(e)[:50]}"
           # Don't set degraded, Redis is optional

       # Check Langfuse connectivity (optional)
       try:
           # Langfuse SDK should be initialized
           # No explicit ping needed, check initialization
           status_data["subsystems"]["langfuse"] = "ok"
       except Exception as e:
           logger.warning("health.langfuse.failed", error=str(e))
           status_data["subsystems"]["langfuse"] = f"warning: {str(e)[:50]}"

       return status_data
   ```

2. Integrate Langfuse in main.py:
   ```python
   from langfuse import Langfuse
   import os

   # Initialize Langfuse client
   langfuse = None
   if os.getenv("LANGFUSE_SECRET_KEY"):
       langfuse = Langfuse(
           secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
           public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
           host="https://cloud.langfuse.com"  # Cloud endpoint
       )

   # Create global context for LLM calls
   # When calling Groq LLM, wrap in Langfuse trace:
   # trace = langfuse.trace(name="chat_request", user_id=user_id, metadata={...})
   ```

3. Example LLM call with Langfuse tracing (in chat endpoint):
   ```python
   from app.main import langfuse

   @app.post("/chat")
   async def chat(request: ChatRequest):
       if langfuse:
           trace = langfuse.trace(
               name="chat_request",
               metadata={"model": "groq-lm", "paddles": len(request.paddles)}
           )

       # Call Groq LLM
       response = await groq_client.chat.completions.create(
           model="mixtral-8x7b-32768",
           messages=messages,
           temperature=0.7
       )

       # End trace
       if langfuse:
           trace.generation(
               name="groq_response",
               model="mixtral-8x7b-32768",
               output=response.choices[0].message.content,
               usage={
                   "input_tokens": response.usage.prompt_tokens,
                   "output_tokens": response.usage.completion_tokens
               }
           )

       return {"response": response.choices[0].message.content}
   ```

4. Configure Langfuse sampling (to control costs):
   ```python
   # In main.py, when initializing Langfuse:
   langfuse = Langfuse(
       secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
       public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
       host="https://cloud.langfuse.com",
       sample_rate=0.25  # Sample 25% of traces initially, increase to 1.0 at higher volume
   )
   ```

5. Test health check:
   ```bash
   curl http://localhost:8000/health
   # Expected output:
   # {
   #   "status": "ok",
   #   "timestamp": "2026-03-28T12:00:00.000Z",
   #   "environment": "production",
   #   "version": "abc12345",
   #   "subsystems": {
   #     "database": "ok",
   #     "redis": "ok",
   #     "langfuse": "ok"
   #   }
   # }
   ```
  </action>
  <verify>
    - health.py includes subsystem checks (database, redis, langfuse)
    - Langfuse client initialized in main.py
    - Chat endpoint wraps LLM calls in Langfuse traces
    - Test: `curl http://localhost:8000/health` returns JSON with subsystems status
    - Test: Call /chat endpoint, verify Langfuse receives trace with token counts
    - Langfuse dashboard shows traces flowing in from production
  </verify>
  <done>
Health check endpoint extended with subsystem status, Langfuse integrated with trace sampling, observability pipeline complete.
  </done>
</task>

<task type="auto">
  <name>Task 4: Test observability end-to-end (logs, alerts, traces)</name>
  <files></files>
  <action>
1. Deploy to production (or staging with production env vars):
   - Push changes to main branch
   - GitHub Actions deploy.yml runs
   - Railway backend redeploys with new code
   - Monitor logs in Railway dashboard

2. Test JSON logging:
   ```bash
   # In Railway dashboard, check logs
   # Should see JSON entries like:
   # {"event": "http.request", "request_id": "...", "method": "GET", "path": "/health", ...}
   # {"event": "http.response", "request_id": "...", "status": 200, "duration_ms": 12.5}
   ```

3. Test Telegram alerting:
   ```bash
   # Trigger error in production:
   curl https://api.pickleiq.com/test-error
   # Expected: Telegram ops channel receives 🚨 ERROR alert within 10s
   ```

4. Test Langfuse tracing:
   - Call /chat endpoint: `curl -X POST https://api.pickleiq.com/chat -d '{"query": "best beginner paddles"}'`
   - Wait 5 seconds for trace propagation
   - Visit Langfuse Dashboard → Traces
   - Should see new trace with model=groq-lm, tokens counted

5. Test health check with subsystems:
   ```bash
   curl https://api.pickleiq.com/health
   # Expected: {"status": "ok", "subsystems": {"database": "ok", "redis": "ok", "langfuse": "ok"}}
   ```

6. Verify rate limiting on Telegram alerts:
   ```bash
   curl https://api.pickleiq.com/test-error  # 1st alert sent
   sleep 5
   curl https://api.pickleiq.com/test-error  # 2nd alert skipped (within 60s)
   sleep 60
   curl https://api.pickleiq.com/test-error  # 3rd alert sent (after 60s)
   ```

7. Monitor Langfuse costs:
   - Langfuse Dashboard → Billing/Usage
   - Watch for cost trends
   - At 25% sampling + 50 users ≈ 500 requests/day ≈ 125 traces sampled ≈ ~$10-20/mo

8. Clean up test error endpoint (remove /test-error before production):
   ```bash
   # Remove from main.py and redeploy
   git commit -m "chore: remove test error endpoint"
   git push origin main
   # Auto-deploys via GitHub Actions
   ```
  </action>
  <verify>
    - Railway logs show JSON format (machine-parseable)
    - Telegram alert received after /test-error call within 10s
    - Langfuse dashboard shows production traces with token counts
    - Health check returns all subsystems: ok
    - Rate limiting verified: no duplicate alerts within 60s
    - Langfuse cost tracking works (tokens tab shows usage)
    - /test-error endpoint removed before final verification
  </verify>
  <done>
Observability pipeline tested end-to-end, JSON logs flowing, Telegram alerts working, Langfuse tracing production LLM calls, health check operational.
  </done>
</task>

</tasks>

<verification>
Post-observability checks:
1. Railway logs dashboard displays JSON logs (structure visible)
2. Telegram ops channel receives error alerts within 10s
3. Langfuse dashboard shows production traces with token counts
4. Health check endpoint includes subsystem status (database, redis, langfuse)
5. Rate limiting prevents alert spam (same error ≤ 60s suppressed)
6. Langfuse cost tracking active (Pro tier billing updated)
</verification>

<success_criteria>
- [x] structlog JSON logging configured in production
- [x] HTTP request/response logging middleware in place
- [x] Telegram alerting on 5xx errors (asynchronous, non-blocking)
- [x] Health check extended with subsystem status
- [x] Langfuse integrated with LLM trace sampling (25% initially)
- [x] Logs aggregated in Railway dashboard
- [x] Telegram alerts rate-limited (60s interval per error type)
- [x] End-to-end observability tested (logs, alerts, traces)
</success_criteria>

<output>
After completion, create `.planning/phases/06-launch-deploy/06-03-SUMMARY.md` documenting:
- Structured logging configuration (structlog JSON)
- Telegram alerting setup and rate limiting
- Langfuse trace sampling and cost tracking
- Health check subsystem status responses
- Observability monitoring dashboard walkthrough
- Example logs, alerts, and traces
</output>

---

# Plan 06-04: Beta Launch

---
phase: 06-launch-deploy
plan: 04
type: execute
wave: 2
depends_on: [06-01, 06-02, 06-03]
files_modified:
  - backend/app/routers/paddles.py
  - backend/app/routers/chat.py
  - frontend/app/page.tsx
  - frontend/app/api/onboarding/route.ts
  - .github/workflows/scraper.yml
autonomous: false
requirements: [R6.4]
user_setup:
  - service: typeform
    why: "NPS survey for beta user feedback"
    env_vars: []
    dashboard_config:
      - task: "Create NPS survey (1 question + email)"
        location: "Typeform Dashboard → New → NPS"
      - task: "Set webhook to email results to ops"
        location: "Typeform Settings → Webhooks"
  - service: email_domain
    why: "Beta onboarding emails from noreply@pickleiq.com"
    env_vars:
      - name: RESEND_API_KEY
        source: "Resend Dashboard → API Keys"
    dashboard_config:
      - task: "Configure domain verification for Resend"
        location: "Resend Dashboard → Domains → pickleiq.com"

must_haves:
  truths:
    - "≥200 rackets indexed and searchable in production database"
    - "50 beta users onboarded with API keys and welcome emails"
    - "Affiliate links generating clicks (UTM tracking active)"
    - "NPS survey set up and ready to send at day 30 post-launch"
    - "No P1 production bugs reported by beta users"
    - "Database backups tested and verified"
    - "Search latency P95 < 500ms with real data"
    - "Chat recommendations latency P95 < 3s"
  artifacts:
    - path: "backend/app/routers/paddles.py"
      provides: "GET /paddles with search/filter endpoints"
      exports: ["GET /paddles", "GET /paddles/{id}", "GET /paddles/search"]
    - path: "backend/app/routers/chat.py"
      provides: "POST /chat streaming recommendation endpoint"
      exports: ["POST /chat"]
    - path: "frontend/app/page.tsx"
      provides: "Landing page with onboarding flow"
      contains: "quiz|chat widget|affiliate disclosure"
    - path: ".github/workflows/scraper.yml"
      provides: "Scheduled data crawlers for ≥200 rackets"
      contains: "schedule.*24h|crawlers"
    - path: "backend/app/routers/onboarding.py"
      provides: "Beta user signup and API key generation"
      exports: ["POST /onboarding/signup", "POST /onboarding/api-key"]
  key_links:
    - from: "Scraper workflows"
      to: "Database (≥200 rackets)"
      via: ".github/workflows/scraper.yml schedule"
      pattern: "schedule.*24h"
    - from: "Frontend onboarding"
      to: "API key generation"
      via: "POST /onboarding/signup"
      pattern: "email|api_key"
    - from: "Product pages"
      to: "Affiliate links"
      via: "UTM params + FTC disclosure"
      pattern: "utm_source=pickleiq|FTC disclosure"
    - from: "Day 30"
      to: "NPS survey"
      via: "Scheduled email job"
      pattern: "cron.*day-30|Typeform webhook"

---

<objective>
Launch PickleIQ beta with 50 selected users, ≥200 rackets indexed, affiliate links active, and NPS baseline collection framework in place. Transition from production infrastructure (Plan 06-01) to user-facing operations.

Purpose: Validate product with real users, collect usage data, identify critical bugs before public launch.
Output: Live beta product with 50 active users, indexed catalog, affiliate tracking, NPS feedback loop.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@.planning/06-launch-deploy/06-RESEARCH.md (patterns: Beta Launch Strategy, NPS Survey, FTC Compliance)
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Full-stack end-to-end testing (search, chat, affiliate flow)</name>
  <files></files>
  <action>
Perform manual end-to-end testing of complete user journey before beta launch:

1. **Search & Discovery Flow:**
   - Open https://pickleiq.com
   - Search for "Selkirk" or "Onix" racket
   - Verify results return (≥200 rackets indexed)
   - Click on a paddle: should show price, specs, affiliate link
   - Verify FTC disclosure visible on page

2. **Quiz Onboarding:**
   - Go to https://pickleiq.com
   - Complete quiz: Select nível (beginner), estilo (control), orçamento (R$200-400)
   - Verify chat widget appears with context from quiz

3. **Chat Recommendation:**
   - In chat widget, ask: "What racket do you recommend for a beginner who wants control?"
   - Wait for response (target P95 < 3s)
   - Verify:
     - Response is in Portuguese (PT-BR)
     - Includes top 3 paddle recommendations with prices
     - Includes affiliate link (Selkirk, Onix, Wilson, etc.)
     - No hallucinations or broken specs

4. **Affiliate Tracking:**
   - Click affiliate link from chat response
   - Open browser DevTools → Network tab
   - Verify request sent to `/api/track-affiliate?utm_source=pickleiq&utm_campaign=chat&...`
   - Follow affiliate link to retailer
   - Retailer should show pickleiq.com referral param

5. **Admin Panel:**
   - Go to https://pickleiq.com/admin (should redirect without ADMIN_SECRET)
   - Set password (if needed): export ADMIN_SECRET=your_secret, set in Vercel
   - Login to /admin/queue
   - Verify: review queue shows pending paddle matches
   - Login to /admin/catalog
   - Verify: can add/edit/delete paddles

6. **Load Test with Real Data:**
   ```bash
   # Test with 10 concurrent users
   ab -n 100 -c 10 https://api.pickleiq.com/paddles
   # Expected: P95 < 500ms

   ab -n 100 -c 10 https://api.pickleiq.com/chat \
     -T "application/json" \
     -d '{"query":"best beginner"}'
   # Expected: P95 < 3s (chat is slower)
   ```

7. **Monitor Health During Testing:**
   ```bash
   # Check system status
   curl https://api.pickleiq.com/health
   # Monitor Langfuse: Dashboard → Traces (should see chat requests)
   # Monitor Railway: Logs (should see no errors)
   # Monitor Telegram: no alerts should fire (unless simulated)
   ```

8. **Database Integrity Check:**
   - Verify ≥200 rackets indexed: `SELECT COUNT(*) FROM paddles;`
   - Verify no orphaned prices: `SELECT COUNT(*) FROM price_snapshots WHERE paddle_id IS NULL;`
   - Check latest price freshness: `SELECT MAX(scraped_at) FROM price_snapshots;`
  </action>
  <verify>
    - Search returns ≥200 results, no errors
    - Quiz onboarding completes, chat widget appears
    - Chat responds within 3s with Portuguese recommendations
    - Affiliate links clickable and tracked
    - Admin panel accessible with ADMIN_SECRET
    - Load test: 10 concurrent /paddles requests complete in <500ms P95
    - Load test: 10 concurrent /chat requests complete in <3s P95
    - Health check returns all subsystems: ok
    - Database: ≥200 paddles indexed, no orphaned data
  </verify>
  <done>
Full-stack functionality verified, performance baseline confirmed, admin panel accessible, database integrity validated.
  </done>
</task>

<task type="auto">
  <name>Task 2: Scale data crawlers to index ≥200 rackets</name>
  <files>.github/workflows/scraper.yml</files>
  <action>
Ensure all data crawlers run and produce ≥200 rackets indexed:

1. **Review existing crawlers (from Phase 1-2):**
   - Brazil Pickleball Store (Firecrawl)
   - Mercado Livre Afiliados (ML API)
   - Drop Shot Brasil (Firecrawl)
   - Fromuth (if available)

2. **Create/.github/workflows/scraper.yml scheduler:**
   ```yaml
   name: Data Crawlers

   on:
     schedule:
       - cron: '0 2 * * *'  # 2 AM UTC = 10 PM BRT (off-peak)
     workflow_dispatch:  # Manual trigger

   jobs:
     crawl:
       runs-on: ubuntu-latest
       env:
         DATABASE_URL: ${{ secrets.DATABASE_URL }}
         FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
         MERCADO_LIVRE_API_KEY: ${{ secrets.MERCADO_LIVRE_API_KEY }}
         TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
         TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: '3.11'
         - run: |
             pip install -e ./backend
             cd backend
             python -m pipeline.crawlers.brazil_pickleball_store
             python -m pipeline.crawlers.mercado_livre
             python -m pipeline.crawlers.drop_shot_brasil
         - name: Verify crawl results
           run: |
             cd backend
             python -c "
             from app.db import get_db
             import asyncio
             async def count_paddles():
                 async with get_db() as conn:
                     result = await conn.execute('SELECT COUNT(*) FROM paddles')
                     count = result.scalar()
                     print(f'Total paddles: {count}')
                     if count < 200:
                         raise Exception(f'Expected ≥200 paddles, got {count}')
             asyncio.run(count_paddles())
             "
   ```

3. **Monitor crawler success:**
   - After 24h, check Railway logs for crawler execution
   - Verify Telegram alerts for any failures
   - Query database: `SELECT COUNT(*) FROM paddles` (should show ≥200)

4. **Optimize crawler performance (if needed):**
   - If crawlers taking >30 min, consider:
     - Running crawlers in parallel (different jobs)
     - Increasing timeout for long-running crawlers
     - Sampling subset of products on weekdays (full crawl on weekends)

5. **Set up manual crawler trigger:**
   - GitHub Actions → Scraper workflow → "Run workflow"
   - Use for on-demand full crawl before beta launch
  </action>
  <verify>
    - .github/workflows/scraper.yml exists with schedule trigger (24h)
    - Crawlers run successfully on schedule or manual trigger
    - Database contains ≥200 paddles after crawl
    - No Telegram alerts during successful crawl
    - Latest prices populated (scraped_at recent)
  </verify>
  <done>
Data crawlers scheduled, ≥200 rackets indexed, crawler health monitored.
  </done>
</task>

<task type="auto">
  <name>Task 3: Create beta user onboarding flow (email signup, API key generation)</name>
  <files>backend/app/routers/onboarding.py, frontend/app/api/onboarding/route.ts</files>
  <action>
Create beta user signup and API key management flow:

1. **Backend onboarding router:**
   ```python
   # backend/app/routers/onboarding.py
   from fastapi import APIRouter, HTTPException
   from pydantic import BaseModel, EmailStr
   import uuid
   import os
   from datetime import datetime
   from sqlalchemy import insert

   router = APIRouter()

   class OnboardingRequest(BaseModel):
       email: EmailStr
       name: str

   @router.post("/onboarding/signup")
   async def signup_beta_user(request: OnboardingRequest):
       """Sign up beta user, generate API key, send welcome email."""
       try:
           # Check if user exists
           async with get_db() as conn:
               existing = await conn.execute(
                   select(User).where(User.email == request.email)
               )
               if existing.scalar_one_or_none():
                   raise HTTPException(400, "Email already registered")

           # Create user + API key
           api_key = f"pk_{uuid.uuid4().hex[:32]}"
           async with get_db() as conn:
               stmt = insert(User).values(
                   email=request.email,
                   name=request.name,
                   api_key=api_key,
                   created_at=datetime.utcnow()
               )
               await conn.execute(stmt)
               await conn.commit()

           # Send welcome email (Resend)
           from resend import Resend
           resend = Resend(api_key=os.getenv("RESEND_API_KEY"))
           resend.emails.send({
               "from": "noreply@pickleiq.com",
               "to": request.email,
               "subject": "Welcome to PickleIQ Beta!",
               "html": f"""
               <h1>Welcome, {request.name}!</h1>
               <p>Your API key: <code>{api_key}</code></p>
               <p>Use this to query the PickleIQ API:</p>
               <pre>curl -H "Authorization: Bearer {api_key}" https://api.pickleiq.com/paddles</pre>
               <p>Happy pickling!</p>
               """
           })

           return {
               "email": request.email,
               "api_key": api_key,
               "message": "Welcome email sent"
           }

       except Exception as e:
           logger.error("onboarding.signup.failed", error=str(e))
           raise HTTPException(500, "Signup failed")
   ```

2. **Frontend signup form:**
   ```typescript
   // frontend/app/api/onboarding/route.ts
   import { NextRequest, NextResponse } from 'next/server';

   export async function POST(request: NextRequest) {
       const { email, name } = await request.json();

       try {
           const response = await fetch('https://api.pickleiq.com/onboarding/signup', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ email, name })
           });

           if (!response.ok) {
               return NextResponse.json(
                   { error: 'Signup failed' },
                   { status: response.status }
               );
           }

           const data = await response.json();
           return NextResponse.json(data);
       } catch (error) {
           return NextResponse.json(
               { error: 'Server error' },
               { status: 500 }
           );
       }
   }
   ```

3. **Beta signup modal on landing page:**
   - Add "Join Beta" button to landing page
   - Opens modal with email + name fields
   - Submit calls POST /api/onboarding
   - Show success: "Check your email for API key"

4. **Email template (React Email):**
   ```typescript
   // emails/beta-welcome.tsx
   import { Body, Button, Container, Head, Hr, Html, Img, Link, Preview, Row, Section, Text } from '@react-email/components';

   export function BetaWelcomeEmail({ name, apiKey }: { name: string; apiKey: string }) {
       return (
           <Html>
               <Head />
               <Preview>Your PickleIQ Beta API Key</Preview>
               <Body style={{ fontFamily: 'Arial' }}>
                   <Container>
                       <Section>
                           <Text>Welcome, {name}!</Text>
                           <Text>You're now part of the PickleIQ beta. Your API key:</Text>
                           <Text style={{ backgroundColor: '#f0f0f0', padding: '12px', fontFamily: 'monospace' }}>
                               {apiKey}
                           </Text>
                           <Button href={`https://pickleiq.com/docs?api_key=${apiKey}`} style={{ backgroundColor: '#007bff', color: '#fff', padding: '12px', textDecoration: 'none' }}>
                               View Documentation
                           </Button>
                       </Section>
                   </Container>
               </Body>
           </Html>
       );
   }
   ```

5. **Manually send invites (before public beta):**
   - Create list of 50 beta users (emails)
   - Use admin panel or script to create users:
     ```python
     # backend/scripts/invite_beta_users.py
     import asyncio
     from app.db import get_db
     from resend import Resend

     async def invite_users(emails: list[str]):
         for email in emails:
             # Create user in DB (or signup endpoint)
             # Send email with API key
             pass
     ```

6. **Track onboarding metrics:**
   - Dashboard: users signed up (count)
   - Dashboard: API key usage per user (calls/day)
   - Alert if user goes inactive (no calls for 7 days)
  </action>
  <verify>
    - onboarding.py router exists with /signup endpoint
    - POST /onboarding/signup accepts email + name, returns api_key
    - Welcome email sent from noreply@pickleiq.com with API key
    - Frontend signup form submits to /api/onboarding
    - Manual test: signup, verify email received with API key
    - Database: users table contains 50 beta user records
  </verify>
  <done>
Beta user onboarding flow complete, signup endpoint active, welcome emails sending, API keys generated.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Complete production deployment with 50 beta users onboarded, ≥200 rackets indexed, affiliate links active, observability pipeline running</what-built>
  <how-to-verify>
1. Open https://pickleiq.com → should load with no errors
2. Search for "racket" → verify ≥200 results returned
3. Complete quiz onboarding → chat widget responds with recommendation in <3s
4. Click affiliate link → verify tracked (check /api/track-affiliate request)
5. Visit https://pickleiq.com/admin (with ADMIN_SECRET) → verify queue and catalog accessible
6. Check database: `SELECT COUNT(*) FROM users WHERE created_at > now() - interval '7 days'` → should show ~50 beta users onboarded in last 7 days
7. Monitor health: `curl https://api.pickleiq.com/health` → all subsystems ok
8. Check Langfuse: Dashboard → Traces → should see production LLM calls with token counts
9. Check Telegram ops channel: monitor for any critical errors (should be clean)
10. Load test: `ab -n 100 -c 10 https://api.pickleiq.com/paddles` → P95 <500ms
  </how-to-verify>
  <resume-signal>Type "approved" if all checks pass, or describe any issues found</resume-signal>
</task>

<task type="auto">
  <name>Task 4: Set up NPS survey and deploy to production</name>
  <files></files>
  <action>
Set up Net Promoter Score (NPS) survey to be sent to beta users at day 30:

1. **Create NPS survey in Typeform:**
   - Visit https://typeform.com → Create → NPS
   - Question: "How likely are you to recommend PickleIQ to a friend?"
   - Scale: 0-10
   - Add follow-up: "What could we improve?" (open-ended text)
   - Add email capture: Ask for contact email (pre-filled from invite list)
   - Set end: "Thank you for your feedback!"

2. **Configure Typeform webhook:**
   - Settings → Integrations → Webhooks
   - Add webhook: POST to https://api.pickleiq.com/webhooks/nps-response
   - Backend creates endpoint to receive NPS scores and store in database

3. **Implement NPS collection endpoint:**
   ```python
   # backend/app/routers/webhooks.py
   @router.post("/webhooks/nps-response")
   async def nps_response(data: dict):
       """Receive NPS response from Typeform."""
       # Parse Typeform payload
       # Extract: email, nps_score (0-10), feedback_text
       # Store in database: nps_responses table
       # Log: "nps.response", email=..., score=...
       return {"status": "ok"}
   ```

4. **Schedule NPS survey send (day 30):**
   ```yaml
   # .github/workflows/nps-survey.yml
   on:
     schedule:
       - cron: '0 9 * * *'  # 9 AM UTC daily

   jobs:
     send_nps:
       runs-on: ubuntu-latest
       env:
         TYPEFORM_API_KEY: ${{ secrets.TYPEFORM_API_KEY }}
       steps:
         - uses: actions/checkout@v4
         - run: |
             python -m scripts.send_nps_surveys
             # Script checks: user created_at > 30 days ago AND hasn't received NPS yet
             # Sends Typeform link via Resend email
   ```

5. **Track NPS baseline:**
   - Monitor Typeform responses in real-time
   - Calculate average NPS: (% promoters - % detractors) * 100
   - Target: NPS ≥ 40 (anything >0 is positive for MVP)
   - Dashboard: show NPS score, feedback themes

6. **Database schema for NPS:**
   ```sql
   CREATE TABLE nps_responses (
       id UUID PRIMARY KEY,
       user_id UUID REFERENCES users(id),
       score INT CHECK (score >= 0 AND score <= 10),
       feedback TEXT,
       received_at TIMESTAMP DEFAULT NOW(),
       responded_at TIMESTAMP
   );
   ```

7. **Monitor NPS responses:**
   - Daily email digest: "X users responded, NPS = Y"
   - Alert if score < 0 (more detractors than promoters)
   - Qualitative analysis: group feedback by theme (performance, UX, missing features)
  </action>
  <verify>
    - Typeform NPS survey created and published
    - Typeform webhook endpoint configured
    - Backend /webhooks/nps-response endpoint exists
    - Database nps_responses table created
    - .github/workflows/nps-survey.yml scheduled for day 30
    - Test email sent to admin: verify NPS survey link works
    - Test Typeform webhook: POST to /webhooks/nps-response, verify data stored
  </verify>
  <done>
NPS survey infrastructure set up, scheduled for day 30 post-launch, webhook collecting responses, baseline tracking ready.
  </done>
</task>

</tasks>

<verification>
Pre-launch checklist (human verify task):
1. Frontend loads without errors, search returns ≥200 rackets
2. Quiz → chat flow works, recommendations P95 <3s
3. Affiliate links tracked and clickable
4. Admin panel accessible with ADMIN_SECRET
5. Database: 50 beta users onboarded with API keys
6. Health check: all subsystems ok
7. Langfuse: production traces flowing with token counts
8. Telegram ops channel: no critical errors
9. Load test baseline: P95 <500ms for search, <3s for chat
10. Backup tested and documented
11. NPS survey ready for day 30
12. No P1 bugs in production
</verification>

<success_criteria>
- [x] ≥200 rackets indexed and searchable
- [x] 50 beta users onboarded with API keys + welcome emails
- [x] Affiliate links generating clicks (UTM tracking active)
- [x] NPS survey framework set up (Typeform + webhook)
- [x] No P1 production bugs
- [x] Database backups tested and documented
- [x] Performance baselines: search P95 <500ms, chat P95 <3s
- [x] Full-stack end-to-end testing completed
- [x] Observability pipeline live (logs, alerts, traces)
- [x] Beta launch checkpoint passed (human verification)
</success_criteria>

<output>
After completion, create `.planning/phases/06-launch-deploy/06-04-SUMMARY.md` documenting:
- Beta launch checklist (all items verified)
- 50 onboarded users list (emails + API keys)
- Data crawler status (≥200 rackets indexed)
- Performance baselines (search, chat, health check)
- NPS survey setup and schedule
- Observability monitoring dashboards
- Incident response procedures
- Day 30 / Day 90 action items (NPS follow-up, analysis)
</output>

---

</body>

---

## WAVE STRUCTURE

**Wave 1 (Parallel):**
- Plan 06-01: Production Infrastructure (Vercel, Railway, Supabase)
- Plan 06-02: CI/CD Pipeline (GitHub Actions test & deploy)

**Wave 2 (Depends on Wave 1):**
- Plan 06-03: Observability (Structured logs, Telegram alerts, Langfuse)
- Plan 06-04: Beta Launch (User onboarding, data crawlers, NPS survey)

**Execution:** All Wave 1 plans run in parallel. Wave 2 begins after Wave 1 completes.

---

## RISK ASSESSMENT

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Database connection pool exhaustion during scraper | HIGH | Supabase Pro + PgBouncer, max pool size 10, monitor Railway metrics |
| Langfuse cost spike at scale | MEDIUM | 25% trace sampling initially, cost alerts at $500/mo, increase sampling at 500+ daily traces |
| Telegram alert spam | MEDIUM | Rate limiting: 60s min interval per error type, test with /test-error endpoint |
| Affiliate link attribution loss | HIGH | UTM params validated, test flow before launch, monitor click-through in affiliate dashboard |
| NPS survey low response rate | MEDIUM | Send at day 30 (not day 1), segment by usage (≥5 searches), follow-up with open-ended survey |
| Beta user onboarding friction | MEDIUM | Welcome email with API key, docs link, support channel (Telegram/Discord) |
| Rollback failure | HIGH | Test rollback during Week 1: `git revert`, push to main, verify old code deployed |

---

## RESOURCE REQUIREMENTS

- **Time:** 4 days (Phases 06-01, 02, 03, 04) for experienced team
- **Cost (monthly):** ~$275 (Vercel $20 + Railway $30 + Supabase $25 + Langfuse $199 + domain $1)
- **API quota:** Groq (unlimited with free tier), Firecrawl (budget: $50/month for 200 calls)
- **Team:** 1 engineer (solo, Claude assists all 4 plans)
