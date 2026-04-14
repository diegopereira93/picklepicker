'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { Paddle } from '@/types/paddle'
import { fetchPaddles } from '@/lib/api'
import { getProfile } from '@/lib/profile'
import { toast } from 'sonner'
import { FilterBar } from './filter-bar'
import { ComparisonTable } from './comparison-table'
import { ProductGrid } from './product-grid'
import { SelectionBar } from './selection-bar'

export function CatalogClient() {
  const [paddles, setPaddles] = useState<Paddle[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table')
  const [sortBy, setSortBy] = useState('name')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  const [activeBrand, setActiveBrand] = useState<string | null>(null)
  const [activeLevel, setActiveLevel] = useState<string | null>(null)
  const [userProfile, setUserProfile] = useState<import('@/types/paddle').UserProfile | null>(null)
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const router = useRouter()

  useEffect(() => {
    async function load() {
      try {
        const result = await fetchPaddles({ limit: 100 })
        setPaddles(result.items)
        setUserProfile(getProfile())
      } catch (err) {
        console.error('[CatalogClient] failed:', err)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [])

  const brands = useMemo(() => [...new Set(paddles.map(p => p.brand).filter(Boolean))].sort(), [paddles])
  const levels = ['beginner', 'intermediate', 'advanced']

  const filtered = useMemo(() => {
    let result = paddles
    if (activeBrand) result = result.filter(p => p.brand === activeBrand)
    if (activeLevel) result = result.filter(p => p.skill_level === activeLevel)
    return result
  }, [paddles, activeBrand, activeLevel])

  const sorted = useMemo(() => {
    const arr = [...filtered]
    arr.sort((a, b) => {
      let cmp = 0
      switch (sortBy) {
        case 'name': cmp = a.name.localeCompare(b.name); break
        case 'price': cmp = (a.price_min_brl ?? 0) - (b.price_min_brl ?? 0); break
        case 'brand': cmp = a.brand.localeCompare(b.brand); break
      }
      return sortDir === 'asc' ? cmp : -cmp
    })
    return arr
  }, [filtered, sortBy, sortDir])

  function handleSort(col: string) {
    if (sortBy === col) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(col)
      setSortDir('asc')
    }
  }

  function handleToggleSelect(id: number) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <div className="py-8">
      <FilterBar
        brands={brands}
        levels={levels}
        activeBrand={activeBrand}
        activeLevel={activeLevel}
        resultCount={sorted.length}
        viewMode={viewMode}
        sortBy={sortBy}
        onBrandChange={setActiveBrand}
        onLevelChange={setActiveLevel}
        onViewModeChange={setViewMode}
        onSortChange={(s) => { setSortBy(s); setSortDir('asc') }}
      />

      {isLoading ? (
        <div className="py-20 text-center" style={{ color: 'var(--color-gray-500)' }}>
          Carregando catalogo...
        </div>
      ) : sorted.length === 0 ? (
        <p style={{ color: 'var(--color-gray-500)' }}>Nenhuma raquete encontrada.</p>
      ) : viewMode === 'table' ? (
        <ComparisonTable
          paddles={sorted}
          selected={selected}
          onSelect={handleToggleSelect}
          sortBy={sortBy}
          onSort={handleSort}
          userProfile={userProfile}
        />
      ) : (
        <ProductGrid
          paddles={sorted}
          selected={selected}
          onSelect={handleToggleSelect}
          userProfile={userProfile}
        />
      )}

      <SelectionBar
        count={selected.size}
        onCompare={() => {
          if (selected.size !== 2) {
            toast.error('Selecione exatamente 2 raquetes para comparar')
            return
          }
          const ids = Array.from(selected)
          router.push(`/compare?a=${ids[0]}&b=${ids[1]}`)
        }}
        onClear={() => {
          setSelected(new Set())
          toast.info('Selecao limpa')
        }}
      />
    </div>
  )
}
