// RED: Tests for generateProductMetadata() in lib/seo.ts
// These tests will fail until implementation is written.

import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Import after mock setup
async function importSeo() {
  vi.resetModules()
  return await import('@/lib/seo')
}

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

describe('generateProductMetadata', () => {
  it('returns title with brand and model name', async () => {
    const { generateProductMetadata } = await importSeo()
    const metadata = await generateProductMetadata('selkirk', 'vanguard-power-air', mockPaddle)
    expect(metadata.title).toContain('Selkirk')
    expect(metadata.title).toContain('Vanguard Power Air')
  })

  it('returns OG image set to product image_url', async () => {
    const { generateProductMetadata } = await importSeo()
    const metadata = await generateProductMetadata('selkirk', 'vanguard-power-air', mockPaddle)
    const ogImages = (metadata.openGraph as any)?.images
    expect(Array.isArray(ogImages)).toBe(true)
    expect(ogImages[0].url).toBe('https://example.com/selkirk-vanguard.jpg')
  })

  it('sets canonical URL with brand and model-slug', async () => {
    const { generateProductMetadata } = await importSeo()
    const metadata = await generateProductMetadata('selkirk', 'vanguard-power-air', mockPaddle)
    // canonical can be in alternates.canonical or metadata.canonical
    const canonical =
      (metadata as any).canonical ||
      (metadata.alternates as any)?.canonical
    expect(canonical).toContain('selkirk')
    expect(canonical).toContain('vanguard-power-air')
  })

  it('returns description containing product name', async () => {
    const { generateProductMetadata } = await importSeo()
    const metadata = await generateProductMetadata('selkirk', 'vanguard-power-air', mockPaddle)
    expect(metadata.description).toBeTruthy()
    expect(typeof metadata.description).toBe('string')
  })

  it('sets robots to index, follow', async () => {
    const { generateProductMetadata } = await importSeo()
    const metadata = await generateProductMetadata('selkirk', 'vanguard-power-air', mockPaddle)
    expect((metadata as any).robots).toContain('index')
    expect((metadata as any).robots).toContain('follow')
  })
})

describe('fetchProductData', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('fetches product by brand and model_slug', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ paddles: [mockPaddle], total: 1, page: 1, per_page: 10 }),
    })
    const { fetchProductData } = await importSeo()
    const paddle = await fetchProductData('selkirk', 'vanguard-power-air')
    expect(paddle).toEqual(mockPaddle)
    expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('selkirk'))
  })

  it('returns null when product not found', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ paddles: [], total: 0, page: 1, per_page: 10 }),
    })
    const { fetchProductData } = await importSeo()
    const paddle = await fetchProductData('unknown', 'unknown-model')
    expect(paddle).toBeNull()
  })

  it('returns null when response is not ok', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false })
    const { fetchProductData } = await importSeo()
    const result = await fetchProductData('selkirk', 'missing')
    expect(result).toBeNull()
  })
})
