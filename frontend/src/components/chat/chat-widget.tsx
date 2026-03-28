'use client'

import { useEffect, useRef, useState } from 'react'
import { useChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'
import type { UserProfile } from '@/types/paddle'
import { MessageBubble } from './message-bubble'

interface ChatWidgetProps {
  profile: UserProfile
}

const SUGGESTED_QUESTIONS = [
  'Qual raquete para iniciante?',
  'Melhor custo-beneficio ate R$ 600?',
  'Qual raquete para jogo de controle?',
]

export function ChatWidget({ profile }: ChatWidgetProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')

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

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const text = input.trim()
    if (!text || isLoading) return
    setInput('')
    sendMessage({ text })
  }

  function handleSuggestedQuestion(question: string) {
    if (isLoading) return
    sendMessage({ text: question })
  }

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-57px)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-6 pb-8">
            <p className="text-muted-foreground text-sm text-center max-w-xs">
              Oi! Sou o PickleIQ. Me conta o que voce procura e vou recomendar as melhores raquetes para voce.
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => handleSuggestedQuestion(q)}
                  className="text-sm border rounded-full px-4 py-2 hover:bg-muted transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
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
          <div className="flex justify-start mb-3">
            <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3 text-sm text-muted-foreground">
              <span className="inline-flex gap-1">
                <span className="animate-bounce [animation-delay:0ms]">.</span>
                <span className="animate-bounce [animation-delay:150ms]">.</span>
                <span className="animate-bounce [animation-delay:300ms]">.</span>
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="flex justify-center my-2">
            <div className="bg-destructive/10 text-destructive text-sm rounded-lg px-4 py-2">
              Erro ao conectar. Tente novamente.
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t px-4 py-3 bg-background">
        <form id="chat-form" onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Pergunte sobre raquetes..."
            className="flex-1 border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-xl text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
          >
            Enviar
          </button>
        </form>
      </div>
    </div>
  )
}
