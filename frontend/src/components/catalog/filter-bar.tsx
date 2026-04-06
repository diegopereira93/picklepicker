'use client'

import { FC } from 'react'

interface FilterBarProps {
  brands: string[]
  levels: string[]
  activeBrand: string | null
  activeLevel: string | null
  resultCount: number
  viewMode: 'table' | 'grid'
  sortBy: string
  onBrandChange: (brand: string | null) => void
  onLevelChange: (level: string | null) => void
  onViewModeChange: (mode: 'table' | 'grid') => void
  onSortChange: (sort: string) => void
}

export const FilterBar: FC<FilterBarProps> = ({
  brands,
  levels,
  activeBrand,
  activeLevel,
  resultCount,
  viewMode,
  sortBy,
  onBrandChange,
  onLevelChange,
  onViewModeChange,
  onSortChange,
}) => {
  const levelLabels: Record<string, string> = {
    beginner: 'Iniciante',
    intermediate: 'Intermediário',
    advanced: 'Avançado',
  }

  return (
    <div className="flex flex-col gap-4 bg-gray-50">
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-4">
          <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--color-gray-500)' }}>
            MARCA
          </span>
          <div className="flex flex-wrap gap-2">
            <button
              className="px-3 py-1.5 rounded-none text-xs font-bold transition-colors"
              style={{
                backgroundColor: activeBrand === null ? '#FF6B6B' : 'transparent',
                color: activeBrand === null ? '#FFFFFF' : 'var(--color-black)',
              }}
              onClick={() => onBrandChange(null)}
              type="button"
            >
              Todos
            </button>
            {brands.map((brand) => (
              <button
                key={brand}
                className="px-3 py-1.5 rounded-none text-xs font-bold transition-colors"
                style={{
                  backgroundColor: activeBrand === brand ? '#FF6B6B' : 'transparent',
                  color: activeBrand === brand ? '#FFFFFF' : 'var(--color-black)',
                }}
                onClick={() => onBrandChange(activeBrand === brand ? null : brand)}
                type="button"
              >
                {brand}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--color-gray-500)' }}>
            NÍVEL
          </span>
          <div className="flex flex-wrap gap-2">
            {levels.map((level) => (
              <button
                key={level}
                className="px-3 py-1.5 rounded-none text-xs font-bold transition-colors"
                style={{
                  backgroundColor: activeLevel === level ? '#FF6B6B' : 'transparent',
                  color: activeLevel === level ? '#FFFFFF' : 'var(--color-black)',
                }}
                onClick={() =>
                  onLevelChange(activeLevel === level ? null : level)
                }
                type="button"
              >
                {levelLabels[level] || level}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between bg-white">
        <span className="text-sm" style={{ color: 'var(--color-gray-500)' }}>
          {resultCount} raquetes encontradas
        </span>

        <div className="flex items-center gap-3">
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="font-sans bg-white text-black border border-gray-border rounded-none px-3 py-1.5 text-sm"
            style={{
              backgroundColor: 'var(--color-white)',
              color: 'var(--color-black)',
              border: '1px solid var(--color-gray-border)',
              borderRadius: 'var(--radius-sharp)',
              padding: '6px 12px',
              fontSize: '14px',
            }}
          >
            <option value="name">Nome</option>
            <option value="price">Preço</option>
            <option value="brand">Marca</option>
          </select>

          <div className="flex gap-2">
            <button
              className="px-3 py-1.5 text-xs font-medium uppercase tracking-wider transition-all border rounded-none"
              style={{
                backgroundColor: viewMode === 'table' ? '#FF6B6B' : 'transparent',
                color: viewMode === 'table' ? '#FFFFFF' : 'var(--color-gray-500)',
                border: '1px solid var(--color-gray-border)',
                borderRadius: 'var(--radius-sharp)',
                padding: '6px 12px',
                fontSize: '14px',
              }}
              onClick={() => onViewModeChange('table')}
              type="button"
            >
              Tabela
            </button>
            <button
              className="px-3 py-1.5 text-xs font-medium uppercase tracking-wider transition-all border rounded-none"
              style={{
                backgroundColor: viewMode === 'grid' ? '#FF6B6B' : 'transparent',
                color: viewMode === 'grid' ? '#FFFFFF' : 'var(--color-gray-500)',
                border: '1px solid var(--color-gray-border)',
                borderRadius: 'var(--radius-sharp)',
                padding: '6px 12px',
                fontSize: '14px',
              }}
              onClick={() => onViewModeChange('grid')}
              type="button"
            >
              Cards
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
