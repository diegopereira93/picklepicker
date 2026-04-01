.PHONY: help setup setup-backend setup-frontend db-up db-down db-logs db-shell test test-backend test-frontend test-e2e dev dev-backend dev-frontend stop clean

# Cores para output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

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

db-up: ## Inicia o banco de dados PostgreSQL via Docker
	@echo "$(BLUE)🐳 Iniciando PostgreSQL...$(NC)"
	docker compose up -d postgres
	@echo "$(YELLOW)⏳ Aguardando DB ficar pronto...$(NC)"
	@sleep 2
	@i=1; while [ $$i -le 10 ]; do \
		if docker compose exec -T postgres pg_isready -U pickleiq >/dev/null 2>&1; then \
			echo "$(GREEN)✅ PostgreSQL pronto!$(NC)"; \
			exit 0; \
		fi; \
		echo "$(YELLOW)   Aguardando... ($$i/10)$(NC)"; \
		sleep 2; \
		i=$$((i + 1)); \
	done; \
	echo "$(RED)❌ Timeout aguardando PostgreSQL$(NC)"; \
	exit 1

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

test: test-backend test-frontend ## Roda todos os testes unitários

test-backend: ## Roda testes do backend com pytest
	@echo "$(BLUE)🧪 Rodando testes do backend...$(NC)"
	cd backend && pytest -v

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
		python3 -m venv .venv 2>/dev/null || true && \
		source .venv/bin/activate && \
		pip install -q -r requirements.txt && \
		echo "$(BLUE)🚀 Rodando testes E2E...$(NC)" && \
		python test_e2e_scraper.py
	@echo "$(GREEN)✅ Testes E2E concluídos!$(NC)"

dev: ## Inicia ambiente de desenvolvimento completo (DB + servidores)
	@echo "$(GREEN)🚀 Iniciando ambiente de desenvolvimento...$(NC)"
	$(MAKE) db-up
	@echo "$(YELLOW)💡 Iniciando servidores em paralelo...$(NC)"
	@echo "$(YELLOW)   Use 'make stop' para parar tudo$(NC)"
	@bash -c 'trap "$(MAKE) stop" EXIT; \
		(cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000) & \
		(cd frontend && npm run dev) & \
		wait'

dev-backend: db-up ## Inicia apenas o servidor backend (requer DB)
	@echo "$(BLUE)🚀 Iniciando backend em http://localhost:8000$(NC)"
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Inicia apenas o servidor frontend
	@echo "$(BLUE)🚀 Iniciando frontend em http://localhost:3000$(NC)"
	cd frontend && npm run dev

stop: db-down ## Para todos os serviços (DB e servidores)
	@echo "$(GREEN)🛑 Todos os serviços parados$(NC)"

clean: db-clean ## Limpa tudo (venv, node_modules, dados)
	@echo "$(RED)🧹 Limpando ambiente...$(NC)"
	rm -rf frontend/node_modules
	rm -rf backend/venv
	rm -rf pipeline/.venv
	rm -rf backend/.pytest_cache
	rm -rf backend/htmlcov
	@echo "$(GREEN)✅ Ambiente limpo!$(NC)"
