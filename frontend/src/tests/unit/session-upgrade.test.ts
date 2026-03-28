/**
 * session-upgrade.test.ts — TDD tests for anon-to-auth migration
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NextRequest } from 'next/server'

// Mock Clerk auth
vi.mock('@clerk/nextjs/server', () => ({
  auth: vi.fn(),
  clerkMiddleware: vi.fn(() => vi.fn()),
}))

// Mock global fetch for backend calls
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('POST /api/users/migrate', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    process.env.NEXT_PUBLIC_FASTAPI_URL = 'http://localhost:8000'
  })

  it('returns 401 for anonymous user', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: null } as any)

    const { POST } = await import('@/app/api/users/migrate/route')
    const req = new NextRequest('http://localhost/api/users/migrate', {
      method: 'POST',
      body: JSON.stringify({ old_uuid: 'anon-uuid-123' }),
    })

    const res = await POST(req)
    expect(res.status).toBe(401)
    const body = await res.json()
    expect(body.error).toBe('Unauthorized')
  })

  it('returns 200 success for authenticated user with old_uuid', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_clerk_abc' } as any)

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ migrated: true }),
    })

    const { POST } = await import('@/app/api/users/migrate/route')
    const req = new NextRequest('http://localhost/api/users/migrate', {
      method: 'POST',
      body: JSON.stringify({ old_uuid: 'anon-uuid-123' }),
    })

    const res = await POST(req)
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.success).toBe(true)
  })

  it('forwards old_uuid and new_user_id to backend', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_clerk_xyz' } as any)

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ migrated: true }),
    })

    const { POST } = await import('@/app/api/users/migrate/route')
    const req = new NextRequest('http://localhost/api/users/migrate', {
      method: 'POST',
      body: JSON.stringify({ old_uuid: 'old-anon-uuid' }),
    })

    await POST(req)

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/users/migrate',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ old_uuid: 'old-anon-uuid', new_user_id: 'user_clerk_xyz' }),
      })
    )
  })

  it('returns 500 when backend migration fails', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_abc' } as any)

    mockFetch.mockResolvedValue({ ok: false })

    const { POST } = await import('@/app/api/users/migrate/route')
    const req = new NextRequest('http://localhost/api/users/migrate', {
      method: 'POST',
      body: JSON.stringify({ old_uuid: 'anon-uuid' }),
    })

    const res = await POST(req)
    expect(res.status).toBe(500)
  })
})

describe('lib/profile - migration helpers', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset localStorage mock
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    }
    vi.stubGlobal('localStorage', localStorageMock)
  })

  it('migrateProfileOnLogin clears old profile key and sets new user_id', async () => {
    mockFetch.mockResolvedValue({ ok: true, json: async () => ({ success: true }) })

    const { migrateProfileOnLogin } = await import('@/lib/profile')
    await migrateProfileOnLogin('old-uuid-abc', 'user_clerk_123')

    expect(localStorage.removeItem).toHaveBeenCalledWith('pickleiq:profile:old-uuid-abc')
    expect(localStorage.setItem).toHaveBeenCalledWith('pickleiq:user_id', 'user_clerk_123')
  })

  it('migrateProfileOnLogin throws on fetch failure', async () => {
    mockFetch.mockResolvedValue({ ok: false })

    const { migrateProfileOnLogin } = await import('@/lib/profile')
    await expect(migrateProfileOnLogin('old-uuid', 'user_abc')).rejects.toThrow('Migration failed')
  })
})
