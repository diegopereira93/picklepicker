'use client'

import { FREQUENCY_OPTIONS } from '@/types/paddle'

interface QuizStepFrequencyProps {
  value: string
  onSelect: (value: string) => void
  onBack: () => void
}

export function QuizStepFrequency({ value, onSelect, onBack }: QuizStepFrequencyProps) {
  const handleSelect = (optionValue: string) => {
    onSelect(optionValue)
  }

  const handleKeyDown = (optionValue: string, e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleSelect(optionValue)
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
          4 de 7: <span className="font-semibold text-coral">Só mais uma...</span>
        </div>
      </div>

      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Com que frequência você joga?</h2>
      </div>

      <div 
        role="radiogroup"
        aria-label="Selecione sua frequência de jogo"
        className="grid gap-4"
      >
        {FREQUENCY_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => handleSelect(opt.value)}
            onKeyDown={(e) => handleKeyDown(opt.value, e)}
            tabIndex={0}
            role="radio"
            aria-checked={value === opt.value ? 'true' : 'false'}
            aria-label={opt.label}
            className={`wg-quiz-card text-left flex items-start gap-4 p-5 transition-all ${
              value === opt.value ? 'wg-quiz-card-selected border-coral' : ''
            }`}
          >
            <div className="flex-1">
              <div className={`font-semibold mb-1 ${value === opt.value ? 'text-coral' : ''}`}>
                {opt.label}
                {value === opt.value && (
                  <span className="inline-block ml-2 w-5 h-5 rounded-full bg-coral text-white text-xs flex items-center justify-center">
                    ✓
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-600">{opt.label}</div>
            </div>
          </button>
        ))}
        <div aria-live="polite" className="sr-only">
          {value ? `Você selecionou: ${FREQUENCY_OPTIONS.find(opt => opt.value === value)?.label}` : ''}
        </div>
      </div>
    </div>
  )
}
