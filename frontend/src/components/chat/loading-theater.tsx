'use client'

import { useEffect, useState } from 'react'
import { Check } from 'lucide-react'

const STEPS = [
  'Analisando seu perfil…',
  'Buscando raquetes compatíveis…',
  'Comparando preços no Brasil…',
]

export function LoadingTheater() {
  const [visible, setVisible] = useState(1)
  const [done, setDone] = useState<Set<number>>(new Set())

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = []
    STEPS.forEach((_, i) => {
      if (i === 0) return
      timers.push(setTimeout(() => setVisible((v) => Math.max(v, i + 1)), 300 * i))
      timers.push(setTimeout(() => setDone((d) => new Set(d).add(i - 1)), 300 * i + 250))
    })
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col gap-1.5 text-sm text-text-secondary px-4 py-3"
    >
      {STEPS.slice(0, visible).map((step, i) => {
        const isDone = done.has(i)
        return (
          <div key={step} className="flex items-center gap-2 animate-slide-in">
            {isDone ? (
              <Check size={14} className="text-brand-primary shrink-0" />
            ) : (
              <span className="w-3.5 h-3.5 shrink-0 rounded-full border-2 border-brand-primary border-t-transparent animate-spin" />
            )}
            <span className={isDone ? 'text-text-muted' : 'text-text-primary'}>{step}</span>
          </div>
        )
      })}
    </div>
  )
}
