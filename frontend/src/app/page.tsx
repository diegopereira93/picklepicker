import { Metadata } from 'next'
import { HomeClient } from '@/components/home/home-client'

export const metadata: Metadata = {
  title: 'PickleIQ — Conselheiro de Raquetes com IA',
  description:
    'Encontre a raquete de pickleball perfeita com ajuda de IA. Comparador de precos, especificacoes tecnicas e recomendacoes personalizadas para jogadores brasileiros.',
  alternates: {
    canonical: 'https://pickleiq.com',
  },
  openGraph: {
    type: 'website',
    url: 'https://pickleiq.com',
    title: 'PickleIQ — Conselheiro de Raquetes com IA',
    description: 'Encontre a raquete de pickleball perfeita com ajuda de IA.',
  },
}

export default function Home() {
  return <HomeClient />
}
