import { cn } from '@/lib/utils'
import { ArrowDown, ArrowUp, Minus } from 'lucide-react'

interface PriceDeltaBadgeProps {
  delta: number
  pulsing?: boolean
  className?: string
}

function PriceDeltaBadge({ delta, pulsing = false, className }: PriceDeltaBadgeProps) {
  const isDown = delta < 0
  const isUp = delta > 0
  const isNeutral = delta === 0
  const displayValue = Math.abs(delta).toFixed(0)

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-mono font-bold cursor-default',
        isDown && 'bg-price-down/20 text-price-down',
        isUp && 'bg-price-up/20 text-price-up',
        isNeutral && 'bg-price-neutral/20 text-price-neutral',
        pulsing && 'animate-pulse-glow',
        className
      )}
    >
      {isDown && <ArrowDown className="w-3 h-3" />}
      {isUp && <ArrowUp className="w-3 h-3" />}
      {isNeutral && <Minus className="w-3 h-3" />}
      {displayValue}%
    </span>
  )
}

export { PriceDeltaBadge }
export type { PriceDeltaBadgeProps }
