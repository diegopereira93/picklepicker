# Chat Page Specification

## 1. ROUTE & GOAL

- **Route path:** `/chat`
- **Primary conversion goal:** AI-powered paddle recommendations via conversation → affiliate click
- **Entry points:**
  - Quiz completion redirect (`/quiz` → `/chat`)
  - Direct navigation (returning users with existing profile)
  - Landing page "AI Chat" feature card (optional deep link)
- **Exit points:**
  - Affiliate links (primary desired exit - monetization)
  - `/catalog` (browse without AI)
  - `/compare` (from product cards in chat)
  - `/quiz` (via "Edit Profile" button)

---

## 2. LAYOUT STRUCTURE

### Desktop (1280px+)
- **Container max-width:** 1280px, full width (no centering)
- **Layout:** Two-column flex
  - Left sidebar: 280px fixed width, `flex-shrink-0`
  - Main chat area: `flex-1`, remaining width
- **Height:** Full viewport `h-screen`, overflow hidden
- **Horizontal padding:** Main chat area has `px-8`, sidebar has `px-4`

### Tablet (768px-1279px)
- **Layout:** Same two-column structure
- **Sidebar:** 240px width (slightly narrower)
- **Main chat area:** `flex-1`
- **Horizontal padding:** Main chat `px-6`, sidebar `px-4`

### Mobile (375px-767px)
- **Layout:** Single column (sidebar hidden by default)
- **Sidebar:** Collapsible drawer/sheet, slides in from left
- **Toggle:** Hamburger menu button (top-left) opens sidebar
- **Main chat area:** Full width, `px-4`
- **Height:** Full viewport `h-screen`, overflow hidden

---

## 3. SECTIONS (top to bottom)

### Sidebar Section

**Component(s):** `ChatSidebar`, `ProfileChips`, `ActionButton`

**Content requirements:**
- Header: "Your Profile"
  - Font: Source Sans 3 `font-semibold`, `text-sm`, `text-muted-foreground`
  - Uppercase `tracking-wide`
- Profile chips (4 chips, horizontal wrap):
  - Level: e.g., "Intermediário"
  - Style: e.g., "Power"
  - Budget: e.g., "R$ 200-400"
  - Priority: e.g., "Controle"
  - Each chip: `bg-surface`, `text-xs`, `px-2 py-1`, rounded-md
- "Edit Profile" button:
  - Icon: `Lucide.Pencil` (16px)
  - Text: "Edit Profile"
  - Link: `/quiz`
  - Style: Ghost button, full width
- "Start Over" button:
  - Icon: `Lucide.RefreshCw` (16px)
  - Text: "Start Over"
  - Action: Clears localStorage profile, redirects to `/quiz`
  - Style: Ghost button, full width, `text-destructive`

**Padding:**
- Section internal: `p-4`
- Chip gap: `gap-2`
- Button vertical gap: `mt-4`

**Background:**
- `bg-surface` (slightly lighter than main chat)
- Border right: `border-r border-border`

---

### Main Chat Area - Header

**Component(s):** `ChatHeader`

**Content requirements:**
- Title: "PickleIQ Assistant"
  - Font: Bebas Neue, `text-xl`, `text-foreground`
- Subtitle: "Ask me anything about paddles"
  - Font: Source Sans 3, `text-xs`, `text-muted-foreground`

**Padding:**
- Vertical: `py-4`
- Horizontal: `px-8` (desktop), `px-4` (mobile)

**Background:**
- `bg-background` (inherits from page)
- Border bottom: `border-b border-border`

---

### Main Chat Area - Messages

**Component(s):** `ChatMessages`, `ChatMessage` (×N), `ProductCard` (embedded), `TypingIndicator`

**Content requirements:**
- Messages scroll vertically, newest at bottom
- AI message (left-aligned):
  - Avatar: Neon green circle (32px), "IQ" text in white (JetBrains Mono, 12px)
  - Bubble: `bg-surface`, rounded-2xl (top-left corner square), max-width 70%
  - Content: Source Sans 3, `text-sm`, `text-foreground`
  - Embedded ProductCard: Compact mode, inline below text
- User message (right-aligned):
  - Bubble: `bg-lime-500`, rounded-2xl (top-right corner square), max-width 70%
  - Content: Source Sans 3, `text-sm`, `text-lime-950` (dark text for contrast)
- Typing indicator (when AI is responding):
  - 3 pulsing dots in neon green
  - Animation: Sequential pulse, 600ms cycle

**Padding:**
- Message vertical gap: `gap-4`
- Bubble internal: `p-4`
- Avatar gap: `gap-3`

**Background:**
- `bg-background` (scrollable area)

---

### Main Chat Area - Input

**Component(s):** `ChatInput`, `QuickPromptChips`, `Textarea`, `SendButton`

