import { cn } from "@/lib/utils"

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="skeleton"
      className={cn("animate-shimmer rounded-rounded bg-gradient-to-r from-surface via-elevated to-surface bg-[length:200%_100%]", className)}
      {...props}
    />
  )
}

export { Skeleton }
