"use client"

import Link from "next/link"
import { useState, createContext, useContext, ReactNode } from "react"
import { Moon, Sun, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { useTheme } from "next-themes"
const navLinks = [
  { href: "/", label: "HOME" },
  { href: "/quiz", label: "QUIZ" },
  { href: "/paddles", label: "CATÁLOGO" },
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

function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="w-9 h-9 rounded-lg flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
      aria-label={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
    >
      {theme === 'dark' ? (
        <Sun className="h-5 w-5 text-[#2A2A2A]" />
      ) : (
        <Moon className="h-5 w-5 text-[#2A2A2A]" />
      )}
    </button>
  )
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
    <header className="sticky top-0 z-50 w-full bg-[#FAFAF8] border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center">
        <Link href="/" className="text-[#2A2A2A] font-bold text-xl mr-6 flex items-center">
          <span className="font-bold text-[#2A2A2A]">Pickle<span className="text-[#F97316]">IQ</span></span>
        </Link>

        <nav className="hidden md:flex items-center space-x-6 flex-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-[#2A2A2A] font-semibold text-sm hover:text-[#F97316] transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden md:flex items-center space-x-2 ml-auto">
          <ThemeToggle />
          <Button asChild size="sm" className="wg-button-coral">
            <Link href="/quiz">Encontrar raquete</Link>
          </Button>
          {clerkAvailable && <AuthButtons />}
        </div>

        <div className="md:hidden flex ml-auto">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Abrir menu">
                <Menu className="h-5 w-5 text-[#2A2A2A]" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="bg-[#FAFAF8]">
              <SheetHeader>
                <SheetTitle>
                  <Link href="/" onClick={() => setOpen(false)} className="text-[#2A2A2A] font-bold text-xl">
                    Pickle<span className="text-[#F97316]">IQ</span>
                  </Link>
                </SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col space-y-4 mt-6">
                <ThemeToggle />
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-[#2A2A2A] font-semibold text-sm"
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
