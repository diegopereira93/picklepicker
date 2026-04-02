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
    size: "default" as const,
  },
  {
    icon: BarChart2,
    title: "Comparador",
    description:
      "Compare raquetes lado a lado com graficos de radar. Swingweight, twistweight, espessura do nucleo — tudo traduzido para voce.",
    size: "default" as const,
  },
  {
    icon: Tag,
    title: "Melhores Precos",
    description:
      "Precos atualizados diariamente dos principais varejistas brasileiros. Encontre o melhor negocio sem precisar visitar varios sites.",
    size: "compact" as const,
  },
];

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero section */}
      <section className="hy-dark-section hy-hero hy-section-hero">
        <div className="hy-container flex flex-col items-center text-center gap-6">
          <h1 className="hy-display max-w-3xl">
            Encontre a raquete{" "}
            <span style={{ color: '#76b900' }}>perfeita</span> para voce
          </h1>
          <p className="hy-subheading max-w-2xl">
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
      <section className="hy-light-section hy-section">
        <div className="hy-container">
          <p className="hy-section-label text-center">RECURSOS</p>
          <h2 className="hy-section-heading text-center mb-10" style={{ color: '#000000' }}>
            Tudo que voce precisa para escolher bem
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {valueProps.map((prop) => {
              const Icon = prop.icon;
              const isCompact = prop.size === "compact";
              return (
                <Card key={prop.title} className={`hy-card flex flex-col ${isCompact ? 'md:transform md:translate-y-4' : ''}`}>
                  <CardHeader>
                    <div className={`mb-2 flex items-center justify-center ${isCompact ? 'w-8 h-8' : 'w-10 h-10'}`}>
                      <Icon className={`${isCompact ? 'h-4 w-4' : 'h-5 w-5'}`} style={{ color: '#76b900' }} />
                    </div>
                    <CardTitle className="hy-card-title-text">{prop.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="hy-card-description">
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
      <section className="hy-dark-section hy-section">
        <div className="hy-container flex flex-col items-center text-center gap-4">
          <p className="hy-section-label">COMECE AGORA</p>
          <h2 className="hy-section-heading">
            Pronto para encontrar sua raquete?
          </h2>
          <p className="hy-subheading max-w-lg">
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
