'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import type { Paddle, UserProfile } from '@/types/paddle'
import { fetchPaddles } from '@/lib/api'
import { getProfile, saveProfile } from '@/lib/profile'
import { QuizWidget } from '@/components/quiz/quiz-widget'
import { RecommendationCard } from '@/components/quiz/recommendation-card'
import { DataStatsSection } from '@/components/home/data-stats-section'
import { FeatureSteps } from '@/components/home/feature-steps'

export default function Home() {
  const [isReturning, setIsReturning] = useState(false)
  const [recommendation, setRecommendation] = useState<Paddle | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [quizComplete, setQuizComplete] = useState(false)

  useEffect(() => {
    const existing = getProfile()
    if (existing) {
      setIsReturning(true)
      fetchMatchingPaddle(existing)
    }
  }, [])

  function handleQuizComplete(profile: UserProfile) {
    saveProfile(profile)
    setQuizComplete(true)
    fetchMatchingPaddle(profile)
  }

  async function fetchMatchingPaddle(profile: UserProfile) {
    setIsLoading(true)
    try {
      const result = await fetchPaddles({
        price_max: profile.budget_max,
        limit: 50,
      })
      const matching = result.items.filter(p =>
        p.skill_level === profile.level || !p.skill_level
      )
      if (matching.length > 0) {
        setRecommendation(matching[0])
      }
    } catch (err) {
      console.error('[fetchMatchingPaddle] failed:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col">
      <section className="hy-dark-section hy-section-hero">
        <div className="hy-container flex flex-col items-center text-center gap-6">
          <h1 className="hy-display max-w-3xl">
            Encontre a raquete{' '}
            <span className="hy-text-underline-lime">ideal</span> para o seu jogo
          </h1>
          <p className="hy-subheading max-w-2xl">
            Responda 3 perguntas e receba uma recomendacao personalizada com os melhores precos do mercado brasileiro.
          </p>

          {isReturning ? (
            <div className="text-center">
              <p className="hy-subheading mb-4">
                Bem-vindo de volta! Seu perfil esta salvo.
              </p>
              {isLoading && (
                <div className="py-8" style={{ color: 'var(--color-gray-500)' }}>
                  Buscando recomendacao...
                </div>
              )}
              {recommendation && <RecommendationCard paddle={recommendation} />}
              <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="hy-button-cta">
                  <Link href="/chat">Falar com o PickleIQ</Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="hy-button-primary">
                  <Link href="/paddles">Ver catalogo</Link>
                </Button>
              </div>
            </div>
          ) : (
            <>
              <QuizWidget onComplete={handleQuizComplete} />
              {isLoading && (
                <div className="py-8" style={{ color: 'var(--color-gray-500)' }}>
                  Buscando recomendacao...
                </div>
              )}
              {recommendation && <RecommendationCard paddle={recommendation} />}
              {quizComplete && (
                <div className="mt-8">
                  <Button asChild size="lg" className="hy-button-cta">
                    <Link href="/chat">Ver recomendacoes no chat →</Link>
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      <DataStatsSection />
      <FeatureSteps />
    </div>
  )
}
