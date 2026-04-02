'use client'

import type { ChatRecommendation } from '@/types/paddle'
import { ProductCard } from './product-card'

interface MessageBubbleProps {
  role: 'user' | 'assistant'
  content: string
  annotations?: unknown[]
}

function isRecommendationArray(val: unknown): val is ChatRecommendation[] {
  return (
    Array.isArray(val) &&
    val.length > 0 &&
    typeof (val[0] as Record<string, unknown>)?.paddle_id === 'number'
  )
}

function renderText(text: string) {
  return text.split('\n').map((line, i) => (
    <span key={i}>
      {i > 0 && <br />}
      {line}
    </span>
  ))
}

function PickleIQAvatar() {
  return (
    <div
      className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-bold shrink-0"
      aria-hidden="true"
    >
      PI
    </div>
  )
}

export function MessageBubble({ role, content, annotations }: MessageBubbleProps) {
  const isUser = role === 'user'

  // Find any paddle recommendation arrays in annotations
  const recommendations = annotations?.find((a) => isRecommendationArray(a)) as
    | ChatRecommendation[]
    | undefined

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 gap-2`}>
      {/* Avatar for assistant messages per DESIGN.md */}
      {!isUser && <PickleIQAvatar />}

      <div className="max-w-[85%] space-y-3">
        {content && (
          <div
            className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              isUser
                ? 'bg-primary text-primary-foreground rounded-br-sm'
                : 'bg-muted text-foreground rounded-bl-sm'
            }`}
          >
            {renderText(content)}
          </div>
        )}
        {recommendations && recommendations.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
            {recommendations.map((rec) => (
              <ProductCard key={rec.paddle_id} {...rec} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}