'use client'

import { cn } from '@/lib/utils'

interface AttributeBadgeProps {
  label: string
  value: number
  variant?: 'dot' | 'pill'
  className?: string
}

const ATTRIBUTE_COLORS: Record<string, string> = {
  Power: 'bg-brand-secondary text-brand-secondary',
  Control: 'bg-brand-primary text-brand-primary',
  Spin: 'bg-info text-info',
  Speed: 'bg-warning text-warning',
  'Sweet Spot': 'bg-chart-5 text-chart-5',
}

const ATTRIBUTE_DOT_BG: Record<string, string> = {
  Power: 'bg-brand-secondary',
  Control: 'bg-brand-primary',
  Spin: 'bg-info',
  Speed: 'bg-warning',
  'Sweet Spot': 'bg-chart-5',
}

function AttributeBadge({ label, value, variant = 'dot', className }: AttributeBadgeProps) {
  const colorClass = ATTRIBUTE_COLORS[label] || 'bg-text-secondary text-text-secondary'
  const dotClass = ATTRIBUTE_DOT_BG[label] || 'bg-text-secondary'

  if (variant === 'dot') {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <span className={cn('w-2 h-2 rounded-full shrink-0', dotClass)} />
        <span className="text-xs text-text-secondary">{label}</span>
        <span className={cn('text-xs font-mono font-bold', colorClass.split(' ')[1])}>{value.toFixed(1)}</span>
      </div>
    )
  }

  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-surface text-xs', className)}>
      <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', dotClass)} />
      <span className="text-text-secondary">{label}</span>
      <span className={cn('font-mono font-bold', colorClass.split(' ')[1])}>{value.toFixed(1)}</span>
    </span>
  )
}

export { AttributeBadge }
export type { AttributeBadgeProps }
