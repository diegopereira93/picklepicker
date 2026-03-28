'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { QueueItemCard } from '@/components/admin/queue-item-card'
import { fetchQueue, resolveQueueItem, dismissQueueItem } from '@/lib/admin-api'
import type { ReviewQueueItem } from '@/types/paddle'

const TYPE_FILTERS = [
  { value: '', label: 'Todos' },
  { value: 'duplicate', label: 'Duplicatas' },
  { value: 'spec_unmatched', label: 'Specs' },
  { value: 'price_anomaly', label: 'Preços' },
] as const

const STATUS_FILTERS = [
  { value: 'pending', label: 'Pendentes' },
  { value: 'resolved', label: 'Resolvidos' },
  { value: '', label: 'Todos' },
] as const

const PAGE_SIZE = 20

export default function QueuePage() {
  const [items, setItems] = useState<ReviewQueueItem[]>([])
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('pending')
  const [offset, setOffset] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const loadItems = useCallback(
    async (reset = false) => {
      setLoading(true)
      setError(null)
      try {
        const currentOffset = reset ? 0 : offset
        const data = await fetchQueue({
          type: typeFilter || undefined,
          status: statusFilter || undefined,
          limit: PAGE_SIZE,
          offset: currentOffset,
        })
        if (reset) {
          setItems(data)
          setOffset(data.length)
        } else {
          setItems((prev) => [...prev, ...data])
          setOffset((prev) => prev + data.length)
        }
        setHasMore(data.length === PAGE_SIZE)
      } catch {
        setError('Erro ao carregar fila. Verifique a conexão.')
      } finally {
        setLoading(false)
      }
    },
    [typeFilter, statusFilter, offset]
  )

  // Initial load and filter change
  useEffect(() => {
    setOffset(0)
    setItems([])
    setHasMore(true)
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchQueue({
          type: typeFilter || undefined,
          status: statusFilter || undefined,
          limit: PAGE_SIZE,
          offset: 0,
        })
        setItems(data)
        setOffset(data.length)
        setHasMore(data.length === PAGE_SIZE)
      } catch {
        setError('Erro ao carregar fila.')
      } finally {
        setLoading(false)
      }
    }
    load()
    // Auto-refresh every 30 seconds
    const interval = setInterval(load, 30_000)
    return () => clearInterval(interval)
  }, [typeFilter, statusFilter])

  const handleResolve = async (id: number, action: string, decision_data?: Record<string, unknown>) => {
    try {
      await resolveQueueItem(id, action, decision_data)
      setItems((prev) => prev.map((item) => item.id === id ? { ...item, status: 'resolved' } : item))
      showToast('Item resolvido com sucesso')
    } catch {
      showToast('Erro ao resolver item')
    }
  }

  const handleDismiss = async (id: number, reason: string) => {
    try {
      await dismissQueueItem(id, reason)
      setItems((prev) => prev.map((item) => item.id === id ? { ...item, status: 'dismissed' } : item))
      showToast('Item dispensado')
    } catch {
      showToast('Erro ao dispensar item')
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold">Fila de Revisão</h1>
        {loading && <span className="text-xs text-muted-foreground">Atualizando...</span>}
      </div>

      {/* Type filter tabs */}
      <div className="flex gap-1 flex-wrap">
        {TYPE_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setTypeFilter(f.value)}
            className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
              typeFilter === f.value
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-background hover:bg-muted border-border'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Status filter */}
      <div className="flex gap-1 flex-wrap">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setStatusFilter(f.value)}
            className={`px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
              statusFilter === f.value
                ? 'bg-secondary text-secondary-foreground border-secondary'
                : 'bg-background hover:bg-muted border-border'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Error state */}
      {error && (
        <div className="border border-destructive/50 bg-destructive/10 rounded p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Items list */}
      {items.length === 0 && !loading ? (
        <div className="text-center py-16 text-muted-foreground">
          <div className="text-4xl mb-3">&#10003;</div>
          <p className="text-lg font-medium">Nenhum item na fila</p>
          <p className="text-sm">Todos os itens foram revisados.</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {items.map((item) => (
            <QueueItemCard
              key={item.id}
              item={item}
              onResolve={handleResolve}
              onDismiss={handleDismiss}
            />
          ))}
        </div>
      )}

      {/* Load more */}
      {hasMore && items.length > 0 && (
        <div className="flex justify-center pt-2">
          <button
            onClick={() => loadItems(false)}
            disabled={loading}
            className="px-4 py-2 text-sm border rounded hover:bg-muted disabled:opacity-50"
          >
            {loading ? 'Carregando...' : 'Carregar mais'}
          </button>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-4 right-4 bg-foreground text-background px-4 py-2 rounded shadow-lg text-sm z-50">
          {toast}
        </div>
      )}
    </div>
  )
}
