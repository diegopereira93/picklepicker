'use client'

interface SuggestedQuestionsProps {
  questions: string[]
  onSelect: (question: string) => void
  disabled?: boolean
}

export function SuggestedQuestions({ questions, onSelect, disabled }: SuggestedQuestionsProps) {
  if (questions.length === 0) {
    return null
  }

  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {questions.map((question, index) => (
        <button
          key={index}
          type="button"
          onClick={() => onSelect(question)}
          disabled={disabled}
          className="hy-quiz-pill text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:border-[var(--sport-primary)]"
        >
          {question}
        </button>
      ))}
    </div>
  )
}
