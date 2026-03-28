import { describe, it, expect, vi, beforeEach } from 'vitest'

// Helper to build a minimal SSE stream from event strings
function buildSSEStream(events: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder()
  return new ReadableStream({
    start(controller) {
      for (const event of events) {
        controller.enqueue(encoder.encode(event))
      }
      controller.close()
    },
  })
}

async function readStream(stream: ReadableStream<Uint8Array>): Promise<string> {
  const reader = stream.getReader()
  const decoder = new TextDecoder()
  let result = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    result += decoder.decode(value)
  }
  return result
}

// Mock the 'ai' module's createUIMessageStream and createUIMessageStreamResponse
// so we can inspect what the route writes without full SSE encoding.
vi.mock('ai', async (importOriginal) => {
  const actual = await importOriginal<typeof import('ai')>()
  return {
    ...actual,
    createUIMessageStream: vi.fn(({ execute }: { execute: (opts: { writer: { write: (chunk: unknown) => void; onError: undefined } }) => Promise<void> }) => {
      const chunks: unknown[] = []
      const writer = {
        write: (chunk: unknown) => chunks.push(chunk),
        onError: undefined,
      }
      // Return a readable stream that captures written chunks
      return new ReadableStream({
        async start(controller) {
          await execute({ writer })
          const encoder = new TextEncoder()
          controller.enqueue(encoder.encode(JSON.stringify(chunks)))
          controller.close()
        },
      })
    }),
    createUIMessageStreamResponse: vi.fn((opts: { stream: ReadableStream }) => {
      return new Response(opts.stream, {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      })
    }),
  }
})

describe('Route Handler integration (mocked fetch + ai)', () => {
  const mockFetch = vi.fn()

  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch)
    vi.stubGlobal('process', { env: { FASTAPI_URL: 'http://localhost:8000' } })
  })

  it('Test 3: returns 503 when FastAPI is unreachable', async () => {
    mockFetch.mockRejectedValueOnce(new Error('ECONNREFUSED'))

    const { POST } = await import('@/app/api/chat/route')

    const request = new Request('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'Qual raquete?' }],
        profile: { level: 'beginner', style: 'control', budget_max: 600 },
      }),
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)
    expect(response.status).toBe(503)
  })

  it('Test 3b: returns 503 when FastAPI returns non-200', async () => {
    mockFetch.mockResolvedValueOnce(new Response('Internal Server Error', { status: 500 }))

    const { POST } = await import('@/app/api/chat/route')

    const request = new Request('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'test' }],
        profile: { level: 'beginner', style: 'control', budget_max: 600 },
      }),
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)
    expect(response.status).toBe(503)
  })

  it('Test 4: propagates AbortSignal to FastAPI fetch', async () => {
    const sseEvents = [
      'event: done\ndata: {"tokens":10,"latency_ms":100,"model":"gpt-4","cache_hit":false}\n\n',
    ]
    mockFetch.mockResolvedValueOnce(
      new Response(buildSSEStream(sseEvents), {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      })
    )

    const { POST } = await import('@/app/api/chat/route')
    const controller = new AbortController()

    const request = new Request('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'test' }],
        profile: { level: 'beginner', style: 'control', budget_max: 600 },
      }),
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
    })

    await POST(request)

    // Verify fetch was called with an AbortSignal
    const [, fetchOptions] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1]
    expect(fetchOptions.signal).toBeInstanceOf(AbortSignal)
  })

  it('Test 5: route exports runtime=edge and maxDuration=30', async () => {
    const mod = await import('@/app/api/chat/route')
    expect(mod.runtime).toBe('edge')
    expect(mod.maxDuration).toBe(30)
  })

  it('Test 1: transforms reasoning event to text-delta chunks', async () => {
    const sseEvents = [
      'event: reasoning\ndata: {"text":"hello"}\n\n',
      'event: done\ndata: {"tokens":5}\n\n',
    ]
    mockFetch.mockResolvedValueOnce(
      new Response(buildSSEStream(sseEvents), {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      })
    )

    const { POST } = await import('@/app/api/chat/route')
    const request = new Request('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'test' }],
        profile: { level: 'beginner', style: 'control', budget_max: 600 },
      }),
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)
    expect(response.status).toBe(200)
    const text = await readStream(response.body as ReadableStream<Uint8Array>)
    const chunks = JSON.parse(text) as { type: string; delta?: string }[]
    const textDelta = chunks.find((c) => c.type === 'text-delta')
    expect(textDelta?.delta).toBe('hello')
  })

  it('Test 2: transforms recommendations event to data-recommendations chunk', async () => {
    const paddles = [{ paddle_id: 1, name: 'Test Paddle', brand: 'Brand', price_min_brl: 500, affiliate_url: 'https://example.com', similarity_score: 0.9 }]
    const sseEvents = [
      `event: recommendations\ndata: ${JSON.stringify({ paddles })}\n\n`,
      'event: done\ndata: {"tokens":5}\n\n',
    ]
    mockFetch.mockResolvedValueOnce(
      new Response(buildSSEStream(sseEvents), {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      })
    )

    const { POST } = await import('@/app/api/chat/route')
    const request = new Request('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'test' }],
        profile: { level: 'beginner', style: 'control', budget_max: 600 },
      }),
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)
    const text = await readStream(response.body as ReadableStream<Uint8Array>)
    const chunks = JSON.parse(text) as { type: string; data?: unknown }[]
    const dataChunk = chunks.find((c) => c.type === 'data-recommendations')
    expect(dataChunk).toBeDefined()
    expect(dataChunk?.data).toEqual(paddles)
  })

  it('Test 8: sends profile in request body to FastAPI', async () => {
    const sseEvents = ['event: done\ndata: {"tokens":5}\n\n']
    mockFetch.mockResolvedValueOnce(
      new Response(buildSSEStream(sseEvents), {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      })
    )

    const { POST } = await import('@/app/api/chat/route')
    const profile = { level: 'advanced', style: 'power', budget_max: 1200 }
    const request = new Request('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'Qual raquete?' }],
        profile,
      }),
      headers: { 'Content-Type': 'application/json' },
    })

    await POST(request)

    const [, fetchOptions] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1]
    const sentBody = JSON.parse(fetchOptions.body as string)
    expect(sentBody.skill_level).toBe('advanced')
    expect(sentBody.budget_brl).toBe(1200)
    expect(sentBody.style).toBe('power')
  })
})
