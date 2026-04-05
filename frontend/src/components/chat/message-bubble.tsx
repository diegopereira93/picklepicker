'use client'

import type { ChatRecommendation } from '@/types/paddle'
import { ProductCard } from './product-card'
import { ComparisonCard } from './comparison-card'
import { TipCard } from './tip-card'

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

function isTipContent(text: string): boolean {
  const tipKeywords = ['dica', 'importante', 'lembre-se', 'saiba que', 'recomendo', 'sugestão', 'sugestao']
  const hasKeyword = tipKeywords.some(kw => text.toLowerCase().includes(kw))
  const isShort = text.length < 300
  return hasKeyword && isShort
}

function PickleIQAvatar() {
  return (
    <div
      style={{ backgroundColor: 'var(--color-near-black)' }}
      className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
      aria-hidden="true"
    >
      <span style={{ color: 'var(--sport-primary)' }}>PI</span>
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
      {!isUser && <PickleIQAvatar />}

      <div style={{ maxWidth: '80%' }}>
        {content && (
          <div
            style={{
              backgroundColor: isUser ? '#111111' : 'transparent',
              borderLeft: isUser ? '2px solid #84CC16' : 'none',
              borderRadius: '8px',
              color: '#ffffff',
              padding: '12px 16px',
              fontSize: 'var(--font-size-body)',
              lineHeight: 'var(--line-height-normal)',
            }}
            className={isUser ? '' : 'hy-animate-chat-enter'}
          >
            {renderText(content)}
          </div>
        )}

        {/* ProductCard(s) or ComparisonCard — rendered inside message bubble area */}
        {recommendations && recommendations.length > 0 && (
          <div className="mt-2">
            {recommendations.length >= 2 ? (
              <ComparisonCard paddles={recommendations} />
            ) : (
              <ProductCard key={recommendations[0].paddle_id} {...recommendations[0]} />
            )}
          </div>
        )}

        {/* TipCard — rendered when there's text but no recommendations */}
        {!recommendations?.length && content && isTipContent(content) && (
          <TipCard content={content} />
        )}
      </div>
    </div>
  )
}
