import { Metadata } from 'next'
import { Suspense } from 'react'
import Image from 'next/image'
import { fetchPaddlesList } from '@/lib/seo'
import { PaddleGridSkeleton } from '@/components/paddle-card-skeleton'

// Force dynamic rendering to avoid build-time data fetching
export const dynamic = 'force-dynamic'
export const revalidate = 0

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: 'Raquetes de Pickleball - PickleIQ',
    description:
      'Catálogo completo de raquetes de pickleball com preços atualizados, especificações técnicas e análises detalhadas.',
    alternates: {
      canonical: 'https://pickleiq.com/paddles',
    },
    openGraph: {
      type: 'website',
      url: 'https://pickleiq.com/paddles',
      title: 'Raquetes de Pickleball - PickleIQ',
      description: 'Encontre a raquete ideal com preços em tempo real.',
    },
  }
}

export default async function PaddlesPage() {
  const { paddles } = await fetchPaddlesList({ page: 1, per_page: 50 })
  console.log('[PaddlesPage] paddles count:', paddles.length)

  return (
    <div className="hy-dark-section">
      <div className="hy-container hy-catalog-header">
      <nav aria-label="Breadcrumb" className="hy-breadcrumb">
        <ol className="flex gap-1">
          <li><a href="/">Home</a></li>
          <li aria-hidden>/</li>
          <li aria-current="page">Raquetes</li>
        </ol>
      </nav>
      <p className="hy-section-label">CATÁLOGO</p>
      <h1 className="hy-section-heading mb-8">Catálogo de Raquetes</h1>
      <Suspense fallback={<PaddleGridSkeleton count={6} />}>
      {paddles.length === 0 ? (
        <p className="hy-body">Nenhuma raquete encontrada.</p>
      ) : (
        <div className="hy-catalog-grid">
          {paddles.map((paddle) => (
            <article
              key={paddle.id}
              className="hy-product-card"
            >
              <a
                href={`/paddles/${encodeURIComponent(paddle.brand?.toLowerCase() ?? '')}/${encodeURIComponent(paddle.model_slug ?? String(paddle.id))}`}
                className="hy-product-card-inner"
                data-testid="paddle-card-link"
              >
                {paddle.image_url && (
                  <Image
                    src={paddle.image_url}
                    alt={`${paddle.brand} ${paddle.name} paddle`}
                    width={320}
                    height={192}
                    className="w-full h-48 object-contain mb-3 hy-product-image"
                    sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
                  />
                )}
                <h2 className="hy-product-card-title">
                  {paddle.name}
                </h2>
                <p className="hy-product-card-brand">{paddle.brand}</p>

                {/* Skill level badge */}
                {paddle.skill_level && (
                  <span className="hy-skill-badge">
                    {paddle.skill_level === 'beginner' ? 'Iniciante' : paddle.skill_level === 'intermediate' ? 'Intermediário' : paddle.skill_level === 'advanced' ? 'Avançado' : paddle.skill_level}
                  </span>
                )}

                {/* Specs row */}
                {(paddle.specs?.swingweight || paddle.specs?.core_thickness_mm) && (
                  <p className="hy-specs-row">
                    {paddle.specs?.swingweight && <span>SW: {paddle.specs.swingweight}</span>}
                    {paddle.specs?.swingweight && paddle.specs?.core_thickness_mm && <span> · </span>}
                    {paddle.specs?.core_thickness_mm && <span>Core: {paddle.specs.core_thickness_mm}mm</span>}
                  </p>
                )}

                {/* Stock badge */}
                {paddle.in_stock != null && (
                  <span className={paddle.in_stock ? 'hy-stock-in' : 'hy-stock-out'}>
                    {paddle.in_stock ? 'Em estoque' : 'Fora de estoque'}
                  </span>
                )}

                {(paddle.price_brl != null || paddle.price_min_brl != null) && (
                  <p className="hy-product-card-price">
                    R${' '}
                    {(paddle.price_brl ?? paddle.price_min_brl ?? 0).toFixed(2)}
                  </p>
                )}
              </a>
            </article>
          ))}
        </div>
      )}
      </Suspense>
      </div>
    </div>
  )
}
