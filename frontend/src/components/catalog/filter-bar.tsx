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
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-4">
          <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--color-gray-500)' }}>
            MARCA
          </span>
          <div className="flex flex-wrap gap-2">
            <button
              className={`hy-filter-chip ${activeBrand === null ? 'active' : ''}`}
              onClick={() => onBrandChange(null)}
              type="button"
            >
              Todos
            </button>
            {brands.map((brand) => (
              <button
                key={brand}
                className={`hy-filter-chip ${
                  activeBrand === brand ? 'active' : ''
                }`}
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
                className={`hy-filter-chip ${
                  activeLevel === level ? 'active' : ''
                }`}
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

      <div className="flex items-center justify-between">
        <span className="text-sm" style={{ color: 'var(--color-gray-300)' }}>
          {resultCount} raquetes encontradas
        </span>

        <div className="flex items-center gap-3">
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="font-sans bg-black text-white border border-gray-border rounded-none px-3 py-1.5 text-sm"
            style={{
              backgroundColor: 'var(--color-black)',
              color: 'var(--color-white)',
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
              className={`px-3 py-1.5 text-xs font-medium uppercase tracking-wider transition-all ${
                viewMode === 'table' ? '' : 'opacity-40'
              }`}
              onClick={() => onViewModeChange('table')}
              type="button"
              style={{
                backgroundColor: viewMode === 'table' ? 'var(--sport-primary)' : 'transparent',
                color: viewMode === 'table' ? 'var(--color-near-black)' : 'var(--color-gray-300)',
                border:
                  viewMode === 'table' ? 'none' : '1px solid var(--color-gray-border)',
              }}
            >
              Tabela
            </button>
            <button
              className={`px-3 py-1.5 text-xs font-medium uppercase tracking-wider transition-all ${
                viewMode === 'grid' ? '' : 'opacity-40'
              }`}
              onClick={() => onViewModeChange('grid')}
              type="button"
              style={{
                backgroundColor: viewMode === 'grid' ? 'var(--sport-primary)' : 'transparent',
                color: viewMode === 'grid' ? 'var(--color-near-black)' : 'var(--color-gray-300)',
                border:
                  viewMode === 'grid' ? 'none' : '1px solid var(--color-gray-border)',
              }}
            >
              Cards
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
