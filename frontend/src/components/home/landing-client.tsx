'use client'

import Link from 'next/link'
import { useState, useEffect, useRef, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { fetchPaddles } from '@/lib/api'
import { ListChecks, Bot, Trophy, Brain, MessageSquare, GitCompare, Bell } from 'lucide-react'

function useScrollAnimation() {
  const ref = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion) {
      setIsVisible(true)
      return
    }

    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(element)
        }
      },
      { threshold: 0.1 }
    )

    observer.observe(element)

    return () => observer.disconnect()
  }, [])

  return { ref, isVisible }
}

function AnimatedSection({ children, className, delay = 0 }: {
  children: ReactNode
  className?: string
  delay?: number
}) {
  const { ref, isVisible } = useScrollAnimation()

  return (
    <div
      ref={ref}
      className={cn(
        'transition-all duration-700 ease-out',
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
        className
      )}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}

export function LandingClient() {
  const [mounted, setMounted] = useState(false)
  const statsRef = useRef<HTMLDivElement>(null)
  const [counterValues, setCounterValues] = useState<number[]>([0, 0, 0])
  const [hasAnimated, setHasAnimated] = useState(false)
  const [paddleTotal, setPaddleTotal] = useState(0)
  const [statsLoaded, setStatsLoaded] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    fetchPaddles({ limit: 1 })
      .then((data) => {
        setPaddleTotal(data.total)
        setStatsLoaded(true)
      })
      .catch(() => {
        setPaddleTotal(500)
        setStatsLoaded(true)
      })
  }, [mounted])

  useEffect(() => {
    if (!mounted || !statsRef.current || hasAnimated || !statsLoaded) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            setHasAnimated(true)

            const targets = [paddleTotal || 500, 10, (paddleTotal || 500) * 5]
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

            if (prefersReducedMotion) {
              setCounterValues(targets)
              return
            }

            const duration = 2000
            const startTime = performance.now()

            const animate = (currentTime: number) => {
              const elapsed = currentTime - startTime
              const progress = Math.min(elapsed / duration, 1)
              const eased = 1 - Math.pow(1 - progress, 3)
              setCounterValues(targets.map(t => Math.floor(t * eased)))

              if (progress < 1) {
                requestAnimationFrame(animate)
              }
            }

            requestAnimationFrame(animate)
          }
        })
      },
      { threshold: 0.1 }
    )

    observer.observe(statsRef.current)

    return () => observer.disconnect()
  }, [mounted, hasAnimated, statsLoaded, paddleTotal])

  if (!mounted) return null

  const precosMonitorados = (paddleTotal || 500) * 5

  return (
    <div className="font-sans bg-base text-text-primary min-h-screen">
      <section className="min-h-[80vh] flex flex-col justify-center items-center text-center px-4">
        <AnimatedSection>
          <h1 className="font-display text-4xl md:text-5xl lg:text-6xl text-text-primary leading-tight tracking-wide mb-6">
            Encontre a raquete perfeita. <br className="hidden md:block" /> Potencializada por IA.
          </h1>

          <p className="font-sans text-base md:text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed mb-8">
            Responda 7 perguntas rápidas. Receba recomendações personalizadas da nossa IA. Sem spam, sem enrolação.
          </p>

          <Button
            asChild
            variant="default"
            size="lg"
            className="mt-4 md:mt-8 font-sans font-semibold tracking-wide bg-brand-primary hover:bg-brand-primary/90 text-base shadow-glow-green hover:shadow-glow-green focus-visible:ring-2 focus-visible:ring-brand-primary focus-visible:ring-offset-2 focus-visible:ring-offset-base"
          >
            <Link href="/quiz" className="text-base">
              Encontrar minha raquete
            </Link>
          </Button>

          <a href="#how-it-works" className="sr-only focus:not-sr-only focus:absolute focus:-translate-y-8 focus:left-4 focus:bg-base focus:text-text-primary focus:px-4 focus:py-2 focus:rounded-rounded focus:z-50">
            Pular para conteúdo principal
          </a>
        </AnimatedSection>
      </section>

      <section id="how-it-works" className="py-20 bg-surface">
        <div className="max-w-7xl mx-auto px-4 md:px-8 lg:px-16">
          <h2 className="sr-only">Como funciona</h2>

          <div className="flex flex-col md:flex-row gap-8 md:gap-12 justify-center">
            <AnimatedSection delay={0}>
              <div className="flex flex-col items-center text-center p-6 max-w-[240px]">
                <div className="w-12 h-12 rounded-full bg-brand-primary flex items-center justify-center mb-4">
                  <span className="font-mono text-2xl font-semibold text-base">1</span>
                </div>
                <ListChecks className="w-8 h-8 text-text-muted mb-4" />
                <h3 className="font-sans font-semibold text-lg text-text-primary">Faça o Quiz</h3>
                <p className="font-sans text-sm text-text-secondary mt-2">
                  7 perguntas sobre seu jogo, estilo e orçamento
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={100}>
              <div className="flex flex-col items-center text-center p-6 max-w-[240px]">
                <div className="w-12 h-12 rounded-full bg-brand-primary flex items-center justify-center mb-4">
                  <span className="font-mono text-2xl font-semibold text-base">2</span>
                </div>
                <Bot className="w-8 h-8 text-text-muted mb-4" />
                <h3 className="font-sans font-semibold text-lg text-text-primary">IA Analisa</h3>
                <p className="font-sans text-sm text-text-secondary mt-2">
                  Nossa IA encontra as raquetes perfeitas entre 500+ opções
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={200}>
              <div className="flex flex-col items-center text-center p-6 max-w-[240px]">
                <div className="w-12 h-12 rounded-full bg-brand-primary flex items-center justify-center mb-4">
                  <span className="font-mono text-2xl font-semibold text-base">3</span>
                </div>
                <Trophy className="w-8 h-8 text-text-muted mb-4" />
                <h3 className="font-sans font-semibold text-lg text-text-primary">Jogue Melhor</h3>
                <p className="font-sans text-sm text-text-secondary mt-2">
                  Receba suas recomendações personalizadas instantaneamente
                </p>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      <section ref={statsRef} className="py-16 bg-elevated">
        <AnimatedSection>
          <div className="max-w-7xl mx-auto px-4 md:px-8 lg:px-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-surface border border-border rounded-lg p-8 text-center">
                <div className="font-mono text-4xl text-brand-primary">
                  {counterValues[0] ?? (paddleTotal || 500)}+
                </div>
                <div className="font-sans text-sm text-text-muted uppercase tracking-widest mt-2">
                  Raquetes analisadas
                </div>
              </div>

              <div className="bg-surface border border-border rounded-lg p-8 text-center">
                <div className="font-mono text-4xl text-brand-primary">
                  {counterValues[1] ?? 10}
                </div>
                <div className="font-sans text-sm text-text-muted uppercase tracking-widest mt-2">
                  Marcas comparadas
                </div>
              </div>

              <div className="bg-surface border border-border rounded-lg p-8 text-center">
                <div className="font-mono text-4xl text-brand-primary">
                  {counterValues[2]?.toLocaleString('pt-BR') ?? precosMonitorados.toLocaleString('pt-BR')}
                </div>
                <div className="font-sans text-sm text-text-muted uppercase tracking-widest mt-2">
                  Preços monitorados
                </div>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </section>

      <section className="py-20 bg-base">
        <div className="max-w-7xl mx-auto px-4 md:px-8 lg:px-16">
          <AnimatedSection>
            <h2 className="font-display text-3xl text-text-primary text-center tracking-wide mb-12">
              Recursos
            </h2>
          </AnimatedSection>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AnimatedSection delay={0}>
              <div className="bg-surface border border-border rounded-lg p-6">
                <div className="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4">
                  <Brain className="w-6 h-6 text-brand-primary" />
                </div>
                <h3 className="font-sans font-semibold text-lg text-text-primary mb-2">
                  Quiz Inteligente
                </h3>
                <p className="font-sans text-sm text-text-secondary leading-relaxed">
                  7 perguntas que realmente importam. Sem enrolação, apenas o que afeta seu jogo.
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={100}>
              <div className="bg-surface border border-border rounded-lg p-6">
                <div className="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4">
                  <MessageSquare className="w-6 h-6 text-brand-primary" />
                </div>
                <h3 className="font-sans font-semibold text-lg text-text-primary mb-2">
                  Chat com IA
                </h3>
                <p className="font-sans text-sm text-text-secondary leading-relaxed">
                  Pergunte qualquer coisa. 'Melhor para iniciantes até R$300?' Respostas instantâneas.
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={200}>
              <div className="bg-surface border border-border rounded-lg p-6">
                <div className="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4">
                  <GitCompare className="w-6 h-6 text-brand-primary" />
                </div>
                <h3 className="font-sans font-semibold text-lg text-text-primary mb-2">
                  Comparador
                </h3>
                <p className="font-sans text-sm text-text-secondary leading-relaxed">
                  Especificações lado a lado. Veja exatamente o que muda. Sem achismo.
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={300}>
              <div className="bg-surface border border-border rounded-lg p-6">
                <div className="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4">
                  <Bell className="w-6 h-6 text-brand-primary" />
                </div>
                <h3 className="font-sans font-semibold text-lg text-text-primary mb-2">
                  Alertas de Preço
                </h3>
                <p className="font-sans text-sm text-text-secondary leading-relaxed">
                  Monitore quedas de preço. Avisamos quando sua raquete entra em promoção.
                </p>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      <section className="py-20 bg-surface">
        <div className="max-w-7xl mx-auto px-4 md:px-8 lg:px-16">
          <AnimatedSection>
            <h2 className="font-display text-3xl text-text-primary text-center tracking-wide mb-12">
              Por que jogadores confiam no PickleIQ
            </h2>
          </AnimatedSection>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <AnimatedSection delay={0}>
              <div className="text-center p-6">
                <div className="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4 mx-auto">
                  <Trophy className="w-6 h-6 text-brand-primary" />
                </div>
                <h3 className="font-sans font-semibold text-lg text-text-primary mb-2">
                  Dados reais
                </h3>
                <p className="font-sans text-sm text-text-secondary leading-relaxed">
                  Preços coletados diariamente de varejistas brasileiros
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={100}>
              <div className="text-center p-6">
                <div className="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4 mx-auto">
                  <Brain className="w-6 h-6 text-brand-primary" />
                </div>
                <h3 className="font-sans font-semibold text-lg text-text-primary mb-2">
                  IA personalizada
                </h3>
                <p className="font-sans text-sm text-text-secondary leading-relaxed">
                  Recomendações baseadas no seu nível e estilo de jogo
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={200}>
              <div className="text-center p-6">
                <div className="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4 mx-auto">
                  <GitCompare className="w-6 h-6 text-brand-primary" />
                </div>
                <h3 className="font-sans font-semibold text-lg text-text-primary mb-2">
                  Comparação justa
                </h3>
                <p className="font-sans text-sm text-text-secondary leading-relaxed">
                  Veja especificações e preços lado a lado
                </p>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      <section className="py-24 bg-elevated">
        <div className="max-w-7xl mx-auto px-4 md:px-8 lg:px-16">
          <AnimatedSection>
            <div className="bg-surface border border-border rounded-2xl p-12 md:p-16 text-center max-w-3xl mx-auto">
              <h2 className="font-display text-3xl md:text-4xl text-text-primary tracking-wide mb-4">
                Pronto para encontrar sua raquete perfeita?
              </h2>

              <p className="font-sans text-base text-text-secondary mt-4">
                Junte-se a {precosMonitorados.toLocaleString('pt-BR')}+ jogadores que melhoraram seu jogo com recomendações IA.
              </p>

              <Button
                asChild
                variant="default"
                size="lg"
                className="mt-8 font-sans font-semibold tracking-wide bg-brand-primary hover:bg-brand-primary/90 text-base shadow-glow-green hover:shadow-glow-green focus-visible:ring-2 focus-visible:ring-brand-primary focus-visible:ring-offset-2 focus-visible:ring-offset-base"
              >
                <Link href="/quiz" className="text-base">
                  Encontrar minha raquete
                </Link>
              </Button>
            </div>
          </AnimatedSection>
        </div>
      </section>
    </div>
  )
}
