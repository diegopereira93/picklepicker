# PickleIQ — AI Assistant Configuration

## Project Overview

Pickleball paddle intelligence platform for Brazilian market. Scrapes prices/specs from BR retailers, runs a RAG AI agent for personalized recommendations, and monetizes via affiliate links.

**Current Version:** See VERSION file
**Stack:** Python 3.12 + FastAPI (backend) | Next.js 14 App Router (frontend) | PostgreSQL + pgvector (DB)

## Workflow

Type `ultrawork` to activate the full agent orchestration engine. Describe what you want and the agents handle exploration, planning, delegation, and verification.

### Available Commands

| Command | Purpose |
|---------|---------|
| `/ship` | Ship PR and merge process |
| `/review` | Pre-landing code review |
| `/investigate` | Systematic debugging with root cause analysis |
| `/qa` | Full QA testing workflow |
| `/browse` | Headless browser for QA and testing |
| `/design-review` | Visual audit against DESIGN.md |
| `/canary` | Post-deploy canary monitoring |

### Agent Delegation

| Category | Use For |
|----------|---------|
| `visual-engineering` | Frontend, UI/UX, design — load skill `frontend-ui-ux` |
| `deep` | Autonomous backend/pipeline work |
| `ultrabrain` | Hard architecture decisions |
| `quick` | Single-file changes, typos, config |
| `writing` | Documentation, prose |

### Subagents

- **explore** — Codebase grep for finding patterns (always background)
- **librarian** — External docs/API reference lookup (always background)
- **oracle** — Architecture/debugging consultation (expensive, use sparingly)
- **plan** — Task decomposition and parallel execution planning

## Design System

Always read DESIGN.md before making any visual or UI decisions.
All font choices, colors, spacing, and aesthetic direction are defined there.
Do not deviate without explicit user approval.
In QA mode, flag any code that doesn't match DESIGN.md.

**Key decisions (DESIGN.md v2.0):**
- Hybrid Modern Sports Tech aesthetic (sport energy + data credibility)
- Lime (#84CC16) on dark backgrounds only — never on white
- Green (#76b900) for data elements: charts, tables, section labels
- JetBrains Mono for specs/tables — signals "we take data seriously"
- 2px border radius everywhere — sharp corners = precision
- Alternating dark/light sections
- Section labels: 14px, weight 700, uppercase, green accent
