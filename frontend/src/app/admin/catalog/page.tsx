'use client'

import React, { useState, useEffect } from 'react'
import { CatalogTable } from '@/components/admin/catalog-table'
import { fetchAdminPaddles, updatePaddle } from '@/lib/admin-api'
import type { Paddle } from '@/types/paddle'

export default function CatalogPage() {
  const [paddles, setPaddles] = useState<Paddle[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchAdminPaddles({ limit: 100, offset: 0 })
        setPaddles(data.paddles)
        setTotal(data.total)
      } catch {
        setError('Erro ao carregar catálogo. Verifique a conexão.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleUpdate = async (id: number, data: Partial<Paddle>) => {
    await updatePaddle(id, data)
    setPaddles((prev) => prev.map((p) => (p.id === id ? { ...p, ...data } : p)))
  }

  // Stats
  const withSpecs = paddles.filter((p) => p.specs && Object.keys(p.specs).length > 0).length
  const withoutSpecs = paddles.length - withSpecs

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Catálogo de Raquetes</h1>

      {/* Stats header */}
      {!loading && paddles.length > 0 && (
        <div className="text-sm text-muted-foreground bg-muted/30 rounded p-3 border">
          Total: <strong>{total}</strong> raquetes
          {' | '}
          Specs completas: <strong className="text-green-600">{withSpecs}</strong>
          {' | '}
          Sem specs: <strong className="text-red-500">{withoutSpecs}</strong>
        </div>
      )}

      {error && (
        <div className="border border-destructive/50 bg-destructive/10 rounded p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-12 text-center text-muted-foreground text-sm">
          Carregando catálogo...
        </div>
      ) : (
        <CatalogTable paddles={paddles} onUpdate={handleUpdate} />
      )}
    </div>
  )
}
