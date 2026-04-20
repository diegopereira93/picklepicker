import Image from 'next/image'
import { cn } from '@/lib/utils'

interface PickleIQAvatarProps {
  size?: 'sm' | 'lg'
  className?: string
}

export function PickleIQAvatar({ size = 'sm', className }: PickleIQAvatarProps) {
  const px = size === 'lg' ? 48 : 32
  return (
    <div
      aria-hidden="true"
      className={cn(
        'shrink-0 rounded-full bg-elevated flex items-center justify-center',
        size === 'lg' ? 'w-12 h-12' : 'w-8 h-8',
        className
      )}
    >
      <Image
        src="/brand/logo-mark.svg"
        alt=""
        width={Math.round(px * 0.6)}
        height={Math.round(px * 0.6)}
        priority={size === 'lg'}
      />
    </div>
  )
}
