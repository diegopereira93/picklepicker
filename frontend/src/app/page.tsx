import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Bot, BarChart2, Tag } from "lucide-react";

const valueProps = [
  {
    icon: Bot,
    title: "Recomendacao IA",
    description:
      "Descreva seu estilo de jogo e orcamento. Nosso agente de IA recomenda as melhores raquetes com justificativa personalizada em linguagem simples.",
  },
  {
    icon: BarChart2,
    title: "Comparador",
    description:
      "Compare raquetes lado a lado com graficos de radar. Swingweight, twistweight, espessura do nucleo — tudo traduzido para voce.",
  },
  {
    icon: Tag,
    title: "Melhores Precos",
    description:
      "Precos atualizados diariamente dos principais varejistas brasileiros. Encontre o melhor negocio sem precisar visitar varios sites.",
  },
];

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero section */}
      <section className="nv-dark-section nv-hero nv-section-hero">
        <div className="nv-container flex flex-col items-center text-center gap-6">
          <h1 className="nv-display max-w-3xl">
            Encontre a raquete{" "}
            <span style={{ color: '#76b900' }}>perfeita</span> para voce
          </h1>
          <p className="nv-subheading max-w-2xl">
            PickleIQ usa inteligencia artificial para recomendar raquetes de
            pickleball com base no seu nivel de jogo, estilo e orcamento.
            Precos em tempo real dos varejistas brasileiros.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 mt-2">
            <Button asChild size="lg">
              <Link href="/chat">Comecar agora — e gratis</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/paddles">Ver catalogo</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Value props */}
      <section className="nv-light-section nv-section">
        <div className="nv-container">
          <p className="nv-section-label text-center">RECURSOS</p>
          <h2 className="nv-section-heading text-center mb-10" style={{ color: '#000000' }}>
            Tudo que voce precisa para escolher bem
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {valueProps.map((prop) => {
              const Icon = prop.icon;
              return (
                <Card key={prop.title} className="nv-card flex flex-col">
                  <CardHeader>
                    <div className="mb-2 w-10 h-10 flex items-center justify-center">
                      <Icon className="h-5 w-5" style={{ color: '#76b900' }} />
                    </div>
                    <CardTitle className="nv-card-title-text">{prop.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="nv-card-description">
                      {prop.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA banner */}
      <section className="nv-dark-section nv-section">
        <div className="nv-container flex flex-col items-center text-center gap-4">
          <p className="nv-section-label">COMECE AGORA</p>
          <h2 className="nv-section-heading">
            Pronto para encontrar sua raquete?
          </h2>
          <p className="nv-subheading max-w-lg">
            Responda 3 perguntas rapidas e receba recomendacoes personalizadas
            com os melhores precos do mercado brasileiro.
          </p>
          <Button asChild size="lg" className="mt-2">
            <Link href="/chat">Falar com o PickleIQ</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
