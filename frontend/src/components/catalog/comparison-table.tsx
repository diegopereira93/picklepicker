'use client'

import { Paddle } from '@/types/paddle'
import { SafeImage } from '@/components/ui/safe-image'
import { UserProfile } from '@/types/paddle'

interface ComparisonTableProps {
  paddles: Paddle[]
  selected: Set<number>
  onSelect: (id: number) => void
  sortBy: string
  onSort: (col: string) => void
  userProfile?: UserProfile | null
}

function ComparisonTable({ paddles, selected, onSelect, sortBy, onSort, userProfile }: ComparisonTableProps) {
  function getScoreBadge(paddle: Paddle) {
    const score = paddle.rating
    if (score == null) return null
    if (score >= 4) return { color: 'var(--color-white)', bg: 'var(--data-green)', label: 'Alto' }
    if (score >= 3) return { color: 'var(--color-black)', bg: '#FDE047', label: 'Médio' }
    return { color: 'var(--color-white)', bg: '#B91C1C', label: 'Baixo' }
  }

  function getParaVoceIcon(userProfile: UserProfile | null, skillLevel: string | null) {
    if (!userProfile || !skillLevel) return null
    if (userProfile.level.toLowerCase() === skillLevel.toLowerCase()) {
      return '⭐'
    }
    return null
  }

  const columns = [
    { key: 'name', label: 'Nome' },
    { key: 'brand', label: 'Marca' },
    { key: 'price', label: 'Preço' },
    { key: 'weight', label: 'Peso' },
    { key: 'face', label: 'Face' },
    { key: 'core', label: 'Core' },
    { key: 'score', label: 'Score' },
  ]

  const handleSort = (key: string) => {
    onSort(key)
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm bg-white">
        <thead>
          <tr className="bg-gray-50">
            <th className="p-3 text-left text-xs font-bold uppercase tracking-wider text-gray-600 bg-gray-100">
              Selecionar
            </th>
            {columns.map((col) => (
               <th
                key={col.key}
                onClick={() => handleSort(col.key)}
                className="cursor-pointer px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-600 bg-gray-100 hover:text-[var(--sport-primary)]"
              >
                <div className="flex items-center gap-1">
                  {col.label}
                  {sortBy === col.key && (
                    <span className="text-[var(--sport-primary)]">
                      ▲
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {paddles.map((p) => {
             const rowColor =
               selected.has(p.id) ? 'var(--color-white)' : 'var(--color-near-white)'
              const textColor = selected.has(p.id) ? 'var(--color-black)' : 'var(--warm-charcoal)'
              const paraVoce = getParaVoceIcon(userProfile ?? null, p.skill_level || null)

            return (
              <tr
                key={p.id}
                className="transition-colors hover:bg-[var(--sport-primary)]/5"
                style={{ backgroundColor: rowColor }}
              >
                <td className="p-3">
                  <input
                    type="checkbox"
                    checked={selected.has(p.id)}
                    onChange={() => onSelect(p.id)}
                    className="h-4 w-4 rounded border-gray-300 text-[var(--sport-primary)] focus:ring-[var(--sport-primary)]"
                  />
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <SafeImage
                      src={p.image_url}
                      alt={p.name}
                      width={40}
                      height={40}
                      className="rounded-sm object-contain"
                    />
                    <span className="font-semibold" style={{ color: textColor }}>
                      {paraVoce && <span className="mr-1">{paraVoce}</span>}
                      {p.name}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 border-r border-gray-100">
                  <span className="text-xs uppercase" style={{ color: 'var(--data-green)' }}>
                    {p.brand}
                  </span>
                </td>
                <td className="px-4 py-3 border-r border-gray-100 font-mono font-bold text-[var(--data-green)]" style={{ fontFamily: 'var(--font-data)' }}>
                  {p.price_min_brl != null
                    ? new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                      }).format(p.price_min_brl)
                    : '—'}
                </td>
                <td className="px-4 py-3 border-r border-gray-100">
                  {p.specs?.weight_oz ? `${p.specs.weight_oz}oz` : '—'}
                </td>
                <td className="px-4 py-3 border-r border-gray-100">
                  {p.specs?.face_material || '—'}
                </td>
                <td className="px-4 py-3 border-r border-gray-100">
                  {p.specs?.core_thickness_mm != null
                    ? `${p.specs.core_thickness_mm}mm`
                    : '—'}
                </td>
                <td className="px-4 py-3 border-r border-gray-100">
                  {(() => {
                    const badge = getScoreBadge(p)
                    if (!badge) return '—'
                    return (
                      <span
                        className="px-2 py-0.5 rounded-sm text-xs font-bold"
                        style={{ backgroundColor: badge.bg, color: badge.color }}
                      >
                        {badge.label}
                      </span>
                    )
                  })()}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export { ComparisonTable }
