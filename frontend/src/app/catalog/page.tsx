'use client'

import { useState, useEffect, useCallback, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { SlidersHorizontal, X, SearchX, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { fetchPaddles } from '@/lib/api'
import { toast } from 'sonner'
import { ProductCard, ProductCardSkeleton } from '@/components/ui/product-card'
import type { Paddle, PaddleListResponse } from '@/types/paddle'

// --- Types ---
interface CatalogFilters {
  brand?: string
  price_min?: number
  price_max?: number
}

type SortOption = 'relevance' | 'price_asc' | 'price_desc' | 'name_asc' | 'newest'

// --- Constants ---
const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'relevance', label: 'Relevância' },
  { value: 'price_asc', label: 'Preço: Menor → Maior' },
  { value: 'price_desc', label: 'Preço: Maior → Menor' },
  { value: 'name_asc', label: 'Nome: A-Z' },
]

const BRANDS = ['Selkirk', 'JOOLA', 'Paddletek', 'Head', 'Wilson', 'Onix', 'Engage', 'Diadem', 'ProLite', 'Vulcan']

function CatalogPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [products, setProducts] = useState<Paddle[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [sortOpen, setSortOpen] = useState(false)

  // Filters from URL or defaults
  const [filters, setFilters] = useState<CatalogFilters>({
    price_min: searchParams.get('price_min') ? Number(searchParams.get('price_min')) : undefined,
    price_max: searchParams.get('price_max') ? Number(searchParams.get('price_max')) : undefined,
    brand: searchParams.get('brand') || undefined,
  })

  const [sort, setSort] = useState<SortOption>(
    (searchParams.get('sort') as SortOption) || 'relevance'
  )

  const [selectedBrands, setSelectedBrands] = useState<string[]>(
    filters.brand ? filters.brand.split(',') : []
  )

  const [compareIds, setCompareIds] = useState<string[]>([])

  const loadProducts = useCallback(async () => {
    setIsLoading(true)
    const params: Record<string, string | number | boolean | undefined> = {
      limit: 200,
      offset: 0,
      in_stock: true,
      sort: sort === 'price_asc' ? 'price' : sort === 'price_desc' ? '-price' : undefined,
      ...filters,
      brand: selectedBrands.length > 0 ? selectedBrands.join(',') : undefined,
    }
    const data = await fetchPaddles(params)
    setProducts(data.items)
    setTotal(data.total)
    setIsLoading(false)
  }, [filters, sort, selectedBrands])

  useEffect(() => {
    loadProducts()
  }, [loadProducts])

  function updateUrl() {
    const params = new URLSearchParams()
    if (filters.price_min) params.set('price_min', String(filters.price_min))
    if (filters.price_max) params.set('price_max', String(filters.price_max))
    if (selectedBrands.length > 0) params.set('brand', selectedBrands.join(','))
    if (sort !== 'relevance') params.set('sort', sort)
    router.replace(`/catalog?${params.toString()}`, { scroll: false })
  }

  function toggleBrand(brand: string) {
    setSelectedBrands(prev =>
      prev.includes(brand) ? prev.filter(b => b !== brand) : [...prev, brand]
    )
  }

  function clearFilters() {
    setFilters({})
    setSelectedBrands([])
    setSort('relevance')
  }

  function handleProductClick(paddle: Paddle) {
    const slug = paddle.model_slug || `${paddle.brand}-${paddle.name}`.toLowerCase().replace(/\s+/g, '-')
    router.push(`/catalog/${slug}`)
  }

  const hasActiveFilters = selectedBrands.length > 0 || filters.price_min || filters.price_max

  return (
    <main className="min-h-screen bg-base">
      {/* Mobile filter toggle */}
      <div className="md:hidden sticky top-0 z-30 bg-base border-b border-border px-4 py-3 flex items-center justify-between">
        <h1 className="font-display text-xl text-text-primary tracking-wide">CATÁLOGO</h1>
        <button
          type="button"
          onClick={() => setFiltersOpen(!filtersOpen)}
          className="flex items-center gap-2 px-3 py-1.5 bg-surface rounded-rounded text-sm text-text-secondary"
        >
          <SlidersHorizontal size={16} />
          Filtros
          {hasActiveFilters && <span className="w-2 h-2 rounded-full bg-brand-primary" />}
        </button>
      </div>

      <div className="max-w-7xl mx-auto flex">
        {/* Desktop Sidebar */}
        <aside className="hidden md:block w-[260px] flex-shrink-0 sticky top-0 h-screen overflow-y-auto bg-surface border-r border-border p-4">
          <FilterContent
            selectedBrands={selectedBrands}
            onToggleBrand={toggleBrand}
            filters={filters}
            setFilters={setFilters}
            hasActiveFilters={hasActiveFilters}
            onClearFilters={clearFilters}
            brands={BRANDS}
          />
        </aside>

        {/* Mobile filter sheet */}
        {filtersOpen && (
          <>
            <div className="md:hidden fixed inset-0 bg-base/80 z-40" onClick={() => setFiltersOpen(false)} />
            <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface border-t border-border rounded-t-lg max-h-[70vh] overflow-y-auto p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-sans text-sm font-semibold text-text-primary">Filtros</h2>
                <button type="button" onClick={() => setFiltersOpen(false)} className="text-text-muted hover:text-text-primary">
                  <X size={20} />
                </button>
              </div>
              <FilterContent
                selectedBrands={selectedBrands}
                onToggleBrand={toggleBrand}
                filters={filters}
                setFilters={setFilters}
                hasActiveFilters={hasActiveFilters}
                onClearFilters={clearFilters}
                brands={BRANDS}
              />
            </div>
          </>
        )}

        {/* Main Content */}
        <div className="flex-1 px-4 md:px-8 py-6">
          {/* Header */}
          <div className="hidden md:flex items-center justify-between mb-6">
            <div>
              <h1 className="font-display text-2xl text-text-primary tracking-wide">CATÁLOGO</h1>
              <p className="font-sans text-sm text-text-muted mt-1">
                {isLoading ? 'Carregando...' : `${total} raquetes encontradas`}
              </p>
            </div>
            {/* Sort dropdown */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setSortOpen(!sortOpen)}
                className="flex items-center gap-2 px-3 py-1.5 bg-surface border border-border rounded-rounded text-sm text-text-secondary hover:text-text-primary transition-colors"
              >
                {SORT_OPTIONS.find(s => s.value === sort)?.label}
                <ChevronDown size={14} />
              </button>
              {sortOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setSortOpen(false)} />
                  <div className="absolute right-0 top-full mt-1 z-20 bg-elevated border border-border rounded-lg shadow-md py-1 min-w-[200px]">
                    {SORT_OPTIONS.map(opt => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => { setSort(opt.value); setSortOpen(false) }}
                        className={cn(
                          'w-full text-left px-4 py-2 text-sm transition-colors',
                          sort === opt.value ? 'text-brand-primary bg-brand-primary/10' : 'text-text-secondary hover:text-text-primary hover:bg-surface'
                        )}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Mobile result count + sort */}
          <div className="md:hidden flex items-center justify-between mb-4">
            <p className="font-sans text-sm text-text-muted">
              {isLoading ? 'Carregando...' : `${total} raquetes`}
            </p>
          </div>

          {/* Product Grid */}
          {products.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {products.map(paddle => (
                <div key={paddle.id} onClick={() => handleProductClick(paddle)} className="cursor-pointer">
                  <ProductCard
                    paddle={paddle}
                    mode="catalog"
                    isCompareSelected={compareIds.includes(String(paddle.id))}
                    onCompare={() => {
                      if (compareIds.includes(String(paddle.id))) {
                        setCompareIds(prev => prev.filter(id => id !== String(paddle.id)))
                        toast.info(`${paddle.name} removido do comparador.`)
                        return
                      }
                      if (compareIds.length >= 2) {
                        toast.error('Comparador cheio! Maximo 2 raquetes.')
                        return
                      }
                      const newIds = [...compareIds, String(paddle.id)]
                      setCompareIds(newIds)
                      if (newIds.length === 2) {
                        router.push(`/compare?a=${newIds[0]}&b=${newIds[1]}`)
                      } else {
                        toast.success(`${paddle.name} adicionado! Clique em Compare em outra raquete para completar.`)
                      }
                    }}
                    onAlert={() => {
                      toast.info('Alerta de preco em breve disponivel!')
                    }}
                  />
                </div>
              ))}
            </div>
          ) : !isLoading ? (
            <div className="bg-surface border border-border rounded-lg py-20 flex flex-col items-center justify-center gap-4 text-center px-4">
              <SearchX size={64} className="text-text-muted" />
              <h2 className="font-sans font-semibold text-xl text-text-primary">Nenhuma raquete encontrada</h2>
              <p className="font-sans text-sm text-text-muted">
                Tente ajustar seus filtros ou pergunte ao chat IA por recomendações
              </p>
              <button
                type="button"
                onClick={clearFilters}
                className="mt-2 px-6 py-2 bg-brand-primary text-base font-semibold rounded-rounded"
              >
                Limpar Filtros
              </button>
            </div>
          ) : null}

          {/* Loading skeleton */}
          {isLoading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {Array.from({ length: 6 }).map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  )
}

export default function CatalogPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-base flex items-center justify-center"><div className="font-sans text-text-muted">Carregando catálogo...</div></div>}>
      <CatalogPageContent />
    </Suspense>
  )
}

