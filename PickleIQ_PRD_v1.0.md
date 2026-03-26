# 🏓 PickleIQ — Product Requirements Document

**Plataforma de Inteligência de Dados & IA para Pickleball**

| Campo | Detalhe |
|---|---|
| Status | v1.0 — Final (CEO + Eng Review Applied) |
| Versão | 1.0 |
| Público-alvo | Equipe de Desenvolvimento |
| Última atualização | 2026-03-26 |

---

## 1. Visão Geral do Produto

### 1.1 Declaração do Problema

O mercado de pickleball cresceu 311% nos últimos três anos, atingindo 19,8 milhões de jogadores nos EUA em 2024. Apesar desse crescimento explosivo, os consumidores enfrentam dois problemas críticos na hora de comprar equipamentos:

- **Complexidade técnica:** Métricas como swingweight, twistweight e composição de materiais são incompreendidas pela maioria dos jogadores, tornando a escolha da raquete confusa e baseada em achismo.
- **Fragmentação de mercado:** Preços e disponibilidade de produtos variam significativamente entre os varejistas online, sem que o consumidor tenha visibilidade centralizada dessas informações.

### 1.2 Solução Proposta (PickleIQ)

A PickleIQ é uma plataforma web que combina monitoramento automatizado de dados de mercado com um agente de IA conversacional para:

- Monitorar em tempo real preços e inventário dos principais varejistas de pickleball usando o Firecrawl.
- Traduzir métricas técnicas de raquetes em benefícios práticos compreensíveis para qualquer jogador.
- Recomendar produtos personalizados via agente RAG (Retrieval-Augmented Generation) baseado no perfil do usuário.
- Gerar receita por meio de links de afiliados contextuais com comissões de 10% a 40% por venda.

### 1.3 Proposta de Valor

| Perspectiva | Valor |
|---|---|
| **Para o Jogador** | Economize tempo e dinheiro: receba recomendações personalizadas de raquetes baseadas no seu nível, estilo de jogo e orçamento, sempre com o melhor preço disponível no mercado. |
| **Para o Negócio** | Canal de afiliação de alta conversão: as recomendações guiadas por IA conectam compradores de alta intenção aos produtos certos, maximizando o click-through e a taxa de conversão. |

---

## 2. Objetivos e Métricas de Sucesso

### 2.1 Objetivos de Negócio

- Gerar receita recorrente por afiliados a partir do mês 7 (lançamento beta).
- Alcançar 500 usuários ativos mensais nos primeiros 3 meses pós-lançamento.
- Atingir taxa de conversão (clique → compra) de pelo menos 3% nos links de afiliados.
- Posicionar-se como referência SEO para termos como "best pickleball paddle for beginners" e "pickleball paddle comparison".

### 2.2 KPIs e Métricas

| KPI | Meta |
|---|---|
| Usuários Ativos (MAU) | 500 no mês 3 \| 2.000 no mês 9 |
| Taxa de Conversão Afiliado | ≥ 3% (clique → compra) |
| Latência do Agente IA | < 3 segundos por resposta |
| Cobertura de Dados | ≥ 500 raquetes indexadas no lançamento |
| Freshness dos Preços | Atualização a cada 24 horas |
| NPS dos Usuários | ≥ 50 após 90 dias de operação |
| Receita Mensal (MRR) | USD 1.000 no mês 9 |

---

## 3. Personas e Casos de Uso

### 3.1 Personas

#### Persona 1 — O Iniciante Entusiasmado

**Perfil:** 35-55 anos, começou a jogar pickleball nos últimos 12 meses, empolgado com o esporte mas perdido na hora de comprar a primeira raquete "de verdade". Renda média-alta. Não entende o que é swingweight ou twistweight.

**Dor principal:** Chega numa loja online e se depara com dezenas de opções técnicas. Não sabe o que importa para o seu jogo. Acaba comprando pela recomendação de um amigo ou pela mais bonita.

**Ganho esperado:** Uma recomendação personalizada em linguagem simples que explique *por que* aquela raquete é certa para ele.

---

#### Persona 2 — O Jogador Intermediário Analítico

**Perfil:** 28-45 anos, joga há 2-4 anos, participa de torneios amadores. Começa a entender as métricas mas quer comparar objetivamente modelos diferentes. Busca reviews técnicos e teme pagar caro por algo que não vai agregar.

