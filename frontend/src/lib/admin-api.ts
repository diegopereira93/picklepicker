/**
 * Admin API client — all requests require ADMIN_SECRET stored in sessionStorage.
 * Proxies through Next.js Route Handlers which add the server-side Authorization header.
 */
import type { ReviewQueueItem, Paddle } from '@/types/paddle'

const ADMIN_SECRET_KEY = 'pickleiq:admin_secret'

export function getAdminSecret(): string | null {
  if (typeof window === 'undefined') return null
  return sessionStorage.getItem(ADMIN_SECRET_KEY)
}

export function setAdminSecret(secret: string): void {
  sessionStorage.setItem(ADMIN_SECRET_KEY, secret)
}

export function clearAdminSecret(): void {
  sessionStorage.removeItem(ADMIN_SECRET_KEY)
}

function authHeaders(): Record<string, string> {
  const secret = getAdminSecret()
  return {
    'Content-Type': 'application/json',
    ...(secret ? { Authorization: `Bearer ${secret}` } : {}),
  }
}

export async function fetchQueue(params?: {
  type?: string
  status?: string
  limit?: number
  offset?: number
}): Promise<ReviewQueueItem[]> {
  const url = new URL('/api/admin/queue', window.location.origin)
  if (params?.type) url.searchParams.set('type', params.type)
  if (params?.status) url.searchParams.set('status', params.status)
  if (params?.limit !== undefined) url.searchParams.set('limit', String(params.limit))
  if (params?.offset !== undefined) url.searchParams.set('offset', String(params.offset))

  const res = await fetch(url.toString(), { headers: authHeaders() })
  if (!res.ok) {
    throw new Error(`fetchQueue failed: ${res.status}`)
  }
  return (await res.json()) as ReviewQueueItem[]
}

export async function resolveQueueItem(
  id: number,
  action: string,
  decision_data?: Record<string, unknown>
): Promise<void> {
  const res = await fetch(`/api/admin/queue/${id}/resolve`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify({ action, decision_data }),
  })
  if (!res.ok) {
    throw new Error(`resolveQueueItem failed: ${res.status}`)
  }
}

export async function dismissQueueItem(id: number, reason?: string): Promise<void> {
  const res = await fetch(`/api/admin/queue/${id}/dismiss`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify({ reason: reason ?? '' }),
  })
  if (!res.ok) {
    throw new Error(`dismissQueueItem failed: ${res.status}`)
  }
}

export interface AdminPaddleListResponse {
  paddles: Paddle[]
  total: number
  limit: number
  offset: number
}

export async function fetchAdminPaddles(params?: {
  limit?: number
  offset?: number
}): Promise<AdminPaddleListResponse> {
  const url = new URL('/api/admin/catalog', window.location.origin)
  if (params?.limit !== undefined) url.searchParams.set('limit', String(params.limit))
  if (params?.offset !== undefined) url.searchParams.set('offset', String(params.offset))

  const res = await fetch(url.toString(), { headers: authHeaders() })
  if (!res.ok) {
    throw new Error(`fetchAdminPaddles failed: ${res.status}`)
  }
  return (await res.json()) as AdminPaddleListResponse
}

export async function updatePaddle(id: number, data: Partial<Paddle>): Promise<void> {
  const res = await fetch(`/api/admin/catalog/${id}`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    throw new Error(`updatePaddle failed: ${res.status}`)
  }
}
