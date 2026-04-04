.PHONY: help setup setup-backend setup-frontend db-up db-down db-logs db-shell test test-backend test-frontend test-e2e dev dev-backend dev-frontend stop clean env-check

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
	@echo "$(BLUE)PickleIQ - Comandos de Desenvolvimento$(NC)"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: setup-backend setup-frontend ## Instala todas as dependências (backend + frontend)
	@echo "$(GREEN)✅ Setup completo!$(NC)"

setup-backend: ## Instala dependências do backend (Python)
	@echo "$(BLUE)📦 Instalando dependências do backend...$(NC)"
	pip install -e ./backend[dev]

setup-frontend: ## Instala dependências do frontend (Node.js)
	@echo "$(BLUE)📦 Instalando dependências do frontend...$(NC)"
	npm install

cd-frontend:
	cd frontend && npm install

# ============================================
# DATABASE
# ============================================

db-up: env-check ## Inicia o banco de dados PostgreSQL via Docker com health check
	@echo "$(BLUE)🐳 Iniciando PostgreSQL...$(NC)"
	@$(MAKE) _db-start
	@$(MAKE) _db-wait

_db-start:
	@[ -f backend/.env ] && \
		set -a && \
		. backend/.env && \
		set +a || true
	docker compose up -d postgres

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
	docker compose down

db-logs: ## Mostra logs do PostgreSQL
	docker compose logs -f postgres

db-shell: ## Abre shell psql no banco de dados
	psql -h localhost -U pickleiq -d pickleiq

db-clean: ## Para e remove volumes do DB (limpa todos os dados!)
	@echo "$(RED)⚠️  Isso vai remover TODOS os dados do banco!$(NC)"
	@read -p "Tem certeza? [y/N] " confirm && [ $$confirm = y ] && docker compose down -v || echo "Cancelado."

# ============================================
# TESTING
# ============================================

test: test-backend test-frontend ## Roda todos os testes unitários

test-backend: ## Roda testes do backend com pytest
	@echo "$(BLUE)🧪 Rodando testes do backend...$(NC)"
	cd backend && . venv/bin/activate && PYTHONPATH=$(PWD) python3 -m pytest -v

test-backend-cov: ## Roda testes do backend com cobertura
	@echo "$(BLUE)🧪 Rodando testes do backend com cobertura...$(NC)"
	cd backend && pytest --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Relatório de cobertura em: backend/htmlcov/index.html$(NC)"

test-frontend: ## Roda testes do frontend
	@echo "$(BLUE)🧪 Rodando testes do frontend...$(NC)"
	cd frontend && npm run test

test-e2e: db-up ## Roda testes E2E (requer DB rodando)
	@echo "$(BLUE)🎭 Preparando ambiente para testes E2E...$(NC)"
	@echo "$(BLUE)🐍 Setup Python para pipeline...$(NC)"
	cd pipeline && \
		. .venv/bin/activate && \
		echo "$(BLUE)🚀 Rodando testes E2E...$(NC)" && \
		python test_e2e_scraper.py
	@echo "$(GREEN)✅ Testes E2E concluídos!$(NC)"

# ============================================
# DEVELOPMENT
# ============================================

dev: ## Inicia ambiente de desenvolvimento completo (DB + servidores) com dependência ordenada
	@echo "$(GREEN)🚀 Iniciando ambiente de desenvolvimento...$(NC)"
	$(MAKE) db-up
	@echo "$(YELLOW)💡 Verificando serviços...$(NC)"
	$(MAKE) _backend-health
	@echo "$(YELLOW)💡 Iniciando servidores em paralelo...$(NC)"
	@echo "$(YELLOW)   Backend:  http://localhost:8000$(NC)"
	@echo "$(YELLOW)   Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)   API Docs: http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)   Use 'make stop' para parar tudo$(NC)"
	@bash -c 'trap "$(MAKE) stop" EXIT; \
		(cd backend && set -a && source .env && set +a && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) & \
		(cd frontend && PORT=3000 npm run dev) & \
		wait'

