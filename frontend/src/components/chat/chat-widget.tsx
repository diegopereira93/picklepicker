'use client'

import { useEffect, useRef, useState } from 'react'
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'
import { Send } from 'lucide-react'
import type { ChatRecommendation, UserProfile } from '@/types/paddle'
import { MessageBubble } from './message-bubble'
import { LoadingTheater } from './loading-theater'
import { ChatEmptyState } from './chat-empty-state'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const SUGGESTED_QUESTIONS = [
  'Qual a diferença entre 13mm e 16mm?',
  'Qual a melhor raquete pra quem está começando?',
  'Quero gastar até R$600, qual você recomenda?',
  'Selkirk ou Joola? Qual vale mais a pena?',
  'Raquete com bom spin até R$800',
  'Qual raquete evolui comigo?',
]

interface ChatWidgetProps {
  profile: UserProfile
  initialMessage?: string
  onRecommendations?: (recs: ChatRecommendation[]) => void
}

export function ChatWidget({ profile, initialMessage, onRecommendations }: ChatWidgetProps) {
  const endRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')
  const [lastMessage, setLastMessage] = useState('')
  const prevRecCount = useRef(0)
  const initialSentRef = useRef(false)

  const { messages, sendMessage, status, error } = useChat({
    transport: new DefaultChatTransport({ api: '/api/chat', body: { profile } }),
  })

  const isLoading = status === 'submitted' || status === 'streaming'
  const showTheater = status === 'submitted'
  const isSendingInitial = initialSentRef.current && messages.length === 0 && !error

  useEffect(() => {
    if (initialMessage && messages.length === 0 && !initialSentRef.current && !isLoading) {
      initialSentRef.current = true
      setLastMessage(initialMessage)
      // Defer to next frame to ensure useChat transport is fully initialized
      requestAnimationFrame(() => {
        sendMessage({ text: initialMessage })
      })
    }
  }, [initialMessage, messages.length, isLoading, sendMessage])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const last = messages[messages.length - 1]
    if (!last) return
    const recPart = last.parts.find((p) => p.type === 'data-recommendations')
    if (!recPart) return
    const recs = (recPart as { data: unknown }).data as ChatRecommendation[]
    if (!Array.isArray(recs) || recs.length === 0 || recs.length === prevRecCount.current) return
    prevRecCount.current = recs.length
    onRecommendations?.(recs)
  }, [messages, onRecommendations])

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const text = input.trim()
    if (!text || isLoading) return
    setLastMessage(text)
    setInput('')
    sendMessage({ text })
  }

  function handleAsk(text: string) {
    if (isLoading) return
    setLastMessage(text)
    sendMessage({ text })
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {isSendingInitial ? (
          <LoadingTheater />
        ) : messages.length === 0 ? (
          <ChatEmptyState questions={SUGGESTED_QUESTIONS} onAsk={handleAsk} disabled={isLoading} />
        ) : (
          messages.map((msg) => {
            const text = msg.parts
              .filter((p): p is { type: 'text'; text: string } => p.type === 'text')
              .map((p) => p.text)
              .join('')
            const data = msg.parts
              .filter((p) => p.type.startsWith('data-'))
              .map((p) => (p as { data: unknown }).data)
            return (
              <MessageBubble
                key={msg.id}
                role={msg.role as 'user' | 'assistant'}
                content={text}
                annotations={data}
              />
            )
          })
        )}

        {showTheater && <LoadingTheater />}

        {error && (
          <div className="flex justify-start mb-3 gap-2">
            <div className="bg-danger/10 border-l-2 border-danger rounded-sharp px-3 py-2 text-sm flex items-center gap-2">
              <span className="text-danger">Ops! Algo deu errado.</span>
              <Button
                type="button"
                size="sm"
                variant="ghost"
                onClick={() => lastMessage && sendMessage({ text: lastMessage })}
              >
                Tentar novamente
              </Button>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      <div className="border-t border-border bg-surface/95 backdrop-blur-md px-4 py-3">
        <form onSubmit={handleSubmit} className="flex gap-2 max-w-3xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Pergunte sobre raquetes…"
            className={cn(
              'flex-1 h-11 px-4 text-sm rounded-rounded',
              'bg-elevated text-text-primary placeholder:text-text-muted',
              'border border-border focus:border-brand-primary',
              'focus:outline-none transition-colors',
              'disabled:opacity-50'
            )}
          />
          <Button
            type="submit"
            size="lg"
            disabled={isLoading || !input.trim()}
            className="h-11 px-4 gap-1.5"
          >
            <span className="hidden sm:inline">Enviar</span>
            <Send size={16} />
          </Button>
        </form>
      </div>
    </div>
  )
}
