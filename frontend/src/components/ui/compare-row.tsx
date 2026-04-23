import { cn } from '@/lib/utils'
import { Check } from 'lucide-react'

const INDEX_LETTERS = ['a', 'b', 'c', 'd'] as const

interface CompareRowProps {
  attribute: string
  values: (string | number | null)[]
  winners?: ('a' | 'b' | 'c' | 'd' | 'tie' | null)[]
  className?: string
}

function CompareRow({ attribute, values, winners, className }: CompareRowProps) {
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
      {values.map((val, idx) => {
        const display = val ?? '—'
        const colLetter = INDEX_LETTERS[idx]
        const isWinner = winners?.[idx] === colLetter || winners?.[idx] === 'tie'
        return (
          <span
            key={idx}
            data-index={idx}
            className={cn(
              'flex-1 px-4 py-3 text-sm font-mono text-center text-text-primary',
              isWinner && 'text-price-down bg-price-down/10'
            )}
          >
            <span className="inline-flex items-center gap-1">
              {isWinner && winners?.[idx] !== 'tie' && <Check className="h-3 w-3" />}
              {formatValue(display)}
            </span>
          </span>
        )
      })}
    </div>
  )
}

export { CompareRow }
export type { CompareRowProps }
