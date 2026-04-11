# Playbook de Limpeza do Catálogo PickleIQ

Guia completo para manutenção e limpeza do catálogo de raquetes do PickleIQ.

## 📋 Visão Geral

Este playbook descreve o processo de limpeza do catálogo de raquetes, incluindo:
- Análise do estado atual
- Backup seguro dos dados
- Limpeza de dados órfãos e inconsistentes
- Verificação contínua de saúde

## ⚠️ Preparação

### Antes de começar:
1. **Verifique se o banco de dados está acessível**: `make db-up`
2. **Tenha o backup do banco**: sempre execute o script de backup antes da limpeza
3. **Execute em ambiente de staging primeiro** (se disponível)
4. **Agende a limpeza para horário de baixo tráfego**

## 🔧 Scripts de Limpeza

### 1. Análise do Catálogo (1_analyze_catalog.py)

**O que faz:** Gera relatório completo do estado atual do catálogo.

**Execute:**
```bash
cd /home/diego/Documentos/picklepicker
python scripts/catalog_cleanup/1_analyze_catalog.py
```

**Saída esperada:**
- Contagem de paddles, snapshots, embeddings, specs
- Anomalias detectadas (sem preços, sem imagens, duplicatas)
- Estatísticas de preços (mínimo, médio, máximo)
- Frescor dos dados (últimas atualizações)
- Review queue pendentes

**Quando executar:**
- Semanalmente para monitoramento
- Antes de qualquer operação de limpeza
- Após grandes atualizações de crawlers

---

### 2. Backup dos Dados (2_backup_data.py)

**O que faz:** Cria backup completo em schema separado do PostgreSQL.

**Execute:**
```bash
cd /home/diego/Documentos/picklepicker
python scripts/catalog_cleanup/2_backup_data.py --verify
```

**Parâmetros:**
- `--schema-name`: nome customizado (default: backup_YYYYMMDD_HHMMSS)
- `--verify`: verifica integridade após backup
- `--list`: lista backups existentes

**Saída esperada:**
```
Schema: backup_20240409_143052
  paddles                       :   1,234 registros
  price_snapshots               :  45,678 registros
  paddle_specs                  :     890 registros
  paddle_embeddings             :   1,234 registros
  review_queue                  :      45 registros
  retailers                     :       3 registros
```

**Restauração (emergência):**
```bash
# Restaurar tabela específica
psql $DATABASE_URL -c "INSERT INTO paddles SELECT * FROM backup_20240409_143052.paddles"
```

---

### 3. Limpeza do Catálogo (3_cleanup_catalog.py)

**O que faz:** Remove dados órfãos e inconsistentes.

**⚠️ ATENÇÃO: Sempre execute em dry-run primeiro!**

**Passo 1 - Simulação:**
```bash
cd /home/diego/Documentos/picklepicker
python scripts/catalog_cleanup/3_cleanup_catalog.py --dry-run
```

**Passo 2 - Execução real (após revisar):**
```bash
python scripts/catalog_cleanup/3_cleanup_catalog.py --execute
```

**Operações realizadas:**
1. **Embeddings órfãos**: remove embeddings sem paddle correspondente
2. **Specs órfãos**: remove especificações sem paddle correspondente
3. **Snapshots antigos**: arquiva snapshots > 90 dias (mantém o mais recente)
4. **Duplicatas**: identifica e adiciona à review_queue
5. **Paddles stale**: marca paddles sem atualização > 30 dias
6. **Imagens quebradas**: marca paddles com imagens suspeitas

---

### 4. Verificação de Saúde (4_maintenance_check.py)

**O que faz:** Checagem diária de saúde do catálogo.

**Execute:**
```bash
cd /home/diego/Documentos/picklepicker
python scripts/catalog_cleanup/4_maintenance_check.py

# Com alertas Telegram para problemas críticos
python scripts/catalog_cleanup/4_maintenance_check.py --alert-telegram

# Salvando relatório JSON
python scripts/catalog_cleanup/4_maintenance_check.py --json-output health_report.json
```

**Checagens:**
- ✅ Total de paddles (threshold: > 100)
- ✅ Frescor dos dados (threshold: < 20% stale)
- ✅ Cobertura de imagens (threshold: > 70%)
- ✅ Cobertura de preços (threshold: > 90%)
- ✅ Taxa de duplicatas (threshold: < 5%)
- ✅ Review queue (threshold: < 50 pendentes)
- ✅ Cobertura de embeddings (threshold: > 95%)
- ✅ Saúde dos crawlers (executados nos últimos 2 dias)

---

## 📅 Fluxo de Limpeza Completo

### Limpeza Semanal (Recomendado)

```bash
# 1. Análise
python scripts/catalog_cleanup/1_analyze_catalog.py

# 2. Backup
python scripts/catalog_cleanup/2_backup_data.py --verify

# 3. Limpeza (dry-run)
python scripts/catalog_cleanup/3_cleanup_catalog.py --dry-run

# 4. Limpeza (execute se aprovado)
python scripts/catalog_cleanup/3_cleanup_catalog.py --execute

# 5. Verificação
python scripts/catalog_cleanup/4_maintenance_check.py
```

### Monitoramento Diário

