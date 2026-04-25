import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

const FASTAPI_BASE = process.env.FASTAPI_INTERNAL_URL || process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'

function validateAuth(req: NextRequest): boolean {
  const authHeader = req.headers.get('Authorization')
  if (!authHeader) return false
  const parts = authHeader.split(' ')
  if (parts.length !== 2 || parts[0] !== 'Bearer') return false
  const adminSecret = process.env.ADMIN_SECRET
  return !!adminSecret && parts[1] === adminSecret
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  if (!validateAuth(req)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const body = await req.json()
  const upstreamUrl = `${FASTAPI_BASE}/admin/paddles/${params.id}`

  try {
    const res = await fetch(upstreamUrl, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${process.env.ADMIN_SECRET}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (err) {
    console.error('[admin/catalog/[id] PATCH] upstream error:', err)
    return NextResponse.json({ error: 'Upstream error' }, { status: 502 })
  }
}
