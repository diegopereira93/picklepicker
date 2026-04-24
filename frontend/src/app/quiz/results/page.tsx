'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import type { Paddle } from '@/types/paddle'
import { loadQuizProfile, clearQuizProfile, type QuizProfile } from '@/lib/quiz-profile'
import { fetchPaddles } from '@/lib/api'
import { SafeImage } from '@/components/ui/safe-image'

const budgetLabels: Record<string, string> = {
  'under-80': 'Até R$ 200',
  '80-150': 'R$ 200 - 400',
  '150-250': 'R$ 400 - 600',
  '250-plus': 'R$ 600+',
}

const identityLabels: Record<string, string> = {
  beginner: 'Iniciante',
  intermediate: 'Intermediário',
  advanced: 'Avançado',
  competitive: 'Profissional',
}

const styleLabels: Record<string, string> = {
  'baseline-grinder': 'Power',
  'dink-control': 'Control',
  'power-hitter': 'Spin',
  'all-round': 'All-Round',
}

export default function QuizResultsPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<QuizProfile | null>(null)
  const [recommendations, setRecommendations] = useState<Paddle[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadProfileAndRecommendations = async () => {
      const storedProfile = loadQuizProfile()
      if (!storedProfile) {
        router.push('/quiz')
        return
      }
      setProfile(storedProfile)

      try {
        const response = await fetchPaddles({ limit: 50 })
        const filtered = response.items.filter(
          (p) => p.skill_level && p.skill_level.toLowerCase() === storedProfile.level.toLowerCase()
        )
        const sorted = filtered.sort((a, b) => {
          const priceA = a.price_min_brl ?? Infinity
          const priceB = b.price_min_brl ?? Infinity
          return priceA - priceB
        })
        setRecommendations(sorted.slice(0, 3))
      } catch (err) {
        console.error('Failed to fetch recommendations:', err)
      } finally {
        setIsLoading(false)
      }
    }

    loadProfileAndRecommendations()
  }, [router])

  const handleRefactorQuiz = () => {
    clearQuizProfile()
    router.push('/quiz')
  }

  const badgeLabels = ['MELHOR COMBINAÇÃO', 'MELHOR CUSTO-BENEFÍCIO', 'MELHOR PARA EVOLUIR']
  const badgeClasses = [
    'bg-brand-secondary text-white',
    'bg-brand-primary text-base',
    'bg-blue-400 text-white',
  ]

  if (isLoading) {
    return (
      <div className="bg-base min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-brand-secondary mb-4"></div>
          <p className="text-text-primary">Analisando seu perfil...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return null
  }

  return (
    <div className="bg-base min-h-screen">
      <div className="container mx-auto px-4 py-12">
        <div className="bg-surface rounded-lg p-6 border border-border mb-12">
          <h2 className="text-lg font-semibold mb-6 text-text-primary">Seu perfil de jogador</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-text-muted mb-1">Nível</p>
              <p className="text-lg font-bold text-text-primary">
                {identityLabels[profile.level] || 'Não classificado'}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted mb-1">Estilo</p>
              <p className="text-lg font-bold text-text-primary">
                {styleLabels[profile.style] || 'Não classificado'}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted mb-1">Prioridade</p>
              <p className="text-lg font-bold text-text-primary capitalize">
                {profile.priority || 'Não classificado'}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted mb-1">Orçamento</p>
              <p className="text-lg font-bold text-text-primary">
                {budgetLabels[profile.budget] || 'Não definido'}
              </p>
            </div>
          </div>
        </div>

        <h3 className="text-xl font-bold mb-8 text-text-primary">
          Nossas recomendações para você
        </h3>

        {recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendations.map((paddle, index) => (
              <div
                key={paddle.id}
                className="bg-surface rounded-lg p-4 shadow-md border border-border"
                style={{ animationDelay: `${index * 150}ms`, animationFillMode: 'both' }}
              >
                <div
                  className={`inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider rounded mb-4 ${badgeClasses[index]}`}
                >
                  {badgeLabels[index]}
                </div>

                <div className="flex items-start gap-4 mb-4">
                  <div className="w-24 h-36 rounded overflow-hidden flex-shrink-0 bg-elevated">
                    {paddle.image_url ? (
                      <SafeImage
                        src={paddle.image_url}
                        alt={paddle.name}
                        width={96}
                        height={144}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-xs text-text-muted">
                        Foto
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-brand-primary uppercase tracking-wider mb-1">
                      {paddle.brand || ''}
                    </div>
                    <h4 className="text-lg font-bold text-text-primary mb-1">{paddle.name}</h4>
                    <div className="text-text-primary font-mono text-lg font-bold">
                      R$ {paddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
                    </div>
                  </div>
                </div>

                <div className="bg-elevated rounded-lg p-3 mt-2">
                  <p className="text-xs font-bold text-brand-primary uppercase tracking-wider mb-2">
                    Por que pra você
                  </p>
                  <ul className="space-y-1 text-sm text-text-primary">
                    {profile.level === 'beginner' && <li className="flex items-start gap-1">
                      <span className="text-brand-primary">✓</span>
                      <span>Perfeita para iniciantes</span>
                    </li>}
                    {profile.style === 'all-round' && <li className="flex items-start gap-1">
                      <span className="text-brand-primary">✓</span>
                      <span>Equilibrada para seu estilo</span>
                    </li>}
                    {profile.budget === '250-plus' && <li className="flex items-start gap-1">
                      <span className="text-brand-primary">✓</span>
                      <span>Excelente custo-benefício</span>
                    </li>}
                    {profile.priority === 'control' && <li className="flex items-start gap-1">
                      <span className="text-brand-primary">✓</span>
                      <span>Foco em precisão e controle</span>
                    </li>}
                    {profile.priority === 'power' && <li className="flex items-start gap-1">
                      <span className="text-brand-primary">✓</span>
                      <span>Potência para suas batidas</span>
                    </li>}
                  </ul>
                </div>

                <div className="mt-4">
                  <Link
                    href={`/catalog/${encodeURIComponent(paddle.model_slug || String(paddle.id))}`}
                    className="inline-flex items-center justify-center rounded-lg font-medium h-8 px-2.5 gap-1.5 w-full bg-brand-secondary hover:bg-brand-secondary/80 text-white"
                  >
                    VER NO SITE →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 border border-dashed border-border rounded-lg">
            <p className="text-text-primary mb-4">
              Nenhuma raquete encontrada para seu nível.
            </p>
            <Link
              href="/catalog"
              className="inline-flex items-center justify-center rounded-lg font-medium h-8 px-2.5 gap-1.5 bg-brand-secondary hover:bg-brand-secondary/80 text-white"
            >
              VER CATÁLOGO COMPLETO
            </Link>
          </div>
        )}

        <div className="mt-12 flex flex-wrap gap-4 justify-center">
          <Link
            href="/chat"
            className="inline-flex items-center justify-center rounded-lg font-medium h-8 px-2.5 gap-1.5 border-border bg-background hover:bg-muted hover:text-foreground"
          >
            Falar com nossa IA
          </Link>
          <Link
            href="/catalog"
            className="inline-flex items-center justify-center rounded-lg font-medium h-8 px-2.5 gap-1.5 hover:bg-muted hover:text-foreground"
          >
            Ver catálogo completo
          </Link>
        </div>

        <div className="mt-12 text-center">
          <button
            onClick={handleRefactorQuiz}
            className="text-sm text-text-muted hover:text-brand-secondary transition-colors"
          >
            Refazer quiz
          </button>
        </div>
      </div>
    </div>
  )
}
