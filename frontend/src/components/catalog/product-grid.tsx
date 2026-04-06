'use client'

import { Paddle } from '@/types/paddle'
import { SafeImage } from '@/components/ui/safe-image'
import Link from 'next/link'
import { UserProfile } from '@/types/paddle'

interface ProductGridProps {
  paddles: Paddle[]
  selected: Set<number>
  onSelect: (id: number) => void
  userProfile?: UserProfile | null
}

function ProductGrid({ paddles, selected, onSelect, userProfile }: ProductGridProps) {
  function getSkillLevelBadge(level: string | null) {
    if (!level) return null
    const levels: Record<string, { color: string; bg: string; label: string }> = {
      beginner: { color: '#76b900', bg: 'var(--color-white)', label: 'Iniciante' },
      intermediate: { color: '#000000', bg: '#FDE047', label: 'Intermediário' },
      advanced: { color: '#ffffff', bg: '#F44336', label: 'Avançado' },
    }
    const entry = levels[level.toLowerCase() as keyof typeof levels]
    if (!entry) return null
    return { color: entry.color, bg: entry.bg, label: entry.label }
  }

  function getParaVoceBadge(userProfile: UserProfile | null, skillLevel: string | null) {
    if (!userProfile || !skillLevel) return null
    if (userProfile.level.toLowerCase() === skillLevel.toLowerCase()) {
      return true
    }
    return null
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {paddles.map((p) => {
        const isSelected = selected.has(p.id)
        const skillBadge = getSkillLevelBadge(p.skill_level || undefined)
        const paraVoce = getParaVoceBadge(userProfile, p.skill_level || null)

        return (
          <div
            key={p.id}
            className={`relative rounded-sm border transition-all duration-200 hover:border-[var(--sport-primary)] ${
              isSelected
                ? 'ring-2 ring-[var(--sport-primary)]/50'
                : ''
            }`}
            style={{
              backgroundColor: 'var(--color-near-white)',
              borderColor: 'var(--color-gray-border)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            }}
          >
            <div className="absolute top-2 right-12 z-10">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onSelect(p.id)}
                className="h-5 w-5 cursor-pointer rounded border-gray-300 text-[var(--sport-primary)] focus:ring-[var(--sport-primary)]"
                style={{ accentColor: 'var(--sport-primary)' }}
              />
            </div>

            {paraVoce && (
              <div className="absolute top-2 right-2 z-10">
                <span
                  className="inline-flex items-center justify-center px-2 py-0.5 rounded-full text-[10px] font-bold w-6 h-6"
                  style={{ backgroundColor: '#FF6B6B', color: '#FFFFFF' }}
                >
                  ⭐
                </span>
                <span
                  className="absolute -top-1 -right-1 inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-[9px] font-bold"
                  style={{ backgroundColor: '#FF6B6B', color: '#FFFFFF' }}
                >
                  Para voce
                </span>
              </div>
            )}

            <div
              className="h-48 w-full overflow-hidden"
              style={{ backgroundColor: 'var(--color-gray-100)' }}
            >
              <SafeImage
                src={p.image_url}
                alt={p.name}
                width={400}
                height={400}
                className="w-full h-48 object-contain"
              />
            </div>

            <div className="p-4">
              <Link
                href={`/paddles/${encodeURIComponent((p.brand || 'unknown').toLowerCase())}/${encodeURIComponent(p.model_slug || p.id.toString())}`}
                className="block no-underline hover:no-underline"
              >
                <h3
                  className="truncate text-base font-semibold"
                  style={{ color: 'var(--color-black)' }}
                >
                  {p.name}
                </h3>

                <p
                  className="mb-2 text-xs font-bold uppercase tracking-wider"
                  style={{ color: 'var(--data-green)' }}
                >
                  {p.brand}
                </p>

                {skillBadge && paraVoce && (
                  <div className="flex gap-2 mb-2">
                    <span
                      className="inline-flex px-2 py-0.5 rounded-sm text-xs font-bold"
                      style={{ backgroundColor: skillBadge.bg, color: skillBadge.color }}
                    >
                      {skillBadge.label}
                    </span>
                    <span
                      className="inline-flex px-2 py-0.5 rounded-full text-xs font-bold"
                      style={{ backgroundColor: '#FF6B6B', color: '#FFFFFF' }}
                    >
                      ⭐ Para voce
                    </span>
                  </div>
                )}

                {!skillBadge && paraVoce && (
                  <span
                    className="inline-flex px-2 py-0.5 rounded-full text-xs font-bold"
                    style={{ backgroundColor: '#FF6B6B', color: '#FFFFFF' }}
                  >
                    ⭐ Para voce
                  </span>
                )}

                {skillBadge && !paraVoce && (
                  <span
                    className="inline-flex px-2 py-0.5 rounded-sm text-xs font-bold"
                    style={{ backgroundColor: skillBadge.bg, color: skillBadge.color }}
                  >
                    {skillBadge.label}
                  </span>
                )}

                <div
                  className="mb-3 flex items-center gap-3 text-xs"
                  style={{ color: 'var(--color-gray-500)' }}
                >
                  {p.specs?.weight_oz && (
                    <span>Peso: {p.specs.weight_oz}oz</span>
                  )}
                  {p.specs?.core_thickness_mm != null && (
                    <span>Core: {p.specs.core_thickness_mm}mm</span>
                  )}
                </div>

                <div
                  className="text-lg font-bold"
                  style={{ fontFamily: 'var(--font-data)', color: 'var(--data-green)' }}
                >
                  {p.price_min_brl != null
                    ? new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                      }).format(p.price_min_brl)
                    : '—'}
                </div>
              </Link>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export { ProductGrid }
