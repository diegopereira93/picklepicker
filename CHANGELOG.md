# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0.0] - 2026-03-27

### Added
- Initial project setup with PickleIQ pipeline infrastructure
- Python project structure with pytest configuration
- Docker Compose setup for local development
- Environment configuration templates

### Changed
- Updated .gitignore to exclude .venv and .env files from version control


## [0.2.0.0] - 2026-03-27

### Added
- Full data pipeline crawlers: Drop Shot Brasil and Mercado Livre expansion via Firecrawl
- 3-tier SKU deduplication with RapidFuzz (title hash + fuzzy matching ≥0.85)
- Review queue system with admin API endpoints for manual dedup review
- GitHub Actions 24h schedule for crawler orchestration with exponential backoff and Telegram alerts
- Railway staging deployment with FastAPI + PostgreSQL
- pgvector embeddings (text-embedding-3-small, HNSW index) with async re-embedding pipeline
- 5 FastAPI GET endpoints: /paddles, /paddles/{id}, /paddles/{id}/prices, /paddles/{id}/latest-prices, /health
- Admin API endpoints: GET /admin/queue, PATCH /admin/resolve, PATCH /admin/dismiss
- .env.example configuration for Phase 2 environment variables
- Dockerfile.railway for containerized FastAPI deployment on Railway
- railway.toml configuration for Railway deployment

### Changed
- Updated .gitignore to exclude Railway and plan artifacts
- Extended backend schema with async re-embedding flag (needs_reembed)
- FastAPI main.py with admin and paddles routers

### Test Coverage
- 43 tests for crawlers and deduplication (Wave 1)
- 13 tests for embeddings and FastAPI endpoints (Wave 2)
- Total: 56+ tests passing with 100% coverage of new code paths
