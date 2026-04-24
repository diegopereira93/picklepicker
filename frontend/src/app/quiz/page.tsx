'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  Trophy, Target, Zap, Crown, Flame, Crosshair, Sparkles, Scale,
  Wallet, Banknote, PiggyBank, Gem, Feather, Dumbbell, HelpCircle,
  Home, Sun, ArrowLeftRight,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { QuizProgressBar } from '@/components/ui/quiz-progress-bar'
import { QuizOptionCard } from '@/components/ui/quiz-option-card'
import {
  saveQuizProfile, type QuizProfile,
} from '@/lib/quiz-profile'
import { Button } from '@/components/ui/button'

interface QuizOption {
  value: string
  label: string
  description: string
  icon: LucideIcon
}

interface QuizStep {
  key: keyof Omit<QuizProfile, 'completedAt' | 'targetPaddle'> | 'targetPaddle'
  question: string
  type?: 'choice' | 'text'
  options?: QuizOption[]
  placeholder?: string
}

const STEPS: QuizStep[] = [
  {
    key: 'level',
    question: 'Qual é o seu nível de jogo?',
    options: [
      { value: 'beginner', label: 'Iniciante', description: 'Começando agora', icon: Trophy },
      { value: 'intermediate', label: 'Intermediário', description: 'Jogo há 6-12 meses', icon: Target },
      { value: 'advanced', label: 'Avançado', description: 'Competitivo, 1+ ano', icon: Zap },
      { value: 'competitive', label: 'Profissional', description: 'Torneios, ranking', icon: Crown },
    ],
  },
  {
    key: 'style',
    question: 'Como você descreveria seu estilo?',
    options: [
      { value: 'baseline-grinder', label: 'Power', description: 'Batidas fortes, fundo de quadra', icon: Flame },
      { value: 'dink-control', label: 'Control', description: 'Precisão, colocação', icon: Crosshair },
      { value: 'power-hitter', label: 'Spin', description: 'Efeitos, jogadas técnicas', icon: Sparkles },
      { value: 'all-round', label: 'All-Round', description: 'Equilibrado, versátil', icon: Scale },
    ],
  },
  {
    key: 'priority',
    question: 'O que mais importa pra você?',
    options: [
      { value: 'power', label: 'Potência', description: 'Maximizar suas batidas', icon: Flame },
      { value: 'control', label: 'Controle', description: 'Precisão em cada jogada', icon: Crosshair },
      { value: 'spin', label: 'Spin', description: 'Efeitos e curvas', icon: Sparkles },
      { value: 'speed', label: 'Velocidade', description: 'Reações rápidas', icon: ArrowLeftRight },
    ],
  },
  {
    key: 'budget',
    question: 'Qual seu orçamento?',
    options: [
      { value: 'under-80', label: 'Até R$ 200', description: 'Entrada, bom preço', icon: Wallet },
      { value: '80-150', label: 'R$ 200 - 400', description: 'Intermediário', icon: Banknote },
      { value: '150-250', label: 'R$ 400 - 600', description: 'Premium', icon: PiggyBank },
      { value: '250-plus', label: 'R$ 600+', description: 'Top de linha', icon: Gem },
    ],
  },
  {
    key: 'weightPreference',
    question: 'Preferência de peso?',
    options: [
      { value: 'light', label: 'Leve (≤ 240g)', description: 'Maneio rápido', icon: Feather },
      { value: 'medium', label: 'Médio (240-260g)', description: 'Equilíbrio perfeito', icon: Scale },
      { value: 'heavy', label: 'Pesado (≥ 260g)', description: 'Mais potência', icon: Dumbbell },
      { value: 'no-preference', label: 'Não sei', description: 'Me recomende', icon: HelpCircle },
    ],
  },
  {
    key: 'location',
    question: 'Onde você joga?',
    options: [
      { value: 'indoor', label: 'Indoor', description: 'Quadras cobertas', icon: Home },
      { value: 'outdoor', label: 'Outdoor', description: 'Ao ar livre', icon: Sun },
      { value: 'both', label: 'Ambos', description: 'Indoor e outdoor', icon: Scale },
    ],
  },
  {
    key: 'targetPaddle',
    question: 'Tem algum modelo em mente?',
    type: 'text',
    placeholder: 'Ex: Selkirk Vanguard, Joola Hyperion...',
  },
]

