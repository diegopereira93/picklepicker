'use client'

import { cn } from '@/lib/utils'
import { Pencil, RotateCcw } from 'lucide-react'
import type { QuizProfile } from '@/lib/quiz-profile'
import { getProfileSummary } from '@/lib/quiz-profile'

interface PlayerProfileSidebarProps {
  profile: QuizProfile | null
  onEditProfile?: () => void
  onStartOver?: () => void
  className?: string
}

function PlayerProfileSidebar({
  profile,
  onEditProfile,
  onStartOver,
  className,
}: PlayerProfileSidebarProps) {
  const profileLabels = profile ? getProfileSummary(profile) : []

  return (
    <aside
      className={cn(
        'bg-surface border-r border-border p-4 w-[280px] flex-shrink-0 flex flex-col gap-4',
        className,
      )}
      aria-label="Player profile sidebar"
    >
      <h2 className="font-sans text-xs font-semibold text-text-muted uppercase tracking-widest">
        SEU PERFIL
      </h2>

      <div className="flex flex-wrap gap-2">
        {profileLabels.length > 0 ? (
          profileLabels.map((label, index) => (
            <span
              key={index}
              className="bg-elevated text-text-secondary text-xs px-2.5 py-1 rounded-full font-medium"
            >
              {label}
            </span>
          ))
        ) : (
          <p className="text-text-muted text-sm">Nenhum perfil encontrado</p>
        )}
      </div>

      {onEditProfile && (
        <button
          onClick={onEditProfile}
          className="flex items-center gap-2 text-text-secondary text-sm hover:text-text-primary transition-colors w-full py-2"
          type="button"
        >
          <Pencil size={16} />
          Editar Perfil
        </button>
      )}

      {onStartOver && (
        <button
          onClick={onStartOver}
          className="flex items-center gap-2 text-text-muted text-sm hover:text-brand-secondary transition-colors w-full py-2"
          type="button"
        >
          <RotateCcw size={16} />
          Começar de Novo
        </button>
      )}
    </aside>
  )
}

export { PlayerProfileSidebar }
