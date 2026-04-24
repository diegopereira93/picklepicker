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
import { Skeleton } from '@/components/ui/skeleton'
import { Breadcrumb } from '@/components/ui/breadcrumb'
import type { Paddle } from '@/types/paddle'

interface RadarDataPoint {
  attribute: string
  fullMark: number
  valueA: number
  valueB: number
}

function buildRadarData(a: Paddle, b: Paddle): RadarDataPoint[] {
  const estimate = (p: Paddle, attr: string): number => {
    const specMap: Record<string, number> = {
      'Power': (p.specs?.swingweight ?? 110) / 15,
      'Control': (p.specs?.twistweight ?? 6) * 1.2,
      'Spin': p.specs?.face_material?.toLowerCase().includes('carbon') ? 7.5 : 5,
      'Speed': (p.specs?.weight_oz ?? 8) * 0.9,
      'Sweet Spot': (p.specs?.twistweight ?? 6) * 1.1,
    }
    return Math.min(10, Math.max(1, specMap[attr] ?? 5))
  }
  return [
    { attribute: 'Power', fullMark: 10, valueA: estimate(a, 'Power'), valueB: estimate(b, 'Power') },
    { attribute: 'Control', fullMark: 10, valueA: estimate(a, 'Control'), valueB: estimate(b, 'Control') },
    { attribute: 'Spin', fullMark: 10, valueA: estimate(a, 'Spin'), valueB: estimate(b, 'Spin') },
    { attribute: 'Speed', fullMark: 10, valueA: estimate(a, 'Speed'), valueB: estimate(b, 'Speed') },
    { attribute: 'Sweet Spot', fullMark: 10, valueA: estimate(a, 'Sweet Spot'), valueB: estimate(b, 'Sweet Spot') },
  ]
}

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

