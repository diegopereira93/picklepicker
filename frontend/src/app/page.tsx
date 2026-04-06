'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { Paddle, UserProfile } from '@/types/paddle'
import { fetchPaddles } from '@/lib/api'
import { getProfile, saveProfile } from '@/lib/profile'
import { QuizWidget } from '@/components/quiz/quiz-widget'
import { RecommendationCard } from '@/components/quiz/recommendation-card'
import { SafeImage } from '@/components/ui/safe-image'
import { DataStatsSection } from '@/components/home/data-stats-section'
import { FeatureSteps } from '@/components/home/feature-steps'

export default function Home() {
  const [isReturning, setIsReturning] = useState(false)
  const [recommendation, setRecommendation] = useState<Paddle | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [quizComplete, setQuizComplete] = useState(false)
  const [featuredPaddles, setFeaturedPaddles] = useState<Paddle[]>([])
  const [isLoadingFeatured, setIsLoadingFeatured] = useState(false)

  useEffect(() => {
    const existing = getProfile()
    if (existing) {
      setIsReturning(true)
      fetchMatchingPaddle(existing)
    }
    fetchFeaturedPaddles()
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

  async function fetchFeaturedPaddles() {
    setIsLoadingFeatured(true)
    try {
      const result = await fetchPaddles({ limit: 6 })
      setFeaturedPaddles(result.items)
    } catch (err) {
      console.error('[fetchFeaturedPaddles] failed:', err)
    } finally {
      setIsLoadingFeatured(false)
    }
  }

  return (
    <div className="flex flex-col">
      <section className="wg-section-light">
        <div className="wg-container">
          <div className="max-w-3xl mx-auto text-center">
            <div className="mb-8 text-6xl">🎾</div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6 tracking-tight">
              Encontre a raquete perfeita para o <span className="text-coral-600">SEU jogo</span>
            </h1>
            
            <p className="text-lg md:text-xl text-gray-600 mb-8 leading-relaxed">
              Responda 7 perguntas rapidas e receba recomendacoes personalizadas com os melhores precos do Brasil.
            </p>
            
            {isReturning ? (
              <div className="max-w-xl mx-auto">
                <p className="text-gray-600 mb-6">
                  Bem-vindo de volta! Baseado no seu perfil, recomendamos:
                </p>
                {isLoading && (
                  <div className="py-8 text-gray-500">
                    Buscando recomendacao...
                  </div>
                )}
                {recommendation && (
                  <div className="mb-6">
                    <RecommendationCard paddle={recommendation} />
                  </div>
                )}
                <div className="flex flex-col sm:flex-row gap-4 justify-center mt-6">
                  <Button asChild size="lg" className="wg-button-coral">
                    <Link href="/chat">Falar com o PickleIQ</Link>
                  </Button>
                  <Button asChild variant="outline" size="lg" className="wg-button-outline">
                    <Link href="/paddles">Ver catalogo</Link>
                  </Button>
                </div>
              </div>
            ) : (
              <>
                <QuizWidget onComplete={handleQuizComplete} />
                {isLoading && (
                  <div className="py-8 text-gray-500">
                    Buscando recomendacao...
                  </div>
                )}
                {recommendation && <RecommendationCard paddle={recommendation} />}
                {quizComplete && (
                  <div className="mt-8">
                    <Button asChild size="lg" className="wg-button-coral">
                      <Link href="/chat">Ver recomendacoes no chat →</Link>
                    </Button>
                  </div>
                )}
              </>
            )}
            
            <div className="mt-10 flex items-center justify-center gap-2 text-sm text-gray-600">
              <span className="text-yellow-500">⭐</span>
              <span>4.9/5</span>
              <span className="text-gray-300">·</span>
              <span>500+ raquetes</span>
              <span className="text-gray-300">·</span>
              <span>3 lojas</span>
            </div>
          </div>
        </div>
      </section>

      <section className="wg-section-cream">
        <div className="wg-container">
          <div className="max-w-3xl mx-auto text-center">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-8">
              PRECOS MONITORADOS EM TEMPO REAL
            </h3>
            
            <div className="flex flex-wrap justify-center gap-8 md:gap-12">
              <a href="https://brazilpickleball.com" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center px-6 py-3">
                <span className="font-semibold text-gray-700">Brazil Store</span>
              </a>
              <a href="https://dropshot.com.br" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center px-6 py-3">
                <span className="font-semibold text-gray-700">Drop Shot Brasil</span>
              </a>
              <a href="https://www.mercadolivre.com.br" target="_blank" rel="noopener noreferrer" className="flex items-center justify-center px-6 py-3">
                <span className="font-semibold text-gray-700">Mercado Livre</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="wg-section-light">
        <div className="wg-container">
          <div className="flex flex-col items-center mb-10">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6">
              RAQUETES EM DESTAQUE
            </h3>
            
            <div className="flex items-center gap-2 mb-8">
              <Link href="/paddles" className="text-sm font-semibold text-coral-600 hover:text-coral-700 transition-colors">
                Ver todas →
              </Link>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {isLoadingFeatured ? (
                <div className="col-span-full py-12 text-center text-gray-500">
                  Carregando raquetes...
                </div>
              ) : featuredPaddles.length > 0 ? (
                featuredPaddles.map((paddle) => (
                  <div key={paddle.id} className="wg-card p-6 hover:shadow-lg transition-shadow duration-300">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-24 h-36 rounded-md overflow-hidden bg-gray-100 flex-shrink-0">
                        <SafeImage
                          src={paddle.image_url}
                          alt={paddle.name}
                          width={96}
                          height={144}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                    
                    <div className="flex-1">
                      <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
                        {paddle.brand}
                      </p>
                      
                      <h4 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2">
                        {paddle.name}
                      </h4>
                      
                      <div className="text-2xl font-bold text-gray-900 mb-3" style={{ fontFamily: 'monospace' }}>
                        R$ {paddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
                      </div>
                      
                      {paddle.skill_level && (
                        <Badge variant="outline" className="mb-4" style={{ borderColor: 'var(--sport-primary)', color: 'var(--sport-primary)' }}>
                          {paddle.skill_level.charAt(0).toUpperCase() + paddle.skill_level.slice(1)}
                        </Badge>
                      )}
                      
                      <Link
                        href={paddle.model_slug && paddle.brand ? `/paddles/${encodeURIComponent(paddle.brand.toLowerCase())}/${encodeURIComponent(paddle.model_slug)}` : '/paddles'}
                        className="inline-flex items-center text-sm font-semibold text-coral-600 hover:text-coral-700 transition-colors"
                      >
                        Ver →
                      </Link>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full py-12 text-center text-gray-500">
                  Nenhuma raquete encontrada no momento.
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <DataStatsSection />

      <section className="wg-section-cream">
        <div className="wg-container">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest text-center mb-10">
              COMO FUNCIONA
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FeatureSteps />
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
