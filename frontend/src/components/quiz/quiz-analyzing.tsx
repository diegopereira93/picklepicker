'use client'

import { useEffect, useState } from 'react'

interface QuizAnalyzingProps {
  onComplete: () => void
}

export function QuizAnalyzing({ onComplete }: QuizAnalyzingProps) {
  const [progress, setProgress] = useState(0)
  const [completedTasks, setCompletedTasks] = useState(0)

  useEffect(() => {
    const taskTimeouts = [
      setTimeout(() => setCompletedTasks(1), 1000),
      setTimeout(() => setCompletedTasks(2), 1500),
    ]

    let completed = false
    const progressInterval = window.setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          if (!completed) {
            completed = true
            setTimeout(() => onComplete(), 1000)
          }
          return 100
        }
        return prev + 4
      })
    }, 100)

    return () => {
      taskTimeouts.forEach(clearTimeout)
      clearInterval(progressInterval)
    }
  }, [onComplete])

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-xl mx-auto text-center space-y-8 wg-animate-fade-up">
      <div className="text-9xl mb-4">🎯</div>
      <h2 className="text-3xl font-bold">Analisando seu perfil...</h2>

      <div className="flex flex-col gap-4 w-full items-center">
        <div className={`flex items-center gap-3 ${completedTasks >= 1 ? 'text-green-600' : 'text-gray-600'}`}>
          {completedTasks >= 1 ? '✓' : '◐'} Nível de jogo identificado
        </div>
        <div className={`flex items-center gap-3 ${completedTasks >= 2 ? 'text-green-600' : 'text-gray-600'}`}>
          {completedTasks >= 2 ? '✓' : ' ◐'} Estilo de jogo mapeado
        </div>
        <div className={`flex items-center gap-3 ${completedTasks >= 3 ? 'text-green-600' : 'text-gray-600 animate-pulse'}`}>
          {completedTasks >= 3 ? '✓' : ' ◐'} Buscando raquetes compatíveis...
        </div>
      </div>

      <div 
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Analisando recomendações"
        className="w-full max-w-sm space-y-2"
      >
        <div className="flex justify-between text-sm text-gray-600">
          <span>Analisando...</span>
          <span>{progress}%</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-coral wg-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  )
}
