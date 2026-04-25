"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { ClerkProvider } from "@clerk/nextjs";

const ClerkAvailableContext = createContext(false);

export function useClerkAvailable(): boolean {
  return useContext(ClerkAvailableContext);
}

const hasClerkKey = typeof window !== "undefined"
  ? !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  : true;

export function ClerkWrapper({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted || !hasClerkKey) {
    return (
      <ClerkAvailableContext.Provider value={false}>
        {children}
      </ClerkAvailableContext.Provider>
    );
  }

  return (
    <ClerkProvider>
      <ClerkAvailableContext.Provider value={true}>
        {children}
      </ClerkAvailableContext.Provider>
    </ClerkProvider>
  );
}
