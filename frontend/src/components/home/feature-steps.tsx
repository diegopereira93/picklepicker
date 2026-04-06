export function FeatureSteps() {
  const steps = [
    {
      number: 1,
      title: 'Responda o quiz',
      description: 'Responda 7 perguntas rapidas sobre seu jogo',
    },
    {
      number: 2,
      title: 'Receba recomendacoes',
      description: '3 raquetes selecionadas pra voce',
    },
    {
      number: 3,
      title: 'Compare precos',
      description: 'Melhores precos em tempo real',
    },
    {
      number: 4,
      title: 'Compre com confianca',
      description: 'Links diretos para as lojas',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {steps.map((step, index) => (
        <div key={step.number} className="flex gap-4">
          <div className="flex-shrink-0 flex flex-col items-center justify-center min-w-[56px]">
            <div className="w-14 h-14 rounded-full flex items-center justify-center"
                 style={{
                   border: '2px solid var(--accent-coral)',
                   backgroundColor: 'white',
                 }}>
              <span className="font-bold" style={{
                fontSize: '1.5rem',
                color: 'var(--accent-coral)',
              }}>
                {step.number}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div className="w-0.5 h-full mt-4" style={{ backgroundColor: 'var(--accent-coral)', opacity: 0.2 }}></div>
            )}
          </div>
          <div>
            <h3 className="font-semibold text-[#2A2A2A] mb-2">
              {step.title}
            </h3>
            <p className="text-sm text-gray-600">
              {step.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
