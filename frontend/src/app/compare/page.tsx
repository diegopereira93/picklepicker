'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, ExternalLink, GitCompare, SearchX, Brain } from 'lucide-react'
import { fetchPaddle } from '@/lib/api'
import { resolveAffiliateUrl, trackAffiliateClick } from '@/lib/affiliate'
import { loadQuizProfile } from '@/lib/quiz-profile'
import { TypingIndicator } from '@/components/ui/typing-indicator'
import { CompareRow } from '@/components/ui/compare-row'
import { RadarChart } from '@/components/ui/radar-chart'
import { PriceTag } from '@/components/ui/price-tag'
import { SafeImage } from '@/components/ui/safe-image'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import type { Paddle } from '@/types/paddle'

const RADAR_DATA = [
  { attribute: 'Power', fullMark: 10, valueA: 5, valueB: 5 },
  { attribute: 'Control', fullMark: 10, valueA: 5, valueB: 5 },
  { attribute: 'Spin', fullMark: 10, valueA: 5, valueB: 5 },
  { attribute: 'Speed', fullMark: 10, valueA: 5, valueB: 5 },
  { attribute: 'Sweet Spot', fullMark: 10, valueA: 5, valueB: 5 },
]

interface CompareVerdictProps {
  paddleA: Paddle
  paddleB: Paddle
}

function CompareVerdict({ paddleA, paddleB }: CompareVerdictProps) {
  const [verdict, setVerdict] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    const fetchVerdict = async () => {
      try {
        const profile = loadQuizProfile()
        const prompt = buildComparisonPrompt(paddleA, paddleB, profile)
        
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: [{ role: 'user', content: prompt }],
            profile: profile ? {
              level: profile.level,
              style: profile.style,
              budget_max: getBudgetMax(profile.budget),
            } : undefined,
          }),
        })

        if (!response.ok) {
          setHasError(true)
          setIsLoading(false)
          return
        }

        const reader = response.body?.getReader()
        if (!reader) {
          setHasError(true)
          setIsLoading(false)
          return
        }

        const decoder = new TextDecoder()
        let buffer = ''
        let fullResponse = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() ?? ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim()
              if (data) {
                try {
                  const parsed = JSON.parse(data)
                  if (parsed.type === 'text-delta' && parsed.delta) {
                    const deltaText = parsed.delta
                    fullResponse += deltaText
                    setVerdict(fullResponse)
                  }
                } catch {}
              }
            }
          }
        }

        setIsLoading(false)
      } catch {
        setHasError(true)
        setIsLoading(false)
      }
    }

    if (paddleA && paddleB) {
      fetchVerdict()
    }
  }, [paddleA, paddleB])

  if (hasError) {
    return (
      <p className="font-sans text-base text-text-secondary leading-relaxed">
        Nao foi possivel gerar o veredito da IA no momento. Tente novamente mais tarde.
      </p>
    )
  }

  return (
    <div>
      {isLoading && <TypingIndicator />}
      <p className="font-sans text-base text-text-secondary leading-relaxed">
        {verdict}
      </p>
    </div>
  )
}

function buildComparisonPrompt(a: Paddle, b: Paddle, profile: any): string {
  const prompt = `Compare estas duas raquetes de pickleball:

${a.brand} ${a.name}
- Preco: R$ ${a.price_min_brl ?? a.price_brl}
- Peso: ${a.specs?.weight_oz ? a.specs.weight_oz + ' oz' : '-'}
- Swingweight: ${a.specs?.swingweight ?? '-'}
- Twistweight: ${a.specs?.twistweight ?? '-'}
- Nivel: ${a.skill_level ?? '-'}

vs

${b.brand} ${b.name}
- Preco: R$ ${b.price_min_brl ?? b.price_brl}
- Peso: ${b.specs?.weight_oz ? b.specs.weight_oz + ' oz' : '-'}
- Swingweight: ${b.specs?.swingweight ?? '-'}
- Twistweight: ${b.specs?.twistweight ?? '-'}
- Nivel: ${b.skill_level ?? '-'}

Dê um veredito conciso sobre qual e melhor e por que. Responda em portugues.`

  if (profile) {
    const profilesText = `O jogador e um jogador ${profile.level} com estilo ${profile.style}, priorizando ${profile.priority}, orcamento ${profile.budget}.`
    return `${prompt}\n\n${profilesText}`
  }

  return prompt
}

function getBudgetMax(budget: string): number {
  const budgetMap: Record<string, number> = {
    'under-80': 80,
    '80-150': 150,
    '150-250': 250,
    '250-plus': 500,
  }
  return budgetMap[budget] ?? 600
}

