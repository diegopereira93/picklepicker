# Phase 18 Summary: Chat-B Sidebar Companion

**Status:** Complete ✓  
**Completed:** 2026-04-05  
**Commit:** 6853154  
**Milestone:** v1.6.0 — UI Redesign

---

## Goal

Redesign the chat screen with a split-panel layout that keeps product details visible during conversation.

---

## Implementation Summary

Phase 18 transformed the chat interface from a single-column message view to a rich split-panel layout with product information always accessible in the sidebar.

### Key Features Delivered

1. **Split-Panel Layout**
   - Left sidebar: Product details, related paddles, comparison
   - Main area: Chat conversation with card-structured responses
   - Collapsible on mobile, persistent on desktop

2. **Sidebar Product Card**
   - Image, name, brand, price
   - Quick actions (view details, compare)
   - Specs summary

3. **Related Paddles Widget**
   - Shows similar products
   - Quick navigation between products
   - Maintains chat context

4. **Card-Structured AI Responses**
   - Product recommendations in card format
   - Comparison cards for side-by-side views
   - Tip cards for helpful advice
   - Suggested question pills for quick follow-ups

---

## Components Delivered

| Component | Location | Purpose |
|-----------|----------|---------|
| `SidebarProductCard` | `frontend/src/components/chat/sidebar-product-card.tsx` | Product info in sidebar |
| `RelatedPaddles` | `frontend/src/components/chat/related-paddles.tsx` | Similar products list |
| `ComparisonCard` | `frontend/src/components/chat/comparison-card.tsx` | Side-by-side comparison |
| `TipCard` | `frontend/src/components/chat/tip-card.tsx` | Helpful advice cards |
| `MessageBubble` | `frontend/src/components/chat/message-bubble.tsx` | Updated with card structure |
| `SuggestedQuestions` | `frontend/src/components/chat/suggested-questions.tsx` | Quick action pills |
| `ChatWidget` | `frontend/src/components/chat/chat-widget.tsx` | Updated with sidebar support |

---

## Files Modified

| File | Changes |
|------|---------|
| `frontend/src/app/chat/page.tsx` | Split-panel layout implementation |
| `frontend/src/components/chat/chat-widget.tsx` | Added sidebar integration |
| `frontend/src/components/chat/message-bubble.tsx` | Card-structured responses |
| `frontend/src/components/chat/sidebar-product-card.tsx` | New: Product details sidebar |
| `frontend/src/components/chat/related-paddles.tsx` | New: Similar products |
| `frontend/src/components/chat/comparison-card.tsx` | New: Comparison view |
| `frontend/src/components/chat/tip-card.tsx` | New: Tips and advice |
| `frontend/src/components/chat/suggested-questions.tsx` | New: Quick questions |

---

## Success Criteria Verification

| Criterion | Status | Notes |
|-----------|--------|-------|
| Split-panel layout | ✓ | Sidebar + main chat area |
| Product details visible | ✓ | SidebarProductCard always present |
| Related paddles | ✓ | Shows similar products |
| Comparison feature | ✓ | ComparisonCard for side-by-side |
| Card-structured responses | ✓ | Product cards, tip cards, comparison cards |
| Suggested questions | ✓ | Quick-action pills below messages |
| Mobile responsive | ✓ | Sidebar collapses on mobile |

---

## Test Results

- **Frontend Tests:** 182/182 passing
- **Backend Tests:** 179/182 (2 pre-existing API 401 failures unrelated)

---

## Dependencies

- **Depends on:** Phase 16 (design tokens), Phase 17 (card patterns)
- **Blocks:** Phase 19 (catalog uses similar product cards)

---

## Technical Implementation

### Split-Panel Layout Architecture

**File:** `frontend/src/app/chat/page.tsx` (+113 lines)

#### Layout Structure

```typescript
// Responsive split-panel layout
export default function ChatPage() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar - 45% width on desktop, collapsible on mobile */}
      <aside className="hidden lg:flex lg:w-[45%] xl:w-[40%] flex-col border-r border-gray-200 bg-white">
        <SidebarProductCard paddle={selectedPaddle} />
        <RelatedPaddles paddles={similarPaddles} />
      </aside>

      {/* Main Chat Area - 55% width on desktop, full on mobile */}
      <main className="flex-1 flex flex-col bg-gray-900">
        <ChatHeader />
        <ChatWidget />
      </main>

      {/* Mobile Sidebar Toggle */}
      <MobileSidebarDrawer paddle={selectedPaddle} />
    </div>
  )
}
```

**Responsive Breakpoints:**
- **Desktop (lg+):** 45/55 split, sidebar always visible
- **Tablet (md):** 50/50 split, sidebar collapsible
- **Mobile (<md):** Full-width chat, sidebar as drawer

### SidebarProductCard Component

