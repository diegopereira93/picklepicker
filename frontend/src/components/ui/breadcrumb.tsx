import Link from 'next/link'
import { ChevronRight, Home } from 'lucide-react'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  className?: string
}

function Breadcrumb({ items, className }: BreadcrumbProps) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.label,
      ...(item.href && { item: `https://pickleiq.com${item.href}` }),
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <nav aria-label="Breadcrumb" className={className}>
        <ol className="flex items-center gap-2 text-sm">
          {items.map((item, index) => {
            const isLast = index === items.length - 1
            const isFirst = index === 0
            return (
              <li key={index} className="flex items-center gap-2">
                {index > 0 && <ChevronRight className="h-3 w-3 text-text-muted" />}
                {isLast ? (
                  <span className="font-sans font-semibold text-text-primary">
                    {isFirst && <Home className="h-4 w-4 inline mr-1" />}
                    {item.label}
                  </span>
                ) : item.href ? (
                  <Link
                    href={item.href}
                    className="font-sans text-text-muted hover:text-text-primary transition-colors flex items-center gap-1"
                  >
                    {isFirst && <Home className="h-4 w-4" />}
                    {item.label}
                  </Link>
                ) : (
                  <span className="font-sans text-text-muted">{item.label}</span>
                )}
              </li>
            )
          })}
        </ol>
      </nav>
    </>
  )
}

export { Breadcrumb }
export type { BreadcrumbProps, BreadcrumbItem }
