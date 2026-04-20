import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { InlinePaddleCard } from '@/components/chat/inline-paddle-card'

vi.mock('@/lib/api', () => ({ fetchPaddle: vi.fn().mockResolvedValue(null) }))

const SAMPLE_PADDLE = {
  paddle_id: 42,
  name: 'ProKing Elite 500',
  brand: 'ProKing',
  price_min_brl: 599.9,
  affiliate_url: 'https://example.com/buy/proking-elite-500',
  similarity_score: 0.92,
}

describe('InlinePaddleCard', () => {
  it('renders paddle name', () => {
    render(React.createElement(InlinePaddleCard, SAMPLE_PADDLE))
    expect(screen.getByText('ProKing Elite 500')).toBeDefined()
  })

  it('renders brand', () => {
    render(React.createElement(InlinePaddleCard, SAMPLE_PADDLE))
    expect(screen.getByText('ProKing')).toBeDefined()
  })

  it('renders affiliate link', () => {
    render(React.createElement(InlinePaddleCard, SAMPLE_PADDLE))
    const link = screen.getByRole('link', { name: /ver ofertas/i })
    expect(link).toBeDefined()
    expect(link.getAttribute('href')).toBe('https://example.com/buy/proking-elite-500')
    expect(link.getAttribute('target')).toBe('_blank')
  })

  it('renders data-testid for the article', () => {
    render(React.createElement(InlinePaddleCard, SAMPLE_PADDLE))
    expect(document.querySelector('[data-testid="inline-paddle-42"]')).not.toBeNull()
  })

  it('hides affiliate link in compact mode', () => {
    render(React.createElement(InlinePaddleCard, { ...SAMPLE_PADDLE, compact: true }))
    expect(screen.queryByRole('link', { name: /ver ofertas/i })).toBeNull()
  })
})
