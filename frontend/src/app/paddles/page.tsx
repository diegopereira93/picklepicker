import { Metadata } from 'next'
import { CatalogClient } from '@/components/catalog/catalog-client'

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
  return (
    <div className="hy-dark-section">
      <div className="hy-container" style={{ maxWidth: 'var(--max-width-data)' }}>
        <nav aria-label="Breadcrumb" className="hy-breadcrumb">
          <ol className="flex gap-1">
            <li><a href="/">Home</a></li>
            <li aria-hidden>/</li>
            <li aria-current="page">Raquetes</li>
          </ol>
        </nav>
        <p className="hy-section-label">CATÁLOGO</p>
        <h1 className="hy-section-heading mb-8">Catálogo de Raquetes</h1>
        <CatalogClient />
      </div>
    </div>
  )
}
