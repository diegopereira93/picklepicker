import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { fetchPaddles, fetchLatestPrices } from '@/lib/api'
import { resolveAffiliateUrl } from '@/lib/affiliate'
import { cn } from '@/lib/utils'
import { ExternalLink, GitCompare, SearchX, Star } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PriceTag } from '@/components/ui/price-tag'
import { PriceChart } from '@/components/ui/price-chart'
import { SafeImage } from '@/components/ui/safe-image'
import { Breadcrumb } from '@/components/ui/breadcrumb'
import { PriceAlertButton } from '@/components/ui/price-alert-button'
import Link from 'next/link'

interface PageParams {
  slug: string
}

function toSlug(p: { brand?: string; name: string; model_slug?: string | null }): string {
  if (p.model_slug) return p.model_slug
  return `${p.brand}-${p.name}`.toLowerCase().replace(/\s+/g, '-')
}

function findBySlug<T extends { id: number; name: string; brand?: string; model_slug?: string | null }>(items: T[], slug: string): T | undefined {
  return items.find((p) => toSlug(p) === slug || p.id.toString() === slug)
}

export async function generateMetadata({
  params,
}: {
  params: PageParams
}): Promise<Metadata | null> {
  const slug = decodeURIComponent(params.slug)
  const allPaddles = await fetchPaddles({ limit: 100 })
  const paddle = findBySlug(allPaddles.items, slug)

  if (!paddle) {
    return {
      title: 'Raquete não encontrada',
    }
  }

  return {
    title: `${paddle.brand} ${paddle.name} — PickleIQ`,
    description: paddle.description || `Compre a raquete ${paddle.name} de ${paddle.brand} com preços comparados.`,
    alternates: {
      canonical: `https://pickleiq.com/catalog/${slug}`,
    },
    openGraph: {
      type: 'website',
      url: `https://pickleiq.com/catalog/${slug}`,
      title: `${paddle.brand} ${paddle.name} — PickleIQ`,
      description: paddle.description || `Compare preços e especificações da raquete ${paddle.name}.`,
    },
  }
}

export const dynamic = 'force-dynamic'
export const revalidate = 0

