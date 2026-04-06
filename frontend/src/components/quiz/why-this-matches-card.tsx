'use client'

interface WhyMatchesCardProps {
  reasons: string[]
}

export function WhyMatchesCard({ reasons }: WhyMatchesCardProps) {
  return (
    <div className="wg-why-matches">
      <p className="text-xs font-bold text-[#84CC16] uppercase tracking-wider mb-2">
        Por que pra voce
      </p>
      <ul className="space-y-1 text-sm text-[#2A2A2A]">
        {reasons.map((reason, index) => (
          <li key={index} className="flex items-start gap-1">
            <span className="text-[#84CC16]">✓</span>
            <span>{reason}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
