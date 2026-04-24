export const runtime = 'edge'
export const maxDuration = 30

import { createUIMessageStream, createUIMessageStreamResponse } from 'ai'
import type { ChatRequest } from '@/types/paddle'

const FASTAPI_URL = process.env.FASTAPI_URL ?? 'http://localhost:8000'

export async function POST(request: Request) {
  let body: {
    messages?: { role: string; parts?: { type: string; text?: string }[]; content?: string }[]
    profile?: { level?: string; style?: string; budget_max?: number }
  }

  try {
    body = await request.json()
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400 })
  }

  const messages = body.messages ?? []
  const lastUserMessage = [...messages].reverse().find((m) => m.role === 'user')
  const profile = body.profile

  if (!lastUserMessage) {
    return new Response(JSON.stringify({ error: 'No user message' }), { status: 400 })
  }

  function extractText(msg: typeof lastUserMessage): string {
    if (!msg) return ''
    if (msg.content) return msg.content
    if (msg.parts) {
      return msg.parts
        .filter((p) => p.type === 'text')
        .map((p) => p.text ?? '')
        .join('')
    }
    return ''
  }

  // Sanitize skill_level to match backend validator (beginner | intermediate | advanced)
  const VALID_LEVELS = ['beginner', 'intermediate', 'advanced'] as const
  const rawLevel = profile?.level?.toLowerCase() ?? ''
  const skill_level: ChatRequest['skill_level'] = VALID_LEVELS.includes(rawLevel as typeof VALID_LEVELS[number])
    ? (rawLevel as ChatRequest['skill_level'])
    : 'beginner'

  const trimmedMessage = extractText(lastUserMessage).trim()
  if (!trimmedMessage) {
    return new Response(JSON.stringify({ error: 'Mensagem vazia — por favor, descreva o que procura.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  const chatRequest: ChatRequest = {
    message: trimmedMessage,
    skill_level,
    budget_brl: Math.max(profile?.budget_max ?? 600, 1),
    style: profile?.style ?? undefined,
  }

  let fastapiResponse: Response
  try {
    fastapiResponse = await fetch(`${FASTAPI_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      body: JSON.stringify(chatRequest),
      signal: request.signal,
    })
  } catch {
    return new Response(JSON.stringify({ error: 'FastAPI unreachable' }), { status: 503 })
  }

  if (!fastapiResponse.ok) {
    const errorBody = await fastapiResponse.text().catch(() => 'Unknown error')
    return new Response(
      JSON.stringify({ error: 'FastAPI error', status: fastapiResponse.status, detail: errorBody }),
      { status: fastapiResponse.status, headers: { 'Content-Type': 'application/json' } }
    )
  }

  const fastapiStream = fastapiResponse.body
  if (!fastapiStream) {
    return new Response(JSON.stringify({ error: 'Empty response from FastAPI' }), { status: 503 })
  }

  const stream = createUIMessageStream({
    execute: async ({ writer }) => {
      const reader = fastapiStream.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let textPartId: string | null = null

      function generateId() {
        return Math.random().toString(36).slice(2)
      }

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() ?? ''

          let eventType = ''
          let dataLine = ''

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7).trim()
            } else if (line.startsWith('data: ')) {
              dataLine = line.slice(6).trim()
            } else if (line === '' && eventType && dataLine) {
              try {
                const data = JSON.parse(dataLine)
                switch (eventType) {
                  case 'reasoning': {
                    const text = data.text ?? ''
                    if (text) {
                      const id: string = textPartId ?? generateId()
                      if (!textPartId) {
                        textPartId = id
                        writer.write({ type: 'text-start', id })
                      }
                      writer.write({ type: 'text-delta', id, delta: text })
                    }
                    break
                  }
                  case 'recommendations': {
                    const paddles = data.paddles ?? []
                    if (paddles.length > 0) {
                      writer.write({
                        type: 'data-recommendations' as `data-${string}`,
                        id: generateId(),
                        data: paddles,
                      } as Parameters<typeof writer.write>[0])
                    }
                    break
                  }
                  case 'degraded': {
                    const paddles = data.paddles ?? []
                    const fallbackText =
                      'Nao consegui gerar uma explicacao completa, mas aqui estao as melhores opcoes:'
                    const id: string = textPartId ?? generateId()
                    if (!textPartId) {
                      textPartId = id
                      writer.write({ type: 'text-start', id })
                    }
                    writer.write({ type: 'text-delta', id, delta: fallbackText })
                    if (paddles.length > 0) {
                      writer.write({
                        type: 'data-degraded' as `data-${string}`,
                        id: generateId(),
                        data: { type: 'degraded', paddles },
                      } as Parameters<typeof writer.write>[0])
                    }
                    break
                  }
                  case 'done': {
                    if (textPartId) {
                      writer.write({ type: 'text-end', id: textPartId })
                    }
                    writer.write({ type: 'finish', finishReason: 'stop' })
                    break
                  }
                  case 'error': {
                    const errMsg = data.error ?? 'Unknown error'
                    writer.write({ type: 'error', errorText: errMsg })
                    break
                  }
                }
              } catch {
                // skip malformed events
              }
              eventType = ''
              dataLine = ''
            }
          }
        }
        // Ensure text part is closed
        if (textPartId) {
          writer.write({ type: 'text-end', id: textPartId })
        }
        writer.write({ type: 'finish', finishReason: 'stop' })
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : 'Stream error'
        writer.write({ type: 'error', errorText: errMsg })
      }
    },
  })

  return createUIMessageStreamResponse({ stream })
}
