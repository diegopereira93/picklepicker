'use client'

import { IDENTITY_OPTIONS } from '@/types/paddle'

interface QuizStepGiftRecipientProps {
  value: string
  onSelect: (value: string) => void
  onBack: () => void
}

export function QuizStepGiftRecipient({ value, onSelect, onBack }: QuizStepGiftRecipientProps) {
  const handleSelect = (optionValue: string) => {
    onSelect(optionValue)
  }

  return (
    <div className="max-w-3xl mx-auto wg-animate-step-enter space-y-6">
      <div className="flex items-center justify-between mb-2">
        <button
          type="button"
          onClick={onBack}
          className="wg-button-ghost text-sm"
        >
          ← Voltar
        </button>
        <div className="text-sm text-gray-600">
          2 de 3: <span className="font-semibold text-coral">Quem vai receber?</span>
        </div>
      </div>

      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Quem vai receber o presente?</h2>
        <p className="text-gray-600">Descreva o nível de jogo da pessoa</p>
      </div>

      <div className="grid gap-4">
        {IDENTITY_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => handleSelect(opt.value)}
            className={`wg-quiz-card text-left flex items-start gap-4 p-5 transition-all ${
              value === opt.value ? 'wg-quiz-card-selected border-coral' : ''
            }`}
          >
            <span className="text-3xl mt-1">{opt.icon}</span>
            <div className="flex-1">
              <div className={`font-semibold mb-1 ${value === opt.value ? 'text-coral' : ''}`}>
                {opt.label}
                {value === opt.value && (
                  <span className="inline-block ml-2 w-5 h-5 rounded-full bg-coral text-white text-xs flex items-center justify-center">
                    ✓
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-600">{opt.description}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
