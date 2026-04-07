'use client'

import { cn } from '@/lib/utils'
import { useEffect, useState } from 'react'

interface MatchScoreBadgeProps {
  score: number
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'text-price-down'
  if (score >= 60) return 'text-warning'
  return 'text-price-up'
}

function getRingColor(score: number): string {
  if (score >= 80) return 'border-price-down'
  if (score >= 60) return 'border-warning'
  return 'border-price-up'
}

function MatchScoreBadge({ score, showLabel = true, size = 'md', className }: MatchScoreBadgeProps) {
  const [displayScore, setDisplayScore] = useState(0)

  useEffect(() => {
    const duration = 800
    const steps = 30
    const increment = score / steps
    let current = 0

    const timer = setInterval(() => {
      current += increment
      if (current >= score) {
        setDisplayScore(score)
        clearInterval(timer)
      } else {
        setDisplayScore(Math.floor(current))
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [score])

  const sizeClasses = {
    sm: 'w-12 h-12 text-sm border-2',
    md: 'w-16 h-16 text-lg border-[3px]',
    lg: 'w-20 h-20 text-xl border-4',
  }

  return (
    <div className={cn('relative inline-flex flex-col items-center', className)}>
      <div
        className={cn(
          'flex items-center justify-center rounded-full border bg-surface',
          sizeClasses[size],
          getRingColor(score)
        )}
      >
        <span className={cn('font-mono font-bold', getScoreColor(score))}>
          {displayScore}%
        </span>
      </div>
      {showLabel && (
        <span className="mt-1 text-[10px] font-medium uppercase tracking-wider text-text-muted">
          match
        </span>
      )}
    </div>
  )
}

export { MatchScoreBadge }
export type { MatchScoreBadgeProps }
