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
  { href: "/paddles", label: "CATÁLOGO" },
]

// Check if Clerk is available by checking for the provider context
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

// Auth buttons that only render if Clerk is available
function AuthButtons() {
  const clerkAvailable = useClerkAvailable()

  if (!clerkAvailable) {
    return null
  }

  // Dynamically import Clerk components only when available
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

// Mobile auth buttons
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
    <header className="hy-nav sticky top-0 z-50 w-full">
      <div className="hy-container flex h-14 items-center">
        {/* Logo */}
        <Link href="/" className="hy-nav-logo mr-6 flex items-center">
          <span className="hy-nav-brand">Pickle<span>IQ</span></span>
        </Link>

        {/* Desktop nav */}
        <nav className="hy-nav-links hidden items-center space-x-6 flex-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="hy-nav-link"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Desktop CTA */}
        <div className="hy-nav-cta hidden items-center space-x-2 ml-auto">
          <Button asChild>
            <Link href="/chat">Encontrar raquete</Link>
          </Button>
          {clerkAvailable && <AuthButtons />}
        </div>

        {/* Mobile hamburger */}
        <div className="hy-nav-mobile flex ml-auto">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Abrir menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="hy-nav-overlay">
              <SheetHeader>
                <SheetTitle>
                  <Link href="/" onClick={() => setOpen(false)} className="hy-nav-brand">
                    Pickle<span>IQ</span>
                  </Link>
                </SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col space-y-4 mt-6">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="hy-nav-link-mobile"
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