export default async function CatalogDetailPage({
  params,
}: {
  params: PageParams
}) {
  const slug = decodeURIComponent(params.slug)
  const allPaddles = await fetchPaddles({ limit: 100 })

  const paddle = findBySlug(allPaddles.items, slug)

  if (!paddle) {
    notFound()
  }

  const priceData = await fetchLatestPrices(paddle.id)
  const similarPaddles = allPaddles.items
    .filter((p) => p.id !== paddle.id)
    .slice(0, 6)

  const productSchema = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: paddle.name,
    description: paddle.description || `${paddle.brand} ${paddle.name} — raquete de pickleball`,
    image: paddle.image_url || undefined,
    brand: {
      '@type': 'Brand',
      name: paddle.brand || 'Unknown',
    },
    offers: {
      '@type': 'Offer',
      price: paddle.price_brl ?? paddle.price_min_brl ?? 0,
      priceCurrency: 'BRL',
      availability: 'https://schema.org/InStock',
      url: `https://pickleiq.com/catalog/${paddle.model_slug || paddle.id}`,
      seller: {
        '@type': 'Organization',
        name: 'PickleIQ',
      },
    },
    ...(paddle.rating && {
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: paddle.rating,
        reviewCount: paddle.review_count || 1,
        bestRating: 5,
        worstRating: 1,
      },
    }),
  }

  return (
    <div className="min-h-screen bg-base">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(productSchema) }}
      />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: 'Início', href: '/' },
            { label: 'Catálogo', href: '/catalog' },
            { label: `${paddle.brand} ${paddle.name}` },
          ]}
          className="mb-6"
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
          <div className="relative group">
            <div className="bg-elevated rounded-lg overflow-hidden">
              <SafeImage
                src={paddle.image_url}
                alt={paddle.name}
                className="aspect-4/3 object-cover w-full transition-transform duration-200 group-hover:scale-105"
                fallbackClassName="aspect-4/3 bg-elevated rounded-lg flex items-center justify-center text-text-muted"
              />
            </div>
            <div className={cn(
              'absolute top-4 right-4 px-3 py-1 text-xs font-medium rounded-rounded',
              paddle.in_stock ? 'bg-brand-primary/10 text-brand-primary' : 'bg-price-up/10 text-price-up'
            )}>
              {paddle.in_stock ? 'Em estoque' : 'Fora de estoque'}
            </div>
          </div>

          <div>
            <p className="font-sans text-xs text-text-muted uppercase tracking-wide mb-2">
              {paddle.brand}
            </p>
            <h1 className="font-display text-4xl md:text-5xl text-text-primary tracking-wide mb-4">
              {paddle.name}
            </h1>
            <div className="mt-4">
              {paddle.price_brl != null ? (
                <PriceTag 
                  price={paddle.price_brl} 
                  size="lg"
                  className="font-mono text-4xl text-brand-primary"
                />
              ) : paddle.price_min_brl != null ? (
                <div className="font-mono text-4xl text-brand-primary">
                  De R$ {paddle.price_min_brl.toFixed(2)}
                </div>
              ) : null}
            </div>
            
            <p className="mt-2 text-text-secondary">
              {paddle.in_stock 
                ? 'Disponível para envio imediato' 
                : 'Previsão de chegada: entre em contato para saber mais'}
            </p>

            <Button 
              variant="default" 
              className="w-full mt-6 bg-brand-primary hover:bg-brand-primary/80 border-none"
              asChild
            >
              <a 
                href={resolveAffiliateUrl({ paddleId: String(paddle.id), page: 'product-detail' })} 
                target="_blank" 
                rel="noopener noreferrer sponsored"
                className="flex items-center justify-center gap-2"
              >
                Comprar Agora <ExternalLink size={16} />
              </a>
            </Button>

            <div className="flex gap-4 mt-4">
              <Button 
                variant="ghost"
                className="text-text-primary hover:bg-surface hover:text-text-primary"
                asChild
              >
                <Link href={`/compare?a=${paddle.id}`} className="flex items-center gap-2">
                  <GitCompare size={16} /> Comparar
                </Link>
              </Button>
              <PriceAlertButton
                paddle={{
                  id: paddle.id,
                  name: paddle.name,
                  brand: paddle.brand || '',
                  price_brl: paddle.price_brl,
                  price_min_brl: paddle.price_min_brl,
                }}
              />
            </div>
          </div>
        </div>

        {paddle.skill_level && (
          <div className="flex flex-wrap gap-2 mt-4">
            <span className="px-3 py-1 text-xs font-sans font-medium rounded-full bg-brand-primary/10 text-brand-primary border border-brand-primary/20">
              {paddle.skill_level === 'beginner' ? 'Iniciante' : paddle.skill_level === 'intermediate' ? 'Intermediario' : paddle.skill_level === 'advanced' ? 'Avancado' : paddle.skill_level}
            </span>
            {paddle.specs?.weight_oz && (
              <span className="px-3 py-1 text-xs font-sans font-medium rounded-full bg-elevated text-text-secondary border border-border">
                {paddle.specs.weight_oz < 7.5 ? 'Leve' : paddle.specs.weight_oz <= 8.2 ? 'Medio' : 'Pesado'}
              </span>
            )}
            {paddle.specs?.face_material && (
              <span className="px-3 py-1 text-xs font-sans font-medium rounded-full bg-elevated text-text-secondary border border-border">
                {paddle.specs.face_material}
              </span>
            )}
          </div>
        )}

        <div className="bg-surface rounded-lg border border-border p-6 mt-8">
          <h2 className="font-sans font-semibold text-lg text-text-primary mb-4">
            ESPECIFICAÇÕES TÉCNICAS
          </h2>
          <dl className="space-y-2">
            {[
              { label: 'Swingweight', value: paddle.specs?.swingweight },
              { label: 'Twistweight', value: paddle.specs?.twistweight },
              { label: 'Peso (oz)', value: paddle.specs?.weight_oz },
              { label: 'Grip size', value: paddle.specs?.grip_size },
              { label: 'Core thickness (mm)', value: paddle.specs?.core_thickness_mm },
              { label: 'Face material', value: paddle.specs?.face_material },
            ].map((spec, index) => (
              <div 
                key={spec.label} 
                className={cn(
                  'grid grid-cols-2 gap-4 px-4 py-3',
                  index % 2 === 0 ? 'bg-surface' : 'bg-elevated'
                )}
              >
                <dt className="font-sans text-sm text-text-muted">{spec.label}</dt>
                <dd className="font-mono text-sm text-text-primary text-right">
                  {spec.value != null ? spec.value : '-'}
                </dd>
              </div>
            ))}
          </dl>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div className="bg-surface px-4 py-3">
              <dt className="font-sans text-sm text-text-muted">Nível de jogo</dt>
              <dd className="font-mono text-sm text-text-primary mt-1">
                {paddle.skill_level ? (
                  <span className="capitalize">{translateSkillLevel(paddle.skill_level)}</span>
                ) : '-'}
              </dd>
            </div>
            <div className="bg-elevated px-4 py-3">
              <dt className="font-sans text-sm text-text-muted">Avaliação</dt>
              <dd className="font-mono text-sm text-text-primary mt-1">
                <div className="flex items-center gap-1">
                  <Star size={14} className="text-amber-400 fill-current" />
                  {paddle.rating != null ? paddle.rating.toFixed(1) : '-'}
                  <span className="text-text-muted ml-1">({paddle.review_count || 0} avaliações)</span>
                </div>
              </dd>
            </div>
          </div>
        </div>

        {priceData?.latest_prices?.length > 0 && (
          <div className="bg-elevated rounded-lg border border-border p-6 mt-8">
            <h2 className="font-sans font-semibold text-lg text-text-primary mb-4">
              HISTÓRICO DE PREÇO
            </h2>
            <PriceChart
              prices={priceData.latest_prices.map((p) => ({
                date: new Date(p.scraped_at).toLocaleDateString('pt-BR'),
                price: p.price_brl,
              }))}
              variant="full"
            />
            <div className="flex gap-8 mt-4">
              <div>
                <p className="font-sans text-sm text-text-muted mb-1">Menor preço</p>
                <p className="font-mono text-sm text-brand-primary">
                  R$ {Math.min(...priceData.latest_prices.map(p => p.price_brl)).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="font-sans text-sm text-text-muted mb-1">Maior preço</p>
                <p className="font-mono text-sm text-brand-secondary">
                  R$ {Math.max(...priceData.latest_prices.map(p => p.price_brl)).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="font-sans text-sm text-text-muted mb-1">Preço atual</p>
                <p className="font-mono text-sm text-text-primary">
                  R$ {priceData.latest_prices[0]?.price_brl.toFixed(2) || '-'}
                </p>
              </div>
            </div>
          </div>
        )}

        {paddle.description && (
          <div className="mt-8">
            <h2 className="font-sans font-semibold text-lg text-text-primary mb-4">
              SOBRE
            </h2>
            <p className="font-sans text-base text-text-secondary leading-relaxed">
              {paddle.description}
            </p>
          </div>
        )}

        {similarPaddles.length > 0 && (
          <div className="mt-8">
            <h2 className="font-sans font-semibold text-lg text-text-primary mb-4">
              RAQUETES SIMILARES
            </h2>
            <div className="flex gap-4 overflow-x-auto pb-4 -mx-4 px-4">
              {similarPaddles.map((similar) => (
                <Link
                  key={similar.id}
                  href={`/catalog/${similar.model_slug || similar.id}`}
                  className="min-w-[200px] bg-surface border border-border rounded-lg overflow-hidden cursor-pointer hover:border-brand-primary/50 transition-colors"
                >
                  <div className="relative aspect-4/3 overflow-hidden">
                    <SafeImage
                      src={similar.image_url}
                      alt={similar.name}
                      className="w-full h-full object-cover"
                      fallbackClassName="w-full h-full bg-elevated"
                    />
                  </div>
                  <div className="px-3 pt-3 pb-3">
                    <p className="font-sans text-xs text-text-muted mb-1">
                      {similar.brand}
                    </p>
                    <h3 className="font-display text-base text-text-primary line-clamp-2 mb-2">
                      {similar.name}
                    </h3>
                    <p className="font-mono text-lg text-brand-primary">
                      R$ {(similar.price_min_brl || similar.price_brl || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function translateSkillLevel(level: string): string {
  const translations: Record<string, string> = {
    beginner: 'Iniciante',
    intermediate: 'Intermediário',
    advanced: 'Avançado',
  }
  return translations[level] || level
}
