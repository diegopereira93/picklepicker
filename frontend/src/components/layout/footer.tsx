import Link from "next/link"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t bg-muted/30">
      <div className="container py-8">
        {/* FTC Disclosure — above affiliate links per plan */}
        <p className="text-xs text-muted-foreground mb-6 max-w-2xl">
          <strong>Divulgacao:</strong> PickleIQ pode receber comissoes por compras qualificadas
          realizadas atraves dos links de afiliados presentes neste site. Isso nao afeta o preco
          que voce paga nem nossas recomendacoes — so recomendamos produtos em que acreditamos.
        </p>

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          {/* Branding */}
          <div>
            <Link href="/" className="font-bold text-lg text-primary">
              PickleIQ
            </Link>
            <p className="text-xs text-muted-foreground mt-1">
              Conselheiro de raquetes de pickleball com IA
            </p>
          </div>

          {/* Links */}
          <nav className="flex items-center space-x-6 text-sm text-muted-foreground">
            <Link href="/privacy" className="hover:text-foreground transition-colors">
              Politica de Privacidade
            </Link>
            <Link href="/chat" className="hover:text-foreground transition-colors">
              Chat IA
            </Link>
            <Link href="/compare" className="hover:text-foreground transition-colors">
              Comparar
            </Link>
          </nav>
        </div>

        <div className="mt-6 pt-6 border-t text-xs text-muted-foreground">
          <p>&copy; {currentYear} PickleIQ. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  )
}