**Content requirements:**
- Quick prompt chips (horizontal scroll, above input):
  - "Show options under $100"
  - "Best for beginners"
  - "Compare top 2 picks"
  - "What's the lightest paddle?"
  - Each chip: `bg-surface`, `text-xs`, `px-3 py-1.5`, rounded-full, hover `bg-lime-500/10`
- Textarea:
  - Placeholder: "Ask me anything..."
  - Font: Source Sans 3, `text-sm`
  - Auto-resize: 1-4 lines max
  - No border, transparent background
- Send button:
  - Icon: `Lucide.Send` (20px)
  - Disabled: When textarea is empty
  - Style: Neon green circle (40px), icon centered

**Padding:**
- Section internal: `p-4`
- Chip gap: `gap-2`
- Input gap: `gap-3`

**Background:**
- `bg-elevated` (card-style)
- Border top: `border-t border-border`

---

## 4. COMPONENT TREE

```
ChatPage
├── PageContainer (flex, h-screen, overflow-hidden)
│   ├── ChatSidebar (280px, flex-shrink-0, bg-surface, border-r)
│   │   ├── SidebarHeader
│   │   │   └── Title (Source Sans 3, xs, semibold, muted, uppercase)
│   │   ├── ProfileChips (flex-wrap, gap-2)
│   │   │   └── ProfileChip[] (×4)
│   │   │       └── Label (text-xs, px-2 py-1, rounded-md)
│   │   ├── EditProfileButton
│   │   │   ├── Lucide.Pencil (16px)
│   │   │   └── Text "Edit Profile" → /quiz
│   │   └── StartOverButton
│   │       ├── Lucide.RefreshCw (16px)
│   │       └── Text "Start Over" → clears profile, /quiz
│   └── MainChatArea (flex-1, flex-col, overflow-hidden)
│       ├── ChatHeader
│       │   ├── Title (Bebas Neue, xl)
│       │   └── Subtitle (Source Sans 3, xs, muted)
│       ├── ChatMessages (flex-1, overflow-y-auto, flex-col, gap-4)
│       │   ├── ChatMessage[] (×N)
│       │   │   ├── AI Message (left-aligned)
│       │   │   │   ├── Avatar (lime circle, 32px, "IQ" text)
│       │   │   │   ├── Bubble (bg-surface, rounded-2xl, p-4, max-w-70%)
│       │   │   │   │   ├── Text (Source Sans 3, sm)
│       │   │   │   │   └── ProductCard[] (embedded, compact mode)
│       │   │   └── User Message (right-aligned)
│       │   │       └── Bubble (bg-lime-500, rounded-2xl, p-4, max-w-70%)
│       │   │           └── Text (Source Sans 3, sm, lime-950)
│       │   └── TypingIndicator (when AI responding)
│       │       └── PulsingDots (×3, sequential pulse)
│       └── ChatInput (bg-elevated, border-t, p-4)
│           ├── QuickPromptChips (horizontal-scroll, gap-2, mb-3)
│           │   └── QuickPromptChip[] (×4)
│           │       └── Text (text-xs, px-3 py-1.5, rounded-full)
│           ├── TextareaContainer (flex, items-end, gap-3)
│           │   ├── Textarea (flex-1, auto-resize, 1-4 lines)
│           │   └── SendButton (lime circle, 40px, disabled when empty)
│           │       └── Lucide.Send (20px)
```

**Props:**
- `ChatSidebar`: `profile`, `onEditProfile`, `onStartOver`
- `ProfileChips`: `profile` (level, style, budget, priority)
- `ChatMessage`: `role` ('ai' | 'user'), `content`, `products[]`, `timestamp`
- `ProductCard`: `paddle`, `mode` ('compact' | 'full'), `onCompare`, `onAlert`
- `TypingIndicator`: `isTyping`
- `ChatInput`: `onSend`, `onQuickPrompt`
- `QuickPromptChip`: `prompt`, `onClick`

**State management:**
- **Local state (ChatPage component):**
  - `messages`: Array<{ role, content, products[], timestamp }>
  - `isTyping`: boolean
  - `inputValue`: string
  - `sidebarOpen`: boolean (mobile only)
- **Persisted state:**
  - Profile from localStorage: `pickleiq_player_profile`
  - Chat history: Optional localStorage sync (not required for MVP)
- **Global state:** None required

---

## 5. INTERACTIONS

### User actions available
| Element | Action | Result |
|---------|--------|--------|
| Textarea | Type | Enable send button when non-empty |
| Textarea | Enter (without Shift) | Send message |
| Textarea | Shift+Enter | New line |
| Send button | Click | Send message, clear textarea |
| Quick prompt chip | Click | Insert prompt text into textarea (or send directly, TBD) |
| Embedded ProductCard | Click "Details" | Navigate to `/catalog/[slug]` |
| Embedded ProductCard | Click "Compare" | Add to compare, navigate to `/compare` if 2+ items |
| Embedded ProductCard | Click "Alert" | Toggle price alert for this paddle |
| Edit Profile button | Click | Navigate to `/quiz` |
| Start Over button | Click | Clear localStorage, confirm dialog, navigate to `/quiz` |
| Sidebar toggle (mobile) | Click | Open/close sidebar drawer |

