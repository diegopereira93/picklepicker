/**
 * Edge Route Handler: POST /api/track
 * Logs affiliate click events as structured JSON to stdout (Vercel Edge logs).
 * Returns 204 No Content on success, 400 on missing required fields.
 */

export const runtime = 'edge'

interface TrackPayload {
  paddle_id: number
  retailer: string
  user_id?: string
  timestamp: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_content?: string
  utm_term?: string
  page_url?: string
  affiliate_url?: string
}

export async function POST(request: Request): Promise<Response> {
  let payload: Partial<TrackPayload>

  try {
    payload = await request.json()
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON body' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  // Validate required fields
  if (!payload.paddle_id || !payload.retailer) {
    return new Response(
      JSON.stringify({ error: 'paddle_id and retailer are required' }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }

  // Structured log to stdout (picked up by Vercel Edge logs)
  console.log(
    JSON.stringify({
      event: 'affiliate_click',
      paddle_id: payload.paddle_id,
      retailer: payload.retailer,
      user_id: payload.user_id ?? null,
      timestamp: payload.timestamp ?? new Date().toISOString(),
      utm_source: payload.utm_source ?? null,
      utm_medium: payload.utm_medium ?? null,
      utm_campaign: payload.utm_campaign ?? null,
      utm_content: payload.utm_content ?? null,
      utm_term: payload.utm_term ?? null,
      page_url: payload.page_url ?? null,
      affiliate_url: payload.affiliate_url ?? null,
    })
  )

  return new Response(null, { status: 204 })
}
