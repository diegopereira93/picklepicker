'use client'

import { PAIN_POINT_OPTIONS } from '@/types/paddle'

interface QuizStepPainPointsProps {
  value: string[]
  onSelect: (value: string[]) => void
  onBack: () => void
  onNext: () => void
}

export function QuizStepPainPoints({ value, onSelect, onBack, onNext }: QuizStepPainPointsProps) {
  const handleToggle = (option: string) => {
    if (value.includes(option)) {
      onSelect(value.filter((v) => v !== option))
    } else {
      onSelect([...value, option])
    }
  }

  const handleKeyDown = (option: string, e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleToggle(option)
    }
  }

  return (
    <div className="max-w-3xl mx-auto wg-animate-step-enter space-y-6">
      <div className="flex items-center justify-between mb-2">
        <button
          type="button"
          onClick={onBack}
          className="wg-button-ghost text-sm"
          aria-label="Voltar ao passo anterior"
        >
          ← Voltar
        </button>
        <div className="text-sm text-gray-600">
          3 de 7: <span className="font-semibold text-coral">Quase lá!</span>
        </div>
      </div>

      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">O que te frustra na sua raquete atual?</h2>
        <p className="text-sm text-gray-600">(selecione todos que se aplicam)</p>
      </div>

      <div 
        role="group"
        aria-label="Selecione seus problemas com a raquete atual"
        className="space-y-3"
      >
        {PAIN_POINT_OPTIONS.map((option) => (
          <label
            key={option}
            onKeyDown={(e) => handleKeyDown(option, e)}
            tabIndex={0}
            className={`wg-quiz-card flex items-center gap-3 p-4 cursor-pointer transition-all ${
              value.includes(option) ? 'wg-quiz-card-selected border-coral' : ''
            }`}
            role="checkbox"
            aria-checked={value.includes(option) ? 'true' : 'false'}
            aria-label={`Problema: ${option}`}
          >
            <input
              type="checkbox"
              checked={value.includes(option)}
              onChange={() => handleToggle(option)}
              className="w-5 h-5 text-coral border-gray-300 rounded focus:ring-coral cursor-pointer"
            />
            <span className="text-gray-800">{option}</span>
          </label>
        ))}
        <div aria-live="polite" className="sr-only">
          {`${value.length} problemas selecionados`}
        </div>
      </div>

      <div className="flex justify-center pt-4">
        <button
          type="button"
          onClick={onNext}
          className="wg-button-coral text-lg px-8 py-3"
        >
          Próximo →
        </button>
      </div>
    </div>
  )
}
