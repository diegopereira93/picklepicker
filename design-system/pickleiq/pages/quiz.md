# Quiz Page Specification

## 1. ROUTE & GOAL

- **Route path:** `/quiz`
- **Primary conversion goal:** Capture 7-question player profile → redirect to `/chat`
- **Entry points:**
  - Landing page CTA (`/` → `/quiz`)
  - Direct navigation (returning users restarting quiz)
  - Chat page "Edit Profile" button
- **Exit points:**
  - `/chat` (primary desired exit after completion)
  - Browser back button (abandon quiz)
  - `/` (if user clicks logo/home)

---

## 2. LAYOUT STRUCTURE

### Desktop (1280px+)
- **Container max-width:** 512px (`max-w-lg`), centered with `mx-auto`
- **Layout:** Full-screen wizard, vertically centered content
- **Horizontal padding:** 16px (`px-4`)
- **Vertical alignment:** Flex column, `justify-center`, min-height `min-h-screen`
- **Progress bar:** Fixed at top, full width of container

### Tablet (768px-1279px)
- **Container max-width:** 512px (`max-w-lg`)
- **Horizontal padding:** 24px (`px-6`)
- **Vertical alignment:** Same as desktop
- **Progress bar:** Same as desktop

### Mobile (375px-767px)
- **Container max-width:** 100% (fluid)
- **Horizontal padding:** 16px (`px-4`)
- **Vertical alignment:** Same as desktop, but content starts lower to accommodate mobile browser chrome
- **Progress bar:** Thinner (4px height vs 6px)

---

## 3. SECTIONS (top to bottom)

### Section 1: Progress Bar

**Component(s):** `QuizProgress`

**Content requirements:**
- Text: "Step X of 7"
  - Font: JetBrains Mono
  - Size: `text-xs`
  - Color: `text-muted-foreground`
- Progress track: Full width, 6px height, rounded-full, `bg-surface`
- Progress fill: `bg-lime-500`, animated width transition
- Percentage: Optional, shown on hover (desktop only)

**Padding:**
- Vertical spacing below: `mb-8`

**Background:**
- Transparent (inherits from page)

---

### Section 2: Question Content

**Component(s):** `QuestionCard`, `QuestionTitle`, `OptionGrid`

**Content requirements:**
- Question title: Varies by step (see question list below)
  - Font: Source Sans 3
  - Size: `text-2xl` (desktop), `text-xl` (mobile)
  - Weight: `font-semibold`
  - Color: `text-foreground`
  - Line height: `leading-tight`

**Padding:**
- Vertical spacing below: `mb-8`

**Background:**
- Transparent (inherits from page)

---

### Section 3: Option Cards

**Component(s):** `OptionCard` (×4), `LucideIcon`

**Content requirements:**
- 4 option cards in 2×2 grid
- Each option contains:
  - Icon: Lucide icon, 32px, `text-lime-400`
  - Label: Source Sans 3 `font-medium`, `text-base`, `text-foreground`
  - Description (optional): Source Sans 3 `text-sm`, `text-muted-foreground`, max 1 line

**Card states:**
- Default: `bg-surface`, `border border-border`
- Hover: `border-lime-500`, subtle glow
- Selected: `bg-lime-500/10`, `border-lime-500`, checkmark icon appears
- Focus: 2px neon green ring

**Padding:**
- Grid gap: `gap-4`
- Card internal: `p-4`

**Background:**
- `bg-surface` (card background)

---

### Section 4: Navigation Buttons

**Component(s):** `QuizNavigation`

**Content requirements:**
- Back button: "Back" (hidden on step 1)
  - Style: Ghost button, `text-muted-foreground`
  - Disabled: Opacity 50% if on step 1
- Next button: "Next" (steps 1-6) or "See My Paddles" (step 7)
  - Style: Primary button, neon green background
  - Disabled: Until an option is selected

**Padding:**
- Vertical spacing above: `mt-12`
- Button gap: `gap-4`

**Background:**
- Transparent (inherits from page)

---

## 4. COMPONENT TREE

