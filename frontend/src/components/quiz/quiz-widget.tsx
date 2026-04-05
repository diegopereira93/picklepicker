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
      <div className="mx-auto max-w-2xl p-8 md:p-10 rounded-sm"
           style={{ backgroundColor: 'var(--color-near-black)', border: '2px solid var(--color-gray-border)' }}>

        <div className="mb-8">
          <span className="hy-section-label block mb-4">SEU NIVEL</span>
          <div className="flex flex-wrap justify-center gap-3">
            {LEVEL_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setLevel(opt.value)}
                className={`hy-quiz-pill ${level === opt.value ? 'selected hy-animate-quiz-ripple' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-8">
          <span className="hy-section-label block mb-4">SEU ORCAMENTO</span>
          <div className="flex flex-wrap justify-center gap-3">
            {BUDGET_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setBudget(opt.value)}
                className={`hy-quiz-pill ${budget === opt.value ? 'selected hy-animate-quiz-ripple' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-0">
          <span className="hy-section-label block mb-4">ESTILO DE JOGO</span>
          <div className="flex flex-wrap justify-center gap-3">
            {STYLE_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setStyle(opt.value)}
                className={`hy-quiz-pill ${style === opt.value ? 'selected hy-animate-quiz-ripple' : ''}`}
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
          className="hy-button hy-button-cta px-8 py-3 text-base disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Comecar Quiz →
        </button>
      </div>
    </div>
  )
}
