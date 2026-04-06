'use client'

import { useEffect, useRef, useState } from 'react'
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'
import type { ChatRecommendation, UserProfile } from '@/types/paddle'
import { MessageBubble } from './message-bubble'
import { SuggestedQuestions } from './suggested-questions'

interface ChatWidgetProps {
  profile: UserProfile
  onRecommendations?: (recommendations: ChatRecommendation[]) => void
}

const SUGGESTED_QUESTIONS = [
  'Qual a diferenca entre 13mm e 16mm?',
  'Qual a melhor raquete pra quem ta comecando?',
  'Quero gastar ate R$600, qual voce me recomenda?',
  'Selkirk ou Joola? Qual vale mais a pena?',
  'Raquete com bom spin ate R$800',
  'Qual raquete evolui comigo?',
]

export function ChatWidget({ profile, onRecommendations }: ChatWidgetProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')
  const [lastMessage, setLastMessage] = useState<string>('')
  const prevRecCountRef = useRef(0)

  const { messages, sendMessage, status, error } = useChat({
    transport: new DefaultChatTransport({
      api: '/api/chat',
      body: { profile },
    }),
  })

  const isLoading = status === 'submitted' || status === 'streaming'

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const lastMsg = messages[messages.length - 1]
    if (!lastMsg) return
    const recPart = lastMsg.parts.find((p) => p.type === 'data-recommendations')
    if (!recPart) return
    const recs = (recPart as { type: string; data: unknown }).data as ChatRecommendation[]
    if (!Array.isArray(recs) || recs.length === 0) return
    if (recs.length === prevRecCountRef.current) return
    prevRecCountRef.current = recs.length
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

  function handleSuggestedQuestion(question: string) {
    if (isLoading) return
    setLastMessage(question)
    sendMessage({ text: question })
  }

  function handleRetry() {
    if (!lastMessage) return
    sendMessage({ text: lastMessage })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-6 pb-8">
            <div className="flex items-center gap-3">
              <div style={{ backgroundColor: 'var(--color-near-black)' }} className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold">
                <span style={{ color: 'var(--sport-primary)' }}>PI</span>
              </div>
              <p className="text-sm" style={{ color: 'var(--color-gray-300)' }}>
                Ola! Sou o PickleIQ. Posso te ajudar a encontrar a raquete ideal. Me conte sobre seu jogo!
              </p>
            </div>
            <SuggestedQuestions questions={SUGGESTED_QUESTIONS} onSelect={handleSuggestedQuestion} disabled={isLoading} />
          </div>
        )}

        {messages.map((msg) => {
          // Extract text content from parts
          const textContent = msg.parts
            .filter((p): p is { type: 'text'; text: string } => p.type === 'text')
            .map((p) => p.text)
            .join('')

          // Extract recommendation data from data-* parts
          const dataParts = msg.parts
            .filter((p) => p.type.startsWith('data-'))
            .map((p) => (p as { type: string; data: unknown }).data)

          return (
            <MessageBubble
              key={msg.id}
              role={msg.role as 'user' | 'assistant'}
              content={textContent || ''}
              annotations={dataParts}
            />
          )
        })}

        {isLoading && (
          <div className="flex justify-start mb-3 gap-2">
            <div style={{ backgroundColor: 'var(--color-near-black)' }} className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0" aria-hidden="true">
              <span style={{ color: 'var(--sport-primary)' }}>PI</span>
            </div>
            <div style={{ backgroundColor: 'transparent', borderRadius: '8px' }} className="px-4 py-3 text-sm">
              <span className="block mb-2">Buscando as melhores opcoes para voce...</span>
              <span className="inline-flex gap-1">
                <span className="animate-bounce [animation-delay:0ms]">.</span>
                <span className="animate-bounce [animation-delay:150ms]">.</span>
                <span className="animate-bounce [animation-delay:300ms]">.</span>
              </span>
            </div>
          </div>
        )}

        {/* Error handling per DESIGN.md: inline retry */}
        {error && (
          <div className="flex justify-start mb-3">
            <div style={{ backgroundColor: 'rgba(185, 28, 28, 0.1)' }} className="text-sm rounded-lg px-4 py-2 flex items-center gap-2">
              <span style={{ color: '#B91C1C' }}>⚠️ Ops! Algo deu errado.</span>
              <button
                type="button"
                onClick={handleRetry}
                className="underline hover:no-underline font-medium"
              >
                Tentar novamente
              </button>
            </div>
          </div>
        )}

        {/* Suggested questions */}
        {messages.length > 0 && (
          <div className="px-4 pt-2">
            <SuggestedQuestions
              questions={SUGGESTED_QUESTIONS}
              onSelect={handleSuggestedQuestion}
              disabled={isLoading}
            />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ backgroundColor: 'var(--color-near-black)', borderColor: 'var(--color-gray-border)' }} className="border-t px-4 py-3">
        <form id="chat-form" onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Pergunte sobre raquetes..."
            style={{ border: '1px solid var(--color-gray-border)', borderRadius: '8px', backgroundColor: 'var(--color-black)', color: 'var(--color-white)' }}
            className="flex-1 px-4 py-2 text-sm focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="hy-chat-send disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Enviar
          </button>
        </form>
      </div>
    </div>
  )
}