```
QuizPage
├── PageContainer (max-w-lg, mx-auto, px-4/6, min-h-screen, flex-col, justify-center)
│   ├── QuizProgress
│   │   ├── StepIndicator (JetBrains Mono, xs, muted)
│   │   ├── ProgressTrack (surface bg, 6px height, rounded-full)
│   │   └── ProgressFill (lime-500, animated width)
│   ├── QuestionCard
│   │   └── QuestionTitle (Source Sans 3, 2xl, semibold)
│   ├── OptionGrid (2×2, gap-4)
│   │   └── OptionCard[] (×4)
│   │       ├── IconContainer
│   │       │   └── LucideIcon (32px, lime-400)
│   │       ├── Label (Source Sans 3, base, medium)
│   │       └── Description (optional, Source Sans 3, sm, muted)
│   └── QuizNavigation
│       ├── BackButton (ghost, hidden on step 1)
│       └── NextButton (primary, disabled until selection)
```

**Props:**
- `QuizProgress`: `currentStep`, `totalSteps`
- `QuestionCard`: `question`, `stepNumber`
- `OptionCard`: `icon`, `label`, `description`, `selected`, `onSelect`
- `QuizNavigation`: `currentStep`, `totalSteps`, `hasSelection`, `onBack`, `onNext`

**State management:**
- **Local state (QuizPage component):**
  - `currentStep`: number (1-7)
  - `answers`: Record<questionKey, string>
  - `hasSelection`: boolean (computed)
- **Persisted state:**
  - On each answer: Save to localStorage as `pickleiq_player_profile`
  - Shape: `{ level, style, priority, budget, weight, location, targetPaddle }`
- **Global state:** None required (profile passed to chat via localStorage)

---

## 5. INTERACTIONS

### User actions available
| Element | Action | Result |
|---------|--------|--------|
| Option card | Click | Select option, highlight card, enable Next button |
| Option card | Keyboard (Enter/Space) | Same as click when focused |
| Next button | Click | Advance to next step OR complete quiz (step 7) |
| Back button | Click | Return to previous step |
| Browser back | PopState | Navigate back, preserve answers in localStorage |

### Animation/transition specs
- **Slide transition:** Horizontal slide 300ms ease-in-out
  - Enter: `translate-x-full` → `translate-x-0`, `opacity-0` → `opacity-100`
  - Exit: `translate-x-0` → `translate-x--full`, `opacity-100` → `opacity-0`
- **Progress bar fill:** Width transition 300ms ease-out
- **Card selection:** Border color 150ms ease-out, background 150ms ease-out
- **Checkmark appearance:** Scale 0 → 1 over 200ms, bounce easing

### Loading state behavior
- **Initial page load:** No loading (quiz is client-side only)
- **Step transition:** Instant (no API calls between steps)
- **Final submission:** "Analyzing your profile..." screen with pulse animation (2s)
  - Pulse: Neon green circle, scale 1 → 1.1 → 1, infinite loop
  - Text: Source Sans 3, `text-lg`, `text-muted-foreground`, fade-in

### Error state behavior
- **localStorage unavailable:** Continue quiz in memory, warn user on completion that profile won't persist
- **Navigation failure (step 7 → chat):** Retry once, show error toast with "Try again" button

### Empty state behavior
- Not applicable (quiz always has questions)

---

## 6. DATA REQUIREMENTS

### API endpoints called
- **None during quiz flow** (fully client-side)
- **On completion (step 7):** POST to `/api/profile` (optional, for analytics)
  - Payload: `{ level, style, priority, budget, weight, location, targetPaddle }`
  - Response: Ignored (fire-and-forget)

### Data shape expected
```typescript
interface PlayerProfile {
  level: 'beginner' | 'intermediate' | 'advanced' | 'pro';
  style: 'power' | 'control' | 'spin' | 'all-court';
  priority: 'power' | 'control' | 'spin' | 'price';
  budget: 'under-200' | '200-400' | '400-600' | '600+';
  weight: 'light' | 'medium' | 'heavy';
  location: 'norte' | 'nordeste' | 'centro-oeste' | 'sudeste' | 'sul';
  targetPaddle: string | null; // Optional: specific paddle they're considering
}
```

### Loading strategy
- **Quiz flow:** CSR (fully client-side)
- **Profile persistence:** localStorage sync on each answer
- **Final redirect:** CSR navigation after 2s "analyzing" delay

---

## 7. ACCESSIBILITY

