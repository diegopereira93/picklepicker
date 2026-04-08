# Análise dos GitHub Actions Workflows

## Workflows Atuais (8 arquivos)

### 1. deploy.yml
- **O que faz**: Testa, faz deploy preview (PR) e deploy produção (main)
- **Problemas**:
  - Python 3.11 vs 3.12 usado em outros workflows (inconsistência)
  - Railway deploy pode estar desatualizado (o backend já está em produção?)
  - Não faz deploy do frontend (apenas preview em PR)
- **Veredito**: MANTER, mas revisar plataformas de deploy

### 2. lighthouse.yml
- **O que faz**: CI do Lighthouse em cada push
- **Problemas**:
  - Roda em TODO push - muito frequente e custoso
  - Falta `npm run lighthouse:ci` no package.json (ou precisa confirmar se existe)
- **Veredito**: MODIFICAR - mudar trigger para PR apenas ou agendado

### 3. nps-survey.yml
- **O que faz**: Envia surveys NPS para usuários com 30 dias
- **Problemas**:
  - Referencia `scripts/send_nps_surveys.py` que existe
  - Depende de Typeform API (está configurado?)
- **Veredito**: MANTER (mas verificar se secrets existem)

### 4. price-alerts-check.yml
- **O que faz**: Verifica alertas de preço diariamente (6h UTC)
- **Problemas**:
  - Usa backend/workers/price_alert_check.py que existe
  - Python 3.11 vs 3.12
- **Veredito**: MANTER (funcionalidade necessária)

### 5. scraper.yml
- **O que faz**: Crawler completo - todos os varejistas
- **Problemas**:
  - Bem estruturado com retry, jitter, verificação de dados
  - Roda todos os crawlers em sequência (poderia ser paralelo)
  - Usa Python 3.11
- **Veredito**: MANTER (é o workflow principal de scraping)

### 6. scrape.yml
- **O que faz**: Crawlers individuais em jobs paralelos + enrichment
- **Problemas CRÍTICOS**:
  - **DUPLICA** funcionalidade do scraper.yml
  - Referencia crawlers que NÃO EXISTEM:
    - pipeline.crawlers.franklin_br (não existe)
    - pipeline.crawlers.head_br (não existe)
    - pipeline.crawlers.joola_br (não existe)
  - Referencia pipeline.crawlers.spec_enrichment (não existe)
  - Agendado para 6h UTC = mesmo horário que price-alerts-check.yml
- **Veredito**: REMOVER ou consolidar com scraper.yml

### 7. test.yml
- **O que faz**: Testes e cobertura em PR e push
- **Problemas**:
  - Usa Python 3.11 (inconsistência)
  - Não testa o frontend
  - Ruff lint apenas (não format)
- **Veredito**: MANTER mas melhorar (adicionar testes frontend)

### 8. validate-production.yml
- **O que faz**: Validação de produção com Playwright
- **Problemas**:
  - Referencia scripts/validate-production.ts que existe
  - Mas não instala dependências do frontend/backend antes de rodar
  - Instala playwright mas não instala node_modules do projeto
- **Veredito**: MODIFICAR - corrigir instalação de dependências

---

## Resumo de Ações

| Workflow | Ação | Prioridade |
|----------|------|------------|
| scrape.yml | REMOVER | Alta (referencia arquivos inexistentes) |
| lighthouse.yml | MODIFICAR triggers | Média |
| test.yml | MODIFICAR (Python 3.12, add frontend tests) | Média |
| validate-production.yml | MODIFICAR (fix deps) | Média |
| deploy.yml | REVISAR deploy targets | Baixa |
| scraper.yml | MANTER (talvez atualizar Python) | Baixa |
| price-alerts-check.yml | MANTER (atualizar Python) | Baixa |
| nps-survey.yml | MANTER | Baixa |

## Problemas Encontrados

1. **Duplicação**: scrape.yml vs scraper.yml (mesma função, duplicada)
2. **Referências quebradas**: scrape.yml referencia 4 arquivos que não existem
3. **Inconsistência Python**: 3.11 vs 3.12 em diferentes workflows
4. **Lighthouse CI**: Trigger muito frequente (todo push)
5. **validate-production.yml**: Instalação de dependências incompleta

## Arquivos Referenciados que Não Existam

- pipeline/crawlers/franklin_br.py ❌
- pipeline/crawlers/head_br.py ❌
- pipeline/crawlers/joola_br.py ❌
- pipeline/crawlers/spec_enrichment.py ❌
