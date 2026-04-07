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
  return <LandingClient />
}
