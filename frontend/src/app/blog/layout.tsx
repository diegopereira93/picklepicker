import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Blog PickleIQ',
  description: 'Guias, análises e dicas de pickleball',
  robots: 'index, follow',
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 container py-12 prose prose-lg max-w-3xl mx-auto dark:prose-invert">
        {children}
      </main>

      <footer className="border-t bg-slate-50 dark:bg-slate-900 py-8">
        <div className="container max-w-3xl mx-auto text-sm text-slate-600 dark:text-slate-400">
          <h3 id="ftc-disclaimer" className="font-bold text-slate-900 dark:text-slate-50 mb-2">
            Divulgação FTC
          </h3>
          <p>
            PickleIQ usa links de afiliado para financiar este site. Quando você compra
            através de um link de afiliado, você não paga nada a mais, mas recebemos uma
            pequena comissão. Isso ajuda a manter nossos guias e análises independentes de
            qualidade.
          </p>
        </div>
      </footer>
    </div>
  )
}
