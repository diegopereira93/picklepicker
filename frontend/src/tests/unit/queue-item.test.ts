/**
 * QueueItemCard component tests
 * TDD: behavior-driven tests for the review queue card component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import type { ReviewQueueItem } from '@/types/paddle'

const mockResolve = vi.fn()
const mockDismiss = vi.fn()

const duplicateItem: ReviewQueueItem = {
  id: 1,
  type: 'duplicate',
  paddle_id: 10,
  related_paddle_id: 11,
  data: { paddle_name: 'Selkirk Vanguard', related_name: 'Selkirk Vanguard 2.0', similarity: 0.97 },
  status: 'pending',
  created_at: '2026-03-27T00:00:00Z',
}

const specItem: ReviewQueueItem = {
  id: 2,
  type: 'spec_unmatched',
  paddle_id: 20,
  data: { spec_key: 'swingweight', spec_value: 112, source: 'PickleballCentral' },
  status: 'pending',
  created_at: '2026-03-27T00:00:00Z',
}

const priceItem: ReviewQueueItem = {
  id: 3,
  type: 'price_anomaly',
  paddle_id: 30,
  data: { price: 1200, expected_min: 400, expected_max: 800, retailer: 'BPS' },
  status: 'pending',
  created_at: '2026-03-27T00:00:00Z',
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('QueueItemCard', () => {
  it('renders type badge with correct label for duplicate', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: duplicateItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    expect(screen.getByText(/duplicata/i)).toBeInTheDocument()
  })

  it('renders type badge with correct label for spec_unmatched', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: specItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    expect(screen.getByText(/spec sem match/i)).toBeInTheDocument()
  })

  it('renders type badge with correct label for price_anomaly', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: priceItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    expect(screen.getByText(/anomalia de pre/i)).toBeInTheDocument()
  })

  it('duplicate type shows "Mesclar" and "Rejeitar" buttons', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: duplicateItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    expect(screen.getByRole('button', { name: /mesclar/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /rejeitar/i })).toBeInTheDocument()
  })

  it('action buttons fire onResolve with correct args for merge', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: duplicateItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    const mergeBtn = screen.getByRole('button', { name: /mesclar/i })
    fireEvent.click(mergeBtn)
    expect(mockResolve).toHaveBeenCalledWith(1, 'merge', undefined)
  })

  it('action buttons fire onResolve with reject for duplicate', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: duplicateItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    const rejectBtn = screen.getByRole('button', { name: /rejeitar/i })
    fireEvent.click(rejectBtn)
    expect(mockResolve).toHaveBeenCalledWith(1, 'reject', undefined)
  })

  it('price anomaly type shows "Dispensar" button', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: priceItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    expect(screen.getByRole('button', { name: /dispensar/i })).toBeInTheDocument()
  })

  it('price anomaly dismiss fires onDismiss callback', async () => {
    const { QueueItemCard } = await import('@/components/admin/queue-item-card')
    render(
      React.createElement(QueueItemCard, {
        item: priceItem,
        onResolve: mockResolve,
        onDismiss: mockDismiss,
      })
    )
    const dismissBtn = screen.getByRole('button', { name: /dispensar/i })
    fireEvent.click(dismissBtn)
    expect(mockDismiss).toHaveBeenCalledWith(3, expect.any(String))
  })
})
