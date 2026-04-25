"use client"

import { SignInButton, UserButton, useAuth } from "@clerk/nextjs"
import { Button } from "@/components/ui/button"
import { useClerkAvailable } from "@/components/clerk-provider"

export function ClerkAuthButtons() {
  const clerkAvailable = useClerkAvailable()
  if (!clerkAvailable) return null
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

export function MobileClerkAuth() {
  const clerkAvailable = useClerkAvailable()
  if (!clerkAvailable) return null
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
