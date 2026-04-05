# Requirements: PickleIQ v1.6 — UI Redesign (Design Review Implementation)

**Defined:** 2026-04-05
**Core Value:** Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs
**Design review source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`

## Context

A comprehensive design review evaluated 9 HTML mockup variants across 3 screens (Home, Catalog, Chat). Three winning variants were selected with hybrid enhancements. The approved combination maximizes funnel conversion for the "intermediário analítico" persona while remaining accessible to beginners.

**Winning combination:**
- Home: C (Quiz-Forward) + data credibility stats from A
- Catalog: A (Comparison Table) + product images from B + grid toggle
- Chat: B (Sidebar Companion) + card-structured responses from C

**6 DESIGN.md changes proposed** by Metis analysis (to be applied as foundation):

| ID | Change | Rationale |
|----|--------|-----------|
| DS-001 | Allow full-dark sections for immersive flows | Chat/terminal/dashboard need continuous dark |
| DS-002 | Add Chat UI section to DESIGN.md | Chat is a core surface, needs patterns |
| DS-003 | Add semantic level colors | Beginner/intermediate/advanced/professional |
| DS-004 | Relax border radius for conversational elements | 8px for chat bubbles, not 2px |
| DS-005 | Add interactive widget patterns section | Quiz cards, carousels, progress indicators |
| DS-006 | Widen max-width for data-dense layouts | 1440px for tables, split-panels |

## v1.6 Requirements

### Design System Foundation

- [ ] **DS-01**: Update DESIGN.md to v3.0 with all 6 proposed changes (DS-001 through DS-006)
- [ ] **DS-02**: Add CSS custom properties for new tokens (--level-beginner, --level-intermediate, --level-advanced, --level-professional, --max-width-data: 1440px, --radius-conversational: 8px)
- [ ] **DS-03**: Add new "Chat Components" section to DESIGN.md (message bubbles, card responses, typing indicator, input area, streaming animation)
- [ ] **DS-04**: Add new "Interactive Widgets" section to DESIGN.md (quiz cards, carousels, progress indicators, toggle switches)
- [ ] **DS-05**: Update "Motion System" section with new patterns (card response enter, quiz card selection ripple, carousel snap)

### Home Screen — Quiz-Forward (Variant C)

- [ ] **HOME-01**: Quiz widget rendered above-the-fold on homepage with interactive pill toggle buttons (level, budget, play style)
- [ ] **HOME-02**: Recommendation card preview shown below quiz — displays sample paddle with image, name, price (JetBrains Mono), specs, and "Ver detalhes" CTA
- [ ] **HOME-03**: Data credibility stats section below quiz — 3 stat cards showing "147 raquetes analisadas", "3 varejistas monitorados", "Preços atualizados diariamente" with JetBrains Mono values
- [ ] **HOME-04**: Feature steps section (light background) with numbered circles, connecting lines, and 3-step process explanation
- [ ] **HOME-05**: Returning visitor support — show "Continue where you left off" or recent recommendations instead of quiz for users who already completed it

### Chat Screen — Sidebar Companion (Variant B)

- [ ] **CHAT-01**: Split-panel layout — 55% left panel (white product card) + 45% right panel (dark chat area)
- [ ] **CHAT-02**: Left panel contains: breadcrumb navigation, product card (image, name, brand, price in JetBrains Mono, specs grid, score badge), "Comprar na loja" CTA button, related paddles horizontal row
- [ ] **CHAT-03**: Right panel contains: chat header with "Assistente IA" + online indicator, scrollable message area, suggested questions, bottom-pinned input area with send button
- [ ] **CHAT-04**: Card-structured AI responses embedded in chat panel — product recommendation cards (image + specs + CTA), comparison mini-tables (2-3 paddles), tip cards (amber accent, informational)
- [ ] **CHAT-05**: User messages right-aligned with lime (#84CC16) left border; AI messages left-aligned with transparent background
- [ ] **CHAT-06**: Responsive: panels stack vertically below 1024px (50/50 height split on mobile)

### Catalog Screen — Comparison Table (Variant A)

- [ ] **CAT-01**: Sticky filter bar with chip filters (MARCA, NÍVEL, PREÇO) — active filters highlighted in lime, results count displayed
- [ ] **CAT-02**: Sortable 9-column comparison table with: product image thumbnail, name, brand, price (JetBrains Mono, data-green), key specs, score badge (green/yellow/red)
- [ ] **CAT-03**: Table/card view toggle — default is table, toggle switches to 3-col visual grid (from Catalog-B variant)
- [ ] **CAT-04**: Sticky bottom selection bar — appears when items selected, shows count + "Comparar N raquetes" CTA
- [ ] **CAT-05**: Score badges with color coding: high (#76b900 bg, white text), medium (#FDE047 bg, black text), low (#B91C1C bg, white text)
- [ ] **CAT-06**: Responsive: table becomes stacked card view on mobile, filter bar collapses vertically

### Cross-Screen Coherence

- [ ] **COH-01**: Consistent navigation bar across all 3 screens — black sticky nav, "PickleIQ" logo with lime accent, uppercase nav links
- [ ] **COH-02**: Consistent CTA style — primary: lime outline on transparent, hover: lime background; secondary: thinner border
- [ ] **COH-03**: Dual funnel flow supported — Home → Chat → Catalog AND Home → Catalog → Chat, with clear navigation paths between screens
- [ ] **COH-04**: Affiliate links use consistent pattern — "Ver no site →" CTA with retailer name, opens in new tab, tracked via existing affiliate system

### Quality Assurance

- [ ] **QA-01**: All existing backend tests pass (174+) with no regressions
- [ ] **QA-02**: All existing frontend tests pass (161+) with no regressions
- [ ] **QA-03**: New component tests for quiz widget, comparison table, sidebar chat, card responses
- [ ] **QA-04**: Manual smoke test: complete quiz → view recommendation → open chat → compare paddles → click affiliate link
- [ ] **QA-05**: AI slop audit passes on all 3 screens — verify against DESIGN.md checklist
- [ ] **QA-06**: Responsive test at 375px (mobile), 768px (tablet), 1440px (desktop) — no layout breaks

## Out of Scope

| Feature | Reason |
|---------|--------|
| v1.5 Production Readiness | Separate milestone — infrastructure, legal, reliability |
| Real product images | Requires scraper re-run — separate effort |
| Clerk auth integration | Not blocking UI redesign |
| Performance optimization | Already addressed in v1.2 |
| New paddle data/scraping | Separate effort |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DS-01..DS-05 | Phase 16 | ⏳ |
| HOME-01..HOME-05 | Phase 17 | ⏳ |
| CHAT-01..CHAT-06 | Phase 18 | ⏳ |
| CAT-01..CAT-06 | Phase 19 | ⏳ |
| COH-01..COH-04 | Phase 19 | ⏳ |
| QA-01..QA-06 | Phase 19 | ⏳ |

**Coverage:**
- v1.6 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-05*
