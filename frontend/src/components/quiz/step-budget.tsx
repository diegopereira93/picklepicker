'use client'

import { useState } from 'react'

interface StepBudgetProps {
  value: number | null
  onChange: (budget: number) => void
}

const PRESETS = [400, 600, 800, 1000, 1200]

export function StepBudget({ value, onChange }: StepBudgetProps) {
  const [customMode, setCustomMode] = useState(false)
  const [customValue, setCustomValue] = useState('')

  function handlePreset(amount: number) {
    setCustomMode(false)
    onChange(amount)
  }

  function handleCustomChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = e.target.value
    setCustomValue(raw)
    const num = parseInt(raw, 10)
    if (!isNaN(num) && num >= 200 && num <= 3000) {
      onChange(num)
    }
  }

  return (
    <div className="space-y-3">
      <h2 className="text-xl font-semibold text-center mb-4">
        Qual seu orcamento maximo?
      </h2>
      <div className="grid grid-cols-3 gap-2">
        {PRESETS.map((amount) => (
          <button
            key={amount}
            type="button"
            onClick={() => handlePreset(amount)}
            className={`p-3 rounded-xl border-2 text-center font-semibold transition-all ${
              value === amount && !customMode
                ? 'border-primary bg-primary/5 ring-2 ring-primary'
                : 'border-border hover:border-primary/50'
            }`}
          >
            {amount === 1200 ? 'R$ 1200+' : `R$ ${amount}`}
          </button>
        ))}
        <button
          type="button"
          onClick={() => { setCustomMode(true); setCustomValue('') }}
          className={`p-3 rounded-xl border-2 text-center font-semibold transition-all ${
            customMode
              ? 'border-primary bg-primary/5 ring-2 ring-primary'
              : 'border-border hover:border-primary/50'
          }`}
        >
          Outro
        </button>
      </div>
      {customMode && (
        <div className="flex items-center gap-2 mt-2">
          <span className="font-semibold text-muted-foreground">R$</span>
          <input
            type="number"
            min={200}
            max={3000}
            value={customValue}
            onChange={handleCustomChange}
            placeholder="Ex: 750"
            className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            autoFocus
          />
        </div>
      )}
      <p className="text-xs text-muted-foreground text-center">
        Minimo R$ 200 — Maximo R$ 3000
      </p>
    </div>
  )
}