**Dor principal:** Passa horas lendo fóruns e reviews dispersos para comparar modelos. Não tem uma fonte única e confiável com dados atualizados de preços.

**Ganho esperado:** Comparativo técnico detalhado com disponibilidade e preço em tempo real.

---

#### Persona 3 — O Gift Buyer

**Perfil:** Familiar ou amigo de um jogador de pickleball querendo dar um presente. Não joga e não entende absolutamente nada do esporte. Orçamento definido.

**Dor principal:** Total desorientação. Vai no Google e não sabe por onde começar.

**Ganho esperado:** Interface simples onde descreve o perfil do presenteado e recebe uma sugestão direta com link de compra.

---

### 3.2 User Stories Prioritizadas

| ID | Como... | Quero... | Para... | Prioridade |
|---|---|---|---|---|
| US-01 | Jogador iniciante | descrever meu nível e estilo de jogo em linguagem simples | receber uma recomendação de raquete personalizada sem precisar entender jargões técnicos | **P0** |
| US-02 | Qualquer usuário | ver o preço atual de uma raquete nos principais varejistas | comprar pelo menor preço disponível sem pesquisar manualmente | **P0** |
| US-03 | Jogador intermediário | comparar duas ou mais raquetes lado a lado com métricas técnicas traduzidas | tomar uma decisão embasada em dados objetivos | **P0** |
| US-04 | Qualquer usuário | receber alertas quando o preço de uma raquete de interesse cair | aproveitar a melhor oferta no momento certo | **P1** |
| US-05 | Gift buyer | descrever o perfil de quem vai receber o presente e meu orçamento | receber sugestões adequadas com link de compra imediato | **P1** |
| US-06 | Jogador avançado | acessar dados históricos de variação de preço de um produto | identificar o melhor momento de compra com base em tendências | **P2** |

---

## 4. Arquitetura Técnica

### 4.1 Visão Geral

A plataforma é composta por três camadas principais desacopladas, cada uma escalável independentemente:

- **Camada de Dados** — scraping, normalização e armazenamento
- **Camada de IA** — RAG + LLM para recomendação personalizada
- **Camada de Apresentação** — frontend Next.js + API de afiliados

### 4.2 Stack Tecnológico

| Componente | Tecnologia |
|---|---|
| Scraping de Dados | Firecrawl API |
| Orquestração de Pipeline | Python + Prefect (MVP) → Airflow (escala) |
| Banco de Dados Vetorial | Pinecone (managed) ou Weaviate (self-hosted) |
| Banco Relacional | PostgreSQL |
| LLM Principal | Claude 3.5 Sonnet via Anthropic API |
| Embeddings | OpenAI text-embedding-3-small ou Cohere embed-v3 |
| Backend API | Python + FastAPI |
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Autenticação | Clerk ou NextAuth.js |
| Hospedagem Backend | Railway / Render (MVP) → AWS ECS (escala) |
| Hospedagem Frontend | Vercel |
| Observabilidade LLM | Langfuse |
| Afiliados | PickleballCentral, Amazon Associates, Selkirk Affiliate Program |

### 4.3 Fluxo de Dados

#### Ciclo de Ingestão (Batch — a cada 24h)

```
Firecrawl
   └─> Extrai: preço, inventário, specs dos varejistas-alvo
         └─> Pipeline Python (normalização + deduplicação)
               ├─> PostgreSQL (histórico de preços)
               └─> Banco Vetorial (embeddings de specs + reviews)
```

#### Ciclo de Consulta (Real-time — por requisição)

```
Usuário (chat no Next.js)
   └─> FastAPI
         └─> Módulo RAG
               ├─> Busca semântica no banco vetorial
               └─> Contexto + query → Claude (LLM)
                     └─> Resposta em linguagem natural
                           + Cards de produto com preço atual
                           + Links de afiliado contextuais
```

### 4.4 Módulo de Tradução de Métricas

Este é o **diferencial central** da plataforma. O agente traduz métricas técnicas em linguagem de benefícios:

