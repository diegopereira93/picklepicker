# 🚀 Plano de Lançamento MVP - PickleIQ

## 📋 Resumo Executivo

**Projeto:** PickleIQ - Plataforma de inteligência para raquetes de pickleball  
**Versão Atual:** 1.3.0.1  
**Status:** Visual/Hardware completo, Software com GAPS CRÍTICOS  
**Data do Plano:** 2026-04-03  

---

## 🎯 O Problema

O MVP está **visualmente completo** (v1.3) mas tem **falhas críticas no software**:

1. **RAG Agent é 100% mockado** - Retorna dados hardcodados, não faz busca semântica real
2. **Chat não usa LLM real** - Raciocínio é string estática em português
3. **Eval Gate retorna scores fake** - Não avalia modelos reais
4. **Tests não rodam** - ModuleNotFoundError no backend, 4 falhas no frontend
5. **Pipeline ID inconsistente** - Dropshot usa retailer_id=3 (inexistente)
6. **GitHub Actions quebrado** - scraper.yml com paths errados

**Resultado:** A "IA" do produto não existe. É tudo mockado.

---

## 🔴 Blockers para Lançamento (MUST FIX)

### 1. Integrar RAG Agent com pgvector REAL [P0 - CRITICAL]
**Arquivo:** `backend/app/agents/rag_agent.py`  
**Problema:** Retorna `_mock_paddles` hardcodados (linhas 44-100)  
**Solução:**
- [ ] Conectar ao `db_pool` real
- [ ] Implementar busca semântica via `pgvector` (`<=>` operator)
- [ ] Usar embeddings da tabela `paddle_embeddings`
- [ ] Retornar paddles reais do banco

**Código alvo:**
```python
# Remover:
self._mock_paddles = self._get_mock_paddles()  # MOCK
return [PaddleResponse(**p) for p in MOCK_PADDLE_DATA]

# Implementar:
async with db_pool.connection() as conn:
    # Gerar embedding da query do usuário via OpenAI
    query_embedding = await generate_embedding(user_message)
    # Buscar similaridade em pgvector
    rows = await conn.execute(
        "SELECT * FROM paddle_embeddings ORDER BY embedding <-> %s LIMIT 5",
        (query_embedding,)
    )
    return [PaddleResponse.from_row(row) for row in rows]
```

---

### 2. Integrar Chat com LLM REAL (Claude/Groq) [P0 - CRITICAL]
**Arquivo:** `backend/app/api/chat.py`  
**Problema:** `reasoning` é string hardcodada (linha 107), `asyncio.sleep(0.1)` simula LLM  
**Solução:**
- [ ] Adicionar `anthropic` a `backend/pyproject.toml`
- [ ] Implementar chamada real à API Claude 3.5 Sonnet
- [ ] Construir prompt com contexto dos paddles + perfil do usuário
- [ ] Streaming de resposta real (não mock)

**Código alvo:**
```python
# Remover:
reasoning = f"Com base no seu perfil..."  # HARDCODADO
await asyncio.sleep(0.1)

# Implementar:
import anthropic
client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

prompt = f"""Você é um especialista em pickleball...
Perfil do usuário: {user_profile}
Raquetes disponíveis: {paddle_context}
Pergunta: {user_message}"""

response = await client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
    stream=True
)
# Streamar chunks via SSE
```

---

### 3. Corrigir Backend Tests [P0 - CRITICAL]
**Problema:** `make test-backend` falha com `ModuleNotFoundError: No module named 'app'`  
**Causa:** Makefile roda `cd backend && pytest` sem ativar venv, imports falham  
**Solução:**
- [ ] Corrigir `Makefile`:
```makefile
test-backend:
	cd backend && source venv/bin/activate && PYTHONPATH=$(PWD)/backend pytest -v
```
- [ ] Ou usar `poetry run pytest` / `python -m pytest`
- [ ] Verificar `conftest.py` tem paths corretos
- [ ] Garantir 100% dos tests passando antes do deploy

---

### 4. Corrigir Frontend Tests [P1 - HIGH]
**Problema:** 4 falhas em `product-card.test.ts`  
**Solução:**
- [ ] Rodar `cd frontend && npm test` e identificar falhas
- [ ] Corrigir asserções do badge "Recomendado"
- [ ] Garantir todos 152 tests passando

