'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { QuizStep, UserProfile, QUIZ_STEPS } from '@/types/paddle'
import { getProfile, saveProfile, clearProfile } from '@/lib/profile'
import { QuizStepWelcome } from '@/components/quiz/quiz-step-welcome'
import { QuizStepIdentity } from '@/components/quiz/quiz-step-identity'
import { QuizStepStyle } from '@/components/quiz/quiz-step-style'
import { QuizStepPainPoints } from '@/components/quiz/quiz-step-pain-points'
import { QuizStepFrequency } from '@/components/quiz/quiz-step-frequency'
import { QuizStepBudgetSlider } from '@/components/quiz/quiz-step-budget-slider'
import { QuizAnalyzing } from '@/components/quiz/quiz-analyzing'
import { ProgressIndicator } from '@/components/quiz/progress-indicator'

export default function QuizPage() {
  const router = useRouter()
  
  const [currentStep, setCurrentStep] = useState<number>(0)
  const [direction, setDirection] = useState<'forward' | 'backward'>('forward')
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [profile, setProfile] = useState<Partial<UserProfile>>({
    level: '',
    style: '',
    budget_max: 400,
    identity: '',
    pain_points: [],
    frequency: '',
  })

  useEffect(() => {
    const existingProfile = getProfile()
    if (existingProfile) {
      setProfile(existingProfile)
      if (
        existingProfile.level &&
        existingProfile.style &&
        existingProfile.budget_max
      ) {
        router.push('/quiz/results')
      }
    }

    if (window.location.hash) {
      const hashStep = parseInt(window.location.hash.replace('#step-', ''), 10)
      if (!isNaN(hashStep) && hashStep >= 0 && hashStep < QUIZ_STEPS.length) {
        setCurrentStep(hashStep)
      }
    }
  }, [])

  const handleNext = useCallback(() => {
    if (isTransitioning) return

    setDirection('forward')
    setIsTransitioning(true)

    setTimeout(() => {
      setCurrentStep((prev) => {
        const next = prev + 1
        if (next < QUIZ_STEPS.length) {
          window.location.hash = `step-${next}`
        }
        return next
      })
      setIsTransitioning(false)
    }, 300)
  }, [isTransitioning])

  const handleBack = useCallback(() => {
    if (isTransitioning || currentStep === 0) return

    setDirection('backward')
    setIsTransitioning(true)

    setTimeout(() => {
      setCurrentStep((prev) => {
        const next = Math.max(0, prev - 1)
        window.location.hash = `step-${next}`
        return next
      })
      setIsTransitioning(false)
    }, 300)
  }, [isTransitioning, currentStep])

  useEffect(() => {
    const handleHashChange = () => {
      if (window.location.hash) {
        const hashStep = parseInt(window.location.hash.replace('#step-', ''), 10)
        if (!isNaN(hashStep) && hashStep >= 0 && hashStep < QUIZ_STEPS.length) {
          setDirection('backward')
          setCurrentStep(hashStep)
        }
      }
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const handleIdentitySelect = (value: string) => {
    setProfile((prev) => ({ ...prev, identity: value, level: value }))
    setTimeout(() => handleNext(), 300)
  }

  const handleStyleSelect = (value: string) => {
    setProfile((prev) => ({ ...prev, style: value }))
    setTimeout(() => handleNext(), 300)
  }

  const handlePainPointsSelect = (value: string[]) => {
    setProfile((prev) => ({ ...prev, pain_points: value }))
    handleNext()
  }

  const handleFrequencySelect = (value: string) => {
    setProfile((prev) => ({ ...prev, frequency: value }))
    setTimeout(() => handleNext(), 300)
  }

  const handleBudgetSelect = (value: number) => {
    setProfile((prev) => ({ ...prev, budget_max: value }))
    setTimeout(() => handleNext(), 300)
  }

  const handleAnalyzingComplete = () => {
    if (profile.level && profile.style && profile.budget_max) {
      saveProfile({
        level: profile.level,
        style: profile.style,
        budget_max: profile.budget_max,
        identity: profile.identity,
        pain_points: profile.pain_points,
        frequency: profile.frequency,
      } as UserProfile)
      router.push('/quiz/results')
    }
  }

  const handleRestart = () => {
    clearProfile()
    setProfile({
      level: '',
      style: '',
      budget_max: 400,
      identity: '',
      pain_points: [],
      frequency: '',
    })
    setCurrentStep(0)
    window.location.hash = 'step-0'
  }

  const renderStep = () => {
    const stepType = QUIZ_STEPS[currentStep]

    switch (stepType) {
      case 'welcome':
        return (
          <div aria-live="polite">
            <QuizStepWelcome
              onStart={handleNext}
            />
          </div>
        )

      case 'identity':
        return (
          <div aria-live="polite">
            <QuizStepIdentity
              value={profile.identity || ''}
              onSelect={handleIdentitySelect}
              onBack={handleBack}
            />
          </div>
        )

      case 'style':
        return (
          <div aria-live="polite">
            <QuizStepStyle
              value={profile.style || ''}
              onSelect={handleStyleSelect}
              onBack={handleBack}
            />
          </div>
        )

      case 'pain-points':
        return (
          <div aria-live="polite">
            <QuizStepPainPoints
              value={profile.pain_points || []}
              onSelect={handlePainPointsSelect}
              onBack={handleBack}
            />
          </div>
        )

      case 'frequency':
        return (
          <div aria-live="polite">
            <QuizStepFrequency
              value={profile.frequency || ''}
              onSelect={handleFrequencySelect}
              onBack={handleBack}
            />
          </div>
        )

      case 'budget':
        return (
          <div aria-live="polite">
            <QuizStepBudgetSlider
              value={profile.budget_max}
              onSelect={handleBudgetSelect}
              onBack={handleBack}
            />
          </div>
        )

      case 'analyzing':
        return (
          <div aria-live="polite">
            <QuizAnalyzing
              onComplete={handleAnalyzingComplete}
            />
          </div>
        )

      default:
        return null
    }
  }

    return (
      <div 
        className="min-h-screen bg-[var(--warm-white)] flex flex-col"
        aria-label="Quiz de recomendação de raquetes"
      >
        <div className="flex items-center justify-between px-4 py-4 max-w-[480px] mx-auto w-full">
          {currentStep > 0 && (
            <button
              type="button"
              onClick={handleBack}
              className="wg-button-ghost"
              aria-label="Voltar ao passo anterior"
            >
              ← Voltar
            </button>
          )}
          {currentStep === 0 && <div />}
          {currentStep > 0 && currentStep < 6 && (
            <div className="text-xs text-gray-500">
              Quiz - {currentStep + 1} de {QUIZ_STEPS.length - 1}
            </div>
          )}
        </div>

        {currentStep > 0 && currentStep < 6 && (
          <div className="px-4 py-2 max-w-[480px] mx-auto w-full">
            <ProgressIndicator currentStep={currentStep} />
          </div>
        )}

        <div className="flex-1 flex flex-col justify-center min-h-[70vh]">
          <div className="max-w-[480px] mx-auto px-4">
            {renderStep()}
          </div>
        </div>

        {currentStep >= 6 && (
          <div className="py-6 text-center">
            <button
              type="button"
              onClick={handleRestart}
              className="text-sm text-gray-500 hover:text-coral transition-colors"
            >
              Refazer quiz
            </button>
          </div>
        )}
      </div>
    )
}
