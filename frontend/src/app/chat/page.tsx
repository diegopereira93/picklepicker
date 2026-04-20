'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Menu, MessageSquare } from 'lucide-react'
import { loadQuizProfile, clearQuizProfile, type QuizProfile } from '@/lib/quiz-profile'
import { PlayerProfileSidebar } from '@/components/ui/player-profile-sidebar'
import { RecommendationRail } from '@/components/chat/recommendation-rail'
import type { ChatRecommendation } from '@/types/paddle'
import dynamic from 'next/dynamic'

const ChatWidget = dynamic(
  () => import('@/components/chat/chat-widget').then((mod) => mod.ChatWidget),
  { loading: () => <div className="flex-1 bg-base animate-pulse" /> }
)

export default function ChatPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<QuizProfile | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [railOpen, setRailOpen] = useState(false)
  const [hydrated, setHydrated] = useState(false)
  const [accumulatedRecs, setAccumulatedRecs] = useState<Map<number, ChatRecommendation>>(new Map())

  useEffect(() => {
    setProfile(loadQuizProfile())
    setHydrated(true)
  }, [])

  function handleRecommendations(recs: ChatRecommendation[]) {
    setAccumulatedRecs((prev) => {
      const next = new Map(prev)
      for (const r of recs) next.set(r.paddle_id, r)
      return next
    })
  }

  function handleEditProfile() {
    router.push('/quiz')
  }

  function handleStartOver() {
    clearQuizProfile()
    setProfile(null)
    router.push('/quiz')
  }

  if (!hydrated) return null

  if (!profile) {
    return (
      <main className="min-h-screen bg-base flex flex-col items-center justify-center px-4">
        <div className="text-center max-w-md">
          <h1 className="font-display text-3xl text-text-primary tracking-wide mb-4">PICKLEIQ</h1>
          <p className="font-sans text-text-secondary mb-8">
            Precisamos conhecer seu perfil para recomendar as melhores raquetes.
          </p>
          <button
            type="button"
            onClick={() => router.push('/quiz')}
            className="px-8 py-3 bg-brand-primary text-base font-semibold rounded-rounded hover:shadow-glow-green transition-all"
          >
            Fazer Quiz →
          </button>
        </div>
      </main>
    )
  }

  const recCount = accumulatedRecs.size

  return (
    <main className="h-screen bg-base flex overflow-hidden">
      {/* Profile sidebar — desktop always visible */}
      <div className="hidden md:block">
        <PlayerProfileSidebar
          profile={profile}
          onEditProfile={handleEditProfile}
          onStartOver={handleStartOver}
        />
      </div>

      {/* Profile sidebar — mobile drawer */}
      {sidebarOpen && (
        <>
          <div
            className="md:hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-40"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="md:hidden fixed inset-y-0 left-0 z-50">
            <PlayerProfileSidebar
              profile={profile}
              onEditProfile={() => { setSidebarOpen(false); handleEditProfile() }}
              onStartOver={() => { setSidebarOpen(false); handleStartOver() }}
            />
          </div>
        </>
      )}

      {/* Rec rail — mobile drawer */}
      {railOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-40"
            onClick={() => setRailOpen(false)}
          />
          <div className="lg:hidden fixed inset-y-0 right-0 z-50 flex">
            <RecommendationRail recommendations={Array.from(accumulatedRecs.values())} />
          </div>
        </>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between px-4 md:px-8 py-4 border-b border-border bg-base">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-text-secondary hover:text-text-primary transition-colors"
              aria-label="Abrir perfil"
            >
              <Menu size={20} />
            </button>
            <div>
              <h1 className="font-display text-xl text-text-primary tracking-wide">
                PICKLE<span className="text-brand-secondary">IQ</span> ASSISTANT
              </h1>
              <p className="font-sans text-xs text-text-muted">Pergunte qualquer coisa sobre raquetes</p>
            </div>
          </div>

          {/* Mobile rec rail FAB */}
          <button
            type="button"
            onClick={() => setRailOpen(true)}
            className="lg:hidden relative p-2 text-text-secondary hover:text-text-primary transition-colors"
            aria-label={`Ver recomendações (${recCount})`}
          >
            <MessageSquare size={20} />
            {recCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] bg-brand-primary text-base text-[10px] font-bold rounded-full flex items-center justify-center px-1">
                {recCount}
              </span>
            )}
          </button>
        </header>

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 bg-base overflow-hidden">
            <ChatWidget
              profile={{
                level: profile.level === 'competitive' ? 'advanced' : profile.level,
                style: profile.style === 'baseline-grinder' ? 'power' : profile.style === 'dink-control' ? 'control' : profile.style === 'power-hitter' ? 'spin' : 'all-court',
                budget_max: profile.budget === 'under-80' ? 200 : profile.budget === '80-150' ? 400 : profile.budget === '150-250' ? 600 : 2000,
              }}
              onRecommendations={handleRecommendations}
            />
          </div>

          {/* Desktop rec rail */}
          <RecommendationRail recommendations={Array.from(accumulatedRecs.values())} />
        </div>
      </div>
    </main>
  )
}
