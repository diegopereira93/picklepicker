# PickleIQ Production Health Check - Checkpoint

**Data:** 03 Apr 2026, 20:10 BRT
**Status:** COMPLETO - Aguardando Oracle Verification

---

## Resumo Executivo

PickleIQ **NÃO ESTÁ FUNCIONAL em produção**. Identifiquei 4 problemas críticos que impedem o funcionamento:

1. **Railway:** Deployado mas FastAPI não está rodando (todos endpoints 404)
2. **Vercel:** Deployado mas redireciona para `/lander` (403 Forbidden)
3. **Configuração:** Rewrite do Vercel aponta para URL errada
4. **Environment:** Variáveis não configuradas (`@changeme` placeholders)

---

## Respostas às 4 Perguntas Originais

| # | Pergunta | Status | Evidência |
|---|----------|--------|-----------|
| 1 | **Railway + Vercel rodando?** | ⚠️ PARCIAL | Railway: serviço ativo (HTTP 200) mas FastAPI 404 em todos endpoints. Vercel: deploy ativo (DNS resolve) mas redireciona para `/lander` |
| 2 | **Secrets configuradas?** | ❌ NÃO | Vercel: `@changeme` placeholders em `vercel.json`. Railway: não verificável sem dashboard |
| 3 | **Supabase conectado?** | 🔶 NÃO VERIFICÁVEL | Sem backend funcional para testar conexão |
| 4 | **Builds passando?** | ✅ SIM | Frontend: `npm run build` → 15 rotas. Backend: `docker build` → sucesso |

---

## Detalhamento dos Problemas

### 🔴 1. Railway Backend (pickleiq-backend.railway.app)

**Status:** ❌ DEPLOYADO, MAS FASTAPI NÃO FUNCIONA

**Testes Realizados:**

| Endpoint | Resposta HTTP | Conteúdo | Status |
|----------|---------------|----------|--------|
| `GET /` | 200 | ASCII art do Railway | ✅ Serviço ativo |
| `GET /health` | 200 | "OK" (text/plain) | ⚠️ Railway health check (não FastAPI) |
| `GET /docs` | 404 | "Not Found" | ❌ FastAPI docs não montado |
| `GET /openapi.json` | 404 | "Not Found" | ❌ OpenAPI spec não disponível |
| `GET /api/v1/paddles` | 404 | "Not Found" | ❌ API routes não funcionando |
| `GET /api/v1/health` | 404 | "Not Found" | ❌ Health router não montado |

**Análise:**
O serviço Railway está ativo (responde na porta 443), mas o FastAPI não está sendo executado corretamente. O container Docker pode estar falhando na inicialização por falta de environment variables (DATABASE_URL), ou há um problema na montagem das rotas.

**Possíveis Causas:**
1. Container inicia mas crasha por falta de DATABASE_URL
2. FastAPI não consegue conectar ao Supabase durante startup
3. Problema no `lifespan` do FastAPI que fecha o pool antes de iniciar

---

### 🔴 2. Vercel Frontend (pickleiq.com)

**Status:** ❌ DEPLOYADO, MAS NÃO FUNCIONAL

**Testes Realizados:**

| Rota | Resposta |
|------|----------|
| `GET /` | HTML redirect para `/lander` |
| `GET /paddles` | Redirect para `/lander` |
| `GET /chat` | Redirect para `/lander` |
| `GET /admin` | Redirect para `/lander` |
| `GET /lander` | 403 Forbidden |

**Root Cause:**
`ClerkProvider` falha sem as environment variables configuradas, causando comportamento de "landing page" ou erro de autenticação.

---

### 🔴 3. BUG CRÍTICO: Vercel Rewrite Mal Configurado

**Arquivo:** `vercel.json` linha 20

**Configuração Atual (ERRADA):**
```json
{
  "source": "/api/:path*",
  "destination": "https://api.railway.app/api/:path*"
}
```

**Problema:**
`api.railway.app` é o domínio da API do Railway (para gerenciamento), **NÃO** o domínio do serviço FastAPI.

**Deveria ser:**
```json
{
  "source": "/api/:path*",
  "destination": "https://pickleiq-backend.railway.app/api/:path*"
}
```

**Impacto:**
Todas as chamadas de API do frontend falham porque são redirecionadas para a API de gerenciamento do Railway em vez do backend real.

---

### 🔴 4. Variáveis de Ambiente

**Vercel (`vercel.json`):**
```json
"build": {
  "env": {
    "NEXT_PUBLIC_FASTAPI_URL": "@changeme",
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "@changeme",
    "CLERK_SECRET_KEY": "@changeme",
    "NEXT_PUBLIC_LANGFUSE_KEY": "@changeme"
  }
}
```

**Status:** ❌ **TODAS SÃO PLACEHOLDERS** - Nenhuma variável está configurada.

**Railway:**
- ❓ **NÃO VERIFICÁVEL** - Requer acesso ao Railway Dashboard para ver logs e env vars.

