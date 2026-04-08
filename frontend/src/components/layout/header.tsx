"use client"

import Link from "next/link"
import { useState, createContext, useContext, ReactNode } from "react"
import { Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
const navLinks = [
  { href: "/", label: "HOME" },
  { href: "/quiz", label: "QUIZ" },
  { href: "/catalog", label: "CATÁLOGO" },
]

const ClerkAvailableContext = createContext<boolean>(false)

export function ClerkAvailableProvider({
  available,
  children
}: {
  available: boolean
  children: ReactNode
}) {
  return (
    <ClerkAvailableContext.Provider value={available}>
      {children}
    </ClerkAvailableContext.Provider>
  )
}

function useClerkAvailable() {
  return useContext(ClerkAvailableContext)
}

function AuthButtons() {
  const clerkAvailable = useClerkAvailable()
  if (!clerkAvailable) {
    return null
  }
  const { SignInButton, UserButton, useAuth } = require("@clerk/nextjs")
  const { isSignedIn } = useAuth()
  return (
    <>
      {!isSignedIn && (
        <SignInButton mode="modal">
          <Button variant="outline" size="sm">Entrar</Button>
        </SignInButton>
      )}
      {isSignedIn && <UserButton afterSignOutUrl="/" />}
    </>
  )
}

function MobileAuth() {
  const clerkAvailable = useClerkAvailable()
  if (!clerkAvailable) {
    return null
  }
  const { SignInButton, UserButton, useAuth } = require("@clerk/nextjs")
  const { isSignedIn } = useAuth()
  return (
    <>
      {!isSignedIn && (
        <SignInButton mode="modal">
          <Button variant="outline" className="mt-2 w-full">Entrar</Button>
        </SignInButton>
      )}
      {isSignedIn && (
        <div className="mt-2">
          <UserButton afterSignOutUrl="/" />
        </div>
      )}
    </>
  )
}

export function Header() {
  const [open, setOpen] = useState(false)
  const clerkAvailable = useClerkAvailable()

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
          {clerkAvailable && <AuthButtons />}
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
                {clerkAvailable && <MobileAuth />}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
