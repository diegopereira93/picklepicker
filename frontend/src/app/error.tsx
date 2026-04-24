'use client'

import { AlertTriangle } from 'lucide-react'
import Link from 'next/link'
import { useEffect } from 'react'

interface ErrorProps {
  error: Error & { digest?: string }
  reset: () => void
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="flex-1 flex flex-col items-center justify-center min-h-[60vh] px-4">
      <AlertTriangle className="h-16 w-16 text-brand-secondary mb-6" />
      <h1 className="text-4xl font-display text-text-primary mb-4">
        Algo deu errado
      </h1>
      <p className="text-text-secondary mb-8 text-center max-w-md">
        Encontramos um erro ao carregar esta página. Tente novamente.
      </p>
      <div className="flex gap-4">
        <button
          onClick={() => reset()}
          className="px-6 py-3 bg-brand-primary text-base font-semibold rounded-md hover:bg-brand-primary/90 transition-colors"
        >
          Tentar novamente
        </button>
        <Link
          href="/catalog"
          className="px-6 py-3 border border-border text-text-primary rounded-md hover:bg-surface transition-colors"
        >
          Voltar ao catálogo
        </Link>
      </div>
    </div>
  )
}
