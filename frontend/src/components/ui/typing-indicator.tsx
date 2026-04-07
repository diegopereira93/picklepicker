'use client'

import { CSSProperties } from 'react'

interface TypingIndicatorProps {
  className?: string
}

function TypingIndicator({ className }: TypingIndicatorProps) {
  const styles = `
    @keyframes pulse {
      0%, 100% {
        opacity: 0.4;
        transform: scale(1);
      }
      50% {
        opacity: 1;
        transform: scale(1.2);
      }
    }
  `

  return (
    <>
      <style>{styles}</style>
      <div
        className={`flex gap-1.5 items-center p-3 ${className || ''}`}
        aria-label="Assistant is typing"
        aria-live="polite"
      >
        <div
          className="w-2 h-2 rounded-full bg-brand-primary animate-pulse"
          style={{
            animation: 'pulse 1s ease-in-out infinite',
            animationDelay: '0ms',
          } as CSSProperties}
        />
        <div
          className="w-2 h-2 rounded-full bg-brand-primary animate-pulse"
          style={{
            animation: 'pulse 1s ease-in-out infinite',
            animationDelay: '200ms',
          } as CSSProperties}
        />
        <div
          className="w-2 h-2 rounded-full bg-brand-primary animate-pulse"
          style={{
            animation: 'pulse 1s ease-in-out infinite',
            animationDelay: '400ms',
          } as CSSProperties}
        />
      </div>
    </>
  )
}

export { TypingIndicator }
