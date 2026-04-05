export function FeatureSteps() {
  const steps = [
    {
      number: 1,
      title: 'Responda o quiz',
      description: 'Responda 3 perguntas sobre seu nivel, orcamento e estilo de jogo',
    },
    {
      number: 2,
      title: 'Analise com IA',
      description: 'Nosso sistema processa suas respostas e gera recomendacoes personalizadas',
    },
    {
      number: 3,
      title: 'Compare precos',
      description: 'Acesse ofertas reais das lojas brasileiras e faca sua escolha',
    },
  ]

  return (
    <section className="hy-light-section hy-section">
      <div className="hy-container">
        <span className="hy-section-label text-center block mb-10">COMO FUNCIONA</span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-6 relative">
          {steps.map((step, index) => (
            <div key={step.number} className="text-center relative">
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-8 left-1/2 w-full h-[2px]"
                     style={{
                       backgroundColor: 'var(--sport-primary)',
                       opacity: 0.5,
                     }} />
              )}

              <div className="relative z-10 mx-auto mb-6 w-16 h-16 rounded-full flex items-center justify-center"
                   style={{
                     border: '2px solid var(--sport-primary)',
                     backgroundColor: 'var(--color-white)',
                   }}>
                <span className="hy-data" style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: 'var(--data-green)',
                }}>
                  {step.number}
                </span>
              </div>

              <h3 className="hy-heading text-center mb-3" style={{ color: '#000000' }}>
                {step.title}
              </h3>
              <p style={{
                fontSize: 'var(--font-size-link)',
                color: 'var(--color-gray-500)',
                lineHeight: 'var(--line-height-normal)',
              }}>
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
