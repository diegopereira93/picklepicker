# PickleIQ — Project State

**Última atualização:** 2026-03-26
**Status:** Milestone v1.0 started — Ready for Phase 1

## Current Position

- **Milestone:** v1.0 (MVP → Beta Launch)
- **Phase:** 0 (não iniciado)
- **Status:** Defining Phase 1
- **Last activity:** 2026-03-26 — Milestone v1.0 started
- **Next action:** `/gsd:plan-phase 1`

## Completed

- [x] PROJECT.md criado
- [x] config.json criado (YOLO, Standard, git tracking, research, plan-check)
- [x] Pesquisa de domínio concluída (4 áreas: scraping, RAG, frontend, afiliados)
- [x] REQUIREMENTS.md criado (6 fases, 24 plans)
- [x] ROADMAP.md criado
- [x] Git inicializado

## Research Findings — Critical Decisions

1. **Amazon**: usar PA-API (não Firecrawl) — scraping bloqueado
2. **RAG**: raw SDK (sem LangChain/LlamaIndex) — menos latência, mais controle
3. **Chat streaming**: Vercel AI SDK `streamText` + Edge runtime (não Server Actions)
4. **Radar chart**: Recharts com `ssr: false` obrigatório
5. **Clerk**: usar `clerkMiddleware` v5 (não `authMiddleware` deprecado)
6. **E-mail**: Resend (free tier 3K/mês) com React Email
7. **Afiliado prioritário**: Selkirk (~10-15% comissão vs Amazon 3%)
8. **FTC**: disclosure acima do primeiro link em cada página (não apenas footer)
9. **Embedding**: narrativo por raquete (200-400 tokens), metadata estruturada no Pinecone
10. **Latência**: dois estágios — Haiku para perfil (turns 1-3) + Sonnet para recomendação

## Open Questions (não bloqueantes para Phase 1)

- [ ] Confirmar Fromuth affiliate program details
- [ ] Confirmar Selkirk affiliate network (Impact Radius vs ShareASale)
- [ ] Verificar keyword volumes (Ahrefs/Semrush) — antes Phase 5
- [ ] Pricing Firecrawl `/extract` por call — verificar antes Phase 2
- [ ] Amazon PA-API: cobertura de SKUs do catálogo target
