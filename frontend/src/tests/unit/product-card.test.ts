import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { ProductCard } from '@/components/chat/product-card'

const SAMPLE_PADDLE = {
  paddle_id: 42,
  name: 'ProKing Elite 500',
  brand: 'ProKing',
  price_min_brl: 599.9,
  affiliate_url: 'https://example.com/buy/proking-elite-500',
  similarity_score: 0.92,
}

describe('ProductCard', () => {
  it('Test 6: renders paddle name', () => {
    render(React.createElement(ProductCard, SAMPLE_PADDLE))
    expect(screen.getByText('ProKing Elite 500')).toBeDefined()
  })

  it('Test 6b: renders brand', () => {
    render(React.createElement(ProductCard, SAMPLE_PADDLE))
    expect(screen.getByText('ProKing')).toBeDefined()
  })

  it('Test 6c: renders price formatted in R$', () => {
    render(React.createElement(ProductCard, SAMPLE_PADDLE))
    // Brazilian locale formats currency as R$ 599,90 or R$\u00a0599,90
    const priceEl = screen.getByText(/R\$/)
    expect(priceEl).toBeDefined()
    expect(priceEl.textContent).toContain('599')
  })

  it('Test 6d: renders affiliate link Comprar button', () => {
    render(React.createElement(ProductCard, SAMPLE_PADDLE))
    const link = screen.getByRole('link', { name: /comprar/i })
    expect(link).toBeDefined()
    expect(link.getAttribute('href')).toBe('https://example.com/buy/proking-elite-500')
    expect(link.getAttribute('target')).toBe('_blank')
    expect(link.getAttribute('rel')).toContain('noopener')
  })

  it('Test 7: shows green Disponivel when in_stock=true', () => {
    render(React.createElement(ProductCard, { ...SAMPLE_PADDLE, in_stock: true }))
    expect(screen.getByText('Disponivel')).toBeDefined()
    const dot = document.querySelector('.bg-green-500')
    expect(dot).not.toBeNull()
  })

  it('Test 7b: shows yellow Poucas unidades when stock_level=low', () => {
    render(React.createElement(ProductCard, { ...SAMPLE_PADDLE, stock_level: 'low' as const }))
    expect(screen.getByText('Poucas unidades')).toBeDefined()
    const dot = document.querySelector('.bg-yellow-500')
    expect(dot).not.toBeNull()
  })

  it('Test 7c: shows red Indisponivel when in_stock=false', () => {
    render(React.createElement(ProductCard, { ...SAMPLE_PADDLE, in_stock: false }))
    expect(screen.getByText('Indisponivel')).toBeDefined()
    const dot = document.querySelector('.bg-red-500')
    expect(dot).not.toBeNull()
  })

  it('shows Recomendado badge when similarity_score > 0.8', () => {
    render(React.createElement(ProductCard, { ...SAMPLE_PADDLE, similarity_score: 0.95 }))
    expect(screen.getByText('Recomendado')).toBeDefined()
  })

  it('does not show Recomendado badge when similarity_score <= 0.8', () => {
    render(React.createElement(ProductCard, { ...SAMPLE_PADDLE, similarity_score: 0.75 }))
    expect(screen.queryByText('Recomendado')).toBeNull()
  })
})
