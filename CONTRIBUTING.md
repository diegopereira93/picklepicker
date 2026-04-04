# Contributing to PickleIQ

## Setup

1. Clone and install:
   ```bash
   git clone https://github.com/diegopereira93/picklepicker.git
   cd picklepicker
   make setup
   ```

2. Configure environment:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your credentials
   ```

3. Verify environment:
   ```bash
   make env-check
   ```

4. Start developing:
   ```bash
   make dev
   # Backend: http://localhost:8000
   # Frontend: http://localhost:3000
   # API Docs: http://localhost:8000/docs
   ```

## CI/CD Pipeline

Every PR triggers automated checks:
- **Lint check** (ruff): Code formatting and style rules
- **Test suite** (pytest): Unit and integration tests
- **Coverage gate** (orgoro): Minimum 80% code coverage required
- **Preview deploy** (Vercel): Staging environment for QA

Merging to `master` triggers production deployment:
- **Backend** (Railway): FastAPI service + PostgreSQL
- **Frontend** (Vercel): Next.js app
- **Smoke tests**: Health checks on both services

## GitHub Secrets Configuration

The following secrets must be configured in GitHub repo settings:

| Secret | Source | Description |
|--------|--------|-------------|
| `RAILWAY_TOKEN` | Railway Dashboard → Account Settings → API Tokens | Railway deployment authentication |
| `VERCEL_TOKEN` | Vercel Dashboard → Settings → Tokens | Vercel deployment authentication |
| `VERCEL_PROJECT_ID` | Vercel Dashboard → Settings (Project ID field) | Vercel frontend project identifier |
| `VERCEL_ORG_ID` | Vercel Dashboard → Team/Org Settings | Vercel organization identifier |

### Adding GitHub Secrets

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter the secret name and value
4. Save

**Important:** Never commit secrets to git. Use GitHub Secrets exclusively.

## Branch Protection Rules

The `master` branch requires:
- All status checks passing (test.yml, deploy.yml)
- 1 code review approval (or 0 for solo development)
- Branches up to date before merging
- No force pushes or deletions

## Development Workflow

1. Create feature branch from `master`:
   ```bash
   git checkout -b feature/your-feature master
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "feat: description of changes"
   git push origin feature/your-feature
   ```

3. Open PR on GitHub:
   - GitHub Actions automatically runs tests
   - Coverage badge shows test coverage status
   - If all checks pass, request code review

4. After approval, merge to `main`:
   - Production deployment starts automatically
   - Smoke tests verify both frontend and backend health

## Testing Locally

Use the Makefile for all testing — it handles venv activation and environment setup automatically.

### Run all tests
```bash
make test
```

### Backend (Python)

```bash
make test-backend         # pytest -v
make test-backend-cov     # pytest with HTML coverage report
```

### Frontend (Next.js)

```bash
make test-frontend        # vitest run
```

### E2E / Scraper tests

```bash
make test-e2e             # Requires DB running (starts it automatically)
```

## Environment Variables

Copy `.env.example` to `backend/.env` and fill in values:

```bash
cp backend/.env.example backend/.env
```

Run `make env-check` to verify your setup. It validates Docker, DATABASE_URL, and API keys automatically.

**For production**, environment variables are set in:
- **Vercel**: Dashboard → Settings → Environment Variables
- **Railway**: Dashboard → Service Settings → Environment
- **GitHub**: Repository → Settings → Secrets and variables

Never commit `.env.local` or other secret files. They are in `.gitignore`.

## Code Style

We use:
- **Python**: ruff for linting, black for formatting
- **TypeScript/JavaScript**: eslint + prettier

Check formatting before committing:
```bash
cd backend
ruff check app/
```

## Rollback Procedure

If production deployment fails:

1. **Identify the problematic commit:**
   ```bash
   git log --oneline -5
   ```

2. **Revert the commit:**
   ```bash
   git revert <commit-sha>
   git push origin main
   ```

3. **GitHub Actions automatically redeploys:**
   - Revert commit triggers deploy.yml workflow
   - Previous working version restored to production

4. **Verify rollback:**
   ```bash
   curl https://pickleiq.com/health
   curl https://api.pickleiq.com/health
   ```

## Questions or Issues?

- Check existing GitHub issues
- Open a new issue with detailed description
- Reference related PRs or discussions
