import Link from "next/link"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-[#F5F2EB] py-16">
      <div className="max-w-6xl mx-auto px-4">
        <p className="text-[#2A2A2A] mb-6 max-w-2xl text-sm leading-relaxed">
          <strong>Divulgacao:</strong> PickleIQ pode receber comissoes por compras qualificadas
          realizadas atraves dos links de afiliados presentes neste site. Isso nao afeta o preco
          que voce paga nem nossas recomendacoes — so recomendamos produtos em que acreditamos.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <Link href="/" className="font-bold text-[#2A2A2A] text-xl">
              PickleIQ
            </Link>
            <p className="text-[#2A2A2A] text-sm mt-2">
              Conselheiro de raquetes de pickleball com IA
            </p>
          </div>

          <nav className="flex flex-col space-y-2">
            <Link href="/privacy" className="text-[#2A2A2A] hover:text-[#F97316] hover:underline transition-colors">
              Politica de Privacidade
            </Link>
            <Link href="/chat" className="text-[#2A2A2A] hover:text-[#F97316] hover:underline transition-colors">
              Chat IA
            </Link>
            <Link href="/paddles" className="text-[#2A2A2A] hover:text-[#F97316] hover:underline transition-colors">
              Comparar
            </Link>
          </nav>

          <div className="text-sm text-[#2A2A2A]">
            <p>&copy; {currentYear} PickleIQ. Todos os direitos reservados.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
