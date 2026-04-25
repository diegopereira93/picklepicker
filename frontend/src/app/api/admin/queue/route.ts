import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

const FASTAPI_BASE = process.env.FASTAPI_INTERNAL_URL || process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'

function validateAuth(req: NextRequest): string | null {
  const authHeader = req.headers.get('Authorization')
  if (!authHeader) return null
  const parts = authHeader.split(' ')
  if (parts.length !== 2 || parts[0] !== 'Bearer') return null
  const adminSecret = process.env.ADMIN_SECRET
  if (!adminSecret || parts[1] !== adminSecret) return null
  return parts[1]
}

export async function GET(req: NextRequest) {
  const secret = validateAuth(req)
  if (!secret) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(req.url)
  const upstreamUrl = new URL(`${FASTAPI_BASE}/admin/queue`)
  searchParams.forEach((value, key) => upstreamUrl.searchParams.set(key, value))

  try {
    const res = await fetch(upstreamUrl.toString(), {
      headers: {
        Authorization: `Bearer ${process.env.ADMIN_SECRET}`,
        'Content-Type': 'application/json',
      },
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (err) {
    console.error('[admin/queue GET] upstream error:', err)
    return NextResponse.json({ error: 'Upstream error' }, { status: 502 })
  }
}
