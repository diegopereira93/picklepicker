"use client"

import * as React from "react"

type Theme = "dark" | "light" | "system"

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
  attribute?: string
  enableSystem?: boolean
  disableTransitionOnChange?: boolean
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
}

const ThemeProviderContext = React.createContext<ThemeProviderState>(initialState)

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "pickleiq-theme",
  attribute = "class",
  enableSystem = true,
  disableTransitionOnChange = false,
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = React.useState<Theme>(() => {
    if (typeof window !== "undefined" && window.localStorage) {
      const stored = window.localStorage.getItem(storageKey) as Theme | null
      if (stored) return stored
    }
    return defaultTheme
  })

  React.useEffect(() => {
    const root = document.documentElement
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")

    const applyTheme = (t: Theme) => {
      root.removeAttribute(attribute)
      const resolvedTheme =
        t === "system" && enableSystem ? (mediaQuery.matches ? "dark" : "light") : t

      if (resolvedTheme === "dark") {
        root.classList.add("dark")
      } else if (resolvedTheme === "light") {
        root.classList.remove("dark")
      }
    }

    applyTheme(theme)

    const handleChange = () => {
      if (theme === "system" && enableSystem) {
        applyTheme("system")
      }
    }

    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme, attribute, enableSystem])

  React.useEffect(() => {
    if (disableTransitionOnChange) {
      document.documentElement.classList.add("[&_*]:!transition-none")
      window.setTimeout(() => {
        document.documentElement.classList.remove("[&_*]:!transition-none")
      }, 0)
    }
  }, [theme, disableTransitionOnChange])

  const value = {
    theme,
    setTheme: (newTheme: Theme) => {
      if (typeof window !== "undefined" && window.localStorage) {
        window.localStorage.setItem(storageKey, newTheme)
      }
      setTheme(newTheme)
    },
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export const useTheme = () => {
  const context = React.useContext(ThemeProviderContext)
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}
