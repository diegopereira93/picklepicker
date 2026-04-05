'use client'

import type { ChatRecommendation } from '@/types/paddle'

interface ComparisonCardProps {
  paddles: ChatRecommendation[]
}

function formatPrice(price: number): string {
  return price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function ComparisonCard({ paddles }: ComparisonCardProps) {
  if (paddles.length < 2) {
    return null
  }

  const bestPriceIndex = paddles.reduce(
    (minIndex, paddle, currentIndex) =>
      paddle.price_min_brl < paddles[minIndex].price_min_brl ? currentIndex : minIndex,
    0
  )

  const bestScoreIndex = paddles.reduce(
    (maxIndex, paddle, currentIndex) =>
      paddle.similarity_score > paddles[maxIndex].similarity_score ? currentIndex : maxIndex,
    0
  )

  return (
    <div className="hy-chat-card hy-chat-card-comparison hy-animate-card-enter mt-2">
      <table className="w-full text-sm border-collapse collapse">
        <thead>
          <tr>
            <th
              className="text-left text-xs font-bold uppercase tracking-wider text-[var(--color-gray-300)] py-3 px-4"
              scope="col"
            >
              Raquete
            </th>
            {paddles.map((paddle, index) => (
              <th
                key={paddle.paddle_id}
                className="text-center py-3 px-4"
                scope="col"
              >
                <span className="font-medium text-[var(--color-white)]">{paddle.brand}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="p-3 text-xs font-medium text-[var(--color-gray-500)]">Modelo</td>
            {paddles.map((paddle) => (
              <td key={paddle.paddle_id} className="p-3 text-center text-[var(--color-white)] font-semibold">
                {paddle.name}
              </td>
            ))}
          </tr>
          <tr>
            <td className="p-3 text-xs font-medium text-[var(--color-gray-500)]">Preco</td>
            {paddles.map((paddle, index) => (
              <td
                key={paddle.paddle_id}
                className="p-3 text-center"
                style={{
                  fontFamily: 'var(--font-data)',
                  color: index === bestPriceIndex ? 'var(--data-green)' : 'var(--color-white)',
                }}
              >
                {formatPrice(paddle.price_min_brl)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="p-3 text-xs font-medium text-[var(--color-gray-500)]">Match</td>
            {paddles.map((paddle, index) => (
              <td
                key={paddle.paddle_id}
                className="p-3 text-center"
                style={{
                  fontFamily: 'var(--font-data)',
                  fontWeight: 'bold',
                  color: index === bestScoreIndex ? 'var(--data-green)' : 'var(--color-white)',
                }}
              >
                {Math.round(paddle.similarity_score * 100)}%
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  )
}
