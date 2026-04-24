/**
 * price-alerts.test.ts — TDD tests for POST /api/price-alerts
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NextRequest } from 'next/server'

// Mock Clerk auth
vi.mock('@clerk/nextjs/server', () => ({
  auth: vi.fn(),
  clerkMiddleware: vi.fn(() => vi.fn()),
}))

// Use vi.hoisted to declare mockEmailSend before vi.mock factory runs
const { mockEmailSend } = vi.hoisted(() => ({
  mockEmailSend: vi.fn(),
}))

vi.mock('resend', () => ({
  Resend: function () {
    return { emails: { send: mockEmailSend } }
  },
}))

// Mock global fetch for backend calls
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('POST /api/price-alerts', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    process.env.NEXT_PUBLIC_FASTAPI_URL = 'http://localhost:8000'
  })

  it('returns 401 for anonymous user', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: null } as { userId: string | null })

    const { POST } = await import('@/app/api/price-alerts/route')
    const req = new NextRequest('http://localhost/api/price-alerts', {
      method: 'POST',
      body: JSON.stringify({ paddle_id: 1, price_target: 200 }),
    })

    const res = await POST(req)
    expect(res.status).toBe(401)
    const body = await res.json()
    expect(body.error).toBe('Unauthorized')
  })

  it('returns 201 and alert for authenticated user', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_abc' } as { userId: string | null })

    const alertData = { id: 1, price_target: 200, created_at: '2026-01-01' }
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => alertData,
    })

    const { POST } = await import('@/app/api/price-alerts/route')
    const req = new NextRequest('http://localhost/api/price-alerts', {
      method: 'POST',
      body: JSON.stringify({ paddle_id: 1, price_target: 200 }),
    })

    const res = await POST(req)
    expect(res.status).toBe(201)
    const body = await res.json()
    expect(body.id).toBe(1)
  })

  it('forwards user_id to backend', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_xyz' } as { userId: string | null })

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, price_target: 300 }),
    })

    const { POST } = await import('@/app/api/price-alerts/route')
    const req = new NextRequest('http://localhost/api/price-alerts', {
      method: 'POST',
      body: JSON.stringify({ paddle_id: 5, price_target: 300 }),
    })

    await POST(req)

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/price-alerts',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ user_id: 'user_xyz', paddle_id: 5, price_target: 300 }),
      })
    )
  })

  it('returns 500 when backend fails', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_abc' } as { userId: string | null })

    mockFetch.mockResolvedValue({ ok: false })

    const { POST } = await import('@/app/api/price-alerts/route')
    const req = new NextRequest('http://localhost/api/price-alerts', {
      method: 'POST',
      body: JSON.stringify({ paddle_id: 1, price_target: 200 }),
    })

    const res = await POST(req)
    expect(res.status).toBe(500)
  })
})

describe('lib/resend - sendPriceAlert structure', () => {
  it('sendPriceAlert is exported as a function', async () => {
    const { sendPriceAlert } = await import('@/lib/resend')
    expect(typeof sendPriceAlert).toBe('function')
  })

  it('email payload includes RFC 8058 unsubscribe headers', async () => {
    mockEmailSend.mockResolvedValue({ id: 'email_123' })

    const { sendPriceAlert } = await import('@/lib/resend')
    await sendPriceAlert({
      email: 'test@example.com',
      paddleName: 'Selkirk Power Air',
      currentPrice: 180,
      priceTarget: 200,
      paddleUrl: 'https://pickleiq.com/paddles/selkirk-power-air',
      userId: 'user_abc',
    })

    expect(mockEmailSend).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({
          'List-Unsubscribe': expect.stringContaining('unsubscribe'),
          'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
        }),
      })
    )
  })
})
