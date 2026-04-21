import { Metadata } from 'next'
import { LandingClient } from '@/components/home/landing-client'

export const metadata: Metadata = {
  title: 'PickleIQ — Encontre a Raquete Perfeita com IA',
  description:
    'Plataforma de inteligência para pickleball. Quiz personalizado, comparador de raquetes e recomendações IA para jogadores brasileiros.',
  alternates: {
    canonical: 'https://pickleiq.com',
  },
  openGraph: {
    type: 'website',
    url: 'https://pickleiq.com',
    title: 'PickleIQ — Encontre a Raquete Perfeita com IA',
    description: 'Plataforma de inteligência para pickleball. Quiz personalizado, comparador de raquetes e recomendações IA para jogadores brasileiros.',
  },
}

export default function Home() {
  const orgSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'PickleIQ',
    url: 'https://pickleiq.com',
    logo: 'https://pickleiq.com/logo.png',
    description: 'Plataforma de inteligência para pickleball. Recomendações personalizadas de raquetes com IA.',
    sameAs: [
      'https://instagram.com/pickleiq',
      'https://youtube.com/@pickleiq',
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(orgSchema) }}
      />
      <LandingClient />
    </>
  )
}
