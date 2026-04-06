'use client'

interface ProgressIndicatorProps {
  currentStep: number
  totalSteps?: number
}

const STEP_MESSAGES = {
  1: 'Vamos lá!',
  2: 'Já sei quem você é...',
  3: 'Quase lá!',
  4: 'Só mais uma...',
  5: 'Última pergunta!',
  6: 'Quase finalizando...',
  7: 'Analisando...',
}

export function ProgressIndicator({ currentStep, totalSteps = 7 }: ProgressIndicatorProps) {
  return (
    <div 
      role="progressbar"
      aria-valuenow={currentStep}
      aria-valuemin={1}
      aria-valuemax={totalSteps}
      aria-label={`Passo ${currentStep} de ${totalSteps}`}
      className="flex flex-col items-center space-y-3"
    >
      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, index) => {
          const stepNumber = index + 1
          const isActive = stepNumber === currentStep
          const isCompleted = stepNumber < currentStep

          return (
            <div
              key={stepNumber}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                isActive
                  ? 'bg-coral ring-2 ring-coral/20 animate-pulse'
                  : isCompleted
                  ? 'bg-coral'
                  : 'bg-gray-300'
              }`}
            />
          )
        })}
      </div>
      <p className="text-xs font-medium text-coral">
        {STEP_MESSAGES[currentStep as keyof typeof STEP_MESSAGES]}
      </p>
    </div>
  )
}
