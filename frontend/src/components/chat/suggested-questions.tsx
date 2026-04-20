'use client'

import { cn } from '@/lib/utils'

interface SuggestedQuestionsProps {
  questions: string[]
  onSelect: (question: string) => void
  disabled?: boolean
  variant?: 'chips' | 'grid'
}

export function SuggestedQuestions({
  questions,
  onSelect,
  disabled,
  variant = 'chips',
}: SuggestedQuestionsProps) {
  if (questions.length === 0) return null

  return (
    <div className={cn(
      variant === 'grid'
        ? 'grid grid-cols-1 sm:grid-cols-2 gap-2'
        : 'flex flex-wrap gap-2'
    )}>
      {questions.map((question) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          disabled={disabled}
          className={cn(
            'text-left text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed',
            'bg-surface text-text-primary border border-border rounded-rounded',
            'hover:bg-elevated hover:border-brand-primary/40',
            variant === 'grid' ? 'px-4 py-3' : 'px-3 py-1.5'
          )}
        >
          {question}
        </button>
      ))}
    </div>
  )
}
