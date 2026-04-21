'use client'

import { useState, useEffect } from 'react'
import type { Paddle } from '@/types/paddle'
import { fetchPaddles } from '@/lib/api'
import { Button } from '@/components/ui/button'

export default function GiftResultsPage() {
  const [recommendedPaddle, setRecommendedPaddle] = useState<Paddle | null>(null)
  const [recipientLevel, setRecipientLevel] = useState<string>('')
  const [budget, setBudget] = useState<number>(400)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setHydrated(true)
    setRecipientLevel('beginner')
    setBudget(600)
    
    setRecommendedPaddle({
      id: 1,
      name: 'Adidas Signature Pro',
      brand: 'Adidas',
      price_min_brl: 599,
      image_url: 'https://example.com/adidas-signature.jpg'
    })
  }, [])

  if (!hydrated) return null

  const levelLabels: Record<string, string> = {
    'beginner': 'iniciante',
    'regular': 'jogador regular',
    'serious': 'competitivo'
  }
  const recipientLabel = recipientLevel ? levelLabels[recipientLevel] : 'o presente'

  function formatCurrency(val: number) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 0,
    }).format(val)
  }

  return (
    <main className="min-h-screen bg-base flex flex-col items-center justify-center p-4">
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <div className="text-8xl mb-4">🎁</div>
          <h1 className="text-3xl font-bold">Presente perfeito!</h1>
          <p className="text-text-secondary">
            Encontramos a raquete ideal para quem vai receber
          </p>
        </div>

        <div className="mx-auto max-w-xl bg-surface rounded-xl p-6 border border-border">
          <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-center">
            <div className="w-[100px] h-[150px] rounded-lg overflow-hidden mx-auto md:mx-0 bg-elevated">
              {recommendedPaddle.image_url ? (
                <img 
                  src={recommendedPaddle.image_url} 
                  alt={recommendedPaddle.name} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-xs text-text-muted">
                  Foto
                </div>
              )}
            </div>

            <div className="text-center md:text-left">
              <h3 className="text-xl font-bold mb-2 text-text-primary">{recommendedPaddle.name}</h3>
              {recommendedPaddle.brand && (
                <p className="text-xs font-bold uppercase tracking-wider mb-2 text-brand-primary">
                  {recommendedPaddle.brand}
                </p>
              )}
              <div className="text-2xl font-bold text-brand-secondary mb-4">
                R$ {recommendedPaddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
              </div>

              <p className="text-sm text-text-secondary mb-3 bg-elevated p-3 rounded-lg">
                Esta raquete é perfeita para {recipientLabel}
              </p>
              <p className="text-sm text-text-secondary mb-4">
                Melhor avaliada na faixa de {formatCurrency(budget)}
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-3">
          <Button
            onClick={() => {
              window.location.href = '/catalog'
            }}
            size="lg"
            className="bg-brand-secondary hover:bg-brand-secondary/80 text-white"
          >
            Ver mais opções
          </Button>
          <Button
            variant="outline"
            size="lg"
            onClick={() => {
              window.location.href = '/quiz'
            }}
          >
            Quero fazer o quiz pra mim
          </Button>
          <Button
            variant="ghost"
            size="lg"
            onClick={() => {
              window.location.href = '/gift'
            }}
          >
            Refazer
          </Button>
        </div>
      </div>
    </main>
  )
}
