'use client'

import { useState, useEffect } from 'react'
import type { UserProfile } from '@/types/paddle'
import { getProfile, saveProfile } from '@/lib/profile'
import { QuizFlow } from '@/components/quiz/quiz-flow'
import { ChatWidget } from '@/components/chat/chat-widget'

export default function ChatPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [editingProfile, setEditingProfile] = useState(false)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setProfile(getProfile())
    setHydrated(true)
  }, [])

  function handleQuizComplete(p: UserProfile) {
    saveProfile(p)
    setProfile(p)
    setEditingProfile(false)
  }

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
    <main className="min-h-screen flex flex-col bg-background">
      <header className="border-b px-4 py-3 flex items-center justify-between">
        <h1 className="font-bold text-lg">PickleIQ</h1>
        <button
          type="button"
          onClick={() => setEditingProfile(true)}
          className="text-sm text-muted-foreground hover:text-foreground underline transition-colors"
        >
          Editar perfil
        </button>
      </header>
      <div className="flex-1 overflow-hidden">
        <ChatWidget profile={profile} />
      </div>
    </main>
  )
}
