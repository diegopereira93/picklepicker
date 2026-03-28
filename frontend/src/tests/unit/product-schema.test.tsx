// RED: Tests for ProductSchema component in components/schema/product-schema.tsx
// These tests will fail until implementation is written.

import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { ProductSchema } from '@/components/schema/product-schema'

const mockPaddle = {
  id: 1,
  name: 'Selkirk Vanguard Power Air',
  brand: 'Selkirk',
  model: 'Vanguard Power Air',
  model_slug: 'vanguard-power-air',
  description: 'Raquete de alta performance para jogadores avançados.',
  image_url: 'https://example.com/selkirk-vanguard.jpg',
  price_brl: 1299.99,
  specs: {
    swingweight: 115,
    twistweight: 6.2,
    core_material: 'Polymer Honeycomb',
    face_material: 'Carbon Fiber',
  },
  skill_level: 'advanced',
  rating: 4.8,
  review_count: 42,
  in_stock: true,
}

const url = 'https://pickleiq.com/paddles/selkirk/vanguard-power-air'

describe('ProductSchema', () => {
  it('renders a script tag with type application/ld+json', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    expect(scriptTag).not.toBeNull()
  })

  it('contains @type Product in JSON-LD', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json['@type']).toBe('Product')
  })

  it('includes product name in schema', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json.name).toBe('Selkirk Vanguard Power Air')
  })

  it('includes brand in schema', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json.brand).toBeDefined()
    expect(json.brand.name).toBe('Selkirk')
  })

  it('includes offers with price and currency', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json.offers).toBeDefined()
    expect(json.offers.priceCurrency).toBe('BRL')
    expect(json.offers.price).toBe('1299.99')
  })

  it('includes aggregateRating when rating and review_count present', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json.aggregateRating).toBeDefined()
    expect(json.aggregateRating['@type']).toBe('AggregateRating')
    expect(json.aggregateRating.ratingValue).toBe('4.8')
    expect(json.aggregateRating.reviewCount).toBe('42')
  })

  it('sets InStock availability when in_stock is true', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json.offers.availability).toContain('InStock')
  })

  it('sets OutOfStock availability when in_stock is false', () => {
    const outOfStockPaddle = { ...mockPaddle, in_stock: false }
    const { container } = render(
      <ProductSchema paddle={outOfStockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json.offers.availability).toContain('OutOfStock')
  })

  it('includes URL in schema', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    const json = JSON.parse(scriptTag!.textContent || '{}')
    expect(json.url).toBe(url)
  })

  it('produces valid JSON without syntax errors', () => {
    const { container } = render(
      <ProductSchema paddle={mockPaddle as any} url={url} />
    )
    const scriptTag = container.querySelector('script[type="application/ld+json"]')
    expect(() => JSON.parse(scriptTag!.textContent || '{}')).not.toThrow()
  })
})
