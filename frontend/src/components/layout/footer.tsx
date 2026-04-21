import Link from "next/link"
import { ExternalLink } from "lucide-react"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-surface border-t border-border py-12">
      <div className="max-w-6xl mx-auto px-4">
        <p className="text-text-muted mb-6 max-w-2xl text-sm leading-relaxed">
          <strong className="text-text-secondary">Divulgação:</strong> PickleIQ pode receber comissões por compras qualificadas
          realizadas através dos links de afiliados presentes neste site. Isso não afeta o preço
          que você paga nem nossas recomendações — só recomendamos produtos em que acreditamos.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <Link href="/" className="font-bold text-text-primary text-xl">
              Pickle<span className="text-brand-secondary">IQ</span>
            </Link>
            <p className="text-text-muted text-sm mt-2">
              Conselheiro de raquetes de pickleball com IA
            </p>
          </div>

          <div>
            <h3 className="font-sans font-semibold text-sm text-text-primary mb-3">Produto</h3>
            <nav className="flex flex-col space-y-2">
              <Link href="/quiz" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Quiz
              </Link>
              <Link href="/catalog" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Catálogo
              </Link>
              <Link href="/compare" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Comparar
              </Link>
              <Link href="/gift" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Presentes
              </Link>
            </nav>
          </div>

          <div>
            <h3 className="font-sans font-semibold text-sm text-text-primary mb-3">Conteúdo</h3>
            <nav className="flex flex-col space-y-2">
              <Link href="/blog" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Blog
              </Link>
              <Link href="/chat" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Chat IA
              </Link>
              <Link href="/about" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Sobre
              </Link>
              <Link href="/faq" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                FAQ
              </Link>
              <Link href="/privacy" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Privacidade
              </Link>
              <Link href="/terms" className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm">
                Termos
              </Link>
            </nav>
          </div>

          <div>
            <h3 className="font-sans font-semibold text-sm text-text-primary mb-3">Social</h3>
            <nav className="flex flex-col space-y-2">
              <a
                href="https://instagram.com/pickleiq"
                target="_blank"
                rel="noopener noreferrer"
                className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm flex items-center gap-2"
              >
                <ExternalLink size={14} />
                Instagram
              </a>
              <a
                href="https://youtube.com/@pickleiq"
                target="_blank"
                rel="noopener noreferrer"
                className="text-text-muted hover:text-brand-secondary hover:underline transition-colors text-sm flex items-center gap-2"
              >
                <ExternalLink size={14} />
                YouTube
              </a>
            </nav>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-border text-sm text-text-muted">
          <p>&copy; {currentYear} PickleIQ. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  )
}
