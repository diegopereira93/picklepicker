import Link from "next/link"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-surface border-t border-border py-12">
      <div className="max-w-6xl mx-auto px-4">
        <p className="text-text-muted mb-6 max-w-2xl text-sm leading-relaxed">
          <strong className="text-text-secondary">Divulgacao:</strong> PickleIQ pode receber comissoes por compras qualificadas
          realizadas atraves dos links de afiliados presentes neste site. Isso nao afeta o preco
          que voce paga nem nossas recomendacoes — so recomendamos produtos em que acreditamos.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <Link href="/" className="font-bold text-text-primary text-xl">
              Pickle<span className="text-brand-secondary">IQ</span>
            </Link>
            <p className="text-text-muted text-sm mt-2">
              Conselheiro de raquetes de pickleball com IA
            </p>
          </div>

          <nav className="flex flex-col space-y-2">
            <Link href="/privacy" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors">
              Politica de Privacidade
            </Link>
            <Link href="/chat" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors">
              Chat IA
            </Link>
            <Link href="/catalog" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors">
              Comparar
            </Link>
          </nav>

          <div className="text-sm text-text-muted">
            <p>&copy; {currentYear} PickleIQ. Todos os direitos reservados.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
