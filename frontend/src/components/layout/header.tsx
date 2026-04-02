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
import { ThemeToggle } from "@/components/theme-toggle"

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/paddles", label: "Catalogo" },
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
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        {/* Logo */}
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <span className="font-bold text-xl text-primary">PickleIQ</span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium flex-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-foreground/60 transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Desktop CTA */}
        <div className="hidden md:flex items-center space-x-2 ml-auto">
          <ThemeToggle />
          <Button asChild size="sm">
            <Link href="/chat">Encontrar raquete</Link>
          </Button>
          {clerkAvailable && <AuthButtons />}
        </div>

        {/* Mobile hamburger */}
        <div className="flex md:hidden ml-auto">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Abrir menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right">
              <SheetHeader>
                <SheetTitle>
                  <Link href="/" onClick={() => setOpen(false)} className="font-bold text-xl text-primary">
                    PickleIQ
                  </Link>
                </SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col space-y-4 mt-6">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-foreground/80 text-lg font-medium transition-colors hover:text-foreground"
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
