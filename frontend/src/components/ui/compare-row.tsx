import { cn } from '@/lib/utils'
import { Check } from 'lucide-react'

interface CompareRowProps {
  attribute: string
  valueA: string | number | null | undefined
  valueB: string | number | null | undefined
  winner?: 'a' | 'b' | 'tie'
  className?: string
}

function CompareRow({ attribute, valueA, valueB, winner, className }: CompareRowProps) {
  const displayA = valueA ?? '—'
  const displayB = valueB ?? '—'
  const formatValue = (val: string | number) => {
    if (typeof val === 'number') return val.toFixed(1)
    return String(val)
  }

  return (
    <div
      className={cn(
        'flex items-center border-b border-border last:border-b-0',
        className
      )}
    >
      <span className="flex-1 px-4 py-3 text-sm text-text-muted font-medium">
        {attribute}
      </span>
      <span
        className={cn(
          'flex-1 px-4 py-3 text-sm font-mono text-center text-text-primary',
          winner === 'a' && 'text-price-down bg-price-down/10'
        )}
      >
        <span className="inline-flex items-center gap-1">
          {winner === 'a' && <Check className="h-3 w-3" />}
          {formatValue(displayA)}
        </span>
      </span>
      <span
        className={cn(
          'flex-1 px-4 py-3 text-sm font-mono text-center text-text-primary',
          winner === 'b' && 'text-price-down bg-price-down/10'
        )}
      >
        <span className="inline-flex items-center gap-1">
          {winner === 'b' && <Check className="h-3 w-3" />}
          {formatValue(displayB)}
        </span>
      </span>
    </div>
  )
}

export { CompareRow }
export type { CompareRowProps }
