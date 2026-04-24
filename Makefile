.PHONY: help setup build rebuild db-up db-down db-logs db-shell db-clean test test-backend test-frontend test-e2e test-backend-cov dev dev-backend dev-frontend stop clean env-check ps logs logs-backend logs-frontend scrape-joola scrape-brazil scrape-dropshot scrape-all shell-backend shell-db

# Cores para output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

# Variáveis de ambiente padrão
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 3000
DB_HOST ?= localhost
DB_PORT ?= 5432

help: ## Mostra esta ajuda
	@echo "$(BLUE)PickleIQ - Comandos de Desenvolvimento (Docker)$(NC)"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ============================================
# SETUP / BUILD
# ============================================

setup: build ## Build all Docker images (primeiro uso)
	@echo "$(GREEN)✅ Setup completo! Use 'make dev' para iniciar$(NC)"

build: ## Build all Docker images
	@echo "$(BLUE)🔨 Building Docker images...$(NC)"
	docker compose build

rebuild: ## Rebuild all Docker images (no cache)
	@echo "$(BLUE)🔨 Rebuilding Docker images (no cache)...$(NC)"
	docker compose build --no-cache

# ============================================
# DATABASE
# ============================================

db-up: ## Inicia o banco de dados PostgreSQL via Docker com health check
	@echo "$(BLUE)🐳 Iniciando PostgreSQL...$(NC)"
	docker compose up -d postgres
	@$(MAKE) _db-wait

_db-wait: ## Espera PostgreSQL ficar pronto (max 30s)
	@echo "$(YELLOW)⏳ Aguardando PostgreSQL ficar pronto...$(NC)"
	@i=1; while [ $$i -le 30 ]; do \
		if docker compose exec -T postgres pg_isready -U pickleiq >/dev/null 2>&1; then \
			echo "$(GREEN)✅ PostgreSQL pronto!$(NC)"; exit 0; \
		fi; \
		echo "   Attempt $$i/30..."; sleep 1; \
		i=$$((i + 1)); \
	done; \
	echo "$(RED)❌ Timeout waiting for PostgreSQL$(NC)"; exit 1

db-down: ## Para o banco de dados
	@echo "$(BLUE)🛑 Parando PostgreSQL...$(NC)"
	docker compose stop postgres

db-logs: ## Mostra logs do PostgreSQL
	docker compose logs -f postgres

db-shell: ## Abre shell psql no banco de dados
	docker compose exec postgres psql -U pickleiq -d pickleiq

db-clean: ## Para e remove volumes do DB (limpa todos os dados!)
	@echo "$(RED)⚠️  Isso vai remover TODOS os dados do banco!$(NC)"
	@read -p "Tem certeza? [y/N] " confirm && [ $$confirm = y ] && docker compose down -v || echo "Cancelado."

# ============================================
# TESTING
# ============================================

test: test-backend test-frontend ## Roda todos os testes unitários

test-backend: ## Roda testes do backend com pytest (via Docker)
	@echo "$(BLUE)🧪 Rodando testes do backend...$(NC)"
	docker compose exec backend python -m pytest -v

test-backend-cov: ## Roda testes do backend com cobertura
	@echo "$(BLUE)🧪 Rodando testes do backend com cobertura...$(NC)"
	docker compose exec backend python -m pytest --cov=app --cov-report=html --cov-report=term -v
	@echo "$(GREEN)✅ Relatório de cobertura em: backend/htmlcov/index.html$(NC)"

test-frontend: ## Roda testes do frontend (via Docker)
	@echo "$(BLUE)🧪 Rodando testes do frontend...$(NC)"
	docker compose exec frontend npm run test

test-e2e: db-up ## Roda testes E2E (requer DB rodando, via pipeline container)
	@echo "$(BLUE)🎭 Rodando testes E2E via pipeline container...$(NC)"
	docker compose run --rm pipeline python test_scraper_integration.py
	@echo "$(GREEN)✅ Testes E2E concluídos!$(NC)"

# ============================================
# DEVELOPMENT
# ============================================

dev: ## Inicia ambiente de desenvolvimento completo (postgres + backend + frontend)
	@echo "$(GREEN)🚀 Iniciando ambiente de desenvolvimento via Docker...$(NC)"
	@echo "$(YELLOW)   Backend:  http://localhost:8000$(NC)"
	@echo "$(YELLOW)   Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)   API Docs: http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)   Use 'make stop' para parar tudo$(NC)"
	docker compose up postgres backend frontend

dev-backend: ## Inicia apenas o servidor backend + postgres
	@echo "$(BLUE)🚀 Iniciando backend em http://localhost:8000$(NC)"
	docker compose up postgres backend

dev-frontend: ## Inicia apenas o servidor frontend
	@echo "$(BLUE)🚀 Iniciando frontend em http://localhost:3000$(NC)"
	docker compose up frontend

stop: ## Para todos os serviços Docker
	@echo "$(GREEN)🛑 Parando todos os serviços...$(NC)"
	docker compose down
	@echo "$(GREEN)✅ Todos os serviços parados$(NC)"

