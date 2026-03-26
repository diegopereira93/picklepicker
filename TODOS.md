# PickleIQ — TODOS

Items capturados durante /plan-eng-review (2026-03-26). Deferred work que não bloqueia o MVP mas deve ser revisitado.

---

## T1 — Provisionar infra desde Phase 1 (não Phase 6)

**What:** Criar projeto Supabase no início da Phase 1 e Railway no início da Phase 2. Rodar migrations contra Supabase desde o começo — não só contra Docker Compose local.

**Why:** Docker Compose e Supabase divergem em extensões, permissões e RLS. Migrations que passam local podem falhar em produção. Descobrir isso na Phase 6 é tarde demais.

**Pros:** Elimina divergência dev/prod desde o início; migrations testadas no ambiente real em todas as fases.

**Cons:** Requer criar contas e projetos antes de escrever qualquer código. Supabase free tier pode ter limitações de conexão simultânea no dev.

**Context:** Atualmente o plano posiciona Vercel + Railway + Supabase como deliverable da Phase 6 (R6.1). Isso cria um risco de integração de última hora. O Supabase free tier é suficiente para dev/staging — não há custo adicional.

**Depends on:** Nada — pode ser feito antes de qualquer código.

---

## T2 — Eval gate de modelo como job mensal (não one-time)

**What:** Adicionar `eval-model-selection.yml` no GitHub Actions rodando todo primeiro dia do mês. Output: `backend/evals/model-selection-{date}.md`. Alerta no Telegram se o modelo selecionado mudou desde o último run.

**Why:** O eval gate atual é rodado uma vez pré-Phase 3 e nunca mais. Se o Groq mudar o modelo OSS disponível (ou a qualidade cair), a seleção fica obsoleta silenciosamente. Ao mesmo tempo, o corpus de paddles cresce e novas queries podem revelar gaps.

**Pros:** Garante que a seleção de modelo está sempre atualizada; custo marginal ~10 API calls/mês.

**Cons:** Adiciona um workflow GH Actions a manter; pode gerar falsos alertas se o threshold for sensível a variância do LLM-as-judge.

**Context:** Implementar na Phase 3 junto com o eval gate inicial. Usar o mesmo script Python, só parametrizando a data de saída.

**Depends on:** Phase 3.1 (eval gate) implementado.

---

## T3 — Avaliar risco legal de scraping de specs internacionais

**What:** Verificar ToS de PickleballCentral e Johnkew antes de implementar os crawlers de specs (Phase 2). Identificar fonte alternativa se necessário (press kits de fabricantes, especificações WPT/PPA).

**Why:** Ambos são varejistas US com ToS que provavelmente proíbem scraping. Um C&D ou bloqueio de IP quebra o pipeline de enriquecimento de specs e inunda o review_queue.

**Pros:** Evitar risco legal antes de investir tempo no crawler; identificar fonte melhor (ex: fabricante diretamente) pode ser mais confiável.

**Cons:** Pode revelar que não há fonte ToS-permissiva disponível — nesse caso, o risco precisa ser aceito conscientemente.

**Context:** Specs de swingweight/twistweight são raras em fontes abertas. A alternativa mais segura é contato direto com fabricantes (Selkirk, JOOLA, Head) para dados técnicos.

**Depends on:** Antes de implementar Phase 2 spec crawlers.

---

## T4 — Monitorar volume do review_queue e definir SLA

**What:** Adicionar métrica de volume do review_queue ao dashboard de observabilidade (Langfuse ou Railway logs). Definir: quantos itens pendentes são aceitáveis antes de bloquear o crawler ou alertar.

**Why:** O threshold RapidFuzz 0.85 pode gerar volume alto de review_queue em escala (títulos inconsistentes entre varejistas BR). Sem visibilidade, o backlog cresce silenciosamente até virar blocker de launch.

**Pros:** Visibilidade antecipada do problema; permite ajustar threshold ou adicionar regras de merge antes do launch.

**Cons:** Adiciona complexidade de monitoramento; o volume real só é conhecido após os crawlers rodarem.

**Context:** Implementar como health check simples: `SELECT COUNT(*) FROM review_queue WHERE status='pending'` exposto via `/health` ou alerta Telegram diário se > threshold (ex: > 50 itens).

**Depends on:** Phase 2 (admin backend) implementado.

---

## T5 — Load test spec para endpoint /chat

**What:** Script k6 ou Locust simulando 50 usuários simultâneos no /chat. Assertar P95 < 3s, P99 < 8s, zero 5xx a 50 concurrent. Rodar contra Railway staging antes do beta launch (Phase 6).

**Why:** O plano tem meta P95 < 3s mas nenhum teste que a verifique. Sem load test, o gargalo (pgvector + Claude API sob carga) só aparece quando os 50 usuários beta chegarem simultaneamente.

**Pros:** Detecta gargalos de pgvector e Claude API antes do beta. Estabelece baseline de performance para comparação futura.

**Cons:** Requer ambiente staging com dados reais. k6/Locust setup leva ~2h humanas.

**Context:** Usar um golden set de 5-10 queries realistas como carga. Rodar contra Railway staging (provisionado na Phase 2). Resultado deve ir em `backend/evals/load-test-{date}.md`.

**Effort:** S (human: 4h / CC: 30min) | **Priority:** P1 | **Depends on:** Phase 3 completo (staging com /chat real)

---

## T6 — Zero-paddle alert no crawler (snapshot test)

**What:** Ao final de cada run do GH Actions, verificar via SQL se cada varejista indexou > 0 paddles naquele dia. Se zero: alerta Telegram imediato — "ZERO PADDLES: brazil-pickleball-store — parser pode estar quebrado."

**Why:** Uma mudança no HTML do varejista faz o Firecrawl retornar sucesso (HTTP 200) mas parse vazio. O preço fica stale silenciosamente — nenhum alerta dispara porque não houve falha HTTP.

**Pros:** Detecta quebra de parser imediatamente. Custa 10 minutos de implementação.

**Cons:** Falsos positivos se um varejista temporariamente tiver catálogo vazio (improvável para estes varejistas).

**Context:** Adicionar como step final no job GH Actions: `SELECT COUNT(*) FROM price_snapshots WHERE DATE(scraped_at) = CURRENT_DATE AND retailer_id = X`. Se 0 → alerta Telegram.

**Effort:** S (human: 1h / CC: 10min) | **Priority:** P2 | **Depends on:** Phase 2 crawlers implementados

---

## T7 — Runbook de migração para Firecrawl self-hosted

**What:** Documentar passos para subir instância Firecrawl no Railway caso o free tier seja insuficiente. Incluir: imagem Docker, configuração de proxies rotativos, variáveis de ambiente no Railway, estimativa de custo ($20-50/mês).

**Why:** O plano depende do free tier (500 créditos/mês). Se o catálogo crescer (Milestone 2: mais varejistas + outras categorias), o free tier falha silenciosamente. Runbook pronto = migração em 2h em vez de 1 dia.

**Pros:** Zero surpresa quando o free tier for superado. Decisão já tomada — só executar o runbook.

**Cons:** Firecrawl self-hosted requer gestão de proxies (rotação de IP), adicionando complexidade operacional.

**Context:** Escrever o runbook na Phase 2 após o primeiro run confirmar o consumo real de créditos. Só executar se o consumo projetar extrapolação do free tier.

**Effort:** S (human: 3h / CC: 20min) | **Priority:** P3 | **Depends on:** Phase 2 crawlers rodando (para medir consumo real de créditos)
