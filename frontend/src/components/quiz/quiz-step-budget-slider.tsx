'use client'

import { BUDGET_MIN, BUDGET_MAX, BUDGET_SMART_ZONE } from '@/types/paddle'

interface QuizStepBudgetSliderProps {
  value: number
  onSelect: (value: number) => void
  onBack: () => void
}

export function QuizStepBudgetSlider({ value, onSelect, onBack }: QuizStepBudgetSliderProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onSelect(Number(e.target.value))
  }

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 0,
    }).format(val)
  }

  return (
    <div className="max-w-3xl mx-auto wg-animate-step-enter space-y-8">
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
          5 de 7: <span className="font-semibold text-coral">Última pergunta!</span>
        </div>
      </div>

      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Quanto você quer investir?</h2>
        <div className="text-4xl font-bold text-coral mt-4">
          {formatCurrency(value)}
        </div>
      </div>

      <div className="space-y-6">
        <div className="relative py-4">
          <input
            type="range"
            min={BUDGET_MIN}
            max={BUDGET_MAX}
            value={value}
            onChange={handleChange}
            role="slider"
            aria-valuemin={BUDGET_MIN}
            aria-valuemax={BUDGET_MAX}
            aria-valuenow={value}
            aria-label={`Orçamento máximo: ${formatCurrency(value)}`}
            aria-valuetext={formatCurrency(value)}
            className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-coral"
          />
          <div className="flex justify-between text-sm text-gray-500 mt-2">
            <span>{formatCurrency(BUDGET_MIN)}</span>
            <span>{formatCurrency(BUDGET_MAX)}</span>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-100 rounded-lg p-4 flex items-start gap-3">
          <span className="text-xl">💡</span>
          <p className="text-sm text-gray-700">
            A maioria dos iniciantes encontra ótimas opções entre <span className="font-semibold text-yellow-700">{formatCurrency(BUDGET_SMART_ZONE.min)} - {formatCurrency(BUDGET_SMART_ZONE.max)}</span>
          </p>
        </div>
      </div>

      <div className="flex justify-center">
        <button
          type="button"
          onClick={onBack}
          className="wg-button-ghost text-lg px-8 py-3 mr-4"
        >
          ← Voltar
        </button>
      </div>
    </div>
  )
}
