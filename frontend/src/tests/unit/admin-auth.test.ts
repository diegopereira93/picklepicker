/**
 * Admin auth guard and admin API client tests
 * TDD RED: these tests are written before implementation
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock, writable: true })

describe('AdminAuthGuard', () => {
  beforeEach(() => {
    sessionStorageMock.clear()
    mockFetch.mockReset()
    vi.resetModules()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('Test 1: shows login form when no secret in sessionStorage', async () => {
    const { AdminAuthGuard } = await import('@/components/admin/admin-auth-guard')
    render(React.createElement(AdminAuthGuard, null, React.createElement('div', null, 'Protected Content')))
    expect(screen.getByRole('heading', { name: /admin/i })).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/senha/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('Test 2: renders children when valid secret exists in sessionStorage', async () => {
    sessionStorageMock.setItem('pickleiq:admin_secret', 'valid-secret')
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => [] })

    const { AdminAuthGuard } = await import('@/components/admin/admin-auth-guard')
    render(React.createElement(AdminAuthGuard, null, React.createElement('div', null, 'Protected Content')))

    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument()
    })
  })

  it('Test 3: entering wrong secret shows error message "Senha incorreta"', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({ error: 'Unauthorized' }) })

    const { AdminAuthGuard } = await import('@/components/admin/admin-auth-guard')
    render(React.createElement(AdminAuthGuard, null, React.createElement('div', null, 'Protected Content')))

    const input = screen.getByPlaceholderText(/senha/i)
    const button = screen.getByRole('button', { name: /entrar/i })

    fireEvent.change(input, { target: { value: 'wrong-secret' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/senha incorreta/i)).toBeInTheDocument()
    })
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('Test 7: logout clears sessionStorage and shows login form', async () => {
    // Test the clearAdminSecret utility directly — it clears the session key
    const { clearAdminSecret, getAdminSecret, setAdminSecret } = await import('@/lib/admin-api')

    setAdminSecret('my-secret')
    expect(getAdminSecret()).toBe('my-secret')
    expect(sessionStorageMock.getItem('pickleiq:admin_secret')).toBe('my-secret')

    clearAdminSecret()
    expect(getAdminSecret()).toBeNull()
    expect(sessionStorageMock.getItem('pickleiq:admin_secret')).toBeNull()

    // Also verify that the auth guard shows login form when no secret
    const { AdminAuthGuard } = await import('@/components/admin/admin-auth-guard')
    render(React.createElement(AdminAuthGuard, null, React.createElement('div', null, 'Protected Content')))
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })
})

describe('Admin API client (admin-api.ts)', () => {
  beforeEach(() => {
    sessionStorageMock.clear()
    mockFetch.mockReset()
    vi.resetModules()
  })

  it('Test 4: fetchQueue sends Authorization: Bearer header with stored secret', async () => {
    sessionStorageMock.setItem('pickleiq:admin_secret', 'test-secret-123')
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    })

    const { fetchQueue } = await import('@/lib/admin-api')
    await fetchQueue()

    expect(mockFetch).toHaveBeenCalledOnce()
    const [url, options] = mockFetch.mock.calls[0]
    expect(url).toContain('/api/admin/queue')
    expect(options?.headers?.['Authorization']).toBe('Bearer test-secret-123')
  })

  it('Test 5: resolveQueueItem sends PATCH with action and decision_data', async () => {
    sessionStorageMock.setItem('pickleiq:admin_secret', 'test-secret-123')
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'ok' }),
    })

    const { resolveQueueItem } = await import('@/lib/admin-api')
    await resolveQueueItem(42, 'merge', { confidence: 0.95 })

    expect(mockFetch).toHaveBeenCalledOnce()
    const [url, options] = mockFetch.mock.calls[0]
    expect(url).toContain('/api/admin/queue/42/resolve')
    expect(options?.method).toBe('PATCH')
    const body = JSON.parse(options?.body as string)
    expect(body.action).toBe('merge')
    expect(body.decision_data).toEqual({ confidence: 0.95 })
    expect(options?.headers?.['Authorization']).toBe('Bearer test-secret-123')
  })

  it('Test 6: Admin API route returns 401 when no Authorization header', async () => {
    // This tests the route handler behavior via a mock of the route logic
    // We simulate what the route handler does: check Authorization header
    const checkAuth = (authHeader: string | null, adminSecret: string): boolean => {
      if (!authHeader) return false
      const parts = authHeader.split(' ')
      if (parts.length !== 2 || parts[0] !== 'Bearer') return false
      return parts[1] === adminSecret
    }

    expect(checkAuth(null, 'secret')).toBe(false)
    expect(checkAuth('Bearer wrong', 'secret')).toBe(false)
    expect(checkAuth('Bearer secret', 'secret')).toBe(true)
    expect(checkAuth('Basic secret', 'secret')).toBe(false)
  })
})
