"use client"

import { createContext, useContext, ReactNode } from "react"

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

export function useClerkAvailable() {
  return useContext(ClerkAvailableContext)
}
