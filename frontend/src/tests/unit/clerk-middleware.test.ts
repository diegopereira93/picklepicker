/**
 * clerk-middleware.test.ts — RED phase
 * Tests for Clerk middleware and auth helpers
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock @clerk/nextjs/server before importing lib/clerk
vi.mock('@clerk/nextjs/server', () => ({
  auth: vi.fn(),
  clerkMiddleware: vi.fn(() => vi.fn()),
}))

describe('lib/clerk - getUserId', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns userId when user is authenticated', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_abc123' } as { userId: string | null })

    const { getUserId } = await import('@/lib/clerk')
    const userId = await getUserId()
    expect(userId).toBe('user_abc123')
  })

  it('returns null when user is anonymous', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: null } as { userId: string | null })

    const { getUserId } = await import('@/lib/clerk')
    const userId = await getUserId()
    expect(userId).toBeNull()
  })

  it('requireUserId throws when user is not authenticated', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: null } as { userId: string | null })

    const { requireUserId } = await import('@/lib/clerk')
    await expect(requireUserId()).rejects.toThrow('Unauthorized')
  })

  it('requireUserId returns userId when authenticated', async () => {
    const { auth } = await import('@clerk/nextjs/server')
    vi.mocked(auth).mockResolvedValue({ userId: 'user_xyz' } as { userId: string | null })

    const { requireUserId } = await import('@/lib/clerk')
    const userId = await requireUserId()
    expect(userId).toBe('user_xyz')
  })
})

describe('middleware config', () => {
  it('exports config with correct matcher', async () => {
    // Dynamically import to get the config export
    // middleware.ts must export a config object with matcher array
    const middleware = await import('@/middleware')
    expect(middleware.config).toBeDefined()
    expect(middleware.config.matcher).toBeInstanceOf(Array)
    expect(middleware.config.matcher.length).toBeGreaterThan(0)
  })
})
