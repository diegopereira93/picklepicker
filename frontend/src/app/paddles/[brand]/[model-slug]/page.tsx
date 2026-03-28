import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import dynamic from 'next/dynamic'
import { generateProductMetadata, fetchProductData } from '@/lib/seo'
import { ProductSchema } from '@/components/schema/product-schema'
import { FTCDisclosure } from '@/components/ftc-disclosure'

// Price chart imported with ssr:false to prevent Recharts hydration mismatch
const PriceHistoryChart = dynamic(
  () => import('@/components/price-history-chart').catch(() => ({ default: () => null })),
  { ssr: false }
)

type PageParams = { brand: string; 'model-slug': string }

export async function generateMetadata({
  params,
}: {
  params: PageParams
}): Promise<Metadata> {
  const paddle = await fetchProductData(params.brand, params['model-slug'])
  if (!paddle) return { title: 'Product not found' }
  return generateProductMetadata(params.brand, params['model-slug'], paddle)
}

// SSR: always fresh — no caching
export const revalidate = false

export default async function ProductPage({ params }: { params: PageParams }) {
  const paddle = await fetchProductData(params.brand, params['model-slug'])
  if (!paddle) notFound()

  const canonicalUrl = `${process.env.NEXT_PUBLIC_SITE_URL || 'https://pickleiq.com'}/paddles/${params.brand}/${params['model-slug']}`

  return (
    <>
      <ProductSchema paddle={paddle} url={canonicalUrl} />
      <article className="max-w-4xl mx-auto px-4 py-8">
        <nav aria-label="Breadcrumb" className="text-sm text-gray-500 mb-4">
          <ol className="flex gap-1">
            <li><a href="/">Home</a></li>
            <li aria-hidden>/</li>
            <li><a href="/paddles">Raquetes</a></li>
            <li aria-hidden>/</li>
            <li>{paddle.brand}</li>
            <li aria-hidden>/</li>
            <li aria-current="page">{paddle.name}</li>
          </ol>
        </nav>
        {paddle.image_url && (
          <img
            src={paddle.image_url}
            alt={paddle.name}
            className="w-full max-w-md mx-auto rounded-lg mb-6"
          />
        )}
        <h1 className="text-3xl font-bold mb-2">{paddle.name}</h1>
        {paddle.description && (
          <p className="text-gray-600 mb-4">{paddle.description}</p>
        )}
        <FTCDisclosure />
        {(paddle.price_brl != null || paddle.price_min_brl != null) && (
          <div className="text-2xl font-semibold text-green-700 mb-4">
            R${' '}
            {(paddle.price_brl ?? paddle.price_min_brl ?? 0).toFixed(2)}
          </div>
        )}
        {paddle.specs && (
          <section className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Especificações</h2>
            <dl className="grid grid-cols-2 gap-2">
              {paddle.specs.swingweight != null && (
                <>
                  <dt className="font-medium">Swingweight</dt>
                  <dd>{paddle.specs.swingweight}</dd>
                </>
              )}
              {paddle.specs.twistweight != null && (
                <>
                  <dt className="font-medium">Twistweight</dt>
                  <dd>{paddle.specs.twistweight}</dd>
                </>
              )}
              {paddle.specs.face_material && (
                <>
                  <dt className="font-medium">Face</dt>
                  <dd>{paddle.specs.face_material}</dd>
                </>
              )}
            </dl>
          </section>
        )}
        <PriceHistoryChart paddleId={paddle.id} days={90} />
      </article>
    </>
  )
}
