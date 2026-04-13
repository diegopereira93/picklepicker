# Getting Started — PickleIQ

Quick-start guide to run PickleIQ locally in under 10 minutes.

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Docker | 20+ | `docker --version` |
| Docker Compose | v2+ | `docker compose version` |
| Python | 3.12+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| pip | latest | `pip --version` |

## 1. Clone and Install

```bash
git clone <repo-url>
cd picklepicker

# Install all dependencies (backend + frontend)
make setup
```

This runs `pip install -e .` in both `backend/` and `pipeline/`, plus `npm install` in `frontend/`.

## 2. Configure Environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your credentials:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `GROQ_API_KEY` | Yes | Groq LLM API key (chat) |
| `JINA_API_KEY` | Yes | Jina AI embeddings |
| `FIRECRAWL_API_KEY` | No | Firecrawl web scraping |
| `CLERK_SECRET_KEY` | No | Clerk auth (production) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | No | Clerk frontend key |

### Local Database URL

For local development with Docker:

```
DATABASE_URL=postgresql://pickleiq:changeme@localhost:5432/pickleiq
```

## 3. Start Services

```bash
# Start everything (DB + backend + frontend)
make dev
```

This starts three services in order:
1. **PostgreSQL** (Docker, port 5432) — waits for health check
2. **FastAPI backend** (port 8000) — uvicorn with hot reload
3. **Next.js frontend** (port 3000) — dev server with hot reload

### Start Individual Services

```bash
make db-up          # PostgreSQL only
make dev-backend    # Backend only (requires running DB)
make dev-frontend   # Frontend only
```

## 4. Verify Everything Works

| Check | URL | Expected |
|-------|-----|----------|
| Frontend | http://localhost:3000 | Landing page loads |
| API docs | http://localhost:8000/docs | Swagger UI |
| Health check | http://localhost:8000/health | `{"status": "healthy"}` |
| Database | `make db-shell` | psql prompt opens |

## 5. Explore the App

1. **Take the quiz** — http://localhost:3000/quiz — 7 questions about your playing style
2. **Chat with AI** — http://localhost:3000/chat — ask about paddles in Portuguese
3. **Browse catalog** — http://localhost:3000/catalog — sortable table of paddles
4. **Compare paddles** — http://localhost:3000/compare — side-by-side comparison

## Troubleshooting

### "DATABASE_URL not set"

Ensure `backend/.env` exists and contains a valid `DATABASE_URL`.

### PostgreSQL won't start

```bash
make db-down    # Stop existing container
make db-up      # Start fresh
```

If port 5432 is in use:

```bash
lsof -i :5432   # Find what's using the port
make db-down    # Stop our container
```

### "pip install fails"

The project uses Python 3.12 features. Verify your version:

```bash
python3 --version   # Must be 3.12+
```

### Frontend build errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Backend import errors

```bash
cd backend
pip install -e .
```

### Docker not running

```bash
docker info    # Check if Docker daemon is running
sudo systemctl start docker   # Linux
```

## Next Steps

- Read [docs/ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system design
- Read [docs/DEVELOPMENT.md](./DEVELOPMENT.md) for contribution workflows
- Run `make test` to verify the test suite passes
- Read [DESIGN.md](../DESIGN.md) before modifying any UI components
