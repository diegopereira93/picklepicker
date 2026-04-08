# Phase 16: DESIGN.md v3.0 + Foundation

**Status:** Ready for execution
**Milestone:** v1.6.0 — UI Redesign
**Dependencies:** None (foundation phase — Phases 17, 18, 19 depend on this)
**Created:** 2026-04-05
**Updated:** 2026-04-05

## Goal

Update the design system (DESIGN.md + globals.css) to support all 3 winning design variants from the 9-variant design review. This phase is the **foundation** — all subsequent phases (17=Home-C, 18=Chat-B, 19=Catalog-A) depend on it.

## Context

**Design Review Source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`

**Winning combination:**
- Home: C (Quiz-Forward) + data stats from A
- Catalog: A (Comparison Table) + product images from B + grid toggle
- Chat: B (Sidebar Companion) + card responses from C

**Current State (DESIGN.md v4.0 — Warm Guide):**
- DESIGN.md updated April 5, 2026 to v4.0 Warm Guide aesthetic
- Has Chat Components section (message bubbles, card responses, typing indicator, input area)
- Has Interactive Widgets section (quiz pills, toggle switch, progress dots, carousel arrows, filter chips)
- Already has conversational border radius (radius-sm: 8px, radius-md: 12px, radius-lg: 16px, radius-xl: 24px)
- Already documents `max-width: 1440px` for data-dense layouts
- Has semantic colors (beginner: #22C55E, intermediate: #F59E0B, advanced: #EF4444)
- Uses Tailwind CSS tokens (`wg-*` classes) instead of `hy-*` CSS custom properties
- `design-tokens.css` contains only dark mode setup; Tailwind config handles design tokens

## Requirements Coverage

| Requirement | Tasks | Notes |
|-------------|-------|-------|
| DS-01 | 16.1, 16.2 | DESIGN.md v3.0 with all 6 changes (DS-001 through DS-006) |
| DS-02 | 16.3 | CSS custom properties for all new tokens |
| DS-03 | 16.1 | Chat Components section in DESIGN.md |
| DS-04 | 16.1 | Interactive Widgets section in DESIGN.md |
| DS-05 | 16.4 | Motion System update with new patterns |

## Execution Waves

```
Wave 1 (parallel — no dependencies):
├── 16.1: DESIGN.md v3.0 header + Chat Components section + Interactive Widgets section + semantic level colors
└── 16.2: DESIGN.md layout exceptions + conversational radius + max-width-data + decisions log

Wave 2 (after Wave 1 — depends on DESIGN.md sections being defined):
└── 16.3: globals.css — new CSS custom properties + chat component base styles + widget base styles

Wave 3 (after Wave 2 — depends on CSS properties existing):
└── 16.4: globals.css — motion system keyframes + animation classes

Wave 4 (after Wave 3 — final verification):
└── 16.5: Design system verification — no contradictions, existing components still compliant
```

---

## Task Details

### Task 16.1 — DESIGN.md v3.0: Chat Components + Interactive Widgets + Level Colors

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `DESIGN.md`
**Dependencies:** None
**Requirements:** DS-01, DS-03, DS-04

**Changes:**

1. Update version header from `2.0` to `3.0`:

```
**Version:** 3.0 (Hybrid Modern Sports Tech — UI Redesign, 2026-04-05)
```

2. Add v3.0 changelog entry after the v2.0 changelog block:

```
**Changelog v3.0:**
- Added Chat Components section (message bubbles, card responses, typing indicator, input area)
- Added Interactive Widgets section (quiz cards with selected state, toggle switches, progress indicators, carousels)
- Added semantic level colors (--level-beginner, --level-intermediate, --level-advanced, --level-professional)
- Added conversational border radius (8px) for chat bubbles and tip cards
- Added --max-width-data: 1440px for data-dense layouts
- Allowed full-dark sections exception for immersive flows (chat, dashboards)
- Updated Motion System with 4 new animation patterns
```

3. Add **Semantic Level Colors** subsection inside Color System (after Semantic Colors, before Interactive Colors):

```css
### Skill Level Colors

