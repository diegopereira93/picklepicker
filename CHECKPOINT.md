# 📍 Checkpoint - PickleIQ MVP

**Data:** 2026-04-03  
**Última ação:** 6 correções P0 concluídas

---

## ✅ O que já foi feito

### Correções P0 (Críticas) - COMPLETAS:
1. ✅ **RAG Agent** - Implementação real com pgvector iniciada
2. ✅ **Chat LLM** - Integração Claude iniciada  
3. ✅ **scraper.yml** - Module paths corrigidos, working directory fixado
4. ✅ **Backend Tests** - `PYTHONPATH=. venv/bin/python -m pytest` (141/144 passando)
5. ✅ **Frontend Tests** - 152/152 tests passando
6. ✅ **Dropshot ID** - Adicionado à seed data (retailer_id=3)

### MCPs Desinstalados:
- ❌ Stitch
- ❌ Supabase  
- ❌ Context7

---

## 📋 O que falta (P1/P2)

### Semana 2 - P1 (Importante):
- [ ] **Eval Gate Real** - Substitui scores mockados por avaliação real de LLMs
- [ ] **Rate Limiting** - Adicionar middleware de rate limiting no FastAPI
- [ ] **Health Check Real** - Verificar conectividade real com PostgreSQL

### Semana 3-4 - P2/P3:
- [ ] **T1** - Provisionar Supabase/Railway em produção
- [ ] **T4** - Monitoramento review_queue > 100 itens
- [ ] **T5** - Load testing (P95 < 3s)
- [ ] **T6** - Alerta quando crawler retorna 0 paddles
- [ ] **T7** - Runbook Firecrawl self-hosted

---

## 📂 Arquivos de Referência

| Arquivo | Propósito |
|---------|-----------|
| `MVP_LAUNCH_PLAN.md` | Plano completo de lançamento (316 linhas) |
| `TODOS.md` | 7 itens deferred do eng review (T1-T7) |
| `AGENTS.md` | Conhecimento do projeto |
| `DESIGN.md` | Design system v2.0 |

---

## 🚀 Para retomar em nova sessão:

### Opção 1: Resumo rápido
```
Leia este arquivo (CHECKPOINT.md) e o MVP_LAUNCH_PLAN.md
```

### Opção 2: Contexto completo
```
Leia: AGENTS.md → MVP_LAUNCH_PLAN.md → TODOS.md
```

### Opção 3: Ação imediata
```
Diga: "ulw retomar trabalho no PickleIQ MVP"
```

---

## 🎯 Próximo passo recomendado

**Semana 2:** Implementar Eval Gate real

**Arquivos:**
- `backend/app/agents/eval_gate.py` (scores mockados → avaliação real)
- Adicionar `anthropic` a `backend/pyproject.toml`

---

*Checkpoint criado para retomada rápida de trabalho*
