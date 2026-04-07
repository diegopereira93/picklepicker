'use client'

import { cn } from '@/lib/utils'
import type { LucideIcon } from 'lucide-react'

interface QuizOptionCardProps {
  icon: LucideIcon
  label: string
  description?: string
  selected: boolean
  onSelect: () => void
}

export function QuizOptionCard({ icon: Icon, label, description, selected, onSelect }: QuizOptionCardProps) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect()
        }
      }}
      className={cn(
        'w-full flex items-start gap-4 p-4 rounded-rounded border text-left transition-all duration-150',
        selected
          ? 'bg-brand-primary/10 border-brand-primary shadow-glow-green'
          : 'bg-surface border-border hover:border-brand-primary/50',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-primary focus-visible:ring-offset-2 focus-visible:ring-offset-base'
      )}
    >
      <div
        className={cn(
          'w-10 h-10 rounded-full flex items-center justify-center shrink-0',
          selected ? 'bg-brand-primary' : 'bg-elevated'
        )}
      >
        <Icon className={cn('w-5 h-5', selected ? 'text-base' : 'text-brand-primary')} />
      </div>
      <div className="flex-1 min-w-0">
        <span className={cn('font-sans font-medium text-base', selected ? 'text-brand-primary' : 'text-text-primary')}>
          {label}
        </span>
        {description && (
          <p className="font-sans text-sm text-text-muted mt-0.5">{description}</p>
        )}
      </div>
      {selected && (
        <div className="w-5 h-5 rounded-full bg-brand-primary flex items-center justify-center shrink-0">
          <svg className="w-3 h-3 text-base" viewBox="0 0 12 12" fill="none">
            <path
              d="M2 6l3 3 5-5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      )}
    </button>
  )
}
