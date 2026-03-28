'use client'

interface StepStyleProps {
  value: string | null
  onChange: (style: string) => void
}

const OPTIONS = [
  {
    value: 'control',
    label: 'Controle',
    description: 'Prefiro precisao e colocacao de bola',
    icon: '🎯',
  },
  {
    value: 'power',
    label: 'Potencia',
    description: 'Gosto de smashes fortes e jogo agressivo',
    icon: '💪',
  },
  {
    value: 'balanced',
    label: 'Equilibrado',
    description: 'Quero o melhor dos dois mundos',
    icon: '⚖️',
  },
]

export function StepStyle({ value, onChange }: StepStyleProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-xl font-semibold text-center mb-4">
        Qual seu estilo de jogo?
      </h2>
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`w-full flex items-center gap-4 p-4 rounded-xl border-2 text-left transition-all ${
            value === opt.value
              ? 'border-primary bg-primary/5 ring-2 ring-primary'
              : 'border-border hover:border-primary/50'
          }`}
        >
          <span className="text-2xl">{opt.icon}</span>
          <div>
            <div className="font-semibold">{opt.label}</div>
            <div className="text-sm text-muted-foreground">{opt.description}</div>
          </div>
        </button>
      ))}
    </div>
  )
}