| Métrica | Valor Técnico | Tradução para o Usuário |
|---|---|---|
| Swingweight | < 100 (baixo) | Raquete mais ágil — ideal para reações rápidas na rede |
| Swingweight | > 120 (alto) | Mais potência nos groundstrokes — ideal para fundo de quadra |
| Twistweight | < 6 (baixo) | Exige precisão de contato — para jogadores experientes |
| Twistweight | > 7 (alto) | Sweet spot ampliado — perdoa erros leves de posicionamento |
| Núcleo | 13mm (fino) | Mais potência e resposta viva — para jogadores agressivos |
| Núcleo | 16mm (espesso) | Mais controle e absorção — indicado para iniciantes |
| Face | Carbono T700 | Alta durabilidade com spin consistente — material premium padrão |
| Face | Fibra de vidro | Toque mais suave e forgiving — ótimo para iniciantes |

---

## 5. Funcionalidades por Fase

### Fase 1 — Pipeline de Dados (Meses 1-3)

#### F1.1 — Scraping Automatizado com Firecrawl

- Crawlers para os varejistas-alvo: PickleballCentral, Fromuth Pickleball, JustPaddles, Amazon (categoria pickleball).
- Extrair: nome do produto, SKU, preço, disponibilidade, imagem, URL.
- Extrair specs técnicas: swingweight, twistweight, peso, grip, espessura do núcleo, material da face.
- Frequência: execução a cada 24h via cron job.
- Tratamento de erros: retry automático + alertas por e-mail em caso de falha persistente.

#### F1.2 — Banco de Dados e Pipeline

- Schema PostgreSQL: tabelas `products`, `price_history`, `retailers`, `paddle_specs`.
- Banco vetorial: embeddings de specs + descrições para consulta semântica.
- API interna FastAPI com endpoints `GET /products` e `GET /products/{id}/prices`.

---

### Fase 2 — Agente de IA (Meses 4-6)

#### F2.1 — Agente RAG de Recomendação

- Interface de chat conversacional no frontend.
- Onboarding: agente coleta nível do jogador, estilo de jogo, orçamento e preferências físicas.
- RAG: busca semântica nos embeddings + contexto de preço/inventário atual.
- LLM gera resposta em linguagem natural com justificativa personalizada.
- Máximo de 3 recomendações por consulta, ordenadas por melhor custo-benefício.

#### F2.2 — Cards de Produto com Afiliados

- Cada recomendação exibe: imagem, nome, métricas traduzidas em bullets simples, menor preço encontrado, botão de compra com link de afiliado.
- Indicador visual de disponibilidade: 🟢 in-stock / 🟡 poucas unidades / 🔴 out-of-stock.
- Se produto estiver out-of-stock, o agente sugere alternativa disponível automaticamente.

#### F2.3 — Página de Comparação de Raquetes

- Seleção de 2-3 raquetes para comparação side-by-side.
- Tabela comparativa com métricas técnicas + tradução em linguagem simples.
- Gráfico radar: Potência, Controle, Manobrabilidade, Sweet Spot, Custo-Benefício.

---

### Fase 3 — Lançamento e Growth (Meses 7-9)

#### F3.1 — Alertas de Preço

- Usuário favorita um produto e define um preço-alvo.
- Sistema envia e-mail/push quando o preço atingir ou cair abaixo do alvo.

#### F3.2 — SEO e Páginas de Conteúdo

- Páginas de review geradas automaticamente por produto (SSR com Next.js para SEO).
- Dados estruturados Schema.org/Product para rich snippets no Google.
- Blog com artigos educativos sobre métricas de raquetes.

#### F3.3 — Histórico de Preços

- Gráfico de linha com variação de preço dos últimos 90/180 dias por produto.
- Indicador: "Bom momento para comprar" baseado na análise do histórico.

---

### Fase 4 — Expansão (Meses 10+)

- Expansão do catálogo: bolas, redes, calçados, vestuário.
- Analytics avançado: tendências de mercado e preferências de consumidores.
- Painel B2B para fabricantes e varejistas (avaliar modelo pago).
- Refinamento contínuo do agente com base no feedback dos usuários.

---

## 6. Roadmap

