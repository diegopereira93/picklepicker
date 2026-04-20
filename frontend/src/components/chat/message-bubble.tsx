'use client'

import type { ChatRecommendation } from '@/types/paddle'
import { InlinePaddleCard } from './inline-paddle-card'
import { TipCard } from './tip-card'
import { PickleIQAvatar } from './pickleiq-avatar'
import { cn } from '@/lib/utils'

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

function isTipContent(text: string): boolean {
  const kw = ['dica', 'importante', 'lembre-se', 'saiba que', 'recomendo', 'sugestão', 'sugestao']
  return text.length < 300 && kw.some((k) => text.toLowerCase().includes(k))
}

export function MessageBubble({ role, content, annotations }: MessageBubbleProps) {
  const isUser = role === 'user'
  const recs = annotations?.find(isRecommendationArray) as ChatRecommendation[] | undefined
  const hasTip = !recs?.length && !!content && isTipContent(content)

  return (
    <div className={cn('flex mb-4 gap-2', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser && <PickleIQAvatar size="sm" />}

      <div className="max-w-[85%] md:max-w-[75%] flex flex-col gap-2">
        {content && !hasTip && (
          <div
            className={cn(
              'rounded-rounded px-4 py-3 text-sm leading-relaxed animate-slide-in',
              isUser
                ? 'bg-elevated text-text-primary border-l-2 border-brand-primary'
                : 'bg-surface text-text-primary shadow-sm'
            )}
          >
            {content.split('\n').map((line, i) => (
              <span key={i}>
                {i > 0 && <br />}
                {line}
              </span>
            ))}
          </div>
        )}

        {hasTip && <TipCard content={content} />}

        {recs?.map((r) => (
          <InlinePaddleCard key={r.paddle_id} {...r} />
        ))}
      </div>
    </div>
  )
}
