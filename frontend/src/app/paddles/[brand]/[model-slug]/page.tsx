import { Metadata } from 'next'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import nextDynamic from 'next/dynamic'
import { generateProductMetadata, fetchProductData } from '@/lib/seo'
import { ProductSchema } from '@/components/schema/product-schema'
import { FTCDisclosure } from '@/components/ftc-disclosure'

// Price chart imported with ssr:false to prevent Recharts hydration mismatch
const PriceHistoryChart = nextDynamic(
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

// Force dynamic rendering to avoid build-time data fetching
export const dynamic = 'force-dynamic'
export const revalidate = 0

export default async function ProductPage({ params }: { params: PageParams }) {
  const paddle = await fetchProductData(params.brand, params['model-slug'])
  if (!paddle) notFound()

  const canonicalUrl = `${process.env.NEXT_PUBLIC_SITE_URL || 'https://pickleiq.com'}/paddles/${params.brand}/${params['model-slug']}`

  return (
    <>
      <ProductSchema paddle={paddle} url={canonicalUrl} />
      <div className="nv-dark-section">
      <article className="nv-container py-8 min-h-[600px]">
        <nav aria-label="Breadcrumb" className="nv-breadcrumb">
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
        <p className="nv-section-label">RAQUETE</p>
        {paddle.image_url ? (
          <Image
            src={paddle.image_url}
            alt={`${paddle.brand} ${paddle.name} paddle`}
            width={600}
            height={600}
            priority={true}
            className="w-full max-w-md mx-auto mb-6 nv-product-image"
            sizes="(max-width: 768px) 100vw, 50vw"
          />
        ) : (
          <div className="w-full max-w-md mx-auto mb-6 h-[300px] bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground text-sm" aria-label={`${paddle.brand} ${paddle.name} — imagem indisponível`}>
            Foto
          </div>
        )}
        <h1 className="nv-display mb-2">{paddle.name}</h1>
        <p className="nv-caption mb-4">{paddle.brand}</p>
        {paddle.description && (
          <p className="nv-body mb-4">{paddle.description}</p>
        )}
        <FTCDisclosure />
        {(paddle.price_brl != null || paddle.price_min_brl != null) && (
          <div className="nv-product-card-price text-2xl mb-4">
            R${' '}
            {(paddle.price_brl ?? paddle.price_min_brl ?? 0).toFixed(2)}
          </div>
        )}
        {paddle.specs && (
          <section className="nv-light-section nv-section mb-6 min-h-[200px]">
            <div className="nv-container">
            <h2 className="nv-section-heading mb-4" style={{ color: '#000000' }}>Especificações</h2>
            <dl className="grid grid-cols-2 gap-2">
              {paddle.specs.swingweight != null && (
                <>
                  <dt className="nv-body-bold">Swingweight</dt>
                  <dd className="nv-body">{paddle.specs.swingweight}</dd>
                </>
              )}
              {paddle.specs.twistweight != null && (
                <>
                  <dt className="nv-body-bold">Twistweight</dt>
                  <dd className="nv-body">{paddle.specs.twistweight}</dd>
                </>
              )}
              {paddle.specs.face_material && (
                <>
                  <dt className="nv-body-bold">Face</dt>
                  <dd className="nv-body">{paddle.specs.face_material}</dd>
                </>
              )}
            </dl>
            </div>
          </section>
        )}
        <PriceHistoryChart paddleId={paddle.id} days={90} />
      </article>
      </div>
    </>
  )
}
