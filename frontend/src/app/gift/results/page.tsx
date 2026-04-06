'use client'

import { useState, useEffect } from 'react'
import type { Paddle } from '@/types/paddle'
import { fetchPaddles } from '@/lib/api'

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
    <main className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <div className="text-8xl mb-4">🎁</div>
          <h1 className="text-3xl font-bold">Presente perfeito!</h1>
          <p className="text-gray-600">
            Encontramos a raquete ideal para quem vai receber
          </p>
        </div>

        <div className="mx-auto max-w-xl bg-gray-50 rounded-xl p-6 border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-center">
            <div className="w-[100px] h-[150px] rounded-lg overflow-hidden mx-auto md:mx-0 bg-gray-200">
              {recommendedPaddle.image_url ? (
                <img 
                  src={recommendedPaddle.image_url} 
                  alt={recommendedPaddle.name} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-xs text-gray-500">
                  Foto
                </div>
              )}
            </div>

            <div className="text-center md:text-left">
              <h3 className="text-xl font-bold mb-2">{recommendedPaddle.name}</h3>
              {recommendedPaddle.brand && (
                <p className="text-xs font-bold uppercase tracking-wider mb-2 text-green-700">
                  {recommendedPaddle.brand}
                </p>
              )}
              <div className="text-2xl font-bold text-coral mb-4">
                R$ {recommendedPaddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
              </div>

              <p className="text-sm text-gray-600 mb-3 bg-yellow-50 p-3 rounded-lg">
                Esta raquete é perfeita para {recipientLabel}
              </p>
              <p className="text-sm text-gray-600 mb-4">
                Melhor avaliada na faixa de {formatCurrency(budget)}
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-3">
          <button
            type="button"
            onClick={() => {
              window.location.href = '/paddles'
            }}
            className="wg-button-coral text-lg px-6 py-3"
          >
            VER MAIS OPÇÕES →
          </button>
          <button
            type="button"
            onClick={() => {
              window.location.href = '/quiz'
            }}
            className="wg-button-ghost text-lg px-6 py-3"
          >
            Quero fazer o quiz pra mim
          </button>
          <button
            type="button"
            onClick={() => {
              window.location.href = '/gift'
            }}
            className="wg-button-ghost text-lg px-6 py-3"
          >
            Refazer
          </button>
        </div>
      </div>
    </main>
  )
}
