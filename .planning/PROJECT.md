# PickleIQ — Plataforma de Inteligência de Dados & IA para Pickleball

## O que estamos construindo

PickleIQ é uma plataforma web que combina monitoramento automatizado de preços de mercado com um agente de IA conversacional para ajudar jogadores de pickleball a escolherem raquetes. A plataforma usa scraping via Firecrawl para coletar preços e especificações técnicas de múltiplos varejistas em tempo real, e um agente RAG (Retrieval-Augmented Generation) para traduzir métricas técnicas em linguagem simples e recomendar produtos personalizados.

## Por que existe

O mercado de pickleball cresceu 311% em 3 anos com 19,8M de jogadores nos EUA. Compradores enfrentam dois problemas: (1) métricas técnicas incompreensíveis como swingweight e twistweight, e (2) preços fragmentados entre varejistas sem visibilidade centralizada. A PickleIQ resolve ambos e monetiza via comissões de afiliados de 10-40% por venda.

## Para quem é

- **Iniciante entusiasmado (35-55 anos):** Quer recomendação personalizada em linguagem simples sem precisar entender jargões técnicos
- **Jogador intermediário analítico (28-45 anos):** Quer comparativo técnico com preço em tempo real de múltiplas fontes
- **Gift buyer:** Descreve o perfil do presenteado e orçamento, recebe sugestão direta com link de compra

## Stack Tecnológico

| Camada | Tecnologia |
|---|---|
| Scraping | Firecrawl API |
| Pipeline | Python + Prefect |
| Banco Relacional | PostgreSQL |
| Banco Vetorial | Pinecone |
| LLM | Claude 3.5 Sonnet (Anthropic API) |
| Embeddings | OpenAI text-embedding-3-small |
| Backend | Python + FastAPI |
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Auth | Clerk |
| Hospedagem Backend | Railway (MVP) |
| Hospedagem Frontend | Vercel |
| Observabilidade LLM | Langfuse |
| Afiliados | PickleballCentral, Amazon Associates, Selkirk |

## O que "done" parece

**MVP (mês 7 — beta):**
- ≥ 500 raquetes indexadas com preços atualizados a cada 24h de 4+ varejistas
- Chat conversacional que recomenda raquetes com justificativa personalizada em < 3s
- Cards de produto com menor preço atual + link de afiliado + indicador de estoque
- Comparador side-by-side com gráfico radar
- Deploy em produção (Vercel + Railway)

**Métricas de sucesso:**
- 500 MAU no mês 3 pós-lançamento
- Taxa de conversão ≥ 3% (clique → compra)
- NPS ≥ 50 após 90 dias
- MRR USD 1.000 no mês 9

## Restrições e Decisões

- Frontend responsivo via browser (sem app mobile nativo)
- Fora de escopo v1: análise de vídeo, marketplace de usados, coaching, wearables, outros esportes, painel B2B
- Anti-bot: proxies rotativos via Firecrawl; negociar APIs com varejistas
- Compliance: GDPR/CCPA básico (consentimento cookies, política de privacidade)
- CI/CD via GitHub Actions; cobertura de testes ≥ 80% no pipeline

## Contexto de Negócio

Receita via comissões de afiliados (10-40% por venda). Lançamento beta no mês 7. SEO como canal de crescimento orgânico (SSR com Next.js + Schema.org). Varejistas-alvo: PickleballCentral, Fromuth Pickleball, JustPaddles, Amazon.