function buildComparisonPrompt(a: Paddle, b: Paddle, profile: ReturnType<typeof loadQuizProfile>): string {
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

type WinnerLetter = 'a' | 'b' | 'c' | 'd' | 'tie' | null

function buildSpecs(paddles: Paddle[]) {
  const INDEX_LETTERS: ('a' | 'b' | 'c' | 'd')[] = ['a', 'b', 'c', 'd']

  const computeWinners = (
    values: (string | number | null)[],
    lowerIsBetter: boolean
  ): WinnerLetter[] => {
    const numeric = values.map(v => typeof v === 'number' ? v : null)
    const valid = numeric.filter((v): v is number => v !== null)
    if (valid.length < 2) return values.map(() => null)
    const best = lowerIsBetter ? Math.min(...valid) : Math.max(...valid)
    const hasMultiple = valid.filter(v => v === best).length > 1
    if (hasMultiple) return values.map(() => 'tie' as const)
    return numeric.map(v => v === best ? INDEX_LETTERS[numeric.indexOf(v)] : null)
  }

  const priceValues = paddles.map(p => p.price_min_brl ?? p.price_brl ?? null)
  const priceDisplay = paddles.map(p => {
    const price = p.price_min_brl ?? p.price_brl
    return price != null ? `R$ ${price}` : null
  })

  return [
    { attribute: 'Preco', values: priceDisplay, winners: computeWinners(priceValues, true) },
    { attribute: 'Peso', values: paddles.map(p => p.specs?.weight_oz != null ? `${p.specs.weight_oz} oz` : null), winners: paddles.map(() => null) },
    { attribute: 'Swingweight', values: paddles.map(p => p.specs?.swingweight != null ? p.specs.swingweight : null), winners: computeWinners(paddles.map(p => p.specs?.swingweight != null ? p.specs.swingweight : null), false) },
    { attribute: 'Twistweight', values: paddles.map(p => p.specs?.twistweight != null ? p.specs.twistweight : null), winners: computeWinners(paddles.map(p => p.specs?.twistweight != null ? p.specs.twistweight : null), false) },
    { attribute: 'Grip Size', values: paddles.map(p => p.specs?.grip_size ?? null), winners: paddles.map(() => null) },
    { attribute: 'Core Thickness', values: paddles.map(p => p.specs?.core_thickness_mm != null ? `${p.specs.core_thickness_mm}mm` : null), winners: paddles.map(() => null) },
    { attribute: 'Face Material', values: paddles.map(p => p.specs?.face_material ?? null), winners: paddles.map(() => null) },
    { attribute: 'Nivel', values: paddles.map(p => p.skill_level ?? null), winners: paddles.map(() => null) },
    { attribute: 'Rating', values: paddles.map(p => p.rating != null ? p.rating : null), winners: computeWinners(paddles.map(p => p.rating != null ? p.rating : null), false) },
    { attribute: 'Estoque', values: paddles.map(p => p.in_stock ? 'Em estoque' : 'Fora de estoque'), winners: paddles.map(() => null) },
  ]
}

const PADDLE_PARAM_KEYS = ['a', 'b', 'c', 'd']

function CompareContent() {
  const searchParams = useSearchParams()

  const paddleIds = PADDLE_PARAM_KEYS
    .map(key => searchParams.get(key))
    .filter(Boolean)
    .map(Number)
    .filter(id => id > 0)

  const [paddles, setPaddles] = useState<Paddle[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (paddleIds.length < 2 || paddleIds.length > 4) {
        setIsLoading(false)
        return
      }
      const results = await Promise.all(paddleIds.map(id => fetchPaddle(id)))
      setPaddles(results.filter(Boolean) as Paddle[])
      setIsLoading(false)
    }
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- paddleIds is derived from searchParams
  }, [searchParams])

  const count = paddleIds.length
  const invalidCount = count < 2 || count > 4
  const isNotFound = !isLoading && !invalidCount && paddles.length === 0

  const specs = paddles.length >= 2 ? buildSpecs(paddles) : []
  const radarData = paddles.length === 2 ? buildRadarData(paddles[0], paddles[1]) : []

  return (
    <div className="min-h-screen bg-base">
      {invalidCount && (
        <div className="max-w-md mx-auto text-center py-20 px-4">
          <GitCompare className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h1 className="font-display text-2xl text-text-primary tracking-wide mb-4">
            COMPARAR RAQUETES
          </h1>
          <p className="font-sans text-text-secondary mb-8">
            {count === 0 || count === 1
              ? 'Selecione entre 2 e 4 raquetes para comparar.'
              : 'Selecione entre 2 e 4 raquetes para comparar.'}
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 mb-8">
            {(paddleIds.length > 0 ? paddleIds : [1, 2]).map((_id, i) => (
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

      {!invalidCount && !isLoading && !isNotFound && paddles.length >= 2 && (
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
          <Breadcrumb
            items={[
              { label: 'Início', href: '/' },
              { label: 'Comparar Raquetes' },
            ]}
            className="mb-4"
          />
          <Link
            href="/catalog"
            className="inline-flex items-center gap-1.5 text-text-muted hover:text-text-primary text-sm transition-colors mb-6"
          >
            <ArrowLeft size={16} />
            Catalogo
          </Link>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 mb-8">
            {paddles.map((paddle) => (
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
                  <PriceTag price={paddle.price_min_brl ?? paddle.price_brl ?? 0} currency="BRL" size="lg" />
                </div>
                <a
                  href={resolveAffiliateUrl({ paddleId: String(paddle.id), page: 'compare-card' })}
                  target="_blank"
                  rel="noopener noreferrer sponsored"
                  className="w-full mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-brand-primary hover:bg-brand-primary/90 text-base hover:shadow-glow-green px-2.5 h-9 font-medium"
                  onClick={() => trackAffiliateClick(String(paddle.id), 'brazil-store', 'compare-card')}
                >
                  Comprar Agora
                  <ExternalLink size={16} />
                </a>
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
                values={row.values}
                winners={row.winners}
              />
            ))}
          </div>

          {paddles.length === 2 && (
            <div className="bg-elevated rounded-lg border border-border p-6 mb-8">
              <h2 className="font-sans font-semibold text-lg text-text-primary mb-4">
                Comparacao de Desempenho
              </h2>
              <RadarChart data={radarData} />
              <div className="flex gap-6 justify-center mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-brand-primary" />
                  <span className="font-sans text-sm text-text-secondary">{paddles[0].name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-brand-secondary" />
                  <span className="font-sans text-sm text-text-secondary">{paddles[1].name}</span>
                </div>
              </div>
            </div>
          )}

          {paddles.length === 2 && (
            <div className="bg-surface rounded-lg border border-border p-6 mb-8">
              <h2 className="font-sans font-semibold text-lg text-text-primary mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5 text-brand-primary" />
                Veredito IA
              </h2>
              <CompareVerdict paddleA={paddles[0]} paddleB={paddles[1]} />
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {paddles.map((paddle) => (
              <a
                key={paddle.id}
                href={resolveAffiliateUrl({ paddleId: String(paddle.id), page: 'compare-cta' })}
                target="_blank"
                rel="noopener noreferrer sponsored"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-primary hover:bg-brand-primary/90 text-base hover:shadow-glow-green px-2.5 py-3 font-medium"
                onClick={() => trackAffiliateClick(String(paddle.id), 'brazil-store', 'compare-cta')}
              >
                Comprar {paddle.name}
                <ExternalLink size={16} />
              </a>
            ))}
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
