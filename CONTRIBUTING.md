# Contributing to PickleIQ

## Setup

1. Clone and install:
   ```bash
   git clone https://github.com/diegopereira93/picklepicker.git
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

### Backend (Python)

```bash
cd backend

# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Run specific test file
pytest tests/test_paddles.py -v

# Run specific test
pytest tests/test_paddles.py::test_paddle_search -v
```

### Frontend (Next.js)

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

## Environment Variables

Copy `.env.example` to `.env.local` and fill in values:

```bash
cp .env.example .env.local
```

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