--level-beginner: #4CAF50;       /* green — Iniciante */
--level-intermediate: #FCD34D;   /* amber — Intermediário */
--level-advanced: #F44336;       /* red — Avançado */
--level-professional: #8B5CF6;   /* violet — Profissional/Elite */
```

**Usage:** Skill level badges on product cards, filter chips in catalog, quiz profile display. Background color with white text (beginner/advanced) or dark text (intermediate). Violet reserved for professional/elite only.

4. Add new **Chat Components** section after the existing Components section (before Motion System). Must document:

- **Message Bubbles:** User messages (right-aligned, lime #84CC16 left border, dark #111 background, `--radius-conversational: 8px`). AI messages (left-aligned, transparent background, max-width 80% of chat container).
- **Card Responses:** ProductCard (image + specs + CTA embedded in AI message), ComparisonCard (mini-table with 2-3 paddles, green highlights), TipCard (amber #FCD34D left border, informational content). Max 1 card type per AI response.
- **Typing Indicator:** 3 animated dots (8px each, `--gray-muted` color, staggered 150ms animation), left-aligned below last AI message.
- **Input Area:** Bottom-pinned, dark #1a1a1a background, rounded text input (`--radius-conversational: 8px`), lime send button. Suggested question pills above input.
- **Streaming Animation:** Cursor blink (1s infinite, lime color) at end of streaming AI text.

Include CSS code blocks for each pattern, following the same format as existing component docs.

5. Add new **Interactive Widgets** section after Chat Components. Must document:

- **Quiz Pill Toggle Buttons:** Inline selectable pills for quiz options (level, budget, style). Default: `--gray-border` border, transparent bg. Selected: `--sport-primary` (#84CC16) border, `rgba(132, 204, 22, 0.1)` bg, lime box-shadow glow. Text: Inter 14px 500. Padding: 8px 16px. `--radius-conversational: 8px`.
- **Toggle Switch (Table/Card view):** 40x22px track, 18x18px thumb. Off: `--gray-border` track. On: `--sport-primary` track. Smooth 150ms transition. Labels "Tabela" and "Cards" beside toggle.
- **Progress Indicators:** Dot style (8px circles). Active: `--sport-primary` fill. Inactive: `--gray-border` fill. Connected by 2px `--gray-border` line. Used in quiz flow and onboarding.
- **Carousel Arrows:** 36x36px circular buttons, `--gray-border` border, centered chevron icon. Hover: `--sport-primary` border, white bg. `--radius-circle: 50%`.
- **Filter Chips:** Inline selectable chips for catalog filters. Default: transparent bg, `--gray-border` border, Inter 12px 500 uppercase. Active: `--sport-primary` border, `rgba(132, 204, 22, 0.1)` bg, lime text.

Include CSS code blocks for each pattern.

**QA:** Verify DESIGN.md renders correctly as markdown. Verify all new CSS values match existing design tokens where applicable.

---

### Task 16.2 — DESIGN.md: Layout Exceptions + Conversational Radius + Max-Width

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `DESIGN.md`
**Dependencies:** None (parallel with 16.1, but changes different sections)
**Requirements:** DS-01 (DS-001, DS-004, DS-006)

**Changes:**

1. Update **Border Radius** section — add new token after existing tokens:

```css
--radius-conversational: 8px;  /* chat bubbles, tip cards, quiz pills — softer for human feel */
```

Update the "Why 2px?" explanation to note the exception:
```
**Why 2px?** Sharp corners signal precision and data. This is a deliberate choice: "we take specs seriously."

**Exception:** `--radius-conversational: 8px` for chat bubbles, tip cards, and interactive widget elements where a softer edge improves readability and reduces visual fatigue in conversation flows.
```

2. Update **Max Content Width** section — add data-dense token:

```css
/* Default: content pages */
max-width: 1200px;

/* Data-dense: comparison tables, split-panels, dashboards */
max-width: 1440px;
```

Add documentation: "Use `--max-width-data: 1440px` for comparison tables (9+ columns), chat split-panels, and dashboard-style layouts. Default `--max-content-width: 1200px` remains for all other pages."

3. Update **Section Alternation** section — add full-dark exception:

After the existing pattern block, add:
```
**Exception — Full-Dark Sections:**
Chat interfaces, dashboards, and terminal-aesthetic flows may use continuous dark backgrounds instead of alternating. This creates immersion for focused interaction. Apply to: `/chat`, admin panels, data visualization screens. Do NOT apply to marketing pages or product listings.
```

4. Add v3.0 decisions to the **Decisions Log** table at the end of DESIGN.md:

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | 8px conversational radius | Chat bubbles need softness for human feel; 2px feels robotic in conversation |
| 2026-04-05 | 1440px max-width for data layouts | 9-column comparison tables need horizontal space; 1200px forces truncation |
| 2026-04-05 | Full-dark section exception | Chat/terminal flows need immersion; alternation breaks conversational context |
| 2026-04-05 | Semantic level colors | Visual taxonomy for paddle categorization across catalog, chat, and quiz |
| 2026-04-05 | Chat Components + Widgets sections | Core surfaces (chat, quiz, catalog filters) lacked documented patterns |
| 2026-04-05 | Card-structured AI responses | Plain text AI answers aren't scannable; cards make recommendations actionable |

**QA:** Verify no contradictions with v2.0 rules. Verify 2px remains the default radius (8px is the exception, not the replacement).

---

### Task 16.3 — globals.css: New CSS Custom Properties + Chat/Widget Base Styles

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/globals.css`
**Dependencies:** Wave 1 complete (16.1, 16.2 — DESIGN.md must define tokens first)
**Requirements:** DS-02