function buildSpecs(a: Paddle, b: Paddle) {
  const priceA = a.price_min_brl ?? a.price_brl ?? 0
  const priceB = b.price_min_brl ?? b.price_brl ?? 0
  return [
    { attribute: 'Preco', valueA: `R$ ${priceA}`, valueB: `R$ ${priceB}`, winner: priceA < priceB ? 'a' : priceB < priceA ? 'b' : 'tie' },
    { attribute: 'Peso', valueA: a.specs?.weight_oz ? `${a.specs.weight_oz} oz` : '-', valueB: b.specs?.weight_oz ? `${b.specs.weight_oz} oz` : '-' },
    { attribute: 'Swingweight', valueA: a.specs?.swingweight?.toString() ?? '-', valueB: b.specs?.swingweight?.toString() ?? '-' },
    { attribute: 'Twistweight', valueA: a.specs?.twistweight?.toString() ?? '-', valueB: b.specs?.twistweight?.toString() ?? '-' },
    { attribute: 'Grip Size', valueA: a.specs?.grip_size ?? '-', valueB: b.specs?.grip_size ?? '-' },
    { attribute: 'Core Thickness', valueA: a.specs?.core_thickness_mm ? `${a.specs.core_thickness_mm}mm` : '-', valueB: b.specs?.core_thickness_mm ? `${b.specs.core_thickness_mm}mm` : '-' },
    { attribute: 'Face Material', valueA: a.specs?.face_material ?? '-', valueB: b.specs?.face_material ?? '-' },
    { attribute: 'Nivel', valueA: a.skill_level ?? '-', valueB: b.skill_level ?? '-' },
    { attribute: 'Rating', valueA: a.rating?.toString() ?? '-', valueB: b.rating?.toString() ?? '-' },
    { attribute: 'Estoque', valueA: a.in_stock ? 'Em estoque' : 'Fora de estoque', valueB: b.in_stock ? 'Em estoque' : 'Fora de estoque' },
  ]
}

