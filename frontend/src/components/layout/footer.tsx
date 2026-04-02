import Link from "next/link"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="hy-footer hy-dark-section">
      <div className="hy-container">
        {/* FTC Disclosure — above affiliate links per plan */}
        <p className="hy-caption-small mb-6 max-w-2xl">
          <strong>Divulgacao:</strong> PickleIQ pode receber comissoes por compras qualificadas
          realizadas atraves dos links de afiliados presentes neste site. Isso nao afeta o preco
          que voce paga nem nossas recomendacoes — so recomendamos produtos em que acreditamos.
        </p>

        <div className="hy-footer-grid">
          {/* Branding */}
          <div>
            <Link href="/" className="hy-nav-brand">
              PickleIQ
            </Link>
            <p className="hy-caption-small mt-1">
              Conselheiro de raquetes de pickleball com IA
            </p>
          </div>

          {/* Links */}
          <nav className="flex flex-col space-y-2">
            <Link href="/privacy" className="hy-link-dark">
              Politica de Privacidade
            </Link>
            <Link href="/chat" className="hy-link-dark">
              Chat IA
            </Link>
            <Link href="/paddles" className="hy-link-dark">
              Comparar
            </Link>
          </nav>

          {/* Copyright */}
          <div className="hy-caption-small">
            <p>&copy; {currentYear} PickleIQ. Todos os direitos reservados.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