### ARIA labels needed
- Progress bar: `aria-label="Quiz progress: step X of 7"`, `aria-valuemin="1"`, `aria-valuemax="7"`, `aria-valuenow={currentStep}`
- Option cards: `role="radio"`, `aria-checked={selected}`, `aria-labelledby="option-{index}-label"`
- Option group: `role="radiogroup"`, `aria-labelledby="question-title"`
- Next button: Dynamic label "Next question" or "See My Paddles"
- Back button: `aria-label="Go back to previous question"`

### Keyboard navigation flow
1. Tab order: Back button (if visible) → Option 1 → Option 2 → Option 3 → Option 4 → Next button
2. Arrow keys within radiogroup: Up/Down/Left/Right navigate between options
3. Enter/Space: Select focused option
4. Tab from last option: Focus Next button
5. Shift+Tab from first option: Focus Back button (if visible)

### Screen reader announcements
- **On step change:** "Step X of 7: [Question title]"
- **On option select:** "[Option label] selected"
- **On final submission:** "Analyzing your profile..." (announced once)
- **Headings hierarchy:**
  - H1: Question title (changes per step)
  - No subheadings (flat structure)

---

## APPENDIX: QUESTION CONTENT

| Step | Key | Question Title | Options (icon, label, description) |
|------|-----|----------------|-----------------------------------|
| 1 | `level` | "Qual é o seu nível de jogo?" | 1. `Lucide.Trophy` / "Iniciante" / "Começando agora" <br> 2. `Lucide.Target` / "Intermediário" / "Jogo há 6-12 meses" <br> 3. `Lucide.Zap` / "Avançado" / "Competitivo, 1+ ano" <br> 4. `Lucide.Crown` / "Profissional" / "Torneios, ranking" |
| 2 | `style` | "Como você descreveria seu estilo?" | 1. `Lucide.Flame` / "Power" / "Batidas fortes, fundo de quadra" <br> 2. `Lucide.Crosshair` / "Control" / "Precisão, colocação" <br> 3. `Lucide.Sparkles` / "Spin" / "Efeitos, jogadas técnicas" <br> 4. `Lucide.Scale` / "All-Court" / "Equilibrado, versátil" |
| 3 | `priority` | "O que mais importa pra você?" | 1. `Lucide.Flame` / "Potência" / "Maximizar suas batidas" <br> 2. `Lucide.Crosshair` / "Controle" / "Precisão em cada jogada" <br> 3. `Lucide.Sparkles` / "Spin" / "Efeitos e curvas" <br> 4. `Lucide.Coins` / "Preço" / "Melhor custo-benefício" |
| 4 | `budget` | "Qual seu orçamento?" | 1. `Lucide.Wallet` / "Até R$ 200" / "Entrada, bom preço" <br> 2. `Lucide.Banknote` / "R$ 200 - 400" / "Intermediário" <br> 3. `Lucide.PiggyBank` / "R$ 400 - 600" / "Premium" <br> 4. `Lucide.Gem` / "R$ 600+" / "Top de linha" |
| 5 | `weight` | "Preferência de peso?" | 1. `Lucide.Feather` / "Leve (≤ 240g)" / "Maneio rápido, menos fadiga" <br> 2. `Lucide.Scale` / "Médio (240-260g)" / "Equilíbrio perfeito" <br> 3. `Lucide.Barbell` / "Pesado (≥ 260g)" / "Mais potência, mais estabilidade" <br> 4. `Lucide.HelpCircle` / "Não sei" / "Me recomende" |
| 6 | `location` | "Onde você mora?" | 1. `Lucide.MapPin` / "Norte" / "AM, PA, AC, etc." <br> 2. `Lucide.MapPin` / "Nordeste" / "BA, PE, CE, etc." <br> 3. `Lucide.MapPin` / "Centro-Oeste" / "DF, MT, GO, MS" <br> 4. `Lucide.MapPin` / "Sudeste" / "SP, RJ, MG, ES" <br> 5. `Lucide.MapPin` / "Sul" / "RS, SC, PR" |
| 7 | `targetPaddle` | "Tem algum modelo em mente?" | 1. `Lucide.Search` / "Não, me surpreenda" / "Confio na IA" <br> 2. `Lucide.Heart` / "Sim, já tenho um" / "Quero comparar" <br> 3. `Lucide.Shuffle` / "Quero explorar" / "Ver várias opções" <br> 4. `Lucide.TrendingUp` / "Quero upgrade" / "Melhorar meu atual" |

**Note:** Step 7 option 2 triggers a follow-up text input (optional, not required for MVP) to capture specific paddle name.
