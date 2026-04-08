'use client'

import { useState, useEffect } from 'react'
import type { UserProfile, Paddle } from '@/types/paddle'
import { QuizStepWelcomeGift } from '@/components/quiz/quiz-step-welcome-gift'
import { QuizStepGiftRecipient } from '@/components/quiz/quiz-step-gift-recipient'
import { QuizStepBudgetSlider } from '@/components/quiz/quiz-step-budget-slider'
import { QuizAnalyzing } from '@/components/quiz/quiz-analyzing'
import { ProgressIndicator } from '@/components/quiz/progress-indicator'
import { fetchPaddles } from '@/lib/api'

type GiftStep = 'welcome' | 'recipient' | 'budget' | 'analyzing' | 'results'

export default function GiftPage() {
  const [step, setStep] = useState<GiftStep>('welcome')
  const [recipientLevel, setRecipientLevel] = useState<string>('')
  const [budget, setBudget] = useState<number>(400)
  const [recommendedPaddle, setRecommendedPaddle] = useState<Paddle | null>(null)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setHydrated(true)
  }, [])

  if (!hydrated) {
    return (
      <main className="min-h-screen bg-[var(--warm-white)] flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Carregando...</div>
      </main>
    )
  }

  const steps: GiftStep[] = ['welcome', 'recipient', 'budget', 'analyzing', 'results']
  const currentStepIndex = steps.indexOf(step)

  function handleNext() {
    if (step === 'welcome') {
      setStep('recipient')
    } else if (step === 'recipient') {
      setStep('budget')
    } else if (step === 'budget') {
      setStep('analyzing')
    }
  }

  function handleBack() {
    if (step === 'recipient') {
      setStep('welcome')
    } else if (step === 'budget') {
      setStep('recipient')
    }
  }

  function handleRecipientSelect(level: string) {
    setRecipientLevel(level)
    handleNext()
  }

  function startAnalyzing() {
    setStep('analyzing')
  }

  function handleAnalyzingComplete() {
    fetchMatchingPaddles()
  }

  async function fetchMatchingPaddles() {
    try {
      const skillLevelMap: Record<string, string> = {
        'beginner': 'beginner',
        'regular': 'intermediate',
        'serious': 'advanced'
      }
      const skillLevel = skillLevelMap[recipientLevel] || 'beginner'
      
      const result = await fetchPaddles({
        skill_level: skillLevel,
        price_max: budget,
        limit: 1,
      })
      
      if (result.items.length > 0) {
        setRecommendedPaddle(result.items[0])
      } else {
        const fallback = await fetchPaddles({
          price_max: budget,
          limit: 1,
        })
        if (fallback.items.length > 0) {
          setRecommendedPaddle(fallback.items[0])
        }
      }
    } catch (err) {
      console.error('[fetchMatchingPaddles] failed:', err)
    }
  }

  function formatCurrency(val: number) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 0,
    }).format(val)
  }

  if (step === 'welcome') {
    return (
      <main 
        className="min-h-screen bg-[var(--warm-white)] flex flex-col items-center justify-center p-4"
        aria-label="Quiz de presente para raquetes"
      >
        <QuizStepWelcomeGift onStart={() => setStep('recipient')} />
      </main>
    )
  }

  if (step === 'recipient') {
    return (
      <main 
        className="min-h-screen bg-[var(--warm-white)] flex flex-col items-center justify-center p-4"
        aria-label="Quiz de presente para raquetes"
      >
        <QuizStepGiftRecipient 
          value={recipientLevel}
          onSelect={handleRecipientSelect}
          onBack={handleBack}
        />
        <div className="mt-8">
          <ProgressIndicator currentStep={currentStepIndex + 1} totalSteps={3} />
        </div>
      </main>
    )
  }

  if (step === 'budget') {
    return (
      <main 
        className="min-h-screen bg-[var(--warm-white)] flex flex-col items-center justify-center p-4"
        aria-label="Quiz de presente para raquetes"
      >
        <QuizStepBudgetSlider 
          value={budget}
          onSelect={(val) => setBudget(val)}
          onBack={handleBack}
        />
        <div className="mt-8">
          <ProgressIndicator currentStep={currentStepIndex + 1} totalSteps={3} />
        </div>
        
        <div className="mt-6">
          <button
            type="button"
            onClick={startAnalyzing}
            disabled={budget === 0}
            tabIndex={0}
            onKeyDown={(e) => {
              if ((e.key === 'Enter' || e.key === ' ') && budget !== 0) {
                e.preventDefault()
                startAnalyzing()
              }
            }}
            className="wg-button-coral text-lg px-8 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ANALISAR →
          </button>
        </div>
      </main>
    )
  }

  if (step === 'analyzing') {
    return (
      <main 
        className="min-h-screen bg-[var(--warm-white)] flex flex-col items-center justify-center p-4"
        aria-label="Quiz de presente para raquetes"
      >
        <QuizAnalyzing onComplete={handleAnalyzingComplete} />
        <div className="mt-8">
          <ProgressIndicator currentStep={currentStepIndex + 1} totalSteps={3} />
        </div>
      </main>
    )
  }

  if (step === 'results') {
    return (
      <main className="min-h-screen bg-[var(--warm-white)] flex flex-col items-center justify-center p-4">
        <GiftResultsPage 
          paddle={recommendedPaddle}
          recipientLevel={recipientLevel}
          budget={budget}
          onTryAgain={() => {
            setStep('welcome')
            setRecipientLevel('')
            setBudget(400)
            setRecommendedPaddle(null)
          }}
          onViewMore={() => {
            window.location.href = '/catalog'
          }}
          onPersonalQuiz={() => {
            window.location.href = '/quiz'
          }}
        />
      </main>
    )
  }

  return null
}