| Fase | Período | Entregáveis Chave | Status |
|---|---|---|---|
| Fase 1 | Mês 1-3 | Setup Firecrawl, pipeline Python, PostgreSQL, banco vetorial, API FastAPI | Planejado |
| Fase 2 | Mês 4-6 | Agente RAG, chat (Next.js), cards com afiliados, comparador de raquetes | Planejado |
| Fase 3 | Mês 7-9 | Lançamento beta, alertas de preço, SEO/páginas de review, histórico de preços | Planejado |
| Fase 4 | Mês 10+ | Expansão de catálogo, analytics avançado, parcerias B2B | Planejado |

---

## 7. Requisitos Não-Funcionais

| Requisito | Especificação |
|---|---|
| Performance | Resposta do agente < 3s (P95). Carregamento de página < 2s (LCP). |
| Disponibilidade | 99,5% de uptime no frontend. Pipeline tolera até 1h de downtime/dia. |
| Escalabilidade | Suportar 10.000 usuários simultâneos. Banco vetorial para 1M+ embeddings. |
| Segurança | HTTPS em todas as rotas. Chaves de API via env vars. Rate limiting na API pública. |
| Conformidade | GDPR/CCPA básico: consentimento de cookies, política de privacidade, opção de exclusão. |
| Observabilidade | Logs estruturados. Traces de LLM via Langfuse. Alertas de falha de scraping. |
| Manutenibilidade | Testes unitários no pipeline (cobertura ≥ 80%). CI/CD via GitHub Actions. |

---

## 8. Fora de Escopo (v1.0)

- Aplicativo mobile nativo (iOS/Android) — frontend será responsivo via browser.
- Análise de vídeo de jogo para recomendação baseada em biomecânica.
- Marketplace próprio de venda de equipamentos usados.
- Coaching ou conteúdo de treinamento (tutoriais, aulas).
- Integração com wearables ou sensores de raquete.
- Expansão para outros esportes de raquete (tênis, padel).
- Painel B2B para fabricantes/varejistas — avaliar na Fase 4.

---

## 9. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Varejistas bloquearem o scraping (anti-bot) | 🔴 Alto | Proxies rotativos via Firecrawl; priorizar varejistas com APIs públicas; negociar parcerias de dados. |
| Dados de specs técnicas inconsistentes ou ausentes | 🟡 Médio | Curadoria manual para as top 100 raquetes; contribuições da comunidade com moderação. |
| Alta latência do agente LLM (> 3s) | 🟡 Médio | Streaming de resposta; cache para queries frequentes; otimizar documentos recuperados no RAG. |
| Baixa taxa de conversão nos links de afiliados | 🔴 Alto | A/B testing nos CTAs; foco em produtos com alta intenção de compra (price drop alerts). |
| Concorrentes lançarem solução similar | 🟡 Médio | Velocidade de execução; moat via qualidade dos dados e comunidade engajada. |

---

## 10. Próximos Passos para o Desenvolvimento

### Semana 1-2: Fundação

- [ ] Criar repositório GitHub com estrutura monorepo (`backend/` + `frontend/`).
- [ ] Configurar ambiente de desenvolvimento com Docker Compose (PostgreSQL + Redis).
- [ ] Implementar o primeiro crawler Firecrawl para PickleballCentral como prova de conceito.
- [ ] Definir e criar o schema do banco de dados PostgreSQL.

### Semana 3-4: Pipeline Completo

- [ ] Expandir crawlers para os 4 varejistas prioritários.
- [ ] Implementar pipeline de normalização e ingestão de dados.
- [ ] Setup do banco vetorial (Pinecone) com embeddings iniciais.
- [ ] API FastAPI com endpoints `GET /products` e `GET /products/{id}/prices`.

### Semana 5-8: Agente de IA

- [ ] Implementar o módulo RAG com LangChain ou LlamaIndex.
- [ ] Desenvolver o sistema de prompt engineering para tradução de métricas.
- [ ] Criar interface de chat com Next.js e integrar com a API.
- [ ] Implementar geração de links de afiliados e cards de produto.

### Semana 9-12: Polimento e Lançamento Beta

- [ ] Testes de carga e otimização de performance.
- [ ] Implementar SEO básico e páginas de produto server-side rendered.
- [ ] Deploy em produção (Vercel + Railway).
- [ ] Lançamento beta para grupo de 50 jogadores de pickleball para coleta de feedback.

---

*PickleIQ PRD v1.0 — Para uso interno e desenvolvimento*
