'use client'

import { PickleIQAvatar } from './pickleiq-avatar'
import { cn } from '@/lib/utils'

interface ChatEmptyStateProps {
  questions: string[]
  onAsk: (q: string) => void
  disabled?: boolean
}

export function ChatEmptyState({ questions, onAsk, disabled }: ChatEmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-6 py-8 md:py-12 max-w-2xl mx-auto">
      <PickleIQAvatar size="lg" />
      <div className="text-center space-y-2">
        <h2 className="font-display text-2xl md:text-3xl text-text-primary tracking-wide">
          OLÁ! SOU O PICKLE<span className="text-brand-secondary">IQ</span>
        </h2>
        <p className="text-text-secondary text-sm md:text-base">
          Me conte sobre seu jogo e eu te ajudo a encontrar a raquete ideal.
        </p>
      </div>

      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
        {questions.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => onAsk(q)}
            disabled={disabled}
            className={cn(
              'text-left px-4 py-3 rounded-rounded text-sm',
              'bg-surface text-text-primary border border-border',
              'hover:bg-elevated hover:border-brand-primary/40 hover:shadow-glow-green',
              'transition-all duration-200 disabled:opacity-50'
            )}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}