**Changes:**

1. Add new CSS custom properties in the `:root` block (after existing `--sport-secondary`):

```css
/* v3.0 — Semantic Level Colors */
--level-beginner: #4CAF50;
--level-intermediate: #FCD34D;
--level-advanced: #F44336;
--level-professional: #8B5CF6;

/* v3.0 — Layout Tokens */
--max-width-data: 1440px;

/* v3.0 — Border Radius */
--radius-conversational: 8px;
```

2. Add base chat component styles (new section after existing chat styles). These are base classes that Phase 18 will build upon:

```css
/* v3.0 — Chat Card Responses (base, extended in Phase 18) */
.hy-chat-card {
  border-radius: var(--radius-conversational);
  overflow: hidden;
}

.hy-chat-card-product {
  background: var(--color-near-black);
  border: 1px solid var(--color-gray-border);
}

.hy-chat-card-tip {
  background: rgba(252, 211, 77, 0.08);
  border-left: 3px solid #FCD34D;
}

.hy-chat-card-comparison {
  background: var(--color-near-black);
  border: 1px solid var(--color-gray-border);
}
```

3. Add base widget styles (new section):

```css
/* v3.0 — Interactive Widget Base Styles */
.hy-quiz-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  border: 2px solid var(--color-gray-border);
  border-radius: var(--radius-conversational);
  background: transparent;
  color: var(--color-white);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast, 150ms) var(--ease-move);
}

.hy-quiz-pill:hover {
  border-color: var(--sport-primary);
}

.hy-quiz-pill.selected {
  border-color: var(--sport-primary);
  background: rgba(132, 204, 22, 0.1);
  box-shadow: 0 0 0 1px var(--sport-primary), 0 0 12px rgba(132, 204, 22, 0.15);
}

.hy-toggle-track {
  width: 40px;
  height: 22px;
  border-radius: 11px;
  background: var(--color-gray-border);
  position: relative;
  cursor: pointer;
  transition: background 150ms ease;
}

.hy-toggle-track.active {
  background: var(--sport-primary);
}

.hy-toggle-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: white;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 150ms ease;
}

.hy-toggle-track.active .hy-toggle-thumb {
  transform: translateX(18px);
}

.hy-filter-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  border: 1px solid var(--color-gray-border);
  border-radius: 4px;
  background: transparent;
  color: var(--color-gray-400);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 150ms ease;
}

.hy-filter-chip.active {
  border-color: var(--sport-primary);
  background: rgba(132, 204, 22, 0.1);
  color: var(--sport-primary);
}

.hy-progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-gray-border);
  transition: background 150ms ease;
}

.hy-progress-dot.active {
  background: var(--sport-primary);
}

.hy-carousel-arrow {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--color-gray-border);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 150ms ease;
}

.hy-carousel-arrow:hover {
  border-color: var(--sport-primary);
  background: white;
}
```

**QA:** Verify all new properties reference existing tokens where possible. Verify no conflicts with existing 81 hy-* classes. Run `npx tailwindcss --help` to confirm no Tailwind config changes needed (these are plain CSS, not Tailwind utilities).

---