### Animation/transition specs
- **Message appear:** Slide up 20px + fade-in, 200ms ease-out
- **Typing indicator:** Sequential pulse, 600ms cycle per dot
- **Streaming text:** Typewriter effect, 20ms per character
- **Sidebar (mobile):** Slide in from left, 300ms ease-out
- **Send button hover:** Scale 1 → 1.05, 150ms ease-out

### Loading state behavior
- **Initial page load:**
  - Show welcome message from AI: "Hey! I'm your PickleIQ assistant. I analyzed your profile: [level, style, budget]. What are you looking for in a paddle?"
  - Profile chips load from localStorage (instant)
  - No skeleton needed (chat is empty initially)
- **During AI response:**
  - Typing indicator appears
  - Streaming text: First chunk appears immediately, then typewriter effect
- **Product card loading:** Skeleton (image placeholder, text lines) embedded in AI message

### Error state behavior
- **API error (chat endpoint):**
  - Show error message in AI bubble: "Hmm, I'm having trouble connecting. Try again?"
  - Retry button inline
- **Profile not found:**
  - Show prompt: "I don't see your quiz profile. Want to take the quiz first?"
  - CTA button: "Take Quiz" → `/quiz`

### Empty state behavior
- **No messages yet:**
  - Welcome message auto-injected on first load (see above)
  - No user messages initially (AI always speaks first)

---

## 6. DATA REQUIREMENTS

### API endpoints called
| Endpoint | Method | Purpose | Caching |
|----------|--------|---------|---------|
| `POST /api/chat` | POST | Send message, receive AI response + product recommendations | No caching (real-time) |
| `GET /api/profile` | GET | Fetch profile from DB (fallback if localStorage missing) | No caching |

### Data shape expected
```typescript
// Request
interface ChatRequest {
  message: string;
  profile?: PlayerProfile; // From localStorage
  conversationHistory: { role: 'user' | 'ai', content: string }[];
}

// Response (streaming SSE)
interface ChatResponse {
  content: string;           // AI response text
  products?: Paddle[];       // Recommended paddles (0-3)
  conversationId: string;    // For session continuity
}

// Profile (from localStorage or DB)
interface PlayerProfile {
  level: 'beginner' | 'intermediate' | 'advanced' | 'pro';
  style: 'power' | 'control' | 'spin' | 'all-court';
  priority: 'power' | 'control' | 'spin' | 'price';
  budget: 'under-200' | '200-400' | '400-600' | '600+';
  weight: 'light' | 'medium' | 'heavy';
  location: 'norte' | 'nordeste' | 'centro-oeste' | 'sudeste' | 'sul';
  targetPaddle: string | null;
}
```

### Loading strategy
- **Initial page load:** SSR for shell, CSR for chat content
- **Welcome message:** Injected client-side on mount (uses profile from localStorage)
- **Chat responses:** Streaming SSE (server-sent events)
  - First chunk: ~500ms
  - Full response: 2-5s depending on complexity
- **Product cards:** Included in chat response (no separate API call)

---

## 7. ACCESSIBILITY

### ARIA labels needed
- Chat messages container: `aria-label="Chat messages"`, `aria-live="polite"`
- Individual messages: `role="article"`, `aria-labelledby="message-{id}"`
- AI avatar: `aria-label="PickleIQ Assistant"`
- Typing indicator: `aria-label="Assistant is typing"`, `aria-live="polite"`
- Textarea: `aria-label="Type your message"`, `aria-multiline="true"`
- Send button: `aria-label="Send message"`
- Quick prompt chips: `aria-label="Quick prompt: [prompt text]"`
- Sidebar toggle (mobile): `aria-label="Toggle sidebar"`, `aria-expanded={sidebarOpen}`
- Profile chips: `aria-label="Your profile: [level], [style], [budget], [priority]"`

### Keyboard navigation flow
1. Tab order (desktop): Sidebar buttons → Chat messages (not focusable) → Quick prompts → Textarea → Send button
2. Tab order (mobile): Sidebar toggle → Textarea → Send button (sidebar hidden by default)
3. Arrow keys: Navigate chat messages (Up/Down), announce sender + content
4. Enter in textarea: Send message (Shift+Enter for new line)
5. Escape: Close sidebar (mobile)

### Screen reader announcements
- **On new message:** "[AI/User]: [Message content]" (aria-live polite)
- **On typing start:** "Assistant is typing..." (aria-live polite)
- **On product card insertion:** "Product recommendation: [Paddle name], [Price]"
- **On error:** "Error: [Error message]. Retry button available."
- **Headings hierarchy:**
  - H1: "PickleIQ Assistant"
  - H2: "Your Profile" (sidebar)
  - No subheadings in chat (flat message list)
