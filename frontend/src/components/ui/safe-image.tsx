"use client"

import React from "react"

export function SafeImage({ src, alt, fallbackClassName, ...props }: {
  src: string | null | undefined
  alt: string
  fallbackClassName?: string
} & Omit<React.ComponentProps<"img">, "src">) {
  const [errored, setErrored] = React.useState(false)

  if (!src || errored) {
    return (
      <div
        className={fallbackClassName ?? "w-full h-48 bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground text-xs mb-3"}
        aria-label={`${alt} — imagem indisponível`}
      >
        Foto
      </div>
    )
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      loading="lazy"
      className={props.className}
      onError={() => setErrored(true)}
    />
  )
}