// --- Filter Content (shared between desktop sidebar and mobile sheet) ---
function FilterContent({
  selectedBrands,
  onToggleBrand,
  filters,
  setFilters,
  hasActiveFilters,
  onClearFilters,
  brands,
}: {
  selectedBrands: string[]
  onToggleBrand: (brand: string) => void
  filters: CatalogFilters
  setFilters: React.Dispatch<React.SetStateAction<CatalogFilters>>
  hasActiveFilters: boolean
  onClearFilters: () => void
  brands: string[]
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-sans text-xs font-semibold text-text-muted uppercase tracking-widest">Filtros</h2>
        {hasActiveFilters && (
          <button type="button" onClick={onClearFilters} className="text-xs text-brand-primary hover:underline">
            Limpar tudo
          </button>
        )}
      </div>

      {/* Price range */}
      <div>
        <h3 className="font-sans text-sm font-medium text-text-primary mb-3">Faixa de Preço (R$)</h3>
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="Min"
            value={filters.price_min || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, price_min: e.target.value ? Number(e.target.value) : undefined }))}
            className="w-full bg-elevated border border-border rounded-sharp px-3 py-2 text-sm font-mono text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-brand-primary"
          />
          <span className="text-text-muted text-sm">—</span>
          <input
            type="number"
            placeholder="Max"
            value={filters.price_max || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, price_max: e.target.value ? Number(e.target.value) : undefined }))}
            className="w-full bg-elevated border border-border rounded-sharp px-3 py-2 text-sm font-mono text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-brand-primary"
          />
        </div>
      </div>

      {/* Brand filter */}
      <div>
        <h3 className="font-sans text-sm font-medium text-text-primary mb-3">Marca</h3>
        <div className="space-y-2 max-h-[300px] overflow-y-auto">
          {brands.map(brand => (
            <label key={brand} className="flex items-center gap-2 cursor-pointer group">
              <div
                className={cn(
                  'w-[18px] h-[18px] rounded-sharp border-2 flex items-center justify-center transition-colors',
                  selectedBrands.includes(brand)
                    ? 'bg-brand-primary border-brand-primary'
                    : 'border-border group-hover:border-text-muted'
                )}
              >
                {selectedBrands.includes(brand) && (
                  <svg className="w-3 h-3 text-base" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
              <span className="font-sans text-sm text-text-secondary group-hover:text-text-primary transition-colors">
                {brand}
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
