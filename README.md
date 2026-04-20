# PickleIQ

[![Version](https://img.shields.io/badge/version-2.3.0-brightgreen.svg)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal.svg)](https://fastapi.tiangolo.com/)

> Plataforma de inteligência para raquetes de Pickleball no mercado brasileiro.

PickleIQ é uma plataforma que compara preços e especificações de raquetes de pickleball em varejistas brasileiros, oferece recomendações personalizadas através de um agente de IA com RAG, e monetiza por meio de links de afiliados.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Recursos](#recursos)
- [Tecnologias](#tecnologias)
- [Como Começar](#como-começar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Comandos de Desenvolvimento](#comandos-de-desenvolvimento)
- [API](#api)
- [Deploy](#deploy)
- [Testing](#testing)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## Sobre o Projeto

O PickleIQ nasceu para resolver um problema real no mercado brasileiro de pickleball, a falta de informações centralizadas sobre raquetes, preços variados entre varejistas, e dificuldade em escolher a raquete ideal para cada perfil de jogador.

Nossa plataforma oferece:

- **Comparação de Preços**: Monitoramento em tempo real de raquetes em 3 varejistas brasileiros (Brazil Store, Dropshot Brasil, Mercado Livre)
- **Recomendações Personalizadas**: Quiz de 7 perguntas para entender seu perfil e sugerir raquetes adequadas
- **Chat com IA**: Agente RAG que responde perguntas sobre raquetes usando busca semântica no catálogo
- **Alertas de Preço**: Receba notificações quando raquetes de interesse tiverem queda de preço
- **Sistema de Afiliados**: Rastreamento de cliques para monetização

## Recursos

### Para Usuários

- **Quiz de Recomendação**: 7 perguntas sobre estilo de jogo, nível, orçamento e preferências
- **Chat Inteligente**: Faça perguntas em português e receba respostas baseadas no catálogo
- **Catálogo Completo**: Mais de 150 raquetes com especificações detalhadas
- **Comparação de Preços**: Veja o melhor preço entre múltiplos varejistas
- **Alertas de Preço**: Cadastre-se para receber avisos de queda de preço
- **Raquetes Similares**: Encontre alternativas semelhantes à sua escolha

### Para Desenvolvedores

- **API RESTful**: Endpoints para raquetes, chat, alertas de preço, tracking de afiliados
- **Streaming SSE**: Chat com respostas em tempo real via Server-Sent Events
- **RAG com pgvector**: Busca semântica usando embeddings Jina AI (768 dimensões)
- **Scraping Robusto**: Crawlers com retry (tenacity) para 3 varejistas
- **Testes Abrangentes**: 174 testes backend + 182 testes frontend
- **CI/CD Automatizado**: Deploy automático via GitHub Actions

## Tecnologias

### Backend
- **Python 3.12** com FastAPI (API assíncrona)
- **PostgreSQL + pgvector** (banco de dados vetorial)
- **Groq** (LLM: Mixtral 8x7B para chat)
- **Jina AI** (embeddings: v2-base, 768d)
- **psycopg_pool** (connection pool assíncrono)

### Frontend
- **Next.js 14** (App Router + Server Components)
- **TypeScript** (tipagem estática)
- **TailwindCSS** (estilização)
- **Clerk** (autenticação)
- **Vitest** (testes unitários)

### Pipeline & Infra
- **Python 3.12** com Firecrawl (scraping)
- **Docker Compose** (Postgres local)
- **GitHub Actions** (CI/CD)
- **Railway** (backend production)
- **Vercel** (frontend production)
- **Supabase** (DB production com pgvector)

## Como Começar

### Pré-requisitos

- Docker (para PostgreSQL local)
- Python 3.12+
- Node.js 18+
- Make

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/picklepicker.git
cd picklepicker

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API (Groq, Jina AI, Clerk, etc.)

# Instale todas as dependências
make setup
```

### Executando Localmente

```bash
# Inicie o banco de dados, backend e frontend (hot-reload)
make dev
```

Isso vai:
1. Subir PostgreSQL com pgvector via Docker
2. Iniciar backend em http://localhost:8000
3. Iniciar frontend em http://localhost:3000

Acesse a aplicação em http://localhost:3000.

## Estrutura do Projeto

```
picklepicker/
├── backend/                 # FastAPI + RAG agent
│   ├── app/
│   │   ├── main.py         # FastAPI entrypoint
│   │   ├── api/            # REST endpoints
│   │   ├── agents/         # RAG agent + eval gate
│   │   ├── middleware/     # Telegram alerting
│   │   ├── routers/        # Affiliate tracking, webhooks
│   │   ├── db.py           # Async connection pool
│   │   ├── schemas.py      # Pydantic models
│   │   ├── prompts.py      # Prompt templates (PT-BR)
│   │   └── cache.py        # Caching layer
│   ├── workers/            # Background workers
│   ├── tests/              # pytest-asyncio tests
│   └── pyproject.toml
├── frontend/               # Next.js 14 App Router
│   ├── src/
│   │   ├── app/            # Pages (/, /paddles, /chat, etc.)
│   │   ├── components/     # UI components
│   │   ├── lib/            # API client, auth, tracking
│   │   ├── types/          # TypeScript types
│   │   ├── hooks/          # Custom hooks
│   │   └── tests/          # Vitest tests
│   └── package.json
├── pipeline/               # Scraping + data pipeline
│   ├── crawlers/           # Brazil Store, Dropshot, ML
│   ├── db/                # Schema, connection pool
│   ├── dedup/             # Spec matching, normalization
│   ├── embeddings/         # Jina AI embeddings
│   ├── alerts/            # Price alert notifications
│   └── tests/              # Pipeline tests
├── .github/workflows/      # CI/CD workflows
├── docker-compose.yml      # Local Postgres
├── Makefile               # Dev orchestration
├── DESIGN.md              # Design system v2.0
├── CLAUDE.md              # AI assistant config
└── README.md              # This file
```

## Comandos de Desenvolvimento

### Setup
```bash
make setup              # Install all deps (backend + frontend)
make setup-backend      # Install backend deps only
make setup-frontend     # Install frontend deps only
make env-check          # Validate environment
```

### Development
```bash
make dev               # Start DB + backend + frontend (parallel)
make dev-backend       # Backend only (:8000)
make dev-frontend      # Frontend only (:3000)
make stop              # Stop all services
```

### Testing
```bash
make test              # All tests (backend + frontend)
make test-backend      # pytest (backend)
make test-frontend     # vitest (frontend)
make test-e2e          # E2E scraper tests
make test-backend-cov  # Coverage report (backend)
```

### Database
```bash
make db-up             # Start PostgreSQL
make db-down           # Stop PostgreSQL
make db-logs           # Tail PostgreSQL logs
make db-shell          # Open psql shell
make db-clean          # Remove all data (destructive!)
```

### Help
```bash
make help              # List all commands
make help-full         # Grouped command reference
```

## API

### Endpoints Principais

#### Paddles
- `GET /api/v1/paddles` — Lista todas as raquetes (com filtros: brand, price_range, skill_level)
- `GET /api/v1/paddles/{id}` — Detalhes de uma raquete específica
- `GET /api/v1/paddles/{id}/similar` — Raquetes similares (embeddings + pgvector)

#### Chat (RAG)
- `POST /api/v1/chat` — Chat com IA (SSE streaming)
  - Body: `{"message": "qual raquete para jogador iniciante?", "history": [...]}`

#### Price Alerts
- `POST /api/v1/price-alerts` — Criar alerta de preço
- `GET /api/v1/price-alerts/{user_id}` — Listar alertas do usuário

#### Affiliate Tracking
- `GET /api/v1/affiliate/{paddle_id}` — Redirecionamento com tracking
- `POST /api/v1/affiliate/click` — Registrar clique

#### Admin
- `GET /api/v1/admin/health` — Health check
- `GET /api/v1/admin/price-history/{paddle_id}` — Histórico de preços

### Documentação Completa

Acesse http://localhost:8000/docs (Swagger UI) para documentação interativa completa.

## Deploy

### Production

- **Backend**: Railway (automatic deployment via GitHub Actions)
- **Frontend**: Vercel (automatic deployment via GitHub Actions)
- **Database**: Supabase (PostgreSQL + pgvector)

### Environment Variables (Production)

```env
# Backend
DATABASE_URL=postgresql://user:pass@host:port/db
GROQ_API_KEY=gsk_...
JINA_API_KEY=jina_...
ADMIN_SECRET=seu-secret-admin
TELEGRAM_BOT_TOKEN=seu-token
TELEGRAM_CHAT_ID=seu-chat-id

# Frontend
NEXT_PUBLIC_API_URL=https://pickleiq-backend.railway.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

### CI/CD Workflows

- `.github/workflows/deploy.yml` — Deploy automático em push para main
- `.github/workflows/test.yml` — Run tests em todos os PRs
- `.github/workflows/scrape.yml` — Scraping diário (cron)
- `.github/workflows/lighthouse.yml` — Lighthouse CI para performance

## Testing

### Backend Tests

```bash
cd backend
pytest --cov=app --cov-report=html
```

- Framework: pytest-asyncio
- Coverage target: 80%+
- 174 passing tests (current)

### Frontend Tests

```bash
cd frontend
npm test
```

- Framework: Vitest + jsdom
- 182 passing tests (current)

### E2E Tests

```bash
make test-e2e
```

- Framework: Playwright
- Testa fluxo completo: quiz → catálogo → chat

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Convenções de Código

- **Backend**: PEP 8, type hints, docstrings (PT-BR)
- **Frontend**: ESLint, Prettier, TypeScript strict mode
- **Commit messages**: Conventional Commits (`feat:`, `fix:`, `docs:`)
- **Tests**: Escreva testes para novas features

### Design System

Leia `DESIGN.md` antes de modificar qualquer componente UI. Seguimos o sistema de design v2.0 com estética Modern Sports Tech.

## Roadmap

- [ ] Fase 21: Price Alerts CRUD (table + POST endpoint)
- [ ] Fase 22: Affiliate Click Tracking (DB persistence)
- [ ] Fase 23: Quiz Profile Persistence (cross-device sync)
- [ ] Integração com mais varejistas brasileiros
- [ ] App mobile (React Native)

## Licença

Este projeto está licenciado sob a Licença MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

- **Issues**: https://github.com/seu-usuario/picklepicker/issues
- **Discussions**: https://github.com/seu-usuario/picklepicker/discussions
- **Email**: contato@pickleiq.com.br

---

Feito com 🥒 para a comunidade brasileira de pickleball.
