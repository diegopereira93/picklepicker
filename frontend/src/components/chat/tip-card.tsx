interface TipCardProps {
  content: string
}

export function TipCard({ content }: TipCardProps) {
  return (
    <div className="hy-chat-card hy-chat-card-tip hy-animate-card-enter mt-2">
      <p
        className="text-sm text-[var(--color-gray-300)] leading-[var(--line-height-normal)]"
        style={{ lineHeight: 'var(--line-height-normal)' }}
      >
        {content}
      </p>
    </div>
  )
}
