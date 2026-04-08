'use client'

import React from 'react'
import { cn } from '@/lib/utils'
import type { Paddle } from '@/types/paddle'
import { ProductCard } from './product-card'

interface AIMessageProps {
  content: string
  products?: Paddle[]
  className?: string
}

function AIMessage({ content, products, className }: AIMessageProps) {
  const formattedContent = content.split('\n').map((line, i, arr) => (
    <React.Fragment key={i}>
      {line.includes('**') ? (
        line.split(/(\*\*[^*]+\*\*)/g).map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={j} className="font-semibold">{part.slice(2, -2)}</strong>
          }
          return part
        })
      ) : (
        line
      )}
      {i < arr.length - 1 && <br />}
    </React.Fragment>
  ))

  return (
    <div
      className={cn('flex justify-start gap-3', className)}
      role="article"
    >
      <div className="w-8 h-8 rounded-full bg-brand-primary flex items-center justify-center shrink-0">
        <span className="font-mono text-xs font-semibold text-base">IQ</span>
      </div>
      <div className="bg-surface rounded-lg rounded-tl-sharp p-4 max-w-[70%]">
        <div className="font-sans text-sm text-text-primary leading-relaxed">
          {formattedContent}
        </div>
        {products && products.length > 0 && (
          <div className="flex flex-col gap-3 mt-3">
            {products.map((product) => (
              <ProductCard key={product.id} paddle={product} mode="chat" />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export { AIMessage }
