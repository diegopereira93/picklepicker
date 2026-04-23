import { SearchX } from 'lucide-react'
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center min-h-[60vh] px-4">
      <SearchX className="h-16 w-16 text-text-muted mb-6" />
      <h1 className="text-4xl font-display text-text-primary mb-4">
        Página não encontrada
      </h1>
      <p className="text-text-secondary mb-8 text-center max-w-md">
        A página que você está procurando não existe ou foi movida.
      </p>
      <Link
        href="/catalog"
        className="px-6 py-3 bg-brand-primary text-base font-semibold rounded-md hover:bg-brand-primary/90 transition-colors"
      >
        Voltar ao catálogo
      </Link>
    </div>
  )
}