```bash
# Adicione ao crontab para execução automática
# 0 9 * * * cd /home/diego/Documentos/picklepicker && python scripts/catalog_cleanup/4_maintenance_check.py --alert-telegram

# Ou execute manualmente
python scripts/catalog_cleanup/4_maintenance_check.py
```

---

## 🚨 Checklist de Catálogo 100% Atualizado

Para ter o catálogo 100% atualizado e completo:

### 1. Crawlers Funcionando ✅
- [ ] **Brazil Pickleball Store**: executando a cada 24h
- [ ] **Drop Shot Brasil**: executando a cada 24h
- [ ] **Mercado Livre**: executando a cada 24h
- [ ] Verificar: GitHub Actions > Actions > scraper.yml
- [ ] Verificar logs de execução: sem erros de API

### 2. Dados Completos ✅
- [ ] **Total de paddles**: > 200 raquetes
- [ ] **Com preços**: > 95% das raquetes
- [ ] **Com imagens**: > 80% das raquetes
- [ ] **Com embeddings**: 100% para busca similar
- [ ] **Com specs técnicas**: máximo possível

### 3. Dados Frescos ✅
- [ ] **Atualização de preços**: < 7 dias para todas as raquetes
- [ ] **Última execução dos crawlers**: < 24h
- [ ] **Materialized view**: atualizado (REFRESH CONCURRENTLY)

### 4. Qualidade dos Dados ✅
- [ ] **Duplicatas**: < 5% (usar fuzzy matching)
- [ ] **Imagens placeholders**: 0% (todas imagens reais)
- [ ] **Preços anômalos**: revisados e corrigidos
- [ ] **Review queue**: processada (0 pendentes críticos)

### 5. Integração com Frontend ✅
- [ ] **API /paddles**: respondendo corretamente
- [ ] **Filtros funcionando**: brand, preço, skill_level
- [ ] **Busca similar**: /paddles/{id}/similar funcionando
- [ ] **Chat RAG**: respondendo com dados atualizados

### 6. Monitoramento Ativo ✅
- [ ] **Alertas configurados**: Telegram para erros
- [ ] **Health check diário**: executando sem falhas
- [ ] **Métricas acompanhadas**: dashboards ou relatórios

---

## 🔄 Procedimentos de Emergência

### Se algo der errado durante a limpeza:

**1. Pare imediatamente:**
```bash
# Não execute mais comandos até avaliar
```

**2. Verifique o que foi afetado:**
```bash
python scripts/catalog_cleanup/1_analyze_catalog.py
```

**3. Execute verificação pós-limpeza:**
```bash
python scripts/catalog_cleanup/5_verify_cleanup.py
```

**4. Rollback de emergência (se necessário):**
```bash
# Listar backups disponíveis
python scripts/catalog_cleanup/6_rollback_emergency.py --list

# Simular rollback (recomendado)
python scripts/catalog_cleanup/6_rollback_emergency.py --backup backup_YYYYMMDD_HHMMSS --dry-run

# Executar rollback (⚠️ PERDE alterações desde o backup)
python scripts/catalog_cleanup/6_rollback_emergency.py --backup backup_YYYYMMDD_HHMMSS

# Confirmação necessária: digite 'FAZER-ROLLBACK'
```

⚠️ **ATENÇÃO**: O rollback restaura TODAS as tabelas ao estado do backup. Use apenas em emergências!

**4. Notifique a equipe:**
- Abra issue no GitHub com logs do erro
- Envie mensagem no canal #ops do Slack/Discord

---

## 📊 Métricas de Sucesso

| Métrica | Target | Mínimo Aceitável |
|---------|--------|------------------|
| Total paddles | > 300 | > 150 |
| Cobertura de preços | 100% | > 90% |
| Cobertura de imagens | > 90% | > 70% |
| Dados fresh (< 7d) | 100% | > 80% |
| Duplicatas | < 2% | < 10% |
| Review queue pendentes | 0 | < 50 |
| Health check | OK | WARNING ok |

---

## 🛠️ Comandos Úteis

### Verificar estado do banco:
```bash
make db-shell
```

### Queries SQL úteis:
```sql
-- Contar paddles por varejista
SELECT r.name, COUNT(*) 
FROM price_snapshots ps 
JOIN retailers r ON r.id = ps.retailer_id 
GROUP BY r.name;

-- Paddles sem preços
SELECT name FROM paddles p 
WHERE NOT EXISTS (SELECT 1 FROM price_snapshots ps WHERE ps.paddle_id = p.id);

-- Verificar última execução dos crawlers
SELECT retailer_id, MAX(scraped_at) 
FROM price_snapshots 
GROUP BY retailer_id;
```

### Executar crawlers manualmente:
```bash
# Requer DATABASE_URL e FIRECRAWL_API_KEY configurados
python -m pipeline.crawlers.brazil_store
python -m pipeline.crawlers.dropshot_brasil
python -m pipeline.crawlers.mercado_livre
```

---

## 📞 Suporte

Em caso de problemas:
1. Consulte os logs em: `make db-logs`
2. Verifique alertas no Telegram
3. Revise este playbook
4. Abra issue no GitHub com: erro completo, ambiente, horário

---

**Última atualização:** 2026-04-09
**Versão:** 1.0
