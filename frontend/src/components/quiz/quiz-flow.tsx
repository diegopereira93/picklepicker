'use client'

import { useState } from 'react'
import type { UserProfile } from '@/types/paddle'
import { saveProfile, getProfile } from '@/lib/profile'
import { StepLevel } from './step-level'
import { StepStyle } from './step-style'
import { StepBudget } from './step-budget'

interface QuizFlowProps {
  onComplete: (profile: UserProfile) => void
  onEditCancel?: () => void
  editMode?: boolean
}

type Step = 'level' | 'style' | 'budget' | 'complete'

const STEPS: Step[] = ['level', 'style', 'budget']

export function QuizFlow({ onComplete, onEditCancel, editMode = false }: QuizFlowProps) {
  const existing = getProfile()

  const [stepIndex, setStepIndex] = useState(0)
  const [level, setLevel] = useState<string | null>(existing?.level ?? null)
  const [style, setStyle] = useState<string | null>(existing?.style ?? null)
  const [budget, setBudget] = useState<number | null>(existing?.budget_max ?? null)

  const currentStep = STEPS[stepIndex]

  function canAdvance(): boolean {
    if (currentStep === 'level') return level !== null
    if (currentStep === 'style') return style !== null
    if (currentStep === 'budget') return budget !== null
    return false
  }

  function handleNext() {
    if (!canAdvance()) return
    if (stepIndex < STEPS.length - 1) {
      setStepIndex(stepIndex + 1)
    } else {
      // Complete
      const profile: UserProfile = {
        level: level!,
        style: style!,
        budget_max: budget!,
      }
      saveProfile(profile)
      onComplete(profile)
    }
  }

  function handleBack() {
    if (stepIndex > 0) setStepIndex(stepIndex - 1)
  }

  const isLastStep = stepIndex === STEPS.length - 1

  return (
    <div className="max-w-md mx-auto p-6 space-y-6">
      {/* Progress */}
      <div className="flex items-center justify-center gap-2">
        {STEPS.map((_, i) => (
          <div
            key={i}
            className={`h-2 rounded-full transition-all ${
              i <= stepIndex ? 'bg-primary w-8' : 'bg-muted w-4'
            }`}
          />
        ))}
      </div>

      <div className="animate-in-scale">

      {/* Step content */}
      {currentStep === 'level' && (
        <StepLevel value={level} onChange={setLevel} />
      )}
      {currentStep === 'style' && (
        <StepStyle value={style} onChange={setStyle} />
      )}
      {currentStep === 'budget' && (
        <StepBudget value={budget} onChange={setBudget} />
      )}

      {/* Navigation */}
      <div className="flex gap-3">
        {stepIndex > 0 && (
          <button
            type="button"
            onClick={handleBack}
            className="flex-1 py-3 rounded-xl border border-border font-semibold hover:bg-muted/50 transition-colors"
          >
            Voltar
          </button>
        )}
        {editMode && stepIndex === 0 && onEditCancel && (
          <button
            type="button"
            onClick={onEditCancel}
            className="flex-1 py-3 rounded-xl border border-border font-semibold hover:bg-muted/50 transition-colors"
          >
            Cancelar
          </button>
        )}
        <button
          type="button"
          onClick={handleNext}
          disabled={!canAdvance()}
          className="flex-1 py-3 rounded-xl bg-primary text-primary-foreground font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
        >
          {isLastStep ? 'Comecar' : 'Proximo'}
        </button>
      </div>
      </div>
    </div>
  )
}
