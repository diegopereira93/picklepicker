import { Metadata } from 'next'
import { Suspense } from 'react'
import Image from 'next/image'
import { fetchPaddlesList } from '@/lib/seo'
import { PaddleGridSkeleton } from '@/components/paddle-card-skeleton'

// ISR: regenerate every minute during development
export const revalidate = 60

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
    <div className="max-w-6xl mx-auto px-4 py-8 min-h-[600px]">
      <nav aria-label="Breadcrumb" className="text-sm text-gray-500 mb-4">
        <ol className="flex gap-1">
          <li><a href="/">Home</a></li>
          <li aria-hidden>/</li>
          <li aria-current="page">Raquetes</li>
        </ol>
      </nav>
      <h1 className="text-3xl font-bold mb-8">Catálogo de Raquetes</h1>
      <Suspense fallback={<PaddleGridSkeleton count={6} />}>
      {paddles.length === 0 ? (
        <p className="text-gray-500">Nenhuma raquete encontrada.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 min-h-[800px]">
          {paddles.map((paddle) => (
            <article
              key={paddle.id}
              className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
            >
              <a
                href={`/paddles/${encodeURIComponent(paddle.brand?.toLowerCase() ?? '')}/${encodeURIComponent(paddle.model_slug ?? String(paddle.id))}`}
                className="block p-4"
                data-testid="paddle-card-link"
              >
                {paddle.image_url && (
                  <Image
                    src={paddle.image_url}
                    alt={`${paddle.brand} ${paddle.name} paddle`}
                    width={320}
                    height={192}
                    className="w-full h-48 object-contain mb-3"
                    sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
                  />
                )}
                <h2 className="font-semibold text-lg hover:text-blue-600">
                  {paddle.name}
                </h2>
                <p className="text-sm text-gray-500">{paddle.brand}</p>

                {/* Skill level badge */}
                {paddle.skill_level && (
                  <span className="inline-block text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 mt-1">
                    {paddle.skill_level === 'beginner' ? 'Iniciante' : paddle.skill_level === 'intermediate' ? 'Intermediário' : paddle.skill_level === 'advanced' ? 'Avançado' : paddle.skill_level}
                  </span>
                )}

                {/* Specs row */}
                {(paddle.specs?.swingweight || paddle.specs?.core_thickness_mm) && (
                  <p className="text-xs text-gray-400 mt-1">
                    {paddle.specs?.swingweight && <span>SW: {paddle.specs.swingweight}</span>}
                    {paddle.specs?.swingweight && paddle.specs?.core_thickness_mm && <span> · </span>}
                    {paddle.specs?.core_thickness_mm && <span>Core: {paddle.specs.core_thickness_mm}mm</span>}
                  </p>
                )}

                {/* Stock badge */}
                {paddle.in_stock != null && (
                  <span className={`inline-block text-xs mt-1 ${paddle.in_stock ? 'text-green-600' : 'text-gray-400'}`}>
                    {paddle.in_stock ? 'Em estoque' : 'Fora de estoque'}
                  </span>
                )}

                {(paddle.price_brl != null || paddle.price_min_brl != null) && (
                  <p className="text-green-700 font-bold mt-1">
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
  )
}
