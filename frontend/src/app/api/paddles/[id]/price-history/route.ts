import { NextRequest, NextResponse } from 'next/server'

const FASTAPI_URL = process.env.FASTAPI_INTERNAL_URL || process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const days = req.nextUrl.searchParams.get('days') || '90'

  try {
    const res = await fetch(
      `${FASTAPI_URL}/paddles/${params.id}/price-history?days=${days}`
    )

    if (!res.ok) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 })
    }

    const data = await res.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Price history API error:', error)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
