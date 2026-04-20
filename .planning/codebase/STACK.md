# Technology Stack

**Analysis Date:** 2026-04-20

## Languages

**Primary:**
- Python 3.12+ - Backend API and data pipeline
- TypeScript 5.x - Frontend (Next.js 14 App Router)

**Secondary:**
- JavaScript - Frontend (React 18)

## Runtime

**Environment:**
- Python 3.12 (slim) - Backend runtime
- Node.js 20.x - Frontend build/dev (Next.js 14 requirement)

**Package Managers:**
- pip/setuptools - Python packages (via `pip install -e .`)
- npm - Frontend JavaScript packages
- Lockfile: Not present (npm uses package-lock.json auto-generated)

## Frameworks

**Backend:**
- FastAPI 0.135.2 - REST API framework
- Uvicorn - ASGI server
- Pydantic 2.x - Data validation

**Frontend:**
- Next.js 14.2.35 - React framework with App Router
- React 18 - UI library
- Tailwind CSS 3.4.1 - Utility-first CSS
- Base UI 1.3.0 + Radix UI - Component primitives

**Testing:**
- pytest-asyncio 0.21+ - Backend async tests
- Vitest 4.1.2 - Frontend unit tests
- Playwright 1.58.2 - E2E tests

**Database:**
- PostgreSQL 16 - Primary database
- pgvector - Vector similarity search
- psycopg 3.1+ - Async PostgreSQL driver

## Key Dependencies

### Backend (`backend/pyproject.toml`)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.135.2 | Web framework |
| uvicorn | (latest) | ASGI server |
| pydantic | 2.x | Data validation |
| psycopg | 3.1+ | PostgreSQL driver |
| structlog | 24.1.0 | Structured logging |
| groq | 0.4.0 | LLM API client |
| httpx | 0.27.0 | HTTP client |

### Pipeline (`pipeline/pyproject.toml`)

| Package | Version | Purpose |
|---------|---------|---------|
| firecrawl-py | 4.21.0 | Web scraping |
| psycopg | 3.3.3 | PostgreSQL driver |
| tenacity | 9.1.4 | Retry logic |
| python-telegram-bot | 22.7 | Telegram notifications |
| httpx | 0.28.1 | HTTP client |
| rapidfuzz | 3.0+ | Fuzzy string matching |

### Frontend (`frontend/package.json`)

| Package | Version | Purpose |
|---------|---------|---------|
| next | 14.2.35 | React framework |
| react | 18 | UI library |
| @clerk/nextjs | 6.39.1 | Authentication |
| @base-ui/react | 1.3.0 | Component primitives |
| @radix-ui/* | latest | UI component primitives |
| ai | 6.0.141 | AI SDK for React |
| @ai-sdk/react | 3.0.143 | AI React hooks |
| recharts | 3.8.1 | Charts |
| resend | 6.9.4 | Email delivery |
| tailwindcss | 3.4.1 | CSS framework |
| lucide-react | 1.7.0 | Icons |

## Infrastructure

**Local Development:**
- Docker + Docker Compose - PostgreSQL via `docker-compose.yml`
- Image: `pgvector/pgvector:pg16`

**Deployment:**
- Backend: Railway (Python 3.12 container)
- Frontend: Vercel (Next.js)
- Database: Supabase (PostgreSQL with pgvector)

**CI/CD:**
- GitHub Actions - 7 workflow files in `.github/workflows/`
- Workflows: test, deploy, scraper, lighthouse, price-alerts, validate-production, nps-survey

## Configuration

**Environment:**
- Backend: `backend/.env` - DATABASE_URL, GROQ_API_KEY, JINA_API_KEY
- Frontend: `frontend/.env` - NEXT_PUBLIC_FASTAPI_URL, ADMIN_SECRET
- Root: `.env` - Shared config (database, API keys)

**Build Tools:**
- pyproject.toml (x2) - Backend and pipeline packaging
- package.json - Frontend scripts and dependencies
- Makefile - Development orchestration

## Version Information

| Component | Version | Source |
|-----------|---------|--------|
| Project | 2.3.0 | `VERSION` file |
| Python | 3.12+ | `pyproject.toml` requires-python |
| Next.js | 14.2.35 | `frontend/package.json` |
| FastAPI | 0.135.2 | `backend/pyproject.toml` |
| PostgreSQL | 16 | Docker Compose (pgvector image) |

## Project Structure

```
picklepicker/
├── backend/          # FastAPI (Python 3.12)
├── frontend/         # Next.js 14 (TypeScript)
├── pipeline/         # Scraping pipeline (Python 3.12)
├── docker-compose.yml # Local PostgreSQL
├── Makefile          # Dev commands
└── .github/workflows/ # CI/CD
```

---

*Stack analysis: 2026-04-20*