_backend-health: ## Verifica se o backend está respondendo (max 10s)
	@echo "🔍 Checking backend health..."
	@i=1; while [ $$i -le 10 ]; do \
		if curl -sf http://localhost:$(BACKEND_PORT)/health >/dev/null 2>&1; then \
			echo "✅ Backend healthy on port $(BACKEND_PORT)"; exit 0; \
		fi; \
		echo "   Attempt $$i/10..."; sleep 1; \
		i=$$((i + 1)); \
	done; \
	echo "$(YELLOW)⚠️ Backend not responding yet (will retry automatically)$(NC)"

dev-backend: db-up ## Inicia apenas o servidor backend (requer DB)
	@echo "$(BLUE)🚀 Iniciando backend em http://localhost:8000$(NC)"
	@cd backend && set -a && source .env && set +a && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Inicia apenas o servidor frontend
	@echo "$(BLUE)🚀 Iniciando frontend em http://localhost:3000$(NC)"
	cd frontend && npm run dev

stop: ## Para todos os serviços (DB e servidores)
	@echo "$(GREEN)🛑 Parando PostgreSQL...$(NC)"
	@docker compose down
	@echo "$(GREEN)🛑 Parando servidores locais...$(NC)"
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "next dev" 2>/dev/null || true
	@pkill -f "next start" 2>/dev/null || true
	@echo "$(GREEN)✅ Todos os serviços parados$(NC)"

# ============================================
# CLEANUP
# ============================================

clean: db-clean ## Limpa tudo (venv, node_modules, dados)
	@echo "$(RED)🧹 Limpando ambiente...$(NC)"
	@echo "  Removendo venvs e caches..."
	rm -rf frontend/node_modules
	rm -rf backend/venv
	rm -rf pipeline/.venv
	rm -rf backend/.pytest_cache
	rm -rf backend/htmlcov
	@echo "   Parando containers Docker..."
	@docker compose down --volumes 2>/dev/null || true
	@echo "$(GREEN)✅ Ambiente limpo!$(NC)"

# ============================================
# ENVIRONMENT CHECK
# ============================================

env-check: ## Verifica dependências obrigatórias antes de iniciar
	@echo "$(BLUE)⚙️ Verificando ambiente...$(NC)"
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "$(RED)❌ Docker não encontrado. Instale: https://docs.docker.com/get-docker/$(NC)"; \
		exit 1; \
	fi
	@if ! command -v docker compose >/dev/null 2>&1; then \
		echo "$(RED)❌ Docker Compose não encontrado. Instale: https://docs.docker.com/compose/install/$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$$DATABASE_URL" ] && [ ! -f "backend/.env" ] && [ ! -f "backend/.env.local" ]; then \
		echo "$(YELLOW)⚠️ DATABASE_URL não definida. Crie backend/.env com DATABASE_URL=$(NC)"; \
		echo "   DATABASE_URL=postgresql://pickleiq:changeme@localhost:5432/pickleiq"; \
	fi
	@if [ -z "$$GROQ_API_KEY" ] && [ ! -f "backend/.env" ]; then \
		echo "$(YELLOW)⚠️ GROQ_API_KEY não definida. Chat/RAG não funcionará corretamente.$(NC)"; \
	fi
	@if ! command -v psql >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠️ psql não encontrado. Usando docker compose para DB.$(NC)"; \
	fi
	@if ! command -v curl >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠️ curl não encontrado. Health checks não funcionarão.$(NC)"; \
	fi
	@echo "$(GREEN)✅ Checks ambiente OK$(NC)"

# ============================================
# HELPERS
# ============================================

help-full: ## Mostra ajuda completa incluindo comandos avançados
	@echo "$(BLUE)PickleIQ - Comandos de Desenvolvimento$(NC)"
	@echo "========================================"
	@$(MAKE) help
	@echo ""
	@echo "$(GREEN)Database$(NC)"
	@echo "  make db-up              Inicia PostgreSQL com health check"
	@echo "  make db-down            Para PostgreSQL"
	@echo "  make db-logs            Mostra logs do PostgreSQL"
	@echo "  make db-shell           Abre psql shell"
	@echo "  make db-clean           Remove todos os dados (destructive!)"
	@echo ""
	@echo "$(GREEN)Cleanup$(NC)"
	@echo "  make clean              Remove tudo (venvs, node_modules, DB)"
	@echo "  make stop               Para todos os serviços"