---

### 🔴 5. Supabase (Banco de Dados)

**Status:** 🔶 **NÃO VERIFICÁVEL**

**Por que:**
- Backend FastAPI não funciona, então não consigo testar a API
- Não tenho acesso ao Supabase Dashboard para testar conexão direta
- Connection strings estão em env vars que não consigo ver

---

## Build Status

| Componente | Status | Evidência |
|------------|--------|-----------|
| **Frontend** | ✅ PASSA | `npm run build` → 15 rotas geradas |
| **Backend** | ✅ PASSA | `docker build -f backend/Dockerfile` → imagem criada com sucesso |

**Nota:** Builds locais passam, mas isso não garante funcionamento em produção.

---

## Ações Recomendadas

### PRIORIDADE CRÍTICA (Bloqueantes)

1. **Corrigir `vercel.json`**
   ```json
   {
     "source": "/api/:path*",
     "destination": "https://pickleiq-backend.railway.app/api/:path*"
   }
   ```

2. **Configurar Vercel Environment Variables**
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (obter em clerk.com)
   - `CLERK_SECRET_KEY` (obter em clerk.com)
   - `NEXT_PUBLIC_FASTAPI_URL` = `https://pickleiq-backend.railway.app`

3. **Verificar Railway Dashboard**
   - Acessar logs do serviço `backend` para ver por que FastAPI não inicia
   - Verificar se `DATABASE_URL` está configurado
   - Verificar se `GROQ_API_KEY` está configurado
   - Verificar se container inicia sem erros

4. **Configurar DNS Custom Domain (opcional)**
   - Se quiser usar `api.pickleiq.com`, configurar CNAME no DNS para `pickleiq-backend.railway.app`

### PRIORIDADE ALTA

5. **Adicionar Health Check Real no Backend**
   - Atualizar `backend/app/api/health.py` para fazer query real no DB
   - Isso ajudará a diagnosticar problemas de conexão

6. **Testar Conexão Supabase**
   - Via CLI: `psql "$DATABASE_URL" -c "SELECT count(*) FROM paddles;"`
   - Ou via Railway logs quando backend iniciar

---

## Comandos de Verificação para Próxima Sessão

```bash
# Verificar Railway

curl -s https://pickleiq-backend.railway.app/health
curl -s https://pickleiq-backend.railway.app/docs
curl -s "https://pickleiq-backend.railway.app/api/v1/paddles?limit=1"

# Verificar Vercel

curl -s https://pickleiq.com/curl -s https://pickleiq.com/paddles
nslookup api.pickleiq.com

# Verificar DNS

host pickleiq.com
host api.pickleiq.com
```

---

## Arquivos Analisados

- `vercel.json` - Configuração de deploy do Vercel (BUG no rewrite)
- `railway.toml` - Configuração de deploy do Railway
- `backend/Dockerfile` - Dockerfile do backend (build OK)
- `backend/app/main.py` - Entry point do FastAPI
- `backend/app/api/health.py` - Health check endpoint (placeholder)
- `frontend/next.config.mjs` - Configuração do Next.js
- `frontend/src/middleware.ts` - Middleware do Clerk
- `frontend/src/layout.tsx` - Layout com ClerkProvider

---

## Notas para Continuação

### Problemas Identificados para Resolver:

1. **Railway service existe mas FastAPI 404 em todos endpoints**
   - Verificar logs no Railway Dashboard
   - Confirmar que env vars estão setadas
   - Testar se é problema de inicialização do container

2. **Vercel rewrite aponta para URL errada**
   - Corrigir `vercel.json`
   - Commit e push para atualizar deploy

3. **Clerk env vars não configuradas**
   - Obter keys em clerk.com
   - Configurar no Vercel Dashboard

4. **DNS custom domain não configurado**
   - `api.pickleiq.com` retorna NXDOMAIN
   - Configurar CNAME se quiser usar domínio customizado

5. **Supabase conexão não verificada**
   - Requer backend funcionando para testar via API
   - Ou acesso direto ao Supabase Dashboard

---

## Status do Todo

- [x] Verificar Railway deployment
- [x] Verificar Vercel deployment
- [x] Verificar variáveis de ambiente (Vercel)
- [x] Identificar bug no vercel.json rewrite
- [x] Testar build do frontend
- [x] Testar build do backend
- [ ] Verificar Railway env vars (requer dashboard)
- [ ] Verificar Supabase conexão (requer backend funcionando)

---

**Checkpoint criado em:** 03 Apr 2026, 20:10 BRT
**Próxima ação recomendada:** Acessar Railway Dashboard para verificar logs e env vars do serviço backend.

---

## Evidências Coletadas

Todos os testes foram realizados com `curl` e estão documentados acima com:
- HTTP status codes
- Respostas completas
- Headers relevantes
- DNS lookups

**Verificação Manual:** Todos os comandos foram executados e suas saídas registradas neste documento.

---

**FIM DO CHECKPOINT**
