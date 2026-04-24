/**
 * Integration test: PriceHistoryChart
 * TDD RED: these tests should fail until the component is implemented.
 */
import { render, screen, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock getPriceHistory before importing the component
vi.mock('@/lib/price-history', () => ({
  getPriceHistory: vi.fn(),
  percentile20: vi.fn((prices: number[]) => {
    if (prices.length === 0) return 0
    const sorted = [...prices].sort((a, b) => a - b)
    return sorted[Math.floor(sorted.length * 0.2)] ?? sorted[sorted.length - 1]
  }),
  isGoodTimeToBuy: vi.fn((price: number, p20: number) => price <= p20),
}))

// Recharts uses ResizeObserver — polyfill for jsdom
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver

import { getPriceHistory } from '@/lib/price-history'
import PriceHistoryChart from '@/components/price-history-chart'

const SAMPLE_DATA = [
  { retailer: 'Mercado Livre', date: '2024-01-01', price: 350, p20: 320, is_good_time: false },
  { retailer: 'Mercado Livre', date: '2024-01-02', price: 310, p20: 320, is_good_time: true },
  { retailer: 'Brazil Pickleball', date: '2024-01-01', price: 380, p20: 350, is_good_time: false },
  { retailer: 'Brazil Pickleball', date: '2024-01-02', price: 345, p20: 350, is_good_time: true },
]

beforeEach(() => {
  vi.clearAllMocks()
})

describe('PriceHistoryChart', () => {
  it('renders loading state initially', () => {
    ;(getPriceHistory as ReturnType<typeof vi.fn>).mockResolvedValue(SAMPLE_DATA)
    render(<PriceHistoryChart paddleId={42} />)
    expect(screen.getByText(/carregando/i)).toBeInTheDocument()
  })

  it('renders chart with retailer series after data loads', async () => {
    ;(getPriceHistory as ReturnType<typeof vi.fn>).mockResolvedValue(SAMPLE_DATA)
    const { container } = render(<PriceHistoryChart paddleId={42} />)

    await waitFor(() => {
      // Section heading confirms chart rendered (not loading/empty state)
      expect(screen.getByText(/histórico de preços/i)).toBeInTheDocument()
      // Recharts responsive container is present in DOM
      expect(container.querySelector('.recharts-responsive-container')).toBeInTheDocument()
    })
  })

  it('shows empty state when no data', async () => {
    ;(getPriceHistory as ReturnType<typeof vi.fn>).mockResolvedValue([])
    render(<PriceHistoryChart paddleId={99} />)

    await waitFor(() => {
      expect(screen.getByText(/sem dados/i)).toBeInTheDocument()
    })
  })

  it('shows good time to buy badge when price <= P20', async () => {
    ;(getPriceHistory as ReturnType<typeof vi.fn>).mockResolvedValue(SAMPLE_DATA)
    render(<PriceHistoryChart paddleId={42} />)

    await waitFor(() => {
      expect(screen.getByText(/bom momento para comprar/i)).toBeInTheDocument()
    })
  })

  it('calls getPriceHistory with correct paddleId and days', async () => {
    ;(getPriceHistory as ReturnType<typeof vi.fn>).mockResolvedValue(SAMPLE_DATA)
    render(<PriceHistoryChart paddleId={7} days={180} />)

    await waitFor(() => {
      expect(getPriceHistory).toHaveBeenCalledWith(7, 180)
    })
  })

  it('renders without crashing (no SSR hydration errors)', async () => {
    ;(getPriceHistory as ReturnType<typeof vi.fn>).mockResolvedValue(SAMPLE_DATA)
    // Should not throw during render
    expect(() => render(<PriceHistoryChart paddleId={42} />)).not.toThrow()
  })
})
