'use client'

import { useState, useEffect, useCallback } from 'react'
import type { UserProfile } from '@/types/paddle'
import { getProfile, saveProfile } from '@/lib/profile'
import type { Paddle, ChatRecommendation } from '@/types/paddle'
import { fetchPaddles, fetchPaddle } from '@/lib/api'
import dynamic from 'next/dynamic'
const QuizFlow = dynamic(
  () => import('@/components/quiz/quiz-flow').then((mod) => mod.QuizFlow),
  {
    loading: () => (
      <div className="animate-pulse space-y-4">
        <div className="h-4 bg-muted rounded w-3/4"></div>
        <div className="h-10 bg-muted rounded"></div>
      </div>
    ),
  }
)

const ChatWidget = dynamic(
  () => import('@/components/chat/chat-widget').then((mod) => mod.ChatWidget),
  {
    loading: () => (
      <div className="animate-pulse space-y-4 p-4">
        <div className="h-12 bg-muted rounded"></div>
        <div className="h-12 bg-muted rounded"></div>
        <div className="h-12 bg-muted rounded"></div>
      </div>
    ),
  }
)

const SidebarProductCard = dynamic(
  () => import('@/components/chat/sidebar-product-card').then((mod) => mod.SidebarProductCard),
  { loading: () => <div className="animate-pulse"><div className="h-[400px]" style={{ backgroundColor: 'var(--color-gray-border)' }} /></div> }
)

const RelatedPaddles = dynamic(
  () => import('@/components/chat/related-paddles').then((mod) => mod.RelatedPaddles),
  { loading: () => <div className="animate-pulse flex gap-3"><div className="h-24 w-32" style={{ backgroundColor: 'var(--color-gray-border)' }} /></div> }
)

export default function ChatPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [editingProfile, setEditingProfile] = useState(false)
  const [hydrated, setHydrated] = useState(false)
  const [selectedPaddle, setSelectedPaddle] = useState<Paddle | null>(null)
  const [selectedScore, setSelectedScore] = useState<number | undefined>(undefined)
  const [selectedAffiliateUrl, setSelectedAffiliateUrl] = useState<string | undefined>(undefined)
  const [relatedPaddles, setRelatedPaddles] = useState<Paddle[]>([])

  useEffect(() => {
    setProfile(getProfile())
    setHydrated(true)
  }, [])

  function handleQuizComplete(p: UserProfile) {
    saveProfile(p)
    setProfile(p)
    setEditingProfile(false)
  }

  const handleRecommendations = useCallback(async (recs: ChatRecommendation[]) => {
    if (recs.length === 0) return
    const rec = recs[0]
    setSelectedScore(rec.similarity_score)
    setSelectedAffiliateUrl(rec.affiliate_url)
    try {
      const fullPaddle = await fetchPaddle(rec.paddle_id)
      if (fullPaddle) {
        setSelectedPaddle(fullPaddle)
      }
    } catch (err) {
      console.error('[fetchPaddle] failed:', err)
      setSelectedPaddle({
        id: rec.paddle_id,
        name: rec.name,
        brand: rec.brand,
        price_min_brl: rec.price_min_brl,
      })
    }
  }, [])

  useEffect(() => {
    if (!selectedPaddle) return
    async function fetchRelated() {
      try {
        const result = await fetchPaddles({ limit: 10 })
        const related = result.items.filter(p => p.id !== selectedPaddle.id).slice(0, 4)
        setRelatedPaddles(related)
      } catch (err) {
        console.error('[fetchRelated] failed:', err)
      }
    }
    fetchRelated()
  }, [selectedPaddle])

  if (!hydrated) return null

  if (!profile || editingProfile) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center bg-background px-4">
        <div className="w-full max-w-md">
          <h1 className="text-2xl font-bold text-center mb-2">PickleIQ</h1>
          <p className="text-muted-foreground text-center mb-8">
            Vamos encontrar a raquete perfeita para voce
          </p>
          <QuizFlow
            onComplete={handleQuizComplete}
            onEditCancel={editingProfile ? () => setEditingProfile(false) : undefined}
            editMode={editingProfile}
          />
        </div>
      </main>
    )
  }

  return (
    <main className="h-screen flex flex-col" style={{ backgroundColor: 'var(--color-near-black)' }}>
      <header className="border-b px-4 py-3 flex items-center justify-between"
              style={{ borderColor: 'var(--color-gray-border)', backgroundColor: 'var(--color-near-black)' }}>
        <h1 className="font-bold text-lg" style={{ color: 'var(--color-white)' }}>PickleIQ</h1>
        <button
          type="button"
          onClick={() => setEditingProfile(true)}
          className="text-sm underline transition-colors"
          style={{ color: 'var(--color-gray-300)' }}
          onMouseEnter={(e) => { (e.target as HTMLElement).style.color = 'var(--color-white)' }}
          onMouseLeave={(e) => { (e.target as HTMLElement).style.color = 'var(--color-gray-300)' }}
        >
          Editar perfil
        </button>
      </header>

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        <aside className="lg:w-[55%] h-[50vh] lg:h-full overflow-y-auto p-4 lg:p-6 border-b lg:border-b-0 lg:border-r"
               style={{ backgroundColor: 'var(--color-white)', borderColor: 'var(--color-gray-border)' }}>
          {selectedPaddle ? (
            <SidebarProductCard
              paddle={selectedPaddle}
              score={selectedScore}
              affiliateUrl={selectedAffiliateUrl}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                   style={{ backgroundColor: 'var(--color-near-black)' }}>
                <span className="text-2xl font-bold" style={{ color: 'var(--sport-primary)' }}>PI</span>
              </div>
              <p style={{ color: 'var(--color-gray-500)', fontSize: 'var(--font-size-body)' }}>
                Envie uma mensagem para ver recomendacoes aqui.
              </p>
            </div>
          )}

          {relatedPaddles.length > 0 && (
            <div className="mt-8">
              <h3 className="text-sm font-bold uppercase tracking-wider mb-4"
                  style={{ color: 'var(--color-gray-500)' }}>
                Raquetes relacionadas
              </h3>
              <RelatedPaddles
                paddles={relatedPaddles}
                onSelect={(p) => {
                  setSelectedPaddle(p)
                  setSelectedScore(undefined)
                  setSelectedAffiliateUrl(undefined)
                }}
              />
            </div>
          )}
        </aside>

        <div className="lg:w-[45%] h-[50vh] lg:h-full flex flex-col"
             style={{ backgroundColor: 'var(--color-near-black)' }}>
          <ChatWidget profile={profile!} onRecommendations={handleRecommendations} />
        </div>
      </div>
    </main>
  )
}
