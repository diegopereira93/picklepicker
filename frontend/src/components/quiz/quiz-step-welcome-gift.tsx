'use client'

interface QuizStepWelcomeGiftProps {
  onStart: () => void
}

export function QuizStepWelcomeGift({ onStart }: QuizStepWelcomeGiftProps) {
  return (
    <div className="max-w-3xl mx-auto wg-animate-step-enter space-y-8">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm text-gray-600">
          1 de 3: <span className="font-semibold text-coral">Vamos lá!</span>
        </div>
      </div>

      <div className="text-center space-y-6">
        <div className="text-9xl mb-4">🎁</div>
        <h2 className="text-2xl font-bold">Quer dar uma raquete de presente?</h2>
        <p className="text-lg text-gray-600">
          Responda 3 perguntas sobre quem vai receber e encontramos a opção perfeita.
        </p>
        <div className="flex justify-center mt-8">
          <button
            type="button"
            onClick={onStart}
            className="wg-button-coral text-lg px-8 py-3"
          >
            COMECAR →
          </button>
        </div>
      </div>
    </div>
  )
}
