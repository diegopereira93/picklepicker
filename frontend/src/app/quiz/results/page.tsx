'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import type { Paddle, UserProfile } from '@/types/paddle'
import { getProfile, clearProfile } from '@/lib/profile'
import { fetchPaddles } from '@/lib/api'
import { SafeImage } from '@/components/ui/safe-image'

export default function QuizResultsPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [recommendations, setRecommendations] = useState<Paddle[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadProfileAndRecommendations = async () => {
      const storedProfile = getProfile()
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
    clearProfile()
    router.push('/quiz')
  }

  const badgeLabels = ['MELHOR COMBINACAO', 'MELHOR CUSTO-BENEFICIO', 'MELHOR PARA EVOLUIR']
  const badgeClasses = [
    'bg-[#F97316] text-white',
    'bg-[#84CC16] text-[#2A2A2A]',
    'bg-[#0EA5E9] text-white',
  ]

  if (isLoading) {
    return (
      <div className="wg-container min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#F97316] mb-4"></div>
          <p className="text-[#2A2A2A]">Analisando seu perfil...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return null
  }

  const identityLabels: Record<string, string> = {
    beginner: 'Estou comecando',
    regular: 'Jogo regularmente',
    serious: 'Levo o jogo a serio',
  }
  const styleLabels: Record<string, string> = {
    control: 'Controle',
    power: 'Potencia',
    balanced: 'Equilibrado',
  }
  const levelLabels: Record<string, string> = {
    beginner: 'Iniciante',
    intermediate: 'Intermediario',
    advanced: 'Avancado',
    professional: 'Profissional',
  }

  return (
    <div className="wg-container py-12">
      <div className="wg-profile-summary mb-12">
        <h2 className="text-lg font-semibold mb-6">Seu perfil de jogador</h2>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <p className="text-sm opacity-90 mb-1">Tipo</p>
            <p className="text-lg font-bold">
              {identityLabels[profile.level] || profile.identity || 'Nao classificado'}
            </p>
          </div>
          <div>
            <p className="text-sm opacity-90 mb-1">Estilo</p>
            <p className="text-lg font-bold">
              {styleLabels[profile.style] || profile.style || 'Nao classificado'}
            </p>
          </div>
          <div>
            <p className="text-sm opacity-90 mb-1">Nivel</p>
            <p className="text-lg font-bold">
              {levelLabels[profile.level] || profile.level || 'Nao classificado'}
            </p>
          </div>
          <div>
            <p className="text-sm opacity-90 mb-1">Orcamento</p>
            <p className="text-lg font-bold">
              ate R$ {profile.budget_max.toLocaleString('pt-BR')}
            </p>
          </div>
        </div>
      </div>

      <h3 className="text-xl font-bold mb-8 text-[#2A2A2A]">
        Nossas recomendacoes para voce
      </h3>

      {recommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recommendations.map((paddle, index) => (
            <div
              key={paddle.id}
              className="wg-recommendation-card wg-animate-fade-up"
              style={{ animationDelay: `${index * 150}ms`, animationFillMode: 'both' }}
            >
              <div
                className={`inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider rounded mb-4 ${badgeClasses[index]}`}
              >
                {badgeLabels[index]}
              </div>

              <div className="flex items-start gap-4 mb-4">
                <div className="w-24 h-36 rounded overflow-hidden flex-shrink-0 bg-[#F5F2EB]">
                  {paddle.image_url ? (
                    <SafeImage
                      src={paddle.image_url}
                      alt={paddle.name}
                      width={96}
                      height={144}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-[#757575]">
                      Foto
                    </div>
                  )}
                </div>
                <div>
                  <div className="text-xs font-bold text-[#84CC16] uppercase tracking-wider mb-1">
                    {paddle.brand || ''}
                  </div>
                  <h4 className="text-lg font-bold text-[#2A2A2A] mb-1">{paddle.name}</h4>
                  <div className="text-[#2A2A2A] font-mono text-lg font-bold">
                    R$ {paddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
                  </div>
                </div>
              </div>

              <div className="wg-why-matches">
                <p className="text-xs font-bold text-[#84CC16] uppercase tracking-wider mb-2">
                  Por que pra voce
                </p>
                <ul className="space-y-1 text-sm text-[#2A2A2A]">
                  {profile.level === 'beginner' && <li className="flex items-start gap-1">
                    <span className="text-[#84CC16]">✓</span>
                    <span>Perfeita para iniciantes</span>
                  </li>}
                  {profile.style === 'balanced' && <li className="flex items-start gap-1">
                    <span className="text-[#84CC16]">✓</span>
                    <span>Equilibrada para seu estilo</span>
                  </li>}
                  {profile.budget_max >= 500 && <li className="flex items-start gap-1">
                    <span className="text-[#84CC16]">✓</span>
                    <span>Excelente custo-beneficio</span>
                  </li>}
                  {profile.frequency === '2-3x' && <li className="flex items-start gap-1">
                    <span className="text-[#84CC16]">✓</span>
                    <span>Bom para quem joga 2-3x/semana</span>
                  </li>}
                  {profile.pain_points?.includes('Erro muitos tiros na rede') && <li className="flex items-start gap-1">
                    <span className="text-[#84CC16]">✓</span>
                    <span>Melhora precisao na rede</span>
                  </li>}
                  {profile.pain_points?.includes('Nao consigo gerar spin') && <li className="flex items-start gap-1">
                    <span className="text-[#84CC16]">✓</span>
                    <span>Boa para gerar spin</span>
                  </li>}
                </ul>
              </div>

              <div className="mt-4">
                <Link
                  href={{
                    pathname: `/paddles/${encodeURIComponent((paddle.brand || 'unknown').toLowerCase())}/${encodeURIComponent(paddle.model_slug || String(paddle.id))}`,
                  }}
                  className="wg-button-coral inline-flex items-center justify-center w-full py-2.5 px-4 text-sm font-semibold rounded hover:bg-[#EA580C] transition-colors"
                >
                  VER NO SITE →
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 border border-dashed border-[#757575] rounded-lg">
          <p className="text-[#2A2A2A] mb-4">
            Nenhuma raquete encontrada para seu nivel.
          </p>
          <Link
            href="/paddles"
            className="wg-button-coral inline-block px-6 py-2"
          >
            VER CATALOGO COMPLETO
          </Link>
        </div>
      )}

      <div className="mt-12 flex flex-wrap gap-4 justify-center">
        <Link
          href="/chat"
          className="wg-button-outline inline-flex items-center justify-center px-6 py-2.5 rounded hover:bg-[#F97316]/5 transition-colors"
        >
          Falar com nossa IA
        </Link>
        <Link
          href="/paddles"
          className="wg-button-ghost inline-flex items-center justify-center px-6 py-2.5 rounded hover:text-[#F97316] transition-colors"
        >
          Ver catalogo completo
        </Link>
      </div>

      <div className="mt-12 text-center">
        <button
          onClick={handleRefactorQuiz}
          className="text-sm text-[#757575] hover:text-[#F97316] transition-colors"
        >
          Refazer quiz
        </button>
      </div>
    </div>
  )
}
