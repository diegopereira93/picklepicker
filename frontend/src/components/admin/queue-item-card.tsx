'use client'

import React from 'react'
import type { ReviewQueueItem } from '@/types/paddle'

interface QueueItemCardProps {
  item: ReviewQueueItem
  onResolve: (id: number, action: string, decision_data?: Record<string, unknown>) => void
  onDismiss: (id: number, reason: string) => void
}

const TYPE_CONFIG = {
  duplicate: {
    label: 'Duplicata',
    badgeClass: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  },
  spec_unmatched: {
    label: 'Spec Sem Match',
    badgeClass: 'bg-orange-100 text-orange-800 border-orange-300',
  },
  price_anomaly: {
    label: 'Anomalia de Preço',
    badgeClass: 'bg-red-100 text-red-800 border-red-300',
  },
} as const

const STATUS_CONFIG = {
  pending: { label: 'Pendente', badgeClass: 'bg-amber-100 text-amber-800' },
  resolved: { label: 'Resolvido', badgeClass: 'bg-green-100 text-green-800' },
  dismissed: { label: 'Dispensado', badgeClass: 'bg-gray-100 text-gray-600' },
} as const

function DataSummary({ data }: { data: Record<string, unknown> }) {
  return (
    <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mt-2">
      {Object.entries(data).map(([key, value]) => (
        <React.Fragment key={key}>
          <dt className="text-muted-foreground font-medium">{key}</dt>
          <dd className="truncate">{String(value)}</dd>
        </React.Fragment>
      ))}
    </dl>
  )
}

export function QueueItemCard({ item, onResolve, onDismiss }: QueueItemCardProps) {
  const typeConfig = TYPE_CONFIG[item.type]
  const statusConfig = STATUS_CONFIG[item.status]
  const isPending = item.status === 'pending'

  return (
    <div className="border rounded-lg p-4 bg-card shadow-sm space-y-3">
      {/* Header row: type badge + status badge + ID */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-semibold ${typeConfig.badgeClass}`}
          >
            {typeConfig.label}
          </span>
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusConfig.badgeClass}`}>
            {statusConfig.label}
          </span>
        </div>
        <span className="text-xs text-muted-foreground">#{item.id}</span>
      </div>

      {/* Data summary */}
      <div className="text-sm">
        <p className="font-medium text-foreground">
          Paddle ID: {item.paddle_id}
          {item.related_paddle_id && ` → #${item.related_paddle_id}`}
        </p>
        <DataSummary data={item.data} />
      </div>

      {/* Created at */}
      {item.created_at && (
        <p className="text-xs text-muted-foreground">
          {new Date(item.created_at).toLocaleString('pt-BR')}
        </p>
      )}

      {/* Action buttons — only shown when pending */}
      {isPending && (
        <div className="flex flex-wrap gap-2 pt-1">
          {item.type === 'duplicate' && (
            <>
              <button
                onClick={() => onResolve(item.id, 'merge', undefined)}
                className="px-3 py-1.5 text-xs font-medium rounded bg-green-600 text-white hover:bg-green-700"
              >
                Mesclar
              </button>
              <button
                onClick={() => onResolve(item.id, 'reject', undefined)}
                className="px-3 py-1.5 text-xs font-medium rounded bg-red-600 text-white hover:bg-red-700"
              >
                Rejeitar
              </button>
              <button
                onClick={() => onResolve(item.id, 'manual', undefined)}
                className="px-3 py-1.5 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50"
              >
                Revisar Manualmente
              </button>
            </>
          )}

          {item.type === 'spec_unmatched' && (
            <>
              <button
                onClick={() => onResolve(item.id, 'merge', undefined)}
                className="px-3 py-1.5 text-xs font-medium rounded bg-green-600 text-white hover:bg-green-700"
              >
                Aceitar Match
              </button>
              <button
                onClick={() => onResolve(item.id, 'reject', undefined)}
                className="px-3 py-1.5 text-xs font-medium rounded bg-red-600 text-white hover:bg-red-700"
              >
                Rejeitar
              </button>
            </>
          )}

          {item.type === 'price_anomaly' && (
            <>
              <button
                onClick={() => onResolve(item.id, 'merge', undefined)}
                className="px-3 py-1.5 text-xs font-medium rounded bg-green-600 text-white hover:bg-green-700"
              >
                Aceitar
              </button>
              <button
                onClick={() => onDismiss(item.id, '')}
                className="px-3 py-1.5 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50"
              >
                Dispensar
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}