### Task 16.4 — globals.css: Motion System Updates

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/globals.css`
**Dependencies:** Task 16.3 complete (CSS properties must exist for animations to reference them)
**Requirements:** DS-05

**Changes:**

1. Add 4 new `@keyframes` definitions (after existing `hy-skeleton-shimmer`):

```css
/* v3.0 — Chat Message Enter */
@keyframes hy-chat-message-enter {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* v3.0 — Card Response Enter (slides up + fades in) */
@keyframes hy-card-response-enter {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* v3.0 — Quiz Selection Ripple (lime glow pulse) */
@keyframes hy-quiz-selection-ripple {
  0% {
    box-shadow: 0 0 0 0 rgba(132, 204, 22, 0.4);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(132, 204, 22, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(132, 204, 22, 0);
  }
}

/* v3.0 — Streaming Cursor Blink */
@keyframes hy-streaming-cursor {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}
```

2. Add animation utility classes:

```css
/* v3.0 — Animation Utilities */
.hy-animate-chat-enter {
  animation: hy-chat-message-enter 250ms cubic-bezier(0, 0, 0.2, 1) forwards;
}

.hy-animate-card-enter {
  animation: hy-card-response-enter 300ms cubic-bezier(0, 0, 0.2, 1) forwards;
}

.hy-animate-quiz-ripple {
  animation: hy-quiz-selection-ripple 400ms ease-out;
}

.hy-streaming-cursor::after {
  content: '▊';
  color: var(--sport-primary);
  animation: hy-streaming-cursor 1s linear infinite;
  margin-left: 2px;
}
```

3. Update DESIGN.md Motion System section — add new entries to the Component Patterns subsection:

```
**Card Response Enter:**
```css
@keyframes hy-card-response-enter {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.hy-chat-card { animation: hy-card-response-enter 300ms var(--ease-enter) forwards; }
```

**Quiz Selection Ripple:**
```css
@keyframes hy-quiz-selection-ripple {
  0% { box-shadow: 0 0 0 0 rgba(132, 204, 22, 0.4); }
  70% { box-shadow: 0 0 0 8px rgba(132, 204, 22, 0); }
  100% { box-shadow: 0 0 0 0 rgba(132, 204, 22, 0); }
}

.hy-quiz-pill.selected { animation: hy-quiz-selection-ripple 400ms ease-out; }
```

**Streaming Cursor:**
```css
.hy-streaming-cursor::after {
  content: '▊';
  color: var(--sport-primary);
  animation: hy-streaming-cursor 1s linear infinite;
}
```
```

**QA:** Verify all 4 keyframes render correctly. Verify animation durations match DESIGN.md documentation. Verify no conflicts with existing `hy-skeleton-shimmer`.

---

### Task 16.5 — Design System Verification

**Category:** `quick`
**Skills:** `['frontend-ui-ux']`
**Files:** `DESIGN.md`, `frontend/src/app/globals.css`
**Dependencies:** Tasks 16.1–16.4 all complete
**Requirements:** DS-01 (verification)

**Checks:**

1. **Token Completeness:** Verify all 6 new tokens from DS-002 are defined in BOTH DESIGN.md and globals.css:
   - `--level-beginner` ✅
   - `--level-intermediate` ✅
   - `--level-advanced` ✅
   - `--level-professional` ✅
   - `--max-width-data: 1440px` ✅
   - `--radius-conversational: 8px` ✅

2. **Section Completeness:** Verify DESIGN.md has both new sections:
   - "Chat Components" section with: message bubbles, card responses, typing indicator, input area, streaming animation ✅
   - "Interactive Widgets" section with: quiz pills, toggle switch, progress dots, carousel arrows, filter chips ✅

3. **Motion Completeness:** Verify 4 new motion patterns documented in DESIGN.md AND implemented in globals.css:
   - `hy-chat-message-enter` (250ms) ✅
   - `hy-card-response-enter` (300ms) ✅
   - `hy-quiz-selection-ripple` (400ms) ✅
   - `hy-streaming-cursor` (1s infinite) ✅

4. **Non-Contradiction Check:** Verify existing rules are preserved:
   - 2px remains default radius (8px is exception only) ✅
   - 1200px remains default max-width (1440px is for data layouts only) ✅
   - Lime on dark backgrounds only rule unchanged ✅
   - Alternating dark/light sections remain default (full-dark is exception) ✅
   - Existing components (nav, footer, buttons, product cards) unchanged ✅

5. **Existing Component Compliance:** Spot-check that existing hy-* classes don't break:
   - `.hy-nav` still uses black bg, sticky position ✅
   - `.hy-button-primary` still uses 2px border radius ✅
   - `.hy-product-card` still uses 4px radius ✅
   - `.hy-quiz-card` still works with existing selected state ✅

6. **Frontend Build:** Run `npm run build` in frontend/ to verify no CSS syntax errors.

**QA:** This task produces no code changes — it's a verification gate. If any check fails, fix in the originating task before marking complete.

---

## Success Criteria

1. ✅ DESIGN.md updated to v3.0 with Chat Components and Interactive Widgets sections
2. ✅ All 6 new CSS custom properties defined in globals.css
3. ✅ 4 new motion patterns documented in DESIGN.md and implemented in globals.css
4. ✅ No contradictions with existing v2.0 design system
5. ✅ Existing 81 hy-* classes unaffected
6. ✅ Frontend builds without CSS errors

## Commit Strategy

4 atomic commits (16.5 is verification-only):

1. `docs(design): v3.0 — add Chat Components, Interactive Widgets, semantic level colors`
2. `docs(design): v3.0 — layout exceptions, conversational radius, max-width-data`
3. `style(css): add v3.0 design tokens, chat card bases, widget styles`
4. `style(css): add v3.0 motion system keyframes and animation utilities`
