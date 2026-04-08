'use client'

import { cn } from '@/lib/utils'

interface PriceTagProps {
  price: number
  previousPrice?: number
  currency?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

function PriceTag({ price, previousPrice, currency = 'BRL', size = 'md', className }: PriceTagProps) {
  const hasDiscount = previousPrice && previousPrice > price

  const sizeClasses = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-4xl',
  }

  const formatPrice = (value: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency, minimumFractionDigits: 2 }).format(value)

  return (
    <div className={cn('flex items-baseline gap-2', className)}>
      <span
        className={cn(
          'font-mono font-bold text-text-primary',
          sizeClasses[size],
          hasDiscount && 'text-price-down'
        )}
      >
        {formatPrice(price)}
      </span>
      {previousPrice && previousPrice !== price && (
        <span className="font-mono text-sm text-text-muted line-through">
          {formatPrice(previousPrice)}
        </span>
      )}
    </div>
  )
}

function PriceTagSkeleton({ size = 'md', className }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const sizeClasses = { sm: 'w-20 h-6', md: 'w-28 h-8', lg: 'w-40 h-10' }

  return (
    <div className={cn('flex items-baseline gap-2', className)}>
      <Skeleton className={cn('rounded-sharp', sizeClasses[size])} />
    </div>
  )
}

export { PriceTag, PriceTagSkeleton }
export type { PriceTagProps }