---

### 5. Corrigir Dropshot Retailer ID [P1 - HIGH]
**Arquivo:** `pipeline/crawlers/dropshot_brasil.py` (linha 128)  
**Problema:** `retailer_id=3` mas schema só tem IDs 1 e 2  
**Solução:**
- [ ] Adicionar INSERT para "Dropshot Brasil" em `pipeline/db/schema.sql`:
```sql
INSERT INTO retailers (name, base_url, integration_type, is_active) VALUES
    ('Dropshot Brasil', 'https://dropshot.com.br', 'firecrawl', TRUE);
```
- [ ] Ou mudar ID para 2 (verificar se não conflita)

---

### 6. Corrigir scraper.yml [P1 - HIGH]
**Arquivo:** `.github/workflows/scraper.yml`  
**Problemas:**
- Linha 45: `pipeline.crawlers.brazil_pickleball_store` → deveria ser `brazil_store`
- Linha 51: `pipeline.crawlers.drop_shot_brasil` → deveria ser `dropshot_brasil`
- Usa SQLAlchemy (`app.db.get_db`) mas projeto usa `psycopg`

**Solução:**
- [ ] Corrigir nomes dos módulos
- [ ] Corrigir import de conexão para usar `pipeline.db.connection`

---

## 🟡 Melhorias Pós-MVP (SHOULD HAVE)

### 7. Implementar Eval Gate Real [P2]
**Arquivo:** `backend/app/agents/eval_gate.py`  
**Atual:** Retorna scores hardcodados  
**Futuro:** Avaliar múltiplos LLMs (Claude, GPT-4) e selecionar o melhor baseado em latência/custo/qualidade

### 8. Adicionar Rate Limiting [P2]
**Arquivo:** `backend/app/main.py`  
- [ ] Adicionar middleware de rate limiting (slowapi ou flask-limiter)
- [ ] Limitar `/chat` endpoint (prevenir abuso)

### 9. Health Check Real [P2]
**Arquivo:** `backend/app/api/health.py`  
**Atual:** Retorna `"ok"` placeholder  
**Futuro:** Verificar conectividade real com PostgreSQL, testar query simples

### 10. Load Test T5 [P2 - do TODOS.md]
- [ ] Rodar k6/locust contra `/chat` endpoint
- [ ] Validar P95 < 3s conforme especificado
- [ ] Garantir 50 usuários beta não derrubam o serviço

---

## 🟢 Preparação para Lançamento

### Checklist de Deploy

#### Infraestrutura
- [ ] T1: Provisionar Supabase/Railway em produção (não deixar para Phase 6)
- [ ] Configurar variáveis de ambiente:
  - [ ] `ANTHROPIC_API_KEY` (Claude)
  - [ ] `OPENAI_API_KEY` (embeddings)
  - [ ] `DATABASE_URL` (produção)
  - [ ] `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`
  - [ ] `ADMIN_SECRET` (para endpoints admin)
  - [ ] `RESEND_API_KEY` (emails)
  - [ ] `TYPEFORM_API_KEY` + `TYPEFORM_FORM_ID` (NPS)

#### Banco de Dados
- [ ] Rodar `pipeline/db/schema.sql` em produção
- [ ] Popular tabela `retailers` com 3 entradas (incluindo Dropshot)
- [ ] Verificar pgvector extension instalada
- [ ] Criar materialized views `latest_prices`

#### Crawlers
- [ ] Testar manualmente cada crawler: `python -m pipeline.crawlers.brazil_store`
- [ ] Verificar se Firecrawl API key está configurada
- [ ] Agendar primeiras execuções e validar dados

#### Backend
- [ ] Instalar dependências: `cd backend && pip install -e .`
- [ ] Adicionar `anthropic` e `openai` a `pyproject.toml`
- [ ] Rodar tests: `make test-backend` (deve passar 100%)
- [ ] Verificar health endpoint responde 200
- [ ] Testar `/chat` com curl: `curl -N -H "Content-Type: application/json" -d '{"message":"Oi"}' http://localhost:8000/api/v1/chat`

