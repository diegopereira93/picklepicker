# Crawlers — Pipeline de Scraping

Scraper de preços e especificações de raquetes de pickleball em varejistas brasileiros.

## Varejistas Suportados

| ID | Nome | `integration_type` | Arquivo |
|----|------|---------------------|---------|
| 1 | Brazil Pickleball Store | `firecrawl` | `brazil_store.py` |
| 2 | JOOLA | `shopify_json` | `joola.py` |
| 3 | Drop Shot Brasil | `firecrawl` | `dropshot_brasil.py` |

Dados seed em `pipeline/db/schema.sql` (INSERT INTO retailers).

## Tipos de Integração

### `firecrawl`

Usa [Firecrawl](https://firecrawl.dev/) para extração estruturada via schema JSON. O crawler define um `FIRECRAWL_SCHEMA` com campos esperados (`name`, `price_brl`, `in_stock`, `image_url`, `brand`, `specs`). Firecrawl faz renderização JavaScript + extração AI.

- **Requer**: `FIRECRAWL_API_KEY` no ambiente
- **Exemplos**: `brazil_store.py`, `dropshot_brasil.py`

### `shopify_json`

Usa endpoints nativos do Shopify (`/collections/{slug}/products.json`). Sem dependência de scraping externo — apenas `httpx`. HTML das descrições é parseado com `HTMLParser` nativo do Python para extrair specs.

- **Requer**: nenhum API key extra
- **Exemplo**: `joola.py`
- **Paginação**: `?limit=250&page=N`

### Outros tipos (CHECK constraint)

O banco aceita `ml_api` e `pa_api` no CHECK constraint, mas não há crawlers implementados para esses tipos. Estão reservados para integração futura com Mercado Livre e Amazon.

## Como Adicionar um Novo Varejista

### 1. Registrar no banco

```sql
INSERT INTO retailers (name, base_url, integration_type, is_active)
VALUES ('Nome do Varejista', 'https://example.com', 'firecrawl', TRUE);
```

Execute via migration ou direto no banco. O `id` gerado será o `retailer_id` usado no crawler.

### 2. Criar o arquivo do crawler

Criar `pipeline/crawlers/<nome>.py` seguindo o padrão dos crawlers existentes:

```
imports (tenacity, firecrawl/httpx, dedup, db, alerts)
├── Constantes (URL, SCHEMA, RETAILER_ID)
├── fetch_products()  → lista de produtos brutos
├── parse_product()   → produto normalizado
├── save_products()   → dedup + INSERT em paddles/price_snapshots
└── main()            → orquestra tudo com retry
```

**Dependências comuns** (já instaladas):
- `tenacity` — retry com backoff exponencial
- `pipeline.crawlers.utils` — `normalize_paddle_name`, `extract_brand_from_name`, `validate_image_belongs_to_product`
- `pipeline.dedup.normalizer` — `tier2_match`, `title_hash`
- `pipeline.dedup.spec_matcher` — `fuzzy_match_paddles`
- `pipeline.db.connection` — `get_connection`
- `pipeline.alerts.telegram` — `send_telegram_alert`

**Padrão mínimo** (firecrawl):

```python
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential
from pipeline.db.connection import get_connection
from pipeline.dedup.normalizer import tier2_match, title_hash

RETAILER_ID = 4  # id do INSERT acima
URL = "https://example.com/pickleball"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=10, max=60))
def fetch_products():
    app = FirecrawlApp()
    result = app.extract([URL], {"type": "object", ...})
    return result.get("products", [])

def main():
    products = fetch_products()
    # normalizar → dedup → INSERT
    ...

if __name__ == "__main__":
    main()
```

**Padrão mínimo** (shopify_json):

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

RETAILER_ID = 4
PRODUCTS_URL = "https://example.com/collections/all/products.json?limit=250"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=10, max=60))
async def fetch_products():
    async with httpx.AsyncClient() as client:
        resp = await client.get(PRODUCTS_URL)
        return resp.json().get("products", [])
```

### 3. Adicionar ao CI/CD

Editar `.github/workflows/scraper.yml` na step `Run crawlers with retry`:

```yaml
echo "Running Novo Varejista crawler..."
python -m pipeline.crawlers.<nome>
```

### 4. Testar

```bash
# Teste unitário (mock)
pytest pipeline/tests/test_<nome>.py

# Teste real (requer banco + API keys)
python -m pipeline.crawlers.<nome>
```

## Arquitetura do Pipeline

```
Crawler (fetch + parse)
  → normalize_paddle_name()
  → tier2_match(title_hash)     -- dedup exata
  → fuzzy_match_paddles()       -- dedup fuzzy (RapidFuzz ≥ 0.85)
  → INSERT paddles + price_snapshots
  → REFRESH latest_prices
```

- **Dedup é conservadora**: duplicatas vão para `review_queue`, nunca são bloqueadas
- **price_snapshots** é append-only (imutável) — histórico completo de preços
- **latest_prices** é materialized view — refresh após cada crawler run

## Controle de Ativação

A coluna `retailers.is_active` controla se um varejista deve ser processado:

- `TRUE` (padrão) — crawler processa normalmente
- `FALSE` — crawler deve ignorar; usado para pausar scraping sem remover dados

Para desativar:

```sql
UPDATE retailers SET is_active = FALSE WHERE name = 'Nome do Varejista';
```

## Troubleshooting

| Problema | Verificar |
|----------|-----------|
| `FIRECRAWL_API_KEY` não definida | `.env` ou secrets do GitHub Actions |
| 0 produtos extraídos | Site mudou estrutura; inspecionar `dead_letter_queue` |
| Duplicatas no catálogo | `SELECT * FROM review_queue WHERE status = 'pending'` |
| Preço desatualizado | `REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices;` |
