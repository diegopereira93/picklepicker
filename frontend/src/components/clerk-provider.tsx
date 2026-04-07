"use client";

import { useEffect, useState, type ReactNode } from "react";
import { ClerkProvider } from "@clerk/nextjs";

const hasClerkKey = typeof window !== "undefined"
  ? !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  : true;

export function ClerkWrapper({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted || !hasClerkKey) return <>{children}</>;
  return <ClerkProvider>{children}</ClerkProvider>;
}
