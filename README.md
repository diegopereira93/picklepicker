# 🏓 PickleIQ

**Plataforma de Inteligência de Dados & IA para Pickleball**

PickleIQ é uma plataforma web que combina monitoramento automatizado de preços de mercado com um agente de IA conversacional para ajudar jogadores de pickleball a escolherem raquetes de forma informada.

---

## O Problema

O mercado de pickleball cresceu **311% em 3 anos**, com 19,8 milhões de jogadores nos EUA. Mas compradores enfrentam dois desafios críticos:

1. **Métricas técnicas incompreensíveis** — Swingweight, twistweight, composição de materiais. A maioria dos jogadores não entende o que significa.
2. **Fragmentação de mercado** — Preços e disponibilidade variam significativamente entre varejistas, sem visibilidade centralizada.

## A Solução

PickleIQ resolve ambos os problemas:

- **Monitoramento de preços em tempo real** — Scraping automatizado de múltiplos varejistas brasileiros (Brazil Pickleball Store, Drop Shot Brasil, Mercado Livre).
- **Agente de IA conversacional** — Um assistente que traduz métricas técnicas em linguagem simples e recomenda raquetes personalizadas baseado no perfil do jogador.
- **Comparador visual** — Compare lado a lado com métricas traduzidas e um gráfico radar intuitivo.
- **Monetização por afiliados** — Links contextuais que geram receita (10-40% de comissão por venda).

---

## Para Quem É

| Persona | Necessidade | Solução |
|---------|-----------|----------|
| **Iniciante entusiasmado** (35-55 anos) | Quer comprar a "raquete certa" mas não entende o jargão técnico | Recomendação personalizada em linguagem simples |
| **Jogador intermediário analítico** (28-45 anos) | Quer comparar objetivamente modelos diferentes com dados atualizados | Comparativo técnico + preços em tempo real |
| **Gift buyer** | Quer dar uma raquete como presente mas não sabe por onde começar | Descreve o perfil, recebe sugestão direta com link de compra |

---

## Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| **Scraping** | Firecrawl API |
| **Pipeline** | Python + Prefect |
| **Banco Relacional** | PostgreSQL (Supabase em produção) |
| **Banco Vetorial** | Pinecone (RAG embeddings) |
| **LLM** | Claude 3.5 Sonnet (Anthropic API) |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Backend API** | Python + FastAPI |
| **Frontend** | Next.js 14 (App Router) + Tailwind CSS |
| **Autenticação** | Clerk (Phase 5+) |
| **Hospedagem Backend** | Railway (MVP) |
| **Hospedagem Frontend** | Vercel |
| **Observabilidade LLM** | Langfuse |

---

## Roadmap de Desenvolvimento

A plataforma é desenvolvida em **8 fases** com duração estimada de **14 semanas** até o lançamento beta:

| Fase | Objetivo | Duração | Status |
|------|----------|---------|--------|
| **1** | Ambiente dev + primeiro crawler funcional | 2 sem | ✅ Concluído (2026-03-26) |
| **2** | Pipeline completo + scraping de todos os varejistas | 3 sem | ✅ Concluído (2026-03-26) |
| **3** | Agente RAG de recomendação com latência < 3s | 2 sem | ✅ Concluído (2026-03-27) |
| **4** | Frontend: chat, comparador, tracking de afiliados | 2 sem | ✅ Concluído (2026-03-27) |
| **5** | Autenticação Clerk, SEO, alertas de preço, blog, admin | 2 sem | ✅ Concluído (2026-03-28) |
| **6** | Deploy produção, beta launch com 50 usuários | 1 sem | ✅ Concluído (2026-03-29) |
| **7** | E2E testing & validação dos scrapers — 101 testes, 90% cobertura | 1 sem | ✅ Concluído (2026-03-29) |
| **8** | Navigation UX fixes — catalog cards, hero CTA, header nav | 1 sem | ✅ Concluído (2026-03-29) |

**Beta launch:** Fases 1-8 concluídas — pronto para Milestone 2

---

## Métricas de Sucesso

- **500 MAU** no mês 3 pós-lançamento
- **Taxa de conversão ≥ 3%** (clique → compra)
- **NPS ≥ 50** após 90 dias de operação
- **MRR USD 1.000** no mês 9
- **P95 latência agente < 3 segundos**

---

## Documentação

- **[PickleIQ_PRD_v1.0.md](./PickleIQ_PRD_v1.0.md)** — Produto completo: problema, solução, personas, user stories, requisitos técnicos, roadmap
- **[.planning/PROJECT.md](./.planning/PROJECT.md)** — Resumo executivo: o que estamos construindo, por que, para quem, decisões
- **[.planning/milestones/v1.0-REQUIREMENTS.md](./.planning/milestones/v1.0-REQUIREMENTS.md)** — Requisitos técnicos detalhados por fase (v1.0, 8 fases)
- **[.planning/ROADMAP.md](./.planning/ROADMAP.md)** — Roadmap executivo com timeline, KPIs e backlog
- **[.planning/STATE.md](./.planning/STATE.md)** — Estado atual do projeto, decisões de pesquisa, questões abertas
- **[TODOS.md](./TODOS.md)** — 7 itens deferred do eng review (T1-T7): infraestrutura, monitoring, legal, testes
- **[CLAUDE.md](./CLAUDE.md)** — Configuração Claude Code: skills gstack disponíveis
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** — Setup de desenvolvimento, CI/CD, workflow de contribuição
- **[DESIGN.md](./DESIGN.md)** — Design system e diretrizes visuais do projeto

---

## Como Começar

### Pré-requisitos
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 16 (via Docker Compose)

### Setup Desenvolvimento
```bash
# Clone e prepare o ambiente
git clone <repo>
cd picklepicker

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Setup Docker Compose (PostgreSQL)
cd ..
docker-compose up -d

# Copie .env.example para .env e preencha credenciais
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Rodar Localmente
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Backend: http://localhost:8000
Frontend: http://localhost:3000

---

## Estrutura do Repositório

```
picklepicker/
├── backend/              # FastAPI + pipeline
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   └── models/
│   ├── pipeline/        # Scripts de scraping e processamento
│   ├── evals/           # Resultados de eval gate + testes de carga
│   └── requirements.txt
├── frontend/             # Next.js
│   ├── app/
│   ├── components/
│   └── public/
├── .github/workflows/    # GitHub Actions (scraping schedule)
├── .planning/            # Artefatos de planejamento GSD
│   ├── PROJECT.md
│   ├── REQUIREMENTS.md
│   ├── ROADMAP.md
│   └── STATE.md
├── docker-compose.yml
├── .gitignore
├── CHANGELOG.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── DESIGN.md
├── PickleIQ_PRD_v1.0.md
├── TODOS.md
└── VERSION
```

---

## Próximas Ações

Fases 1-8 concluídas — projeto em Milestone 2 (v1.1).
Veja [.planning/ROADMAP.md](./.planning/ROADMAP.md) para o roadmap completo.

---

## Contato & Suporte

- **Documentação interna:** Veja [CLAUDE.md](./CLAUDE.md) para skills gstack disponíveis
- **Deferred work:** Veja [TODOS.md](./TODOS.md) para 7 itens do eng review

---

**Status do Projeto:** v0.2.4.0 — Fases 1-8 concluídas, Milestone 2 em progresso
**Última atualização:** 2026-03-29
