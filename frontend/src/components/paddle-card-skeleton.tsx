import { Skeleton } from '@/components/ui/skeleton'

export function PaddleCardSkeleton() {
  return (
    <div className="space-y-3 border rounded-lg p-4">
      <Skeleton className="h-[192px] w-full rounded-lg" />
      <Skeleton className="h-5 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <Skeleton className="h-4 w-1/4" />
      <Skeleton className="h-6 w-1/3" />
    </div>
  )
}

export function PaddleGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 min-h-[800px]">
      {Array.from({ length: count }).map((_, i) => (
        <PaddleCardSkeleton key={i} />
      ))}
    </div>
  )
}
