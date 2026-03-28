import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

const FASTAPI_BASE = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'

function validateAuth(req: NextRequest): boolean {
  const authHeader = req.headers.get('Authorization')
  if (!authHeader) return false
  const parts = authHeader.split(' ')
  if (parts.length !== 2 || parts[0] !== 'Bearer') return false
  const adminSecret = process.env.ADMIN_SECRET
  return !!adminSecret && parts[1] === adminSecret
}

export async function GET(req: NextRequest) {
  if (!validateAuth(req)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(req.url)
  const upstreamUrl = new URL(`${FASTAPI_BASE}/admin/paddles`)
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
    console.error('[admin/catalog GET] upstream error:', err)
    return NextResponse.json({ error: 'Upstream error' }, { status: 502 })
  }
}
