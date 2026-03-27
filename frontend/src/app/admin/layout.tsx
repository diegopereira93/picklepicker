'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { AdminAuthGuard, useAdminAuth } from '@/components/admin/admin-auth-guard'

function AdminNav() {
  const pathname = usePathname()
  const { logout } = useAdminAuth()

  const navLinks = [
    { href: '/admin/queue', label: 'Fila de Revisão' },
    { href: '/admin/catalog', label: 'Catálogo' },
  ]

  return (
    <header className="border-b bg-card px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <span className="font-bold text-lg">PickleIQ Admin</span>
        <nav className="hidden sm:flex items-center gap-4">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                pathname?.startsWith(link.href)
                  ? 'text-primary underline underline-offset-4'
                  : 'text-muted-foreground'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
      <button
        onClick={logout}
        className="text-sm text-muted-foreground hover:text-destructive transition-colors"
      >
        Sair
      </button>
    </header>
  )
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminAuthGuard>
      <div className="min-h-screen bg-background flex flex-col">
        <AdminNav />
        {/* Mobile nav */}
        <nav className="sm:hidden border-b bg-card px-4 py-2 flex gap-4">
          <Link href="/admin/queue" className="text-sm font-medium text-muted-foreground hover:text-primary">
            Fila
          </Link>
          <Link href="/admin/catalog" className="text-sm font-medium text-muted-foreground hover:text-primary">
            Catálogo
          </Link>
        </nav>
        <main className="flex-1 p-4 md:p-6 max-w-6xl mx-auto w-full">
          {children}
        </main>
      </div>
    </AdminAuthGuard>
  )
}
