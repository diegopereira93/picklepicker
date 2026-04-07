'use client'

import { useState } from 'react'
import type { UserProfile } from '@/types/paddle'

interface QuizWidgetProps {
  onComplete: (profile: UserProfile) => void
}

const LEVEL_OPTIONS = [
  { value: 'beginner', label: 'Iniciante' },
  { value: 'intermediate', label: 'Intermediario' },
  { value: 'advanced', label: 'Avancado' },
]

const BUDGET_OPTIONS = [
  { value: 300, label: 'Ate R$300' },
  { value: 600, label: 'R$300-600' },
  { value: 9999, label: 'Acima R$600' },
]

const STYLE_OPTIONS = [
  { value: 'control', label: 'Controle' },
  { value: 'power', label: 'Potencia' },
  { value: 'balanced', label: 'Equilibrado' },
]

export function QuizWidget({ onComplete }: QuizWidgetProps) {
  const [level, setLevel] = useState<string | null>(null)
  const [budget, setBudget] = useState<number | null>(null)
  const [style, setStyle] = useState<string | null>(null)

  const isComplete = level !== null && budget !== null && style !== null

  function handleComplete() {
    if (!isComplete) return
    onComplete({ level: level!, style: style!, budget_max: budget! })
  }

  return (
    <div className="quiz-widget">
      <div className="mx-auto max-w-2xl p-8 md:p-10 rounded-[var(--radius-md)] bg-white border border-gray-200 shadow-sm">

        <div className="mb-8">
          <span className="text-sm font-bold text-[var(--accent-coral)] uppercase tracking-widest block mb-4">SEU NIVEL</span>
          <div className="flex flex-wrap justify-center gap-3">
            {LEVEL_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setLevel(opt.value)}
                className={`wg-quiz-card inline-flex items-center px-4 py-2 ${level === opt.value ? 'wg-quiz-card-selected' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-8">
          <span className="text-sm font-bold text-[var(--accent-coral)] uppercase tracking-widest block mb-4">SEU ORCAMENTO</span>
          <div className="flex flex-wrap justify-center gap-3">
            {BUDGET_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setBudget(opt.value)}
                className={`wg-quiz-card inline-flex items-center px-4 py-2 ${budget === opt.value ? 'wg-quiz-card-selected' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-0">
          <span className="text-sm font-bold text-[var(--accent-coral)] uppercase tracking-widest block mb-4">ESTILO DE JOGO</span>
          <div className="flex flex-wrap justify-center gap-3">
            {STYLE_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setStyle(opt.value)}
                className={`wg-quiz-card inline-flex items-center px-4 py-2 ${style === opt.value ? 'wg-quiz-card-selected' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="text-center mt-6">
        <button
          type="button"
          onClick={handleComplete}
          disabled={!isComplete}
          className="wg-button-coral px-8 py-3 text-base disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Comecar Quiz →
        </button>
      </div>
    </div>
  )
}
