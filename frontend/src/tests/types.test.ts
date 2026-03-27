import { describe, it, expect } from 'vitest'
import type {
  Paddle,
  PaddleListResponse,
  PriceSnapshot,
  LatestPriceResponse,
  ChatRequest,
  ReviewQueueItem,
} from '@/types/paddle'

describe('TypeScript types — backend contract validation', () => {
  it('Test 1: PaddleListResponse accepts valid backend response JSON', () => {
    const response: PaddleListResponse = {
      items: [
        {
          id: 1,
          name: 'Selkirk Vanguard Power Air',
          brand: 'Selkirk',
          sku: 'SKU-001',
          image_url: 'https://example.com/img.jpg',
          specs: {
            swingweight: 114.5,
            twistweight: 6.2,
            weight_oz: 8.1,
            grip_size: '4 1/4',
            core_thickness_mm: 16,
            face_material: 'carbon fiber',
          },
          price_min_brl: 299.9,
          created_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    }
    expect(response.items).toHaveLength(1)
    expect(response.total).toBe(1)
    expect(response.items[0].name).toBe('Selkirk Vanguard Power Air')
  })

  it('Test 2: ChatRequest type matches backend contract', () => {
    const req: ChatRequest = {
      message: 'Quero uma raquete para iniciante',
      skill_level: 'beginner',
      budget_brl: 500,
    }
    expect(req.message).toBeDefined()
    expect(['beginner', 'intermediate', 'advanced']).toContain(req.skill_level)
    expect(req.style).toBeUndefined()

    const reqWithStyle: ChatRequest = {
      message: 'Jogo agressivo',
      skill_level: 'advanced',
      budget_brl: 1000,
      style: 'power',
    }
    expect(reqWithStyle.style).toBe('power')
  })

  it('Test 3: Paddle type has all required and optional fields', () => {
    const paddle: Paddle = {
      id: 42,
      name: 'Franklin Ben Johns',
      brand: 'Franklin',
      created_at: '2024-03-01T10:00:00Z',
    }
    expect(paddle.id).toBe(42)
    expect(paddle.sku).toBeUndefined()
    expect(paddle.image_url).toBeUndefined()
    expect(paddle.specs).toBeUndefined()
    expect(paddle.price_min_brl).toBeUndefined()
  })

  it('Test 4: PriceSnapshot and LatestPriceResponse shapes are correct', () => {
    const snapshot: PriceSnapshot = {
      retailer_name: 'Brazil Pickleball Store',
      price_brl: 349.9,
      currency: 'BRL',
      in_stock: true,
      scraped_at: '2024-03-27T12:00:00Z',
    }
    const latest: LatestPriceResponse = {
      paddle_id: 1,
      paddle_name: 'Selkirk Vanguard',
      latest_prices: [snapshot],
    }
    expect(latest.latest_prices[0].price_brl).toBe(349.9)
    expect(latest.latest_prices[0].in_stock).toBe(true)
  })

  it('Test 5: ReviewQueueItem type matches backend admin schema', () => {
    const item: ReviewQueueItem = {
      id: 10,
      type: 'duplicate',
      paddle_id: 1,
      related_paddle_id: 2,
      data: { confidence: 0.95 },
      status: 'pending',
    }
    expect(item.type).toBe('duplicate')
    expect(item.status).toBe('pending')
    expect(item.created_at).toBeUndefined()
  })
})
