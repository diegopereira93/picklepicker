import Link from "next/link"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="nv-footer nv-dark-section">
      <div className="nv-container">
        {/* FTC Disclosure — above affiliate links per plan */}
        <p className="nv-caption-small mb-6 max-w-2xl">
          <strong>Divulgacao:</strong> PickleIQ pode receber comissoes por compras qualificadas
          realizadas atraves dos links de afiliados presentes neste site. Isso nao afeta o preco
          que voce paga nem nossas recomendacoes — so recomendamos produtos em que acreditamos.
        </p>

        <div className="nv-footer-grid">
          {/* Branding */}
          <div>
            <Link href="/" className="nv-nav-brand">
              PickleIQ
            </Link>
            <p className="nv-caption-small mt-1">
              Conselheiro de raquetes de pickleball com IA
            </p>
          </div>

          {/* Links */}
          <nav className="flex flex-col space-y-2">
            <Link href="/privacy" className="nv-link-dark">
              Politica de Privacidade
            </Link>
            <Link href="/chat" className="nv-link-dark">
              Chat IA
            </Link>
            <Link href="/paddles" className="nv-link-dark">
              Comparar
            </Link>
          </nav>

          {/* Copyright */}
          <div className="nv-caption-small">
            <p>&copy; {currentYear} PickleIQ. Todos os direitos reservados.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
