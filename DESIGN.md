# PickleIQ — Design System

**Version:** 1.0 (established during Phase 4 design review, 2026-03-29)
**Type:** APP UI — task-focused, data-dense, utility language

---

## Brand Identity

**Product:** PickleIQ — Brazilian pickleball AI advisor
**Market:** Brazil (PT-BR), all skill levels from beginners to competitive
**Voice:** Utility-first, sport-appropriate, not corporate or generic

**Landing page H1:** "Encontre a raquete ideal para o seu jogo"
**Value prop:** IA que analisa specs, preços e avaliações para recomendar a raquete certa para você.

---

## Color System

Override shadcn/ui defaults in `frontend/src/styles/globals.css`:

```css
/* PickleIQ brand palette — sport-appropriate */
--primary: #84CC16;           /* lime-500: pickleball yellow-green */
--primary-foreground: #0F172A; /* near-black for text on lime */
--accent: #FCD34D;            /* amber-300: paddle face/ball color */
--accent-foreground: #0F172A;

/* Neutral base — keep shadcn defaults */
/* --background, --foreground, --border, --card: unchanged */
```

**Contrast rule:** `--primary` (#84CC16) on white = 2.7:1 — fails WCAG AA.
- ✅ Use lime-500 on dark backgrounds only
- ✅ Use lime-500 for large text (H1, H2) where 3:1 is acceptable
- ✅ Use `--primary-foreground` (#0F172A) as button text on lime backgrounds
- ❌ Never use lime-500 as small body text on white

---

## Typography

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| H1 | 64px / 40px mobile | bold (700) | Landing page headline only |
| H2 | 28px | semibold (600) | Quiz questions, section headings |
| H3 | 20px | semibold (600) | Card headings, product names |
| Body | 16px | regular (400) | Paragraphs, descriptions |
| Small/Label | 14px | medium (500) | Step indicators, metadata, captions |
| Micro | 12px | regular (400) | Tooltips, legal, timestamps |

**Font:** Inter (installed via Next.js font optimization)
**Fallback:** system-ui, -apple-system, sans-serif

**PT-BR truncation rules:**
- Card labels: max 24 chars
- Card descriptions: max 48 chars
- Toast messages: max 60 chars
- Button text: max 20 chars

---

## Screen Hierarchy

### Landing Page
```
H1: "Encontre a raquete ideal para o seu jogo"  (sport-first)
H2: "IA que analisa specs, preços e avaliações..."
CTA: [ COMEÇAR QUIZ → ]  (primary, full-width mobile)
Secondary: link to /compare (below the fold)
```
Layout: single column, max-w-2xl centered on desktop. No hero image — headline IS the hero.

### Quiz (all 3 steps)
```
"1 de 3"  (step indicator, small, secondary color)
H2: Question text
[Card] [Card]         ← 2-col on tablet+, full-width on mobile
[Card] [Card]
● ○ ○               ← dot progress indicator
← Voltar            ← text link, not a button
```
Pattern: large selection cards, **auto-advance on selection** (no "Próximo" button).

### Quiz → Chat Bridge
```
"Seu perfil: [Nível] · [Estilo] · [Orçamento]"
"Encontrando as melhores raquetes para você..."
[spinner]
```
Duration: 1-2 seconds, then auto-redirect to chat.

### Chat Widget
```
[PickleIQ avatar]  AI message text streaming...     (left-aligned)
                              User message          (right-aligned)
[PickleIQ avatar]  Here are my recommendations:

  +---------------------------+      +---------------------------+
  | [img] Selkirk Luxx Control|      | [img] Joola Ben Johns     |
  |       R$ 489 · Brazil Store|     |       R$ 529 · Drop Shot  |
  |                           |      |                           |
  | Por que essa raquete?     |      | Por que essa raquete?     |
  | Ideal para iniciantes...  |      | Excelente controle para.. |
  |                           |      |                           |
  | [   VER NO SITE →   ]   |      | [   VER NO SITE →   ]   |
  +---------------------------+      +---------------------------+

[_________________________________] [ Enviar ]  ← bottom-pinned input
```
Product cards: max 3 per response, stacked vertically on mobile.

### Comparison Page
```
[ Buscar raquetes...                    🔍 ]
[ Selkirk Luxx × ]  [ Joola Ben × ]  [ + Adicionar ]  ← disabled at 3

| Atributo       | Selkirk Luxx | Joola Ben |
| Preço          | R$ 489       | R$ 529    |
| Swing Weight   | 82           | 87        |
| ...            | ...          | ...       |

[ Ver gráfico radar ▼ ]  ← accordion, hidden by default on mobile
[RadarChart — Potência/Controle/Toque/Swing Weight/Peso/Equilíbrio]
```

---

## Product Card

The primary revenue component. Trust-first design.

```
+-------------------------------+
| [paddle image 80×80]          |
| Brand + Model name            |
| R$ price · Retailer name      |
|                               |
| Por que essa raquete?         |
| [1-line reason from AI]       |
|                               |
| [     VER NO SITE →     ]    |  target="_blank" rel="noopener"
+-------------------------------+
```

**Fallback reason** (if SSE metadata lacks reason field): "Recomendada para o seu perfil de jogo."
**Image fallback:** paddle icon placeholder (not broken image)

---

## Interaction States (summary)

See Phase 4 PLAN.md for full state table. Key states:

| Scenario | Treatment |
|----------|-----------|
| Chat SSE error mid-stream | Keep partial text + inline "⚠️ Erro ao carregar. [Tentar novamente]" |
| Comparison: 0 search results | 🏓 "Nenhuma raquete encontrada para '[query]'" + search tips |
| Comparison: 3/3 paddles | 4th add button disabled + "Máximo 3 raquetes" tooltip |
| Admin queue empty | 🎉 "Nenhum item na fila de revisão" |
| Product card image fail | Paddle icon placeholder |

---

## Responsive Breakpoints

| Viewport | Class | Layout |
|----------|-------|--------|
| Mobile | < 640px | Single column, full-width cards, bottom-pinned chat input |
| Tablet | 640–1024px | Quiz cards 2-col grid, horizontal scroll on comparison table |
| Desktop | > 1024px | max-w-2xl centered, full comparison table |

---

## Accessibility

- Touch targets: minimum 44×44px
- Quiz cards: `role="radio"`, `aria-checked`, `aria-label` includes full option text
- Chat message list: `role="log"`, `aria-live="polite"`
- Affiliate CTAs: `aria-label="Ver [Paddle Name] no site [Retailer]"` (not "VER NO SITE")
- Keyboard navigation: tab order follows visual order on all screens

---

## AI Slop Avoidance Checklist

Verify before any UI ship:
- [ ] No 3-column feature grid (icon + bold title + 2-line description × 3)
- [ ] No icons in colored circles as decoration
- [ ] No centered-everything layout (left-align body copy)
- [ ] No "Welcome to..." / "Your all-in-one solution" copy
- [ ] No decorative blobs or wavy SVG dividers
- [ ] No purple/violet gradient backgrounds
- [ ] Cards earn existence — comparison and product cards ARE the interaction

---

## Decisions Log

| Decision | Choice | Date |
|----------|--------|------|
| Quiz UI pattern | Large selection cards, auto-advance | 2026-03-29 |
| Landing H1 direction | Sport-first | 2026-03-29 |
| Product card trust element | "Por que essa raquete?" + AI reason | 2026-03-29 |
| Chat streaming error | Inline retry below partial response | 2026-03-29 |
| RadarChart axes | 6 hardcoded: Potência/Controle/Toque/Swing Weight/Peso/Equilíbrio | 2026-03-29 |
| Quiz persistence | URL params (?skill=&style=&budget=) | 2026-03-29 |
| Comparison max paddles | 3 | 2026-03-29 |
| Affiliate link behavior | new tab (target="_blank" rel="noopener") | 2026-03-29 |
| Primary brand color | #84CC16 lime-500 (sport-appropriate) | 2026-03-29 |
| Font | Inter (Geist unavailable in Next.js 14.2) | 2026-03-28 |
