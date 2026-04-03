# Checkpoint - MVP Launch Plan

**Data:** 2026-04-03  
**Branch:** gsd/phase-13-nvidia-ui-redesign  
**Commit:** c3af7f6 "MVP Launch Fixes: RAG pgvector, Claude LLM, Tests, Scraper"

---

## ✅ O QUE FOI IMPLEMENTADO

### P0 - Crítico (Código Escrito, Não Testado)

#### 1. RAG Agent (`backend/app/agents/rag_agent.py`)
- ✅ Integração real com pgvector via `get_similar_paddle_ids()`
- ✅ Geração de embeddings via OpenAI (`generate_query_embedding()`)
- ✅ Queries SQL reais em `paddle_embeddings` e `latest_prices`
- ✅ Fallback para mock quando OPENAI_API_KEY não disponível
- ❌ **NÃO TESTADO** - Requer API key + banco populado

#### 2. Chat API (`backend/app/api/chat.py`)
- ✅ Integração real com Claude 3.5 Sonnet via Anthropic SDK
- ✅ Streaming SSE com respostas reais (não hardcoded)
- ✅ Timeout de 8s com fallback para degraded mode
- ✅ Token counting real da API
- ❌ **NÃO TESTADO** - Requer ANTHROPIC_API_KEY

#### 3. Dependências (`backend/pyproject.toml`)
- ✅ Adicionados: openai>=1.0.0, anthropic>=0.25.0, httpx>=0.27.0

#### 4. Backend Tests
- ✅ Corrigido sys.path em `backend/tests/conftest.py`
- ✅ Corrigido PYTHONPATH no `Makefile`
- ⚠️ **PARCIALMENTE TESTADO** - 141/144 tests passando (3 falhas pré-existentes)

### P1 - Alto (Concluído)
- ✅ Frontend tests: 152/152 passando
- ✅ Dropshot retailer_id: Adicionado ao schema.sql
- ✅ scraper.yml: Corrigidos nomes dos módulos

---

## ❌ O QUE NÃO FOI TESTADO/VALIDADO

### Blockers Críticos para Lançamento:

1. **RAG Agent - Integração Real NÃO Validada**
   - Código escrito mas não executado contra banco real
   - Necessita: `OPENAI_API_KEY` + `DATABASE_URL` + banco com embeddings
   - Pendente: Verificar se retorna paddles reais (não mocks)

2. **Chat LLM - Integração Real NÃO Validada**
   - Código escrito mas não testado com API real
   - Necessita: `ANTHROPIC_API_KEY`
   - Pendente: Verificar se respostas variam (não templates)

3. **Embeddings NÃO Gerados**
   - Tabela `paddle_embeddings` precisa ser populada
   - Pipeline: `python -m pipeline.embeddings.batch_embedder`
   - Necessita: `OPENAI_API_KEY` + dados em `paddles`

### Testes Manuais Pendentes:

```bash
# 1. Iniciar backend
make dev-backend

# 2. Testar RAG + Chat
export ANTHROPIC_API_KEY="sk-ant-..."
curl -N http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Qual raquete para iniciante?","skill_level":"beginner","budget_brl":500}'

# Esperado: Resposta em português gerada por Claude (não template)
# Esperado: Lista de paddles do banco (não mocks hardcoded)

# 3. Verificar logs
# Deve mostrar: "Found X similar paddles" (pgvector query)
# Deve mostrar: "Generating embedding for query..."

# 4. Rodar todos os testes
make test-backend   # Deve passar 100%
make test-frontend  # Deve passar 152/152
```

---

## 📋 PRÓXIMOS PASSOS (Próxima Sessão ULW)

### Fase 1: Configuração de Ambiente
- [ ] Obter API keys (OpenAI + Anthropic)
- [ ] Configurar `.env` no backend
- [ ] Instalar novas dependências: `cd backend && pip install -e .`
- [ ] Popular banco com embeddings: `python -m pipeline.embeddings.batch_embedder`

### Fase 2: Testes de Integração
- [ ] Executar `make test-backend` e verificar todos passam
- [ ] Testar endpoint `/chat` manualmente com curl
- [ ] Verificar logs mostram queries pgvector reais
- [ ] Confirmar respostas do chat variam (não são templates)

### Fase 3: Validação Final
- [ ] Rodar testes frontend: `cd frontend && npm test`
- [ ] Verificar scraper.yml funciona no GitHub Actions
- [ ] Atualizar MVP_LAUNCH_PLAN.md marcando o que foi validado

---

## 📂 ARQUIVOS MODIFICADOS

```
backend/app/agents/rag_agent.py              # Reescrito com pgvector real
backend/app/api/chat.py                      # Claude LLM integration
backend/pyproject.toml                       # Novas dependências
backend/tests/conftest.py                    # Fix imports
frontend/src/components/chat/product-card.tsx # Fix tests
frontend/src/tests/unit/product-card.test.ts # Fix assertions
pipeline/db/schema.sql                       # Add Dropshot retailer
.github/workflows/scraper.yml               # Fix module names
Makefile                                      # Fix PYTHONPATH
```

---

## 🎯 CRITÉRIOS DE SUCESSO PENDENTES

| Critério | Status | Como Validar |
|----------|--------|--------------|
| RAG retorna paddles reais | ❌ Pendente | Log mostra query pgvector, retorna dados do banco |
| Chat responde com Claude real | ❌ Pendente | Respostas variam por input, não são templates |
| Backend tests 100% | ⚠️ Parcial | 141/144 → precisa 144/144 |
| Frontend tests 100% | ✅ OK | 152/152 passando |
| Scraper workflow | ✅ OK | Corrigido, aguardando validação em prod |

---

## 🔑 VARIÁVEIS DE AMBIENTE NECESSÁRIAS

```bash
# backend/.env (não commitado)
OPENAI_API_KEY=sk-...           # Para embeddings RAG
ANTHROPIC_API_KEY=sk-ant-...    # Para Chat LLM
DATABASE_URL=postgresql://...   # Production DB
```

---

## 🚨 RISCOS

1. **Sem testes reais**, não sabemos se o código funciona
2. **Sem embeddings**, RAG não funciona (tabela vazia)
3. **Sem API keys**, não podemos testar Claude/OpenAI
4. **Sem banco populado**, não há dados para retornar

---

## 💡 NOTAS PARA PRÓXIMA SESSÃO

- O código está escrito e commitado, mas precisa de ambiente configurado
- Prioridade #1: Obter API keys e configurar .env
- Prioridade #2: Popular banco com embeddings
- Prioridade #3: Executar testes manuais de integração
- Prioridade #4: Validar que RAG e Chat funcionam com dados reais

**Estado: Código pronto, aguardando testes de integração.**
