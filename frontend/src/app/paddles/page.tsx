import Link from 'next/link'
import { Metadata } from 'next'
import { fetchPaddlesList } from '@/lib/seo'

// ISR: regenerate every hour
export const revalidate = 3600

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

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <nav aria-label="Breadcrumb" className="text-sm text-gray-500 mb-4">
        <ol className="flex gap-1">
          <li><a href="/">Home</a></li>
          <li aria-hidden>/</li>
          <li aria-current="page">Raquetes</li>
        </ol>
      </nav>
      <h1 className="text-3xl font-bold mb-8">Catálogo de Raquetes</h1>
      {paddles.length === 0 ? (
        <p className="text-gray-500">Nenhuma raquete encontrada.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {paddles.map((paddle) => (
            <Link
              key={paddle.id}
              href={`/paddles/${encodeURIComponent(paddle.brand?.toLowerCase() ?? '')}/${encodeURIComponent(paddle.model_slug ?? String(paddle.id))}`}
              className="group"
            >
              <article className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                {paddle.image_url && (
                  <img
                    src={paddle.image_url}
                    alt={paddle.name}
                    className="w-full h-48 object-contain mb-3"
                  />
                )}
                <h2 className="font-semibold text-lg group-hover:text-blue-600">
                  {paddle.name}
                </h2>
                <p className="text-sm text-gray-500">{paddle.brand}</p>
                {(paddle.price_brl != null || paddle.price_min_brl != null) && (
                  <p className="text-green-700 font-bold mt-1">
                    R${' '}
                    {(paddle.price_brl ?? paddle.price_min_brl ?? 0).toFixed(2)}
                  </p>
                )}
              </article>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