#### Frontend
- [ ] `npm install` e `npm run build` (deve passar sem erros)
- [ ] `npm test` (152 tests devem passar)
- [ ] Verificar Clerk keys configuradas
- [ ] Testar build de produção localmente

#### GitHub Actions
- [ ] Verificar `deploy.yml` funciona (Railway + Vercel)
- [ ] Corrigir e testar `scraper.yml`
- [ ] Validar `test.yml` roda em PRs

#### Segurança
- [ ] T3: Avaliação legal de scraping (conforme TODOS.md)
- [ ] Verificar RLS policies em todas as tabelas
- [ ] Confirmar `ADMIN_SECRET` é strong/random
- [ ] Revisar headers de segurança em `vercel.json`

#### Monitoramento
- [ ] T4: Configurar alerta para review_queue > 100 itens
- [ ] T6: Configurar alerta quando crawler retorna 0 paddles
- [ ] T7: Documentar runbook para Firecrawl self-hosted

---

## 📅 Timeline Sugerida

### Semana 1: Correções Críticas (P0)
- **Dia 1-2:** Integrar RAG Agent com pgvector real
- **Dia 3-4:** Integrar Chat com Claude/Groq
- **Dia 5:** Corrigir backend tests + frontend tests

### Semana 2: Correções Importantes (P1)
- **Dia 1:** Corrigir Dropshot retailer_id
- **Dia 2:** Corrigir scraper.yml
- **Dia 3-4:** Implementar Eval Gate real
- **Dia 5:** Adicionar rate limiting + health check real

### Semana 3: Deploy e Validação
- **Dia 1:** T1 - Provisionar infra de produção
- **Dia 2:** Popular banco com dados reais (rodar crawlers)
- **Dia 3:** Deploy backend + frontend
- **Dia 4:** T5 - Load testing
- **Dia 5:** Beta test com 5 usuários internos

### Semana 4: Lançamento
- **Dia 1-2:** Beta test com 50 usuários (conforme plano original)
- **Dia 3:** Monitorar métricas (P95 < 3s, zero erros)
- **Dia 4:** Go/No-go decision
- **Dia 5:** 🚀 Lançamento público

---

## 🎯 Critérios de Sucesso para Lançamento

| Critério | Target | Como Medir |
|----------|--------|------------|
| Latência Chat P95 | < 3s | k6 load test |
| Tests Backend | 100% pass | `make test-backend` |
| Tests Frontend | 100% pass | `npm test` |
| Crawlers funcionando | 3/3 | Execução manual + GH Actions |
| RAG real | ✅ | Logs mostram queries pgvector |
| Chat LLM real | ✅ | Responses variam, não são templates |
| Zero erros 24h | 0 | Telegram alerts |

---

## 📝 Notas Adicionais

### Dependências Pendentes no pyproject.toml
```toml
[project]
dependencies = [
    # ... existentes ...
    "anthropic>=0.25.0",      # Claude API
    "openai>=1.0.0",          # Embeddings API
    "httpx>=0.27.0",          # HTTP client
    "python-dotenv>=1.0.0",   # Env vars
]
```

### Comandos de Verificação
```bash
# Testar RAG
curl http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Qual raquete para iniciante?"}'
# Deve retornar paddles REAIS do banco, não mocks

# Testar Health
curl http://localhost:8000/health
# Deve mostrar conexão real com DB

# Rodar todos os tests
make test  # Deve passar 100%
```

### Referências
- `AGENTS.md` - Conhecimento do projeto
- `DESIGN.md` - Design system v2.0
- `TODOS.md` - 7 itens deferred (T1-T7)
- `pipeline/db/schema.sql` - Schema completo

---

## ✅ Sign-off

Este plano foi gerado após análise completa do codebase em 2026-04-03.

**Estado Atual:** MVP visualmente pronto, software com gaps críticos  
**Estimativa para Lançamento:** 4 semanas (com correções P0/P1)  
**Risco Principal:** RAG/Chat mockados - sem isso, produto não entrega valor  

**Próximo Passo Imediato:** Delegar implementação das correções P0 para agents especializados.

---

*Plano gerado por Sisyphus com Ultrawork Mode*
