import { cn } from '@/lib/utils'

interface QuizProgressBarProps {
  currentStep: number
  totalSteps?: number
  className?: string
}

export function QuizProgressBar({ currentStep, totalSteps = 7, className }: QuizProgressBarProps) {
  const percentage = (currentStep / totalSteps) * 100
  return (
    <div className={cn('w-full', className)}>
      <div className="flex justify-between items-center mb-2">
        <span className="font-mono text-xs text-text-muted">PASSO {currentStep} DE {totalSteps}</span>
      </div>
      <div
        className="w-full h-1.5 rounded-full bg-surface overflow-hidden"
        role="progressbar"
        aria-valuenow={currentStep}
        aria-valuemin={1}
        aria-valuemax={totalSteps}
        aria-label={`Quiz progress: step ${currentStep} of ${totalSteps}`}
      >
        <div
          className="h-full bg-brand-primary rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