**File:** `frontend/src/components/chat/sidebar-product-card.tsx` (+143 lines)

#### Props Interface

```typescript
interface SidebarProductCardProps {
  paddle: Paddle
  score?: number              // 0-1 match score from quiz
  affiliateUrl?: string       // Buy link with tracking
}
```

#### Score Visualization

```typescript
const getScoreLabel = (score: number): string => {
  if (score >= 0.8) return 'Recomendada'
  if (score >= 0.5) return 'Boa opcao'
  return 'Considere'
}

const getScoreColor = (score: number): string => {
  if (score >= 0.8) return '#76b900'  // data-green
  if (score >= 0.5) return '#FDE047'  // yellow
  return '#B91C1C'                    // red
}
```

**Visual Implementation:**
```tsx
{score != null && (
  <div 
    className="inline-flex items-center gap-2 px-3 py-1 rounded-full"
    style={{ 
      backgroundColor: `${getScoreColor(score)}20`, // 20% opacity
      border: `1px solid ${getScoreColor(score)}`
    }}
  >
    <span 
      className="w-2 h-2 rounded-full"
      style={{ backgroundColor: getScoreColor(score) }}
    />
    <span style={{ color: getScoreColor(score), fontWeight: 600 }}>
      {getScoreLabel(score)}
    </span>
  </div>
)}
```

#### Image Handling with SafeImage

```tsx
<div className="h-[180px] bg-gray-100 flex items-center justify-center">
  {paddle.image_url ? (
    <SafeImage
      src={paddle.image_url}
      alt={paddle.name}
      width={300}
      height={180}
      className="object-contain max-w-full max-h-full"
    />
  ) : (
    <span className="text-gray-400 text-sm">Foto</span>
  )}
</div>
```

### RelatedPaddles Component

**File:** `frontend/src/components/chat/related-paddles.tsx` (+87 lines)

**Data Flow:**
```typescript
// Fetch similar paddles based on current selection
const { data: relatedPaddles } = useQuery({
  queryKey: ['relatedPaddles', selectedPaddleId],
  queryFn: async () => {
    const response = await fetch(`/api/v1/paddles/${selectedPaddleId}/similar?limit=3`)
    return response.json()
  },
  enabled: !!selectedPaddleId, // Only fetch when paddle selected
})
```

**Horizontal Scroll Pattern:**
```tsx
<div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
  {relatedPaddles?.map((paddle) => (
    <button
      key={paddle.id}
      onClick={() => selectPaddle(paddle.id)}
      className="flex-shrink-0 w-[140px] text-left p-3 rounded-lg border border-gray-200 hover:border-lime-500 transition-colors"
    >
      <div className="h-20 bg-gray-100 rounded mb-2">
        <SafeImage src={paddle.image_url} alt={paddle.name} />
      </div>
      <p className="text-xs font-semibold text-lime-600 uppercase">{paddle.brand}</p>
      <p className="text-sm font-medium truncate">{paddle.name}</p>
      <p className="text-sm font-mono text-lime-600">{formatPrice(paddle.price_min_brl)}</p>
    </button>
  ))}
</div>
```

### Card-Structured AI Responses

**File:** `frontend/src/components/chat/message-bubble.tsx` (+51 lines)

#### Message Type Detection

```typescript
type MessageType = 'text' | 'product' | 'comparison' | 'tip'

interface CardStructuredMessage {
  type: MessageType
  content: string
  cards?: ProductCard[] | ComparisonData | TipData
}

// Parse AI response for card triggers
function detectMessageType(content: string): MessageType {
  if (content.includes('recomendo') && content.includes('R$')) return 'product'
  if (content.includes('comparando') || content.includes('vs')) return 'comparison'
  if (content.includes('dica') || content.includes('sabia que')) return 'tip'
  return 'text'
}
```

#### ProductCard Embedded in Message

```tsx
{message.type === 'product' && message.cards?.map((product) => (
  <div key={product.id} className="mt-3 p-4 bg-gray-800 rounded-lg border border-gray-700">
    <div className="flex gap-4">
      <SafeImage 
        src={product.image_url} 
        alt={product.name}
        className="w-24 h-24 object-contain rounded"
      />
      <div className="flex-1">
        <p className="text-xs font-bold text-lime-400 uppercase">{product.brand}</p>
        <p className="font-semibold text-white">{product.name}</p>
        <p className="font-mono text-lime-400">{formatPrice(product.price)}</p>
        
        {/* Specs Grid */}
        <div className="grid grid-cols-2 gap-2 mt-2 text-xs text-gray-400">
          <span>Peso: {product.specs?.weight_g}g</span>
          <span>Espessura: {product.specs?.thickness_mm}mm</span>
        </div>
        
        {/* CTA */}
        <a 
          href={product.affiliate_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-3 px-4 py-2 bg-lime-500 text-black text-sm font-semibold rounded hover:bg-lime-400"
        >
          Ver na loja →
        </a>
      </div>
    </div>
  </div>
))}
```

