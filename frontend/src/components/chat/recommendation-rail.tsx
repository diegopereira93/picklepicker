'use client'

import type { ChatRecommendation } from '@/types/paddle'
import { InlinePaddleCard } from './inline-paddle-card'

interface RecommendationRailProps {
  recommendations: ChatRecommendation[]
}

export function RecommendationRail({ recommendations }: RecommendationRailProps) {
  const sorted = [...recommendations].sort((a, b) => b.similarity_score - a.similarity_score)

  return (
    <aside className="hidden lg:flex flex-col w-80 shrink-0 border-l border-border bg-surface">
      <header className="px-4 py-3 border-b border-border flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-widest text-text-muted">
          Recomendações
        </span>
        {sorted.length > 0 && (
          <span className="font-mono text-xs text-text-primary bg-elevated px-2 py-0.5 rounded-sharp">
            {sorted.length}
          </span>
        )}
      </header>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {sorted.length === 0 ? (
          <p className="text-sm text-text-muted px-2 py-4">
            Faça uma pergunta para ver recomendações aqui.
          </p>
        ) : (
          sorted.map((r) => <InlinePaddleCard key={r.paddle_id} {...r} compact />)
        )}
      </div>
    </aside>
  )
}
