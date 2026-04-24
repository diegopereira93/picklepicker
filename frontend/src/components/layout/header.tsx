"use client"

import dynamic from "next/dynamic"
import Link from "next/link"
import { useState } from "react"
import { Menu } from "lucide-react"
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

const ClerkAuthButtons = dynamic(
  () => import("./clerk-auth-buttons").then(m => ({ default: m.ClerkAuthButtons })),
  { ssr: false }
)
const MobileClerkAuth = dynamic(
  () => import("./clerk-auth-buttons").then(m => ({ default: m.MobileClerkAuth })),
  { ssr: false }
)

const navLinks = [
  { href: "/", label: "HOME" },
  { href: "/quiz", label: "QUIZ" },
  { href: "/catalog", label: "CATÁLOGO" },
  { href: "/gift", label: "PRESENTE" },
  { href: "/blog", label: "BLOG" },
]

export { ClerkAvailableProvider } from "./clerk-available-provider"

export function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full bg-surface/95 backdrop-blur-md border-b border-border">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center">
        <Link href="/" className="font-bold text-xl mr-6 flex items-center py-1">
          <span className="text-text-primary">Pickle<span className="text-brand-secondary">IQ</span></span>
        </Link>

        <nav className="hidden md:flex items-center space-x-6 flex-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-text-primary font-semibold text-sm hover:text-brand-secondary transition-colors py-1"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden md:flex items-center space-x-2 ml-auto">
          <Link
            href="/quiz"
            className="inline-flex h-8 shrink-0 items-center justify-center rounded-lg bg-primary px-2.5 text-sm font-medium text-primary-foreground whitespace-nowrap transition-all outline-none select-none hover:bg-primary/80 focus-visible:ring-2 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50"
          >
            Encontrar raquete
          </Link>
          <ClerkAuthButtons />
        </div>

        <div className="md:hidden flex ml-auto">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger variant="ghost" size="icon" aria-label="Abrir menu">
              <Menu className="h-5 w-5 text-text-primary" />
            </SheetTrigger>
            <SheetContent side="right" className="bg-surface border-border">
              <SheetHeader>
                <SheetTitle>
                  <Link href="/" onClick={() => setOpen(false)} className="text-text-primary font-bold text-xl">
                    Pickle<span className="text-brand-secondary">IQ</span>
                  </Link>
                </SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col space-y-4 mt-6">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-text-primary font-semibold text-sm"
                    onClick={() => setOpen(false)}
                  >
                    {link.label}
                  </Link>
                ))}
                <MobileClerkAuth />
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