function CompareContent() {
  const searchParams = useSearchParams()
  const paddleAId = searchParams.get('a')
  const paddleBId = searchParams.get('b')

  const [paddleA, setPaddleA] = useState<Paddle | null>(null)
  const [paddleB, setPaddleB] = useState<Paddle | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (!paddleAId || !paddleBId) {
        setIsLoading(false)
        return
      }
      const [a, b] = await Promise.all([
        fetchPaddle(Number(paddleAId)),
        fetchPaddle(Number(paddleBId)),
      ])
      setPaddleA(a)
      setPaddleB(b)
      setIsLoading(false)
    }
    load()
  }, [paddleAId, paddleBId])

  const priceA = paddleA?.price_min_brl ?? paddleA?.price_brl ?? 0
  const priceB = paddleB?.price_min_brl ?? paddleB?.price_brl ?? 0
  const specs = paddleA && paddleB ? buildSpecs(paddleA, paddleB) : []

  const isEmpty = !paddleAId || !paddleBId
  const isNotFound = !isLoading && !isEmpty && (!paddleA || !paddleB)

  return (
    <div className="min-h-screen bg-base">
      {isEmpty && (
        <div className="max-w-md mx-auto text-center py-20 px-4">
          <GitCompare className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h1 className="font-display text-2xl text-text-primary tracking-wide mb-4">
            COMPARAR RAQUETES
          </h1>
          <p className="font-sans text-text-secondary mb-8">
            Selecione duas raquetes para ver a comparacao detalhada.
          </p>
          <Link
            href="/catalog"
            className="inline-block px-6 py-2 bg-brand-primary text-base font-semibold rounded-rounded hover:bg-brand-primary/90 transition-colors"
          >
            Ver Catalogo
          </Link>
        </div>
      )}

      {isLoading && (
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {[1, 2].map(i => (
              <div key={i} className="space-y-4">
                <Skeleton className="h-64 rounded-lg w-full" />
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-10 w-full" />
              </div>
            ))}
          </div>
          <Skeleton className="h-72 rounded-lg w-full" />
        </div>
      )}

      {isNotFound && (
        <div className="max-w-md mx-auto text-center py-20 px-4">
          <SearchX className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h1 className="font-sans font-semibold text-xl text-text-primary mb-2">
            Raquete nao encontrada
          </h1>
          <p className="font-sans text-sm text-text-muted mb-8">
            Busque por outro modelo ou volte ao catalogo.
          </p>
          <Link
            href="/catalog"
            className="inline-block px-6 py-2 bg-brand-primary text-base font-semibold rounded-rounded hover:bg-brand-primary/90 transition-colors"
          >
            Ver Catalogo
          </Link>
        </div>
      )}

      {!isEmpty && !isLoading && !isNotFound && paddleA && paddleB && (
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
          <Link
            href="/catalog"
            className="inline-flex items-center gap-1.5 text-text-muted hover:text-text-primary text-sm transition-colors mb-6"
          >
            <ArrowLeft size={16} />
            Catalogo
          </Link>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {[paddleA, paddleB].map((paddle, i) => (
              <div key={paddle.id} className="bg-surface border border-border rounded-lg p-5">
                <div className="aspect-[4/3] rounded-lg overflow-hidden bg-elevated mb-3">
                  <SafeImage
                    src={paddle.image_url}
                    alt={`${paddle.brand} ${paddle.name}`}
                    fallbackClassName="w-full h-full bg-elevated flex items-center justify-center text-text-muted text-xs"
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                  />
                </div>
                <p className="font-sans text-xs text-text-muted uppercase tracking-wide">
                  {paddle.brand}
                </p>
                <h1 className="font-display text-2xl text-text-primary tracking-wide mt-1">
                  {paddle.name}
                </h1>
                <div className="mt-3">
                  <PriceTag price={i === 0 ? priceA : priceB} currency="BRL" size="lg" />
                </div>
                <Button
                  variant="default"
                  className="w-full mt-4 bg-brand-primary hover:bg-brand-primary/90 text-base hover:shadow-glow-green"
                  asChild
                >
                  <a
                    href={resolveAffiliateUrl({ paddleId: String(paddle.id), page: 'compare-card' })}
                    target="_blank"
                    rel="noopener noreferrer sponsored"
                    className="flex items-center justify-center gap-2"
                    onClick={() => trackAffiliateClick(String(paddle.id), 'brazil-store', 'compare-card')}
                  >
                    Comprar Agora
                    <ExternalLink size={16} />
                  </a>
                </Button>
              </div>
            ))}
          </div>

          <div className="bg-surface rounded-lg border border-border overflow-hidden mb-8">
            <h2 className="font-sans font-semibold text-lg text-text-primary p-4 border-b border-border">
              ESPECIFICACOES TECNICAS
            </h2>
            {specs.map((row) => (
              <CompareRow
                key={row.attribute}
                attribute={row.attribute}
                valueA={row.valueA}
                valueB={row.valueB}
                winner={row.winner as 'a' | 'b' | 'tie'}
              />
            ))}
          </div>

          <div className="bg-elevated rounded-lg border border-border p-6 mb-8">
            <h2 className="font-sans font-semibold text-lg text-text-primary mb-4">
              Comparacao de Desempenho
            </h2>
            <RadarChart data={RADAR_DATA} />
            <div className="flex gap-6 justify-center mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-brand-primary" />
                <span className="font-sans text-sm text-text-secondary">{paddleA.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-brand-secondary" />
                <span className="font-sans text-sm text-text-secondary">{paddleB.name}</span>
              </div>
            </div>
          </div>

          <div className="bg-surface rounded-lg border border-border p-6 mb-8">
            <h2 className="font-sans font-semibold text-lg text-text-primary mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-brand-primary" />
              Veredito IA
            </h2>
            <CompareVerdict paddleA={paddleA} paddleB={paddleB} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button
              variant="default"
              className="bg-brand-primary hover:bg-brand-primary/90 text-base hover:shadow-glow-green"
              asChild
            >
              <a
                href={resolveAffiliateUrl({ paddleId: String(paddleA.id), page: 'compare-cta' })}
                target="_blank"
                rel="noopener noreferrer sponsored"
                className="flex items-center justify-center gap-2 py-3"
                onClick={() => trackAffiliateClick(String(paddleA.id), 'brazil-store', 'compare-cta')}
              >
                Comprar {paddleA.name}
                <ExternalLink size={16} />
              </a>
            </Button>
            <Button
              variant="default"
              className="bg-brand-primary hover:bg-brand-primary/90 text-base hover:shadow-glow-green"
              asChild
            >
              <a
                href={resolveAffiliateUrl({ paddleId: String(paddleB.id), page: 'compare-cta' })}
                target="_blank"
                rel="noopener noreferrer sponsored"
                className="flex items-center justify-center gap-2 py-3"
                onClick={() => trackAffiliateClick(String(paddleB.id), 'brazil-store', 'compare-cta')}
              >
                Comprar {paddleB.name}
                <ExternalLink size={16} />
              </a>
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ComparePage() {
  return (
    <Suspense>
      <CompareContent />
    </Suspense>
  )
}