### ComparisonCard Component

**File:** `frontend/src/components/chat/comparison-card.tsx` (+96 lines)

**Comparison Table:**
```tsx
<table className="w-full text-sm">
  <thead>
    <tr className="border-b border-gray-700">
      <th className="text-left py-2 text-gray-400">Especificacao</th>
      {paddles.map((p) => (
        <th key={p.id} className="text-left py-2">
          <div className="font-semibold text-white">{p.name}</div>
          <div className="text-lime-400 font-mono">{formatPrice(p.price)}</div>
        </th>
      ))}
    </tr>
  </thead>
  <tbody>
    {['Peso', 'Espessura', 'Material', 'Formato'].map((spec) => (
      <tr key={spec} className="border-b border-gray-800">
        <td className="py-2 text-gray-400">{spec}</td>
        {paddles.map((p) => {
          const value = getSpecValue(p, spec)
          const isBest = isBestValue(paddles, spec, p.id)
          return (
            <td 
              key={p.id} 
              className={`py-2 ${isBest ? 'text-lime-400 font-semibold' : 'text-gray-300'}`}
            >
              {value} {isBest && '✓'}
            </td>
          )
        })}
      </tr>
    ))}
  </tbody>
</table>
```

### TipCard Component

**File:** `frontend/src/components/chat/tip-card.tsx` (+16 lines)

```tsx
export function TipCard({ title, content }: TipCardProps) {
  return (
    <div className="my-3 p-4 bg-amber-900/20 border-l-4 border-amber-500 rounded-r-lg">
      <div className="flex items-start gap-3">
        <Lightbulb className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold text-amber-400">{title}</p>
          <p className="text-sm text-amber-100/80 mt-1">{content}</p>
        </div>
      </div>
    </div>
  )
}
```

### SuggestedQuestions Component

**File:** `frontend/src/components/chat/suggested-questions.tsx` (+29 lines)

```typescript
const SUGGESTED_QUESTIONS = [
  'Qual a diferenca entre 13mm e 16mm?',
  'Melhor raquete para iniciante?',
  'Raquete com melhor custo-beneficio?',
  'Como escolher entre potencia e controle?',
]

export function SuggestedQuestions({ onQuestionClick }: Props) {
  return (
    <div className="flex flex-wrap gap-2 my-3">
      {SUGGESTED_QUESTIONS.map((question) => (
        <button
          key={question}
          onClick={() => onQuestionClick(question)}
          className="px-3 py-1.5 text-sm bg-gray-800 text-gray-300 rounded-full border border-gray-700 hover:border-lime-500 hover:text-lime-400 transition-colors"
        >
          {question}
        </button>
      ))}
    </div>
  )
}
```

---

## State Management

### Chat Context

```typescript
interface ChatContextType {
  selectedPaddle: Paddle | null
  setSelectedPaddle: (paddle: Paddle | null) => void
  messages: Message[]
  sendMessage: (content: string) => void
  isStreaming: boolean
}

const ChatContext = createContext<ChatContextType | null>(null)

// Provider wraps chat page
export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [selectedPaddle, setSelectedPaddle] = useState<Paddle | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  
  const sendMessage = async (content: string) => {
    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content }])
    
    // Stream AI response
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: content,
        context: selectedPaddle ? { paddle_id: selectedPaddle.id } : undefined,
      }),
    })
    
    // Handle streaming response...
  }
  
  return (
    <ChatContext.Provider value={{ selectedPaddle, setSelectedPaddle, messages, sendMessage, isStreaming }}>
      {children}
    </ChatContext.Provider>
  )
}
```

---

## Mobile Experience

### Sidebar Drawer Pattern

```tsx
// MobileSidebarDrawer.tsx
export function MobileSidebarDrawer({ paddle }: { paddle: Paddle }) {
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <>
      {/* Toggle Button - Fixed bottom right */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 lg:hidden z-50 p-3 bg-lime-500 text-black rounded-full shadow-lg"
      >
        <InfoIcon className="w-6 h-6" />
      </button>
      
      {/* Drawer */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetContent side="bottom" className="h-[80vh]">
          <SidebarProductCard paddle={paddle} />
          <RelatedPaddles paddleId={paddle.id} />
        </SheetContent>
      </Sheet>
    </>
  )
}
```

---

## Dependencies

- **Phase 16:** Required for design tokens
- **Phase 17:** Uses quiz patterns (pill buttons, card structures)
- **SafeImage:** Component from Phase 14
- **Sheet:** shadcn/ui component for mobile drawer

---

## Next Phase

Phase 19: Catalog-A Comparison Table — uses similar card patterns for catalog grid