# ============================================
# SCRAPERS (pipeline - on-demand)
# ============================================

scrape-joola: ## Roda scraper JOOLA via pipeline container
	@echo "$(BLUE)🕷️ Rodando scraper JOOLA...$(NC)"
	docker compose run --rm pipeline python -m crawlers.joola

scrape-brazil: ## Roda scraper Brazil Store via pipeline container
	@echo "$(BLUE)🕷️ Rodando scraper Brazil Store...$(NC)"
	docker compose run --rm pipeline python -m crawlers.brazil_store

scrape-dropshot: ## Roda scraper Dropshot Brasil via pipeline container
	@echo "$(BLUE)🕷️ Rodando scraper Dropshot Brasil...$(NC)"
	docker compose run --rm pipeline python -m crawlers.dropshot_brasil

scrape-all: ## Roda todos os scrapers em sequência
	@echo "$(BLUE)🕷️ Rodando todos os scrapers...$(NC)"
	@$(MAKE) scrape-joola
	@$(MAKE) scrape-brazil
	@$(MAKE) scrape-dropshot
	@echo "$(GREEN)✅ Todos os scrapers concluídos!$(NC)"

# ============================================
# LOGS / STATUS
# ============================================

ps: ## Lista status dos containers Docker
	docker compose ps

logs: ## Mostra logs de todos os serviços (follow)
	docker compose logs -f

logs-backend: ## Mostra logs do backend
	docker compose logs -f backend

logs-frontend: ## Mostra logs do frontend
	docker compose logs -f frontend

# ============================================
# SHELLS
# ============================================

shell-backend: ## Abre shell bash no container do backend
	docker compose exec backend bash

shell-db: ## Abre psql shell no banco de dados
	docker compose exec postgres psql -U pickleiq -d pickleiq

# ============================================
# CLEANUP
# ============================================

clean: ## Limpa tudo (containers, volumes, imagens locais, caches)
	@echo "$(RED)🧹 Limpando ambiente Docker...$(NC)"
	docker compose down -v --rmi local 2>/dev/null || true
	rm -rf backend/.pytest_cache backend/htmlcov
	rm -rf pipeline/.pytest_cache
	@echo "$(GREEN)✅ Ambiente limpo! Use 'make setup' para reconstruir$(NC)"

# ============================================
# ENVIRONMENT CHECK
# ============================================

env-check: ## Verifica dependências obrigatórias (Docker)
	@echo "$(BLUE)⚙️ Verificando ambiente...$(NC)"
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "$(RED)❌ Docker não encontrado. Instale: https://docs.docker.com/get-docker/$(NC)"; \
		exit 1; \
	fi
	@if ! docker compose version >/dev/null 2>&1; then \
		echo "$(RED)❌ Docker Compose v2 não encontrado. Instale: https://docs.docker.com/compose/install/$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)⚠️ .env não encontrado. Crie a partir de .env.example$(NC)"; \
	fi
	@echo "$(GREEN)✅ Checks ambiente OK$(NC)"

# ============================================
# HELPERS
# ============================================

help-full: ## Mostra ajuda completa incluindo comandos avançados
	@echo "$(BLUE)PickleIQ - Comandos de Desenvolvimento (Docker)$(NC)"
	@echo "========================================"
	@$(MAKE) help
	@echo ""
	@echo "$(GREEN)Setup$(NC)"
	@echo "  make setup              Build all Docker images"
	@echo "  make build              Build sem cache dos Dockerfiles"
	@echo "  make rebuild            Rebuild completo (no cache)"
	@echo ""
	@echo "$(GREEN)Database$(NC)"
	@echo "  make db-up              Inicia PostgreSQL com health check"
	@echo "  make db-down            Para PostgreSQL"
	@echo "  make db-logs            Mostra logs do PostgreSQL"
	@echo "  make db-shell           Abre psql shell (via Docker)"
	@echo "  make db-clean           Remove todos os dados (destructive!)"
	@echo ""
	@echo "$(GREEN)Scrapers$(NC)"
	@echo "  make scrape-joola       Roda scraper JOOLA"
	@echo "  make scrape-brazil      Roda scraper Brazil Store"
	@echo "  make scrape-dropshot    Roda scraper Dropshot Brasil"
	@echo "  make scrape-all         Roda todos os scrapers em sequência"
	@echo ""
	@echo "$(GREEN)Logs / Status$(NC)"
	@echo "  make ps                 Lista status dos containers"
	@echo "  make logs               Logs de todos os serviços"
	@echo "  make logs-backend       Logs do backend"
	@echo "  make logs-frontend      Logs do frontend"
	@echo ""
	@echo "$(GREEN)Shells$(NC)"
	@echo "  make shell-backend      Bash no container do backend"
	@echo "  make shell-db           psql no banco via Docker"
	@echo ""
	@echo "$(GREEN)Cleanup$(NC)"
	@echo "  make clean              Remove tudo (containers, volumes, imagens)"
	@echo "  make stop               Para todos os serviços"
