// Revalidation helpers for ISR and on-demand cache busting
// revalidateTag/revalidatePath are Next.js server-only APIs — gracefully no-op outside Next.js runtime

async function safeRevalidateTag(tag: string): Promise<void> {
  try {
    const { revalidateTag } = await import('next/cache')
    revalidateTag(tag)
  } catch {
    // Not in Next.js runtime (tests, non-Next env) — no-op
  }
}

async function safeRevalidatePath(path: string): Promise<void> {
  try {
    const { revalidatePath } = await import('next/cache')
    revalidatePath(path)
  } catch {
    // Not in Next.js runtime (tests, non-Next env) — no-op
  }
}

export async function revalidatePaddlePages(paddleId?: number): Promise<void> {
  if (paddleId != null) {
    // On-demand revalidation for single paddle
    await safeRevalidateTag(`paddle:${paddleId}`)
  } else {
    // Bulk revalidation (used by scheduled workers)
    await safeRevalidatePath('/paddles')
  }
}

export async function revalidateWebhook(req: Request): Promise<Response> {
  const auth = req.headers.get('authorization')
  const expectedSecret = process.env.REVALIDATE_SECRET

  if (!expectedSecret || auth !== `Bearer ${expectedSecret}`) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  let paddleId: number | undefined
  try {
    const body = await req.json()
    paddleId = body.paddle_id
  } catch {
    // malformed JSON — still revalidate all
  }

  await revalidatePaddlePages(paddleId)

  return new Response(JSON.stringify({ revalidated: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  })
}
