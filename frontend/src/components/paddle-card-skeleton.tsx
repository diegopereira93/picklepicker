export function PaddleCardSkeleton() {
  return (
    <div className="nv-product-card nv-skeleton-card">
      <div className="nv-skeleton-line nv-skeleton-image" />
      <div className="nv-skeleton-line nv-skeleton-line-title" />
      <div className="nv-skeleton-line w-1/2" />
      <div className="nv-skeleton-line w-1/4" />
      <div className="nv-skeleton-line w-1/3" />
    </div>
  )
}

export function PaddleGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="nv-catalog-grid">
      {Array.from({ length: count }).map((_, i) => (
        <PaddleCardSkeleton key={i} />
      ))}
    </div>
  )
}