export default function QuizPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [answers, setAnswers] = useState<Partial<Record<string, string>>>({})
  const [direction, setDirection] = useState<'forward' | 'backward'>('forward')
  const [showAnalyzing, setShowAnalyzing] = useState(false)
  const [animKey, setAnimKey] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const currentStepData = STEPS[step - 1]
  const selectedValue = currentStepData ? answers[currentStepData.key] : undefined
  const isTextStep = currentStepData?.type === 'text'

  useEffect(() => {
    if (isTextStep && inputRef.current) {
      inputRef.current.focus()
    }
  }, [step, isTextStep])

  function handleSelect(value: string) {
    const key = currentStepData.key
    setAnswers(prev => ({ ...prev, [key]: value }))

    if (step < 7) {
      setDirection('forward')
      setAnimKey(k => k + 1)
      setTimeout(() => setStep(s => s + 1), 150)
    } else {
      finishQuiz(value)
    }
  }

  function handleSkip() {
    if (step < 7) {
      setDirection('forward')
      setAnimKey(k => k + 1)
      setTimeout(() => setStep(s => s + 1), 150)
    } else {
      finishQuiz('')
    }
  }

  function finishQuiz(targetPaddleValue: string) {
    const finalAnswers: Record<string, string | undefined> = { ...answers, targetPaddle: targetPaddleValue }
    const profile: QuizProfile = {
      level: (finalAnswers.level as QuizProfile['level']) || 'beginner',
      style: (finalAnswers.style as QuizProfile['style']) || 'all-round',
      priority: (finalAnswers.priority as QuizProfile['priority']) || 'control',
      budget: (finalAnswers.budget as QuizProfile['budget']) || 'under-80',
      weightPreference: (finalAnswers.weightPreference as QuizProfile['weightPreference']) || 'no-preference',
      location: (finalAnswers.location as QuizProfile['location']) || 'both',
      targetPaddle: finalAnswers.targetPaddle || undefined,
      completedAt: new Date().toISOString(),
    }
    saveQuizProfile(profile)
    setShowAnalyzing(true)
    setTimeout(() => router.push('/chat'), 2000)
  }

  function handleBack() {
    if (step > 1) {
      setDirection('backward')
      setAnimKey(k => k + 1)
      setTimeout(() => setStep(s => s - 1), 150)
    }
  }

  if (showAnalyzing) {
    return (
      <main className="min-h-screen bg-base flex flex-col items-center justify-center px-4">
        <div className="flex flex-col items-center gap-6">
          <div className="w-16 h-16 rounded-full bg-brand-primary animate-pulse flex items-center justify-center">
            <Zap className="w-8 h-8 text-base" />
          </div>
          <p className="font-sans text-lg text-text-muted animate-pulse">
            Analisando seu perfil...
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-base flex flex-col">
      <div className="max-w-lg mx-auto w-full px-4 md:px-6 flex-1 flex flex-col justify-center">
        <div className="mb-8">
          <QuizProgressBar currentStep={step} />
        </div>

        <div
          key={animKey}
          className={cn(
            'transition-all duration-300 ease-in-out',
            direction === 'forward'
              ? 'animate-[fadeInRight_300ms_ease-in-out]'
              : 'animate-[fadeInLeft_300ms_ease-in-out]'
          )}
        >
          <h1 className="font-sans text-2xl md:text-3xl font-semibold text-text-primary mb-8 leading-tight">
            {currentStepData.question}
          </h1>

          {isTextStep ? (
            <div className="space-y-4">
              <input
                ref={inputRef}
                type="text"
                placeholder={currentStepData.placeholder}
                value={selectedValue || ''}
                onChange={(e) => setAnswers(prev => ({ ...prev, [currentStepData.key]: e.target.value }))}
                maxLength={120}
                className="w-full bg-elevated border border-border rounded-rounded px-4 py-3 text-base font-sans text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-brand-primary"
              />
              <button
                type="button"
                onClick={handleSkip}
                className="text-sm text-text-muted hover:text-text-primary transition-colors"
              >
                Pular esta etapa
              </button>
            </div>
          ) : (
            <div
              className="grid grid-cols-2 gap-4"
              role="radiogroup"
              aria-labelledby="quiz-question"
            >
              {currentStepData.options!.map((opt) => (
                <QuizOptionCard
                  key={opt.value}
                  icon={opt.icon}
                  label={opt.label}
                  description={opt.description}
                  selected={selectedValue === opt.value}
                  onSelect={() => handleSelect(opt.value)}
                />
              ))}
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-12">
          {step > 1 && (
            <Button
              variant="ghost"
              onClick={handleBack}
              className="flex-1 text-text-secondary hover:text-text-primary"
            >
              Voltar
            </Button>
          )}
          {isTextStep ? (
            <Button
              variant="default"
              onClick={() => handleSelect(selectedValue || '')}
              className="flex-1 bg-brand-primary hover:bg-brand-primary/90 text-base"
            >
              {step === 7 ? 'Ver Minhas Raquetes' : 'Próximo'}
            </Button>
          ) : (
            <Button
              variant="default"
              onClick={() => selectedValue && handleSelect(selectedValue)}
              disabled={!selectedValue}
              className="flex-1 bg-brand-primary hover:bg-brand-primary/90 text-base disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {step === 7 ? 'Ver Minhas Raquetes' : 'Próximo'}
            </Button>
          )}
        </div>
      </div>
    </main>
  )
}