function GiftResultsPage({ 
  paddle, 
  recipientLevel, 
  budget,
  onTryAgain,
  onViewMore,
  onPersonalQuiz
}: { 
  paddle: any
  recipientLevel: string
  budget: number
  onTryAgain: () => void
  onViewMore: () => void
  onPersonalQuiz: () => void
}) {
  const levelLabels: Record<string, string> = {
    'beginner': 'iniciante',
    'regular': 'jogador regular',
    'serious': 'competitivo'
  }
  const recipientLabel = levelLabels[recipientLevel] || 'o presente'

  function formatCurrency(val: number) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 0,
    }).format(val)
  }

  if (!paddle) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Carregando recomendação...</p>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <div className="text-8xl mb-4">🎁</div>
        <h1 className="text-3xl font-bold">Presente perfeito!</h1>
        <p className="text-gray-600">
          Encontramos a raquete ideal para quem vai receber
        </p>
      </div>

      <div className="mx-auto max-w-xl bg-gray-50 rounded-xl p-6 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-center">
          <div className="w-[100px] h-[150px] rounded-lg overflow-hidden mx-auto md:mx-0 bg-gray-200">
            {paddle.image_url ? (
              <img 
                src={paddle.image_url} 
                alt={paddle.name} 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-xs text-gray-500">
                Foto
              </div>
            )}
          </div>

          <div className="text-center md:text-left">
            <h3 className="text-xl font-bold mb-2">{paddle.name}</h3>
            {paddle.brand && (
              <p className="text-xs font-bold uppercase tracking-wider mb-2 text-green-700">
                {paddle.brand}
              </p>
            )}
            <div className="text-2xl font-bold text-coral mb-4">
              R$ {paddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
            </div>

            <p className="text-sm text-gray-600 mb-3 bg-yellow-50 p-3 rounded-lg">
              Esta raquete é perfeita para {recipientLabel} que está começando
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Melhor avaliada na faixa de {formatCurrency(budget)}
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-3">
        <button
          type="button"
          onClick={onViewMore}
          className="wg-button-coral text-lg px-6 py-3"
        >
          VER MAIS OPÇÕES →
        </button>
        <button
          type="button"
          onClick={onPersonalQuiz}
          className="wg-button-ghost text-lg px-6 py-3"
        >
          Quero fazer o quiz pra mim
        </button>
        <button
          type="button"
          onClick={onTryAgain}
          className="wg-button-ghost text-lg px-6 py-3"
        >
          Refazer
        </button>
      </div>
    </div>
  )
}
