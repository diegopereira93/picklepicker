import { Metadata } from "next"

export const metadata: Metadata = {
  title: "Catálogo de Raquetes | PickleIQ",
  description: "Compare preços e especificações de raquetes de pickleball. Encontre a raquete ideal com análise de IA.",
  alternates: {
    canonical: "https://pickleiq.com/catalog",
  },
  openGraph: {
    type: "website",
    url: "https://pickleiq.com/catalog",
    title: "Catálogo de Raquetes | PickleIQ",
    description: "Compare preços e especificações de raquetes de pickleball disponíveis no Brasil.",
  },
}

export default function CatalogLayout({ children }: { children: React.ReactNode }) {
  return children
}