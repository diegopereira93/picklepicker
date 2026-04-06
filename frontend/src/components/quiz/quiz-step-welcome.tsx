'use client'

interface QuizStepWelcomeProps {
  onStart: () => void
}

export function QuizStepWelcome({ onStart }: QuizStepWelcomeProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-2xl mx-auto text-center wg-animate-fade-up space-y-6">
      <div className="text-8xl mb-4">🎾</div>
      <div className="space-y-3">
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
          Vamos encontrar sua raquete perfeita em 2 minutos
        </h2>
        <p className="text-lg text-gray-600 max-w-md mx-auto">
          Responda algumas perguntas rápidas e receba recomendações personalizadas com os melhores preços do Brasil.
        </p>
      </div>
      <button
        type="button"
        onClick={onStart}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onStart()
          }
        }}
        className="wg-button-coral text-lg px-8 py-3"
      >
        COMECAR →
      </button>
      <p className="text-sm text-gray-500 mt-2">
        ~2 minutos · Sem cadastro necessário
      </p>
    </div>
  )
}
