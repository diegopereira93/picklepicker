interface TipCardProps {
  content: string
}

export function TipCard({ content }: TipCardProps) {
  return (
    <div className="mt-2 bg-elevated border-l-2 border-brand-primary rounded-rounded px-4 py-3 animate-slide-in">
      <p className="text-sm text-text-secondary leading-relaxed">{content}</p>
    </div>
  )
}
