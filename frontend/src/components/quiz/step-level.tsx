'use client'

interface StepLevelProps {
  value: string | null
  onChange: (level: string) => void
}

const OPTIONS = [
  {
    value: 'beginner',
    label: 'Iniciante',
    description: 'Comecei a jogar recentemente',
    icon: '⭐',
  },
  {
    value: 'intermediate',
    label: 'Intermediario',
    description: 'Jogo ha alguns meses com consistencia',
    icon: '🎯',
  },
  {
    value: 'advanced',
    label: 'Avancado',
    description: 'Jogo competitivamente ou treino frequentemente',
    icon: '🏆',
  },
]

export function StepLevel({ value, onChange }: StepLevelProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-xl font-semibold text-center mb-4">
        Qual o seu nivel de jogo?
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
