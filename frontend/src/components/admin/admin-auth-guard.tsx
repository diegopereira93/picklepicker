'use client'

import React, { useState, useEffect, useCallback, createContext, useContext } from 'react'
import { getAdminSecret, clearAdminSecret, fetchQueue } from '@/lib/admin-api'

const ADMIN_SECRET_KEY = 'pickleiq:admin_secret'

interface AdminAuthContextValue {
  logout: () => void
}

const AdminAuthContext = createContext<AdminAuthContextValue>({ logout: () => {} })

export function useAdminAuth() {
  return useContext(AdminAuthContext)
}

interface AdminAuthGuardProps {
  children: React.ReactNode
  onLogout?: () => void
}

type AuthState = 'checking' | 'unauthenticated' | 'authenticated'

export function AdminAuthGuard({ children, onLogout }: AdminAuthGuardProps) {
  const [authState, setAuthState] = useState<AuthState>('checking')
  const [inputSecret, setInputSecret] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const verify = useCallback(async (secret: string) => {
    try {
      // Temporarily set the secret so fetchQueue can use it
      sessionStorage.setItem(ADMIN_SECRET_KEY, secret)
      await fetchQueue({ limit: 1 })
      setAuthState('authenticated')
    } catch {
      clearAdminSecret()
      setAuthState('unauthenticated')
      setError('Senha incorreta')
    }
  }, [])

  useEffect(() => {
    const stored = getAdminSecret()
    if (!stored) {
      setAuthState('unauthenticated')
      return
    }
    verify(stored)
  }, [verify])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputSecret.trim()) return
    setLoading(true)
    setError(null)
    await verify(inputSecret.trim())
    setLoading(false)
  }

  const handleLogout = () => {
    clearAdminSecret()
    setAuthState('unauthenticated')
    setInputSecret('')
    setError(null)
    onLogout?.()
  }

  if (authState === 'checking') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Verificando acesso...</p>
      </div>
    )
  }

  if (authState === 'unauthenticated') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-full max-w-sm p-6 border rounded-lg shadow-sm bg-card">
          <h1 className="text-2xl font-bold text-center mb-6">Admin PickleIQ</h1>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="admin-secret" className="block text-sm font-medium mb-1">
                Senha de administrador
              </label>
              <input
                id="admin-secret"
                type="password"
                placeholder="Senha admin"
                value={inputSecret}
                onChange={(e) => setInputSecret(e.target.value)}
                className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                autoComplete="current-password"
                disabled={loading}
              />
            </div>
            {error && (
              <p className="text-sm text-destructive font-medium">{error}</p>
            )}
            <button
              type="submit"
              disabled={loading || !inputSecret.trim()}
              className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Verificando...' : 'Entrar'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <AdminAuthContext.Provider value={{ logout: handleLogout }}>
      {children}
    </AdminAuthContext.Provider>
  )